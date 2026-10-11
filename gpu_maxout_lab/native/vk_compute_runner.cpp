#include <vulkan/vulkan.h>
#include <algorithm>
#include <chrono>
#include <cmath>
#include <cstdint>
#include <cstdlib>
#include <cstring>
#include <ctime>
#include <fstream>
#include <iostream>
#include <numeric>
#include <set>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

using Clock=std::chrono::steady_clock;
static void ck(VkResult r,const char* w){ if(r!=VK_SUCCESS) throw std::runtime_error(std::string(w)+" failed: "+std::to_string(int(r))); }
static std::vector<uint32_t> read_spv(const std::string&p){ std::ifstream f(p,std::ios::binary|std::ios::ate); if(!f) throw std::runtime_error("cannot open SPV"); std::streamsize n=static_cast<std::streamsize>(f.tellg()); if(n<=0||(n%4)!=0) throw std::runtime_error("bad SPV size"); std::vector<uint32_t>v(size_t(n)/4); f.seekg(0); f.read(reinterpret_cast<char*>(v.data()),n); if(!f) throw std::runtime_error("short SPV read"); return v; }
static std::string esc(const char*s){ std::ostringstream o; for(;*s;++s){ if(*s=='"'||*s=='\\')o<<'\\'<<*s; else if((unsigned char)*s>=32)o<<*s; } return o.str(); }
struct Args{uint32_t dispatch_batch=0;bool pipeline_rt=false,hybrid=false;std::string miss_spv,hit_spv;bool rt=false;std::string rt_hint="fast_trace";std::string memory_pattern="sequential_read";uint32_t rt_pack=1;uint32_t memory_oracle_items=0;std::string spv,out;int gpu=0;uint32_t threads=131072,local=128,input_mb=64,input_kib=0,loops=256,warmup_ms=500,measure_ms=1000,inflight=1,chunk_groups=0,subgroup=0;};
static Args parse(int ac,char**av){Args a;for(int i=1;i<ac;i++){std::string s=av[i];auto need=[&](){if(i+1>=ac)throw std::runtime_error("missing value for "+s);return std::string(av[++i]);};if(s=="--dispatch-batch")a.dispatch_batch=std::stoul(need());else if(s=="--rt-pipeline"){a.rt=true;a.pipeline_rt=true;}else if(s=="--hybrid"){a.rt=true;a.hybrid=true;}else if(s=="--miss-spv")a.miss_spv=need();else if(s=="--hit-spv")a.hit_spv=need();else if(s=="--rt")a.rt=true;else if(s=="--rt-pack")a.rt_pack=std::stoul(need());else if(s=="--rt-build-hint")a.rt_hint=need();else if(s=="--memory-pattern")a.memory_pattern=need();else if(s=="--spv")a.spv=need();else if(s=="--output")a.out=need();else if(s=="--gpu")a.gpu=std::stoi(need());else if(s=="--threads")a.threads=std::stoul(need());else if(s=="--local")a.local=std::stoul(need());else if(s=="--input-mb")a.input_mb=std::stoul(need());else if(s=="--input-kib")a.input_kib=std::stoul(need());else if(s=="--memory-oracle-items")a.memory_oracle_items=std::stoul(need());else if(s=="--loops")a.loops=std::stoul(need());else if(s=="--warmup-ms")a.warmup_ms=std::stoul(need());else if(s=="--measure-ms")a.measure_ms=std::stoul(need());else if(s=="--inflight")a.inflight=static_cast<uint32_t>(std::max(1,std::stoi(need())));else if(s=="--chunk-groups")a.chunk_groups=std::stoul(need());else if(s=="--subgroup-size")a.subgroup=std::stoul(need());else throw std::runtime_error("unknown arg "+s);}if(a.spv.empty()||a.out.empty())throw std::runtime_error("--spv and --output required");if(!a.threads||!a.local||!a.loops||(!a.input_mb&&!a.input_kib)||a.inflight>16||a.dispatch_batch>256||a.rt_pack<1||a.rt_pack>8||a.memory_oracle_items>a.threads)throw std::runtime_error("invalid dimensions");if(a.rt_hint!="fast_trace"&&a.rt_hint!="fast_build")throw std::runtime_error("invalid RT build hint");if(a.pipeline_rt&&(a.hybrid||a.local!=1||a.subgroup||a.miss_spv.empty()||a.hit_spv.empty()))throw std::runtime_error("RT pipeline requires local=1, no subgroup, miss/hit shaders and no hybrid flag");return a;}
struct Buf{VkBuffer b=VK_NULL_HANDLE;VkDeviceMemory m=VK_NULL_HANDLE;VkDeviceSize size=0;};
struct Ctx{VkInstance inst=VK_NULL_HANDLE;VkPhysicalDevice pd=VK_NULL_HANDLE;VkDevice dev=VK_NULL_HANDLE;VkQueue q=VK_NULL_HANDLE;uint32_t qf=0;VkPhysicalDeviceProperties prop{};VkPhysicalDeviceMemoryProperties mem{};};
static uint32_t memtype(const Ctx&c,uint32_t bits,VkMemoryPropertyFlags flags){for(uint32_t i=0;i<c.mem.memoryTypeCount;i++)if((bits&(1u<<i))&&(c.mem.memoryTypes[i].propertyFlags&flags)==flags)return i;throw std::runtime_error("no compatible memory type");}
static Buf mkbuf(Ctx&c,VkDeviceSize sz,VkBufferUsageFlags use,VkMemoryPropertyFlags flags){Buf x;x.size=sz;VkBufferCreateInfo bi{};bi.sType=VK_STRUCTURE_TYPE_BUFFER_CREATE_INFO;bi.size=sz;bi.usage=use;bi.sharingMode=VK_SHARING_MODE_EXCLUSIVE;ck(vkCreateBuffer(c.dev,&bi,nullptr,&x.b),"vkCreateBuffer");VkMemoryRequirements mr{};vkGetBufferMemoryRequirements(c.dev,x.b,&mr);VkMemoryAllocateInfo ai{};ai.sType=VK_STRUCTURE_TYPE_MEMORY_ALLOCATE_INFO;ai.allocationSize=mr.size;ai.memoryTypeIndex=memtype(c,mr.memoryTypeBits,flags);VkMemoryAllocateFlagsInfo af{};af.sType=VK_STRUCTURE_TYPE_MEMORY_ALLOCATE_FLAGS_INFO;af.flags=VK_MEMORY_ALLOCATE_DEVICE_ADDRESS_BIT;if(use&VK_BUFFER_USAGE_SHADER_DEVICE_ADDRESS_BIT)ai.pNext=&af;ck(vkAllocateMemory(c.dev,&ai,nullptr,&x.m),"vkAllocateMemory");ck(vkBindBufferMemory(c.dev,x.b,x.m,0),"vkBindBufferMemory");return x;}
static void freebuf(Ctx&c,Buf&b){if(b.b)vkDestroyBuffer(c.dev,b.b,nullptr);if(b.m)vkFreeMemory(c.dev,b.m,nullptr);b={};}
static void onecopy(Ctx&c,VkCommandPool pool,VkBuffer s,VkBuffer d,VkDeviceSize n){VkCommandBufferAllocateInfo ai{};ai.sType=VK_STRUCTURE_TYPE_COMMAND_BUFFER_ALLOCATE_INFO;ai.commandPool=pool;ai.level=VK_COMMAND_BUFFER_LEVEL_PRIMARY;ai.commandBufferCount=1;VkCommandBuffer cb;ck(vkAllocateCommandBuffers(c.dev,&ai,&cb),"alloc copy cb");VkCommandBufferBeginInfo bi{};bi.sType=VK_STRUCTURE_TYPE_COMMAND_BUFFER_BEGIN_INFO;bi.flags=VK_COMMAND_BUFFER_USAGE_ONE_TIME_SUBMIT_BIT;ck(vkBeginCommandBuffer(cb,&bi),"begin copy");VkMemoryBarrier mb{};mb.sType=VK_STRUCTURE_TYPE_MEMORY_BARRIER;mb.srcAccessMask=VK_ACCESS_MEMORY_WRITE_BIT;mb.dstAccessMask=VK_ACCESS_TRANSFER_READ_BIT;vkCmdPipelineBarrier(cb,VK_PIPELINE_STAGE_ALL_COMMANDS_BIT,VK_PIPELINE_STAGE_TRANSFER_BIT,0,1,&mb,0,nullptr,0,nullptr);VkBufferCopy r{0,0,n};vkCmdCopyBuffer(cb,s,d,1,&r);mb.srcAccessMask=VK_ACCESS_TRANSFER_WRITE_BIT;mb.dstAccessMask=VK_ACCESS_MEMORY_READ_BIT;vkCmdPipelineBarrier(cb,VK_PIPELINE_STAGE_TRANSFER_BIT,VK_PIPELINE_STAGE_ALL_COMMANDS_BIT,0,1,&mb,0,nullptr,0,nullptr);ck(vkEndCommandBuffer(cb),"end copy");VkFenceCreateInfo fi{};fi.sType=VK_STRUCTURE_TYPE_FENCE_CREATE_INFO;VkFence f;ck(vkCreateFence(c.dev,&fi,nullptr,&f),"copy fence");VkSubmitInfo si{};si.sType=VK_STRUCTURE_TYPE_SUBMIT_INFO;si.commandBufferCount=1;si.pCommandBuffers=&cb;ck(vkQueueSubmit(c.q,1,&si,f),"copy submit");ck(vkWaitForFences(c.dev,1,&f,VK_TRUE,UINT64_MAX),"copy wait");vkDestroyFence(c.dev,f,nullptr);vkFreeCommandBuffers(c.dev,pool,1,&cb);}
#include "rt_scene.hpp"
#include "rt_pipeline.hpp"
struct PC{uint32_t threads,input_words,seed,loops,base_item;};
struct Slot{VkCommandBuffer cb=VK_NULL_HANDLE;VkFence fence=VK_NULL_HANDLE;uint32_t q0=0,q1=0;uint32_t base=0,groups=0,repeats=0;bool recorded=false,live=false;Clock::time_point submit_t;};
static double ms_since(Clock::time_point a,Clock::time_point b){return std::chrono::duration<double,std::milli>(b-a).count();}
static double pctile(std::vector<double> v,double p){if(v.empty())return 0;std::sort(v.begin(),v.end());size_t i=size_t(std::llround((v.size()-1)*p));return v[std::min(i,v.size()-1)];}
static uint64_t monotonic_ns(){timespec ts{};if(clock_gettime(CLOCK_MONOTONIC,&ts))throw std::runtime_error("monotonic clock failed");return uint64_t(ts.tv_sec)*1000000000ull+uint64_t(ts.tv_nsec);}
static uint32_t mix32(uint32_t x){x^=x>>16;x*=0x7feb352du;x^=x>>15;x*=0x846ca68bu;x^=x>>16;return x;}
static uint32_t fold32(uint32_t h,uint32_t x){return h^mix32(x+0x9e3779b9u+(h<<6)+(h>>2));}
static uint32_t memory_expected(const std::vector<uint32_t>& input,uint32_t gid,uint32_t loops,const std::string& pattern){uint32_t h=0x811c9dc5u;uint64_t start=(uint64_t(gid)*16u)%input.size();if(pattern=="pointer_chase"){for(uint32_t k=0;k<loops;k++){uint32_t r=input[start];h=fold32(h,r);start=(uint64_t(r)+257u)%input.size();}return h;}uint32_t stride=1;if(pattern.rfind("read_stride",0)==0)stride=std::max(1,std::stoi(pattern.substr(11)));bool random_mode=pattern=="random"||pattern=="gather";for(uint32_t k=0;k<loops;k++){for(uint32_t j=0;j<16;j++){uint32_t offset=j*(pattern=="gather"?13u:0x9e37u);uint64_t index=random_mode?uint64_t(mix32(uint32_t(start+offset)))%input.size():(start+uint64_t(j)*stride)%input.size();h=fold32(h,input[index]);}start=(start+257u)%input.size();}return h;}
int main(int argc,char**argv){
 try{
  Args a=parse(argc,argv);
  VkApplicationInfo app{};app.sType=VK_STRUCTURE_TYPE_APPLICATION_INFO;app.pApplicationName="ASTRO GPU Max-Out Probe";app.apiVersion=a.rt?VK_API_VERSION_1_2:VK_API_VERSION_1_1;VkInstanceCreateInfo ici{};ici.sType=VK_STRUCTURE_TYPE_INSTANCE_CREATE_INFO;ici.pApplicationInfo=&app;Ctx c;ck(vkCreateInstance(&ici,nullptr,&c.inst),"vkCreateInstance");
  uint32_t nd=0;ck(vkEnumeratePhysicalDevices(c.inst,&nd,nullptr),"enum gpu count");if(a.gpu<0||a.gpu>=int(nd))throw std::runtime_error("GPU index out of range");std::vector<VkPhysicalDevice> pds(nd);ck(vkEnumeratePhysicalDevices(c.inst,&nd,pds.data()),"enum gpus");c.pd=pds[a.gpu];vkGetPhysicalDeviceProperties(c.pd,&c.prop);vkGetPhysicalDeviceMemoryProperties(c.pd,&c.mem);
  uint32_t nq=0;vkGetPhysicalDeviceQueueFamilyProperties(c.pd,&nq,nullptr);std::vector<VkQueueFamilyProperties>qf(nq);vkGetPhysicalDeviceQueueFamilyProperties(c.pd,&nq,qf.data());bool found=false;for(uint32_t i=0;i<nq;i++)if(qf[i].queueFlags&VK_QUEUE_COMPUTE_BIT){c.qf=i;found=true;break;}if(!found)throw std::runtime_error("no compute queue");if(!qf[c.qf].timestampValidBits)throw std::runtime_error("compute timestamps unsupported");if(a.local>c.prop.limits.maxComputeWorkGroupInvocations||a.local>c.prop.limits.maxComputeWorkGroupSize[0])throw std::runtime_error("local size exceeds device limit");
  uint32_t ne=0;vkEnumerateDeviceExtensionProperties(c.pd,nullptr,&ne,nullptr);std::vector<VkExtensionProperties> ep(ne);vkEnumerateDeviceExtensionProperties(c.pd,nullptr,&ne,ep.data());std::set<std::string> ext;for(auto&x:ep)ext.insert(x.extensionName);
  float pri=1.0f;VkDeviceQueueCreateInfo qci{};qci.sType=VK_STRUCTURE_TYPE_DEVICE_QUEUE_CREATE_INFO;qci.queueFamilyIndex=c.qf;qci.queueCount=1;qci.pQueuePriorities=&pri;
  std::vector<const char*> enabled;
#ifdef VK_EXT_subgroup_size_control
  VkPhysicalDeviceSubgroupSizeControlFeaturesEXT sgf{};sgf.sType=VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_SUBGROUP_SIZE_CONTROL_FEATURES_EXT;
  VkPhysicalDeviceFeatures2 f2{};f2.sType=VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_FEATURES_2;f2.pNext=&sgf;vkGetPhysicalDeviceFeatures2(c.pd,&f2);
  bool want_sg=a.subgroup!=0;bool have_sg=ext.count(VK_EXT_SUBGROUP_SIZE_CONTROL_EXTENSION_NAME)&&sgf.subgroupSizeControl;
  if(want_sg&&!have_sg)throw std::runtime_error("required subgroup size requested but VK_EXT_subgroup_size_control unavailable");
  if(have_sg){enabled.push_back(VK_EXT_SUBGROUP_SIZE_CONTROL_EXTENSION_NAME);sgf.subgroupSizeControl=VK_TRUE;sgf.computeFullSubgroups=VK_FALSE;}
#else
  bool want_sg=a.subgroup!=0;bool have_sg=false;if(want_sg)throw std::runtime_error("subgroup size control not in Vulkan headers");
#endif
  VkDeviceCreateInfo dci{};dci.sType=VK_STRUCTURE_TYPE_DEVICE_CREATE_INFO;dci.queueCreateInfoCount=1;dci.pQueueCreateInfos=&qci;dci.enabledExtensionCount=uint32_t(enabled.size());dci.ppEnabledExtensionNames=enabled.empty()?nullptr:enabled.data();
#ifdef VK_EXT_subgroup_size_control
  dci.pNext=have_sg?&sgf:nullptr;
#endif
  VkPhysicalDeviceBufferDeviceAddressFeatures bda{};
  bda.sType=VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_BUFFER_DEVICE_ADDRESS_FEATURES;
  VkPhysicalDeviceAccelerationStructureFeaturesKHR asf{};
  asf.sType=VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_ACCELERATION_STRUCTURE_FEATURES_KHR;
  VkPhysicalDeviceRayQueryFeaturesKHR rq{};
  rq.sType=VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_RAY_QUERY_FEATURES_KHR;
  VkPhysicalDeviceRayTracingPipelineFeaturesKHR rtf{};rtf.sType=VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_RAY_TRACING_PIPELINE_FEATURES_KHR;
  if(a.rt){
    if(c.prop.apiVersion<VK_API_VERSION_1_2)throw std::runtime_error("RT backend requires Vulkan 1.2");
    for(const char* name:{VK_KHR_ACCELERATION_STRUCTURE_EXTENSION_NAME,(a.pipeline_rt?VK_KHR_RAY_TRACING_PIPELINE_EXTENSION_NAME:VK_KHR_RAY_QUERY_EXTENSION_NAME),VK_KHR_DEFERRED_HOST_OPERATIONS_EXTENSION_NAME}){
      if(!ext.count(name))throw std::runtime_error(std::string("missing RT extension: ")+name);
      enabled.push_back(name);
    }
    VkPhysicalDeviceFeatures2 features{};features.sType=VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_FEATURES_2;
    features.pNext=&bda;bda.pNext=&asf;asf.pNext=a.pipeline_rt?static_cast<void*>(&rtf):static_cast<void*>(&rq);vkGetPhysicalDeviceFeatures2(c.pd,&features);
    if(!bda.bufferDeviceAddress||!asf.accelerationStructure||(a.pipeline_rt?!rtf.rayTracingPipeline:!rq.rayQuery))throw std::runtime_error("RT feature bits unavailable");
    bda.bufferDeviceAddressCaptureReplay=VK_FALSE;bda.bufferDeviceAddressMultiDevice=VK_FALSE;
    asf.accelerationStructureCaptureReplay=VK_FALSE;asf.accelerationStructureIndirectBuild=VK_FALSE;
    asf.accelerationStructureHostCommands=VK_FALSE;asf.descriptorBindingAccelerationStructureUpdateAfterBind=VK_FALSE;
    if(a.pipeline_rt){
      rtf.rayTracingPipelineShaderGroupHandleCaptureReplay=VK_FALSE;
      rtf.rayTracingPipelineShaderGroupHandleCaptureReplayMixed=VK_FALSE;
      rtf.rayTracingPipelineTraceRaysIndirect=VK_FALSE;rtf.rayTraversalPrimitiveCulling=VK_FALSE;
      rtf.pNext=const_cast<void*>(dci.pNext);
    }else rq.pNext=const_cast<void*>(dci.pNext);
    dci.pNext=&bda;
    dci.enabledExtensionCount=uint32_t(enabled.size());dci.ppEnabledExtensionNames=enabled.data();
  }
  ck(vkCreateDevice(c.pd,&dci,nullptr,&c.dev),"vkCreateDevice");vkGetDeviceQueue(c.dev,c.qf,0,&c.q);

  VkCommandPoolCreateInfo cpci{};cpci.sType=VK_STRUCTURE_TYPE_COMMAND_POOL_CREATE_INFO;cpci.queueFamilyIndex=c.qf;cpci.flags=VK_COMMAND_POOL_CREATE_RESET_COMMAND_BUFFER_BIT;VkCommandPool pool;ck(vkCreateCommandPool(c.dev,&cpci,nullptr,&pool),"cmd pool");
  RtScene scene;if(a.rt)scene.create(c,pool,a.rt_hint,a.pipeline_rt);
  VkShaderStageFlags shader_stages=a.pipeline_rt?VK_SHADER_STAGE_RAYGEN_BIT_KHR:VK_SHADER_STAGE_COMPUTE_BIT;
  VkPipelineStageFlagBits execution_stage=a.pipeline_rt?VK_PIPELINE_STAGE_RAY_TRACING_SHADER_BIT_KHR:VK_PIPELINE_STAGE_COMPUTE_SHADER_BIT;
  VkPipelineBindPoint bind_point=a.pipeline_rt?VK_PIPELINE_BIND_POINT_RAY_TRACING_KHR:VK_PIPELINE_BIND_POINT_COMPUTE;
  VkDeviceSize input_sz=a.input_kib?VkDeviceSize(a.input_kib)*1024ull:VkDeviceSize(a.input_mb)*1024ull*1024ull;VkDeviceSize out_sz=VkDeviceSize(a.threads)*4ull;VkDeviceSize meta_sz=4096;
  Buf input=mkbuf(c,input_sz,VK_BUFFER_USAGE_STORAGE_BUFFER_BIT|VK_BUFFER_USAGE_TRANSFER_DST_BIT,VK_MEMORY_PROPERTY_DEVICE_LOCAL_BIT);
  Buf output=mkbuf(c,out_sz,VK_BUFFER_USAGE_STORAGE_BUFFER_BIT|VK_BUFFER_USAGE_TRANSFER_SRC_BIT,VK_MEMORY_PROPERTY_DEVICE_LOCAL_BIT);
  Buf meta=mkbuf(c,meta_sz,VK_BUFFER_USAGE_STORAGE_BUFFER_BIT|VK_BUFFER_USAGE_TRANSFER_SRC_BIT,VK_MEMORY_PROPERTY_DEVICE_LOCAL_BIT);
  Buf stin=mkbuf(c,input_sz,VK_BUFFER_USAGE_TRANSFER_SRC_BIT,VK_MEMORY_PROPERTY_HOST_VISIBLE_BIT|VK_MEMORY_PROPERTY_HOST_COHERENT_BIT);
  Buf stout=mkbuf(c,out_sz,VK_BUFFER_USAGE_TRANSFER_DST_BIT,VK_MEMORY_PROPERTY_HOST_VISIBLE_BIT|VK_MEMORY_PROPERTY_HOST_COHERENT_BIT);
  std::vector<uint32_t> host_input(size_t(input_sz/4));void*pm=nullptr;ck(vkMapMemory(c.dev,stin.m,0,input_sz,0,&pm),"map input");uint32_t*ip=(uint32_t*)pm;uint64_t nw=input_sz/4;uint32_t x=0x12345678u;for(uint64_t i=0;i<nw;i++){x^=x<<13;x^=x>>17;x^=x<<5;host_input[size_t(i)]=x+uint32_t(i*0x9e3779b9u);ip[i]=host_input[size_t(i)];}vkUnmapMemory(c.dev,stin.m);onecopy(c,pool,stin.b,input.b,input_sz);

  VkDescriptorSetLayoutBinding binds[4]{};for(uint32_t i=0;i<3;i++){binds[i].binding=i;binds[i].descriptorType=VK_DESCRIPTOR_TYPE_STORAGE_BUFFER;binds[i].descriptorCount=1;binds[i].stageFlags=shader_stages;}
  if(a.rt){binds[3].binding=3;binds[3].descriptorType=VK_DESCRIPTOR_TYPE_ACCELERATION_STRUCTURE_KHR;binds[3].descriptorCount=1;binds[3].stageFlags=shader_stages;}
  VkDescriptorSetLayoutCreateInfo slci{};slci.sType=VK_STRUCTURE_TYPE_DESCRIPTOR_SET_LAYOUT_CREATE_INFO;slci.bindingCount=a.rt?4:3;slci.pBindings=binds;VkDescriptorSetLayout dsl;ck(vkCreateDescriptorSetLayout(c.dev,&slci,nullptr,&dsl),"dsl");
  VkPushConstantRange pcr{};pcr.stageFlags=shader_stages;pcr.offset=0;pcr.size=sizeof(PC);VkPipelineLayoutCreateInfo plci{};plci.sType=VK_STRUCTURE_TYPE_PIPELINE_LAYOUT_CREATE_INFO;plci.setLayoutCount=1;plci.pSetLayouts=&dsl;plci.pushConstantRangeCount=1;plci.pPushConstantRanges=&pcr;VkPipelineLayout layout;ck(vkCreatePipelineLayout(c.dev,&plci,nullptr,&layout),"pipeline layout");
  RtPipeline rtpipe;VkShaderModule sm=VK_NULL_HANDLE;VkPipeline pipe=VK_NULL_HANDLE;
  if(a.pipeline_rt){rtpipe.create(c,layout,a.spv,a.miss_spv,a.hit_spv);pipe=rtpipe.pipeline;}
  else{
  auto code=read_spv(a.spv);VkShaderModuleCreateInfo smci{};smci.sType=VK_STRUCTURE_TYPE_SHADER_MODULE_CREATE_INFO;smci.codeSize=code.size()*4;smci.pCode=code.data();ck(vkCreateShaderModule(c.dev,&smci,nullptr,&sm),"shader module");
  VkPipelineShaderStageCreateInfo stage{};stage.sType=VK_STRUCTURE_TYPE_PIPELINE_SHADER_STAGE_CREATE_INFO;stage.stage=VK_SHADER_STAGE_COMPUTE_BIT;stage.module=sm;stage.pName="main";
#ifdef VK_EXT_subgroup_size_control
  VkPipelineShaderStageRequiredSubgroupSizeCreateInfoEXT req{};req.sType=VK_STRUCTURE_TYPE_PIPELINE_SHADER_STAGE_REQUIRED_SUBGROUP_SIZE_CREATE_INFO_EXT;if(a.subgroup){req.requiredSubgroupSize=a.subgroup;stage.pNext=&req;}
#endif
  VkComputePipelineCreateInfo pci{};pci.sType=VK_STRUCTURE_TYPE_COMPUTE_PIPELINE_CREATE_INFO;pci.stage=stage;pci.layout=layout;pci.flags=VK_PIPELINE_CREATE_DISPATCH_BASE_BIT;ck(vkCreateComputePipelines(c.dev,VK_NULL_HANDLE,1,&pci,nullptr,&pipe),"compute pipeline");
  }
  VkDescriptorPoolSize ps[2]={{VK_DESCRIPTOR_TYPE_STORAGE_BUFFER,3},{VK_DESCRIPTOR_TYPE_ACCELERATION_STRUCTURE_KHR,1}};VkDescriptorPoolCreateInfo dpci{};dpci.sType=VK_STRUCTURE_TYPE_DESCRIPTOR_POOL_CREATE_INFO;dpci.maxSets=1;dpci.poolSizeCount=a.rt?2:1;dpci.pPoolSizes=ps;VkDescriptorPool dp;ck(vkCreateDescriptorPool(c.dev,&dpci,nullptr,&dp),"descriptor pool");VkDescriptorSetAllocateInfo dsai{};dsai.sType=VK_STRUCTURE_TYPE_DESCRIPTOR_SET_ALLOCATE_INFO;dsai.descriptorPool=dp;dsai.descriptorSetCount=1;dsai.pSetLayouts=&dsl;VkDescriptorSet ds;ck(vkAllocateDescriptorSets(c.dev,&dsai,&ds),"descriptor set");
  VkDescriptorBufferInfo dbi[3]={{input.b,0,input_sz},{output.b,0,out_sz},{meta.b,0,meta_sz}};VkWriteDescriptorSet wr[3]{};for(uint32_t i=0;i<3;i++){wr[i].sType=VK_STRUCTURE_TYPE_WRITE_DESCRIPTOR_SET;wr[i].dstSet=ds;wr[i].dstBinding=i;wr[i].descriptorCount=1;wr[i].descriptorType=VK_DESCRIPTOR_TYPE_STORAGE_BUFFER;wr[i].pBufferInfo=&dbi[i];}vkUpdateDescriptorSets(c.dev,3,wr,0,nullptr);
  if(a.rt){VkWriteDescriptorSetAccelerationStructureKHR asw{};asw.sType=VK_STRUCTURE_TYPE_WRITE_DESCRIPTOR_SET_ACCELERATION_STRUCTURE_KHR;asw.accelerationStructureCount=1;asw.pAccelerationStructures=&scene.tlas;VkWriteDescriptorSet w{};w.sType=VK_STRUCTURE_TYPE_WRITE_DESCRIPTOR_SET;w.pNext=&asw;w.dstSet=ds;w.dstBinding=3;w.descriptorCount=1;w.descriptorType=VK_DESCRIPTOR_TYPE_ACCELERATION_STRUCTURE_KHR;vkUpdateDescriptorSets(c.dev,1,&w,0,nullptr);}

  uint32_t depth=std::max<uint32_t>(1u,a.inflight);VkQueryPoolCreateInfo qpci{};qpci.sType=VK_STRUCTURE_TYPE_QUERY_POOL_CREATE_INFO;qpci.queryType=VK_QUERY_TYPE_TIMESTAMP;qpci.queryCount=depth*2;VkQueryPool qp;ck(vkCreateQueryPool(c.dev,&qpci,nullptr,&qp),"query pool");std::vector<Slot>slots(depth);std::vector<VkCommandBuffer> cbs(depth);VkCommandBufferAllocateInfo cbai{};cbai.sType=VK_STRUCTURE_TYPE_COMMAND_BUFFER_ALLOCATE_INFO;cbai.commandPool=pool;cbai.level=VK_COMMAND_BUFFER_LEVEL_PRIMARY;cbai.commandBufferCount=depth;ck(vkAllocateCommandBuffers(c.dev,&cbai,cbs.data()),"command buffers");for(uint32_t i=0;i<depth;i++){slots[i].cb=cbs[i];slots[i].q0=2*i;slots[i].q1=2*i+1;VkFenceCreateInfo fi{};fi.sType=VK_STRUCTURE_TYPE_FENCE_CREATE_INFO;ck(vkCreateFence(c.dev,&fi,nullptr,&slots[i].fence),"fence");}
  PC pc{a.threads,uint32_t(input_sz/4),0xa57f31cdu,a.loops,0};uint32_t items_per_group=a.local*(a.rt?a.rt_pack:1);uint32_t total_groups=uint32_t((uint64_t(a.threads)+items_per_group-1)/items_per_group);if(!a.pipeline_rt&&total_groups>c.prop.limits.maxComputeWorkGroupCount[0])throw std::runtime_error("dispatch exceeds device limit");uint32_t chunk=a.chunk_groups?a.chunk_groups:total_groups;chunk=std::min(chunk,total_groups);
  uint32_t next_base=0,batch_repeats=1;
  uint64_t logical_items=0,dispatches=0,submissions=0,command_records=0;
  uint64_t measure_start_ns=0,measure_end_ns=0;
  std::vector<double> gpu_ms,calibration_ms;
  bool calibrating=false;
  double timestamp_ns=c.prop.limits.timestampPeriod,last_gpu_ms=0;
  auto record=[&](Slot& s,uint32_t base,uint32_t groups){
    // Only reuse after its fence completed. No ONE_TIME_SUBMIT flag on reusable buffers.
    ck(vkResetFences(c.dev,1,&s.fence),"reset fence");
    if(s.recorded && s.base==base && s.groups==groups && s.repeats==batch_repeats)return;
    ck(vkResetCommandBuffer(s.cb,0),"reset command");
    VkCommandBufferBeginInfo bi{};bi.sType=VK_STRUCTURE_TYPE_COMMAND_BUFFER_BEGIN_INFO;
    ck(vkBeginCommandBuffer(s.cb,&bi),"begin cb");
    VkMemoryBarrier waw{};waw.sType=VK_STRUCTURE_TYPE_MEMORY_BARRIER;
    waw.srcAccessMask=VK_ACCESS_SHADER_WRITE_BIT;waw.dstAccessMask=VK_ACCESS_SHADER_WRITE_BIT;
    vkCmdPipelineBarrier(s.cb,execution_stage,execution_stage,0,1,&waw,0,nullptr,0,nullptr);
    vkCmdResetQueryPool(s.cb,qp,s.q0,2);vkCmdWriteTimestamp(s.cb,execution_stage,qp,s.q0);
    vkCmdBindPipeline(s.cb,bind_point,pipe);vkCmdBindDescriptorSets(s.cb,bind_point,layout,0,1,&ds,0,nullptr);
    PC dispatch_pc=pc;if(a.pipeline_rt)dispatch_pc.base_item=base*items_per_group;
    vkCmdPushConstants(s.cb,layout,shader_stages,0,sizeof(PC),&dispatch_pc);
    for(uint32_t repeat=0;repeat<batch_repeats;repeat++){
      if(repeat)vkCmdPipelineBarrier(s.cb,execution_stage,execution_stage,0,1,&waw,0,nullptr,0,nullptr);
      if(a.pipeline_rt){
        if(uint64_t(groups)>uint64_t(c.prop.limits.maxComputeWorkGroupCount[0])*c.prop.limits.maxComputeWorkGroupSize[0])
          throw std::runtime_error("RT launch width exceeds device limit");
        rtpipe.dispatch(s.cb,groups);
      }else if(base==0&&groups==total_groups)vkCmdDispatch(s.cb,groups,1,1);
      else vkCmdDispatchBase(s.cb,base,0,0,groups,1,1);
    }
    vkCmdWriteTimestamp(s.cb,execution_stage,qp,s.q1);ck(vkEndCommandBuffer(s.cb),"end cb");
    s.base=base;s.groups=groups;s.repeats=batch_repeats;s.recorded=true;command_records++;
  };
  auto complete=[&](Slot&s,bool collect){
    if(!s.live)return;
    ck(vkWaitForFences(c.dev,1,&s.fence,VK_TRUE,UINT64_MAX),"wait fence");
    uint64_t ts[2]{};ck(vkGetQueryPoolResults(c.dev,qp,s.q0,2,sizeof(ts),ts,sizeof(uint64_t),VK_QUERY_RESULT_64_BIT|VK_QUERY_RESULT_WAIT_BIT),"query results");
    uint64_t mask=qf[c.qf].timestampValidBits>=64?UINT64_MAX:((uint64_t(1)<<qf[c.qf].timestampValidBits)-1);
    last_gpu_ms=double((ts[1]-ts[0])&mask)*timestamp_ns/1e6;
    if(calibrating && s.groups==chunk)calibration_ms.push_back(last_gpu_ms/s.repeats);
    if(collect){
      gpu_ms.push_back(last_gpu_ms);
      uint64_t start_item=uint64_t(s.base)*items_per_group,cap=uint64_t(s.groups)*items_per_group;
      uint64_t n=start_item>=a.threads?0:std::min<uint64_t>(cap,uint64_t(a.threads)-start_item);
      logical_items+=n*s.repeats;dispatches+=s.repeats;submissions++;
    }
    s.live=false;
  };
  auto submit_next=[&](Slot&s){uint32_t g=std::min(chunk,total_groups-next_base);record(s,next_base,g);VkSubmitInfo si{};si.sType=VK_STRUCTURE_TYPE_SUBMIT_INFO;si.commandBufferCount=1;si.pCommandBuffers=&s.cb;ck(vkQueueSubmit(c.q,1,&si,s.fence),"queue submit");s.live=true;s.submit_t=Clock::now();next_base+=g;if(next_base>=total_groups)next_base=0;};
  auto timed=[&](uint32_t duration_ms,bool collect){
    if(collect)measure_start_ns=monotonic_ns();
    auto t0=Clock::now();uint64_t it=0;
    while(true){
      Slot&s=slots[it%depth];complete(s,collect);submit_next(s);it++;
      if(ms_since(t0,Clock::now())>=duration_ms && it>=depth)break;
    }
    for(auto &s:slots)complete(s,collect);
    auto end=Clock::now();if(collect)measure_end_ns=monotonic_ns();
    return ms_since(t0,end);
  };
  // Initialize the entire deterministic payload; only full chunks train batching.
  next_base=0;
  for(uint32_t b=0;b<total_groups;){
    uint32_t g=std::min(chunk,total_groups-b);Slot&s=slots[0];
    complete(s,false);record(s,b,g);VkSubmitInfo si{};si.sType=VK_STRUCTURE_TYPE_SUBMIT_INFO;
    si.commandBufferCount=1;si.pCommandBuffers=&s.cb;ck(vkQueueSubmit(c.q,1,&si,s.fence),"prime submit");
    s.live=true;complete(s,false);if(g==chunk)calibration_ms.push_back(last_gpu_ms);b+=g;
  }
  // A few full-chunk probes avoid choosing a batch from a cold first dispatch.
  for(uint32_t i=0;i<3;i++){
    next_base=0;submit_next(slots[0]);complete(slots[0],false);calibration_ms.push_back(last_gpu_ms);
  }
  double calibration=pctile(calibration_ms,0.5);
  batch_repeats=a.dispatch_batch?a.dispatch_batch:uint32_t(std::clamp(std::ceil(4.0/std::max(calibration,0.001)),1.0,256.0));
  next_base=0;calibration_ms.clear();calibrating=true;double warm=timed(a.warmup_ms,false);calibrating=false;
  // A cold clock can under-size the first batch. Retune from the end of warmup,
  // using only full chunks and measured GPU time, never power or clock inputs.
  if(!a.dispatch_batch && !calibration_ms.empty()){
    size_t begin=calibration_ms.size()>32?calibration_ms.size()-32:0;
    calibration=pctile(std::vector<double>(calibration_ms.begin()+begin,calibration_ms.end()),0.5);
    uint32_t adjusted=uint32_t(std::clamp(std::ceil(4.0/std::max(calibration,0.001)),1.0,256.0));
    if(adjusted!=batch_repeats){batch_repeats=adjusted;warm+=timed(std::min(a.warmup_ms,100u),false);}
  }
  gpu_ms.clear();logical_items=0;dispatches=0;submissions=0;next_base=0;
  double wall=timed(a.measure_ms,true);ck(vkQueueWaitIdle(c.q),"measurement idle");
  onecopy(c,pool,output.b,stout.b,out_sz);void*po=nullptr;ck(vkMapMemory(c.dev,stout.m,0,out_sz,0,&po),"map output");uint64_t semantic_mismatches=0;uint32_t memory_oracle_items=std::min(a.memory_oracle_items,a.threads);if(a.rt){auto words=static_cast<const uint32_t*>(po);for(uint32_t gid=0;gid<a.threads;gid++)if(words[gid]!=rt_expected(gid,a.loops,pc.seed,a.hybrid))semantic_mismatches++;}else if(memory_oracle_items){auto words=static_cast<const uint32_t*>(po);for(uint32_t gid=0;gid<memory_oracle_items;gid++)if(words[gid]!=memory_expected(host_input,gid,a.loops,a.memory_pattern))semantic_mismatches++;}std::ofstream of(a.out,std::ios::binary);if(!of)throw std::runtime_error("cannot create payload file");of.write((char*)po,out_sz);of.close();if(!of)throw std::runtime_error("payload write failed");vkUnmapMemory(c.dev,stout.m);
  double sum=std::accumulate(gpu_ms.begin(),gpu_ms.end(),0.0);double med=pctile(gpu_ms,0.5),p95=pctile(gpu_ms,0.95),p99=pctile(gpu_ms,0.99);double ips=wall>0?double(logical_items)/(wall/1000.0):0;double qd=wall>0?std::min(100.0,sum/wall*100.0):0;
  std::cout<<"{\"dispatch_batch\":"<<batch_repeats<<",\"dispatch_batch_requested\":"<<a.dispatch_batch
           <<",\"batch_target_ms\":4,\"batch_calibration_gpu_ms\":"<<calibration
           <<",\"command_records\":"<<command_records<<",\"submissions\":"<<submissions
           <<",\"logical_items\":"<<logical_items
           <<",\"measure_start_monotonic_ns\":"<<measure_start_ns<<",\"measure_end_monotonic_ns\":"<<measure_end_ns
           <<",\"gpu_batch_ms_p50\":"<<med<<",\"gpu_batch_ms_p95\":"<<p95<<",\"gpu_batch_ms_p99\":"<<p99
           <<",\"gpu_timing_scope\":\"dispatch-batch-including-internal-barriers\",\"semantic_validation_pass\":"<<(semantic_mismatches?"false":"true")<<",\"semantic_mismatch_items\":"<<semantic_mismatches<<",\"semantic_validated_items\":"<<(a.rt?a.threads:0)<<",\"memory_oracle_items\":"<<memory_oracle_items<<",\"memory_oracle_scope\":\""<<(memory_oracle_items?"cpu-prefix":"not-requested")<<"\",\"memory_pattern\":\""<<a.memory_pattern<<"\",\"rt_scene_build_ms\":"<<scene.build_ms<<",\"rt_scene_triangles\":"<<(a.rt?4096:0)<<",\"schema\":\"ASTRO_GPU_MAXOUT_NATIVE_PROBE_V1\",\"device\":\""<<esc(c.prop.deviceName)<<"\",\"threads\":"<<a.threads<<",\"groups\":"<<total_groups<<",\"local\":"<<a.local<<",\"subgroup_requested\":"<<a.subgroup<<",\"inflight\":"<<depth<<",\"chunk_groups\":"<<chunk<<",\"input_bytes\":"<<input_sz<<",\"input_kib\":"<<(input_sz/1024)<<",\"warmup_wall_ms\":"<<warm<<",\"measure_wall_ms\":"<<wall<<",\"dispatches\":"<<dispatches<<",\"gpu_ms_sum\":"<<sum<<",\"gpu_ms_p50\":"<<(med/batch_repeats)<<",\"gpu_ms_p95\":"<<(p95/batch_repeats)<<",\"gpu_ms_p99\":"<<(p99/batch_repeats)<<",\"queue_duty_pct\":"<<qd<<",\"items_per_s\":"<<ips<<",\"gitems_s\":"<<(ips/1e9)<<"}"<<std::endl;
  for (auto &s : slots) {
    vkDestroyFence(c.dev, s.fence, nullptr);
  }
  vkDestroyQueryPool(c.dev, qp, nullptr);
  vkDestroyDescriptorPool(c.dev, dp, nullptr);
  if(a.pipeline_rt)rtpipe.destroy(c);else vkDestroyPipeline(c.dev, pipe, nullptr);
  if(sm)vkDestroyShaderModule(c.dev, sm, nullptr);
  vkDestroyPipelineLayout(c.dev, layout, nullptr);
  vkDestroyDescriptorSetLayout(c.dev, dsl, nullptr);
  if(a.rt)scene.destroy(c);
  freebuf(c, stin);
  freebuf(c, stout);
  freebuf(c, input);
  freebuf(c, output);
  freebuf(c, meta);
  vkDestroyCommandPool(c.dev, pool, nullptr);
  vkDestroyDevice(c.dev, nullptr);
  vkDestroyInstance(c.inst, nullptr);
  return 0;
 }catch(const std::exception&e){std::cerr<<"ERROR: "<<e.what()<<"\n";return 2;}
}
