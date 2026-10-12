// Reuse existing checked Vulkan helpers, never the mapper's synthetic payload.
#define main astro_unused_probe_main
#include "vk_compute_runner.cpp"
#undef main
#include "exact_scene.hpp"
#include "triangle_scene.hpp"
#include <iomanip>
struct SciencePC {uint32_t first,count;};
int main(int argc,char**argv){try{
 Args a;bool reuse_commands=false;bool rebuild=false,workgroup_per_record=false;uint32_t records_per_group=1;std::string input_path;uint32_t pack=1,repeats=1;uint32_t first=0,count=0;double warmup_ms=0,measurement_ms=0;
 for(int i=1;i<argc;i++){std::string key=argv[i];auto value=[&](){if(++i>=argc)throw std::runtime_error("missing argument");return std::string(argv[i]);};
  if(key=="--input")input_path=value();else if(key=="--spv")a.spv=value();else if(key=="--output")a.out=value();else if(key=="--gpu")a.gpu=std::stoi(value());else if(key=="--local")a.local=std::stoul(value());else if(key=="--pack")pack=std::stoul(value());else if(key=="--repeats")repeats=std::stoul(value());else if(key=="--first")first=std::stoul(value());else if(key=="--count")count=std::stoul(value());else if(key=="--warmup-ms")warmup_ms=std::stod(value());else if(key=="--measurement-ms")measurement_ms=std::stod(value());else if(key=="--records-per-group")records_per_group=std::stoul(value());else if(key=="--reuse-command-buffer")reuse_commands=true;else if(key=="--workgroup-per-record")workgroup_per_record=true;else if(key=="--rt")a.rt=true;else if(key=="--rt-rebuild"){a.rt=true;rebuild=true;}else throw std::runtime_error("unknown argument "+key);
 }
 if(!a.local||a.local>256||!records_per_group||records_per_group>4||a.rt)throw std::runtime_error("invalid demo configuration");
 if(a.spv.empty()||a.out.empty()||input_path.empty()||!pack||pack>4||!repeats||repeats>4096)throw std::runtime_error("invalid science arguments");
 bool sustained=warmup_ms!=0||measurement_ms!=0;if(sustained&&(!std::isfinite(warmup_ms)||!std::isfinite(measurement_ms)||warmup_ms<2000||measurement_ms<1000||warmup_ms>10000||measurement_ms>10000))throw std::runtime_error("benchmark requires warmup 2000..10000ms and measurement 1000..10000ms");
 auto words=read_spv(input_path);if(words.size()<16||words[0]!=0x41535452u||words[1]!=1||words[2]<1||words[2]>81||words[3]>1000000||words[13]>(words[2]==47?1024u:words[2]==46?516u:512u)||!words[13]||words[11]>words.size()||words[12]>words.size())throw std::runtime_error("invalid science packet");
 if(words[2]!=11u && words[2]!=30u && words[2]!=31u && words[2]!=32u)throw std::runtime_error("MathSpec outside four-task demo allowlist");
 if(!count)count=words[3]-first;if(first>words[3]||count>words[3]-first||!count)throw std::runtime_error("invalid partition");
 if(a.rt&&words[2]!=5&&words[2]!=7&&words[2]!=9&&words[2]!=37&&words[2]!=38)throw std::runtime_error("RT not applicable");
 if(reuse_commands && (a.rt || words[2]<30 || words[2]>32))throw std::runtime_error("command reuse validated only for FFT256/Convolution/XCORR compute");
 bool triangle=(words[2]==37u||words[2]==38u),dynamic=words[2]==38u;
 if(triangle&&(!words[4]||!words[5]||words[5]>4096||!words[6]||words[6]>8||uint64_t(words[4])*words[6]!=words[3]))throw std::runtime_error("invalid triangle header");
 if(rebuild&&!dynamic)throw std::runtime_error("rebuild backend requires dynamic triangles");
 auto process_start=Clock::now();
  VkApplicationInfo app{};app.sType=VK_STRUCTURE_TYPE_APPLICATION_INFO;app.pApplicationName="ASTRO GPU Max-Out Probe";app.apiVersion=a.rt?VK_API_VERSION_1_2:VK_API_VERSION_1_1;VkInstanceCreateInfo ici{};ici.sType=VK_STRUCTURE_TYPE_INSTANCE_CREATE_INFO;ici.pApplicationInfo=&app;Ctx c;ck(vkCreateInstance(&ici,nullptr,&c.inst),"vkCreateInstance");
  uint32_t nd=0;ck(vkEnumeratePhysicalDevices(c.inst,&nd,nullptr),"enum gpu count");if(a.gpu<0||a.gpu>=int(nd))throw std::runtime_error("GPU index out of range");std::vector<VkPhysicalDevice> pds(nd);ck(vkEnumeratePhysicalDevices(c.inst,&nd,pds.data()),"enum gpus");c.pd=pds[a.gpu];vkGetPhysicalDeviceProperties(c.pd,&c.prop);vkGetPhysicalDeviceMemoryProperties(c.pd,&c.mem);
  uint32_t nq=0;vkGetPhysicalDeviceQueueFamilyProperties(c.pd,&nq,nullptr);std::vector<VkQueueFamilyProperties>qf(nq);vkGetPhysicalDeviceQueueFamilyProperties(c.pd,&nq,qf.data());bool found=false;for(uint32_t i=0;i<nq;i++)if(qf[i].queueFlags&VK_QUEUE_COMPUTE_BIT){c.qf=i;found=true;break;}if(!found)throw std::runtime_error("no compute queue");if(!qf[c.qf].timestampValidBits)throw std::runtime_error("compute timestamps unsupported");if(a.local>c.prop.limits.maxComputeWorkGroupInvocations||a.local>c.prop.limits.maxComputeWorkGroupSize[0])throw std::runtime_error("local size exceeds device limit");
  uint32_t ne=0;vkEnumerateDeviceExtensionProperties(c.pd,nullptr,&ne,nullptr);std::vector<VkExtensionProperties> ep(ne);vkEnumerateDeviceExtensionProperties(c.pd,nullptr,&ne,ep.data());std::set<std::string> ext;for(auto&x:ep)ext.insert(x.extensionName);
  VkPhysicalDeviceIDProperties identity{};identity.sType=VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_ID_PROPERTIES;
  VkPhysicalDevicePCIBusInfoPropertiesEXT bus{};bus.sType=VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_PCI_BUS_INFO_PROPERTIES_EXT;
  bool pci_available=ext.count(VK_EXT_PCI_BUS_INFO_EXTENSION_NAME)!=0;
  VkPhysicalDeviceProperties2 properties{};properties.sType=VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_PROPERTIES_2;properties.pNext=&identity;
  if(pci_available)identity.pNext=&bus;vkGetPhysicalDeviceProperties2(c.pd,&properties);
  std::ostringstream uuid_text,pci_text;uuid_text<<std::hex<<std::setfill('0');for(auto byte:identity.deviceUUID)uuid_text<<std::setw(2)<<unsigned(byte);
  if(pci_available)pci_text<<std::hex<<std::setfill('0')<<std::setw(4)<<bus.pciDomain<<":"<<std::setw(2)<<bus.pciBus<<":"<<std::setw(2)<<bus.pciDevice<<"."<<bus.pciFunction;
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

 ExactScene scene;TriangleScene tri_scene;if(a.rt){if(triangle)tri_scene.create_triangles(c,pool,words);else scene.create_exact(c,pool,words);}
 VkDeviceSize input_size=words.size()*4ull,output_size=uint64_t(words[3])*words[13]*4ull;
 VkDeviceSize scratch_size=a.rt?std::max<uint64_t>(4,uint64_t(words[3])*((words[5]+31)/32)*4):4;
 uint32_t boxbase=(9u*words[5]+1u)&~1u,frame_stride=boxbase+6u*words[5];
 if(triangle)scratch_size=dynamic?uint64_t(frame_stride)*words[6]*4u:4u;
 bool staged=words[2]==34u||words[2]==35u;
 uint32_t prepass_count=staged?words[5]:0u;
 if(staged)scratch_size=std::max<uint64_t>(4,uint64_t(prepass_count)*(words[2]==35u?129u:1u)*4u);
 if(input_size>c.prop.limits.maxStorageBufferRange||output_size>c.prop.limits.maxStorageBufferRange||scratch_size>std::min<uint64_t>(c.prop.limits.maxStorageBufferRange,128000000))throw std::runtime_error("science buffer limits; partition job more finely");
 Buf in=mkbuf(c,input_size,VK_BUFFER_USAGE_STORAGE_BUFFER_BIT|VK_BUFFER_USAGE_TRANSFER_DST_BIT,VK_MEMORY_PROPERTY_DEVICE_LOCAL_BIT);
 Buf out=mkbuf(c,output_size,VK_BUFFER_USAGE_STORAGE_BUFFER_BIT|VK_BUFFER_USAGE_TRANSFER_SRC_BIT|VK_BUFFER_USAGE_TRANSFER_DST_BIT,VK_MEMORY_PROPERTY_DEVICE_LOCAL_BIT);
 Buf scratch=mkbuf(c,scratch_size,VK_BUFFER_USAGE_STORAGE_BUFFER_BIT|VK_BUFFER_USAGE_TRANSFER_SRC_BIT|((dynamic&&a.rt)?(VK_BUFFER_USAGE_ACCELERATION_STRUCTURE_BUILD_INPUT_READ_ONLY_BIT_KHR|VK_BUFFER_USAGE_SHADER_DEVICE_ADDRESS_BIT):0),VK_MEMORY_PROPERTY_DEVICE_LOCAL_BIT);
 Buf staging=mkbuf(c,std::max(std::max(input_size,output_size),scratch_size),VK_BUFFER_USAGE_TRANSFER_SRC_BIT|VK_BUFFER_USAGE_TRANSFER_DST_BIT,VK_MEMORY_PROPERTY_HOST_VISIBLE_BIT|VK_MEMORY_PROPERTY_HOST_COHERENT_BIT);
 void* ptr;ck(vkMapMemory(c.dev,staging.m,0,input_size,0,&ptr),"input map");std::memcpy(ptr,words.data(),input_size);vkUnmapMemory(c.dev,staging.m);onecopy(c,pool,staging.b,in.b,input_size);
 VkDescriptorSetLayoutBinding bindings[4]{};for(uint32_t j=0;j<3;j++){bindings[j].binding=j;bindings[j].descriptorType=VK_DESCRIPTOR_TYPE_STORAGE_BUFFER;bindings[j].descriptorCount=1;bindings[j].stageFlags=VK_SHADER_STAGE_COMPUTE_BIT;}if(a.rt){bindings[3]={3,VK_DESCRIPTOR_TYPE_ACCELERATION_STRUCTURE_KHR,1,VK_SHADER_STAGE_COMPUTE_BIT,nullptr};}
 VkDescriptorSetLayoutCreateInfo dslci{VK_STRUCTURE_TYPE_DESCRIPTOR_SET_LAYOUT_CREATE_INFO};dslci.bindingCount=a.rt?4:3;dslci.pBindings=bindings;VkDescriptorSetLayout dsl;ck(vkCreateDescriptorSetLayout(c.dev,&dslci,nullptr,&dsl),"science descriptor layout");
 VkPushConstantRange push{VK_SHADER_STAGE_COMPUTE_BIT,0,sizeof(SciencePC)};VkPipelineLayoutCreateInfo plci{VK_STRUCTURE_TYPE_PIPELINE_LAYOUT_CREATE_INFO};plci.setLayoutCount=1;plci.pSetLayouts=&dsl;plci.pushConstantRangeCount=1;plci.pPushConstantRanges=&push;VkPipelineLayout layout;ck(vkCreatePipelineLayout(c.dev,&plci,nullptr,&layout),"science pipeline layout");
 auto code=read_spv(a.spv);VkShaderModuleCreateInfo smci{VK_STRUCTURE_TYPE_SHADER_MODULE_CREATE_INFO};smci.codeSize=code.size()*4;smci.pCode=code.data();VkShaderModule module;ck(vkCreateShaderModule(c.dev,&smci,nullptr,&module),"science module");
 VkComputePipelineCreateInfo pci{VK_STRUCTURE_TYPE_COMPUTE_PIPELINE_CREATE_INFO};pci.stage.sType=VK_STRUCTURE_TYPE_PIPELINE_SHADER_STAGE_CREATE_INFO;pci.stage.stage=VK_SHADER_STAGE_COMPUTE_BIT;pci.stage.module=module;pci.stage.pName="main";pci.layout=layout;VkPipeline pipeline;ck(vkCreateComputePipelines(c.dev,VK_NULL_HANDLE,1,&pci,nullptr,&pipeline),"science pipeline");
 VkDescriptorPoolSize sizes[2]={{VK_DESCRIPTOR_TYPE_STORAGE_BUFFER,3},{VK_DESCRIPTOR_TYPE_ACCELERATION_STRUCTURE_KHR,1}};VkDescriptorPoolCreateInfo dpci{VK_STRUCTURE_TYPE_DESCRIPTOR_POOL_CREATE_INFO};dpci.maxSets=1;dpci.poolSizeCount=a.rt?2:1;dpci.pPoolSizes=sizes;VkDescriptorPool dp;ck(vkCreateDescriptorPool(c.dev,&dpci,nullptr,&dp),"science descriptor pool");VkDescriptorSetAllocateInfo dsai{VK_STRUCTURE_TYPE_DESCRIPTOR_SET_ALLOCATE_INFO};dsai.descriptorPool=dp;dsai.descriptorSetCount=1;dsai.pSetLayouts=&dsl;VkDescriptorSet ds;ck(vkAllocateDescriptorSets(c.dev,&dsai,&ds),"science descriptor set");
 VkDescriptorBufferInfo bi[3]={{in.b,0,input_size},{out.b,0,output_size},{scratch.b,0,scratch_size}};VkWriteDescriptorSet writes[4]{};for(uint32_t j=0;j<3;j++){writes[j].sType=VK_STRUCTURE_TYPE_WRITE_DESCRIPTOR_SET;writes[j].dstSet=ds;writes[j].dstBinding=j;writes[j].descriptorCount=1;writes[j].descriptorType=VK_DESCRIPTOR_TYPE_STORAGE_BUFFER;writes[j].pBufferInfo=&bi[j];}
 VkWriteDescriptorSetAccelerationStructureKHR aw{VK_STRUCTURE_TYPE_WRITE_DESCRIPTOR_SET_ACCELERATION_STRUCTURE_KHR};aw.accelerationStructureCount=1;aw.pAccelerationStructures=triangle?&tri_scene.tlas:&scene.tlas;if(a.rt){writes[3].sType=VK_STRUCTURE_TYPE_WRITE_DESCRIPTOR_SET;writes[3].pNext=&aw;writes[3].dstSet=ds;writes[3].dstBinding=3;writes[3].descriptorCount=1;writes[3].descriptorType=VK_DESCRIPTOR_TYPE_ACCELERATION_STRUCTURE_KHR;}
 vkUpdateDescriptorSets(c.dev,a.rt?4:3,writes,0,nullptr);
 VkQueryPoolCreateInfo qpci{VK_STRUCTURE_TYPE_QUERY_POOL_CREATE_INFO};qpci.queryType=VK_QUERY_TYPE_TIMESTAMP;qpci.queryCount=2;VkQueryPool qp;ck(vkCreateQueryPool(c.dev,&qpci,nullptr,&qp),"science timestamps");
 VkCommandBufferAllocateInfo cbai{VK_STRUCTURE_TYPE_COMMAND_BUFFER_ALLOCATE_INFO};cbai.commandPool=pool;cbai.level=VK_COMMAND_BUFFER_LEVEL_PRIMARY;cbai.commandBufferCount=1;VkCommandBuffer cb;ck(vkAllocateCommandBuffers(c.dev,&cbai,&cb),"science command");
 if(workgroup_per_record && (pack!=1 || (words[2]!=30u && words[2]!=32u)))throw std::runtime_error("workgroup-record mode only for FFT256/XCORR pack1");
 if(!records_per_group || (records_per_group!=1 && (!workgroup_per_record || records_per_group>4)))throw std::runtime_error("invalid records per group");
 uint64_t groups=workgroup_per_record?(uint64_t(count)+records_per_group-1)/records_per_group:(uint64_t(count)+a.local*pack-1)/(a.local*pack);if(groups>c.prop.limits.maxComputeWorkGroupCount[0])throw std::runtime_error("dispatch limit; split output range");
 SciencePC pc{first,count};
 uint64_t measurement_begin_ns=0,measurement_end_ns=0;
 // Online totals: constant host memory even for very short GPU batches.
 uint64_t total_dispatches=0,queue_submissions=0,gap_count=0;
 double gap_sum=0,gap_max=0,record_total_ms=0,submit_total_ms=0,retire_total_ms=0,query_total_ms=0;
 uint64_t previous_gpu_end=0;bool have_previous_gpu_end=false;
 const uint64_t timestamp_mask=qf[c.qf].timestampValidBits>=64?UINT64_MAX:((uint64_t(1)<<qf[c.qf].timestampValidBits)-1);
 bool recorded=false;uint32_t recorded_reps=0;uint64_t recorded_dispatches=0,command_recordings=0,command_reuses=0;
 auto submit=[&](uint32_t reps,bool warm){
  auto record_begin=Clock::now();uint64_t dispatch_count=0;
  if(!reuse_commands || !recorded || recorded_reps!=reps){
  command_recordings++;
  auto dispatch=[&](uint32_t n){vkCmdDispatch(cb,n,1,1);dispatch_count++;};
  ck(vkResetCommandBuffer(cb,0),"reset science command");VkCommandBufferBeginInfo begin{VK_STRUCTURE_TYPE_COMMAND_BUFFER_BEGIN_INFO};ck(vkBeginCommandBuffer(cb,&begin),"begin science command");
  vkCmdFillBuffer(cb,out.b,0,output_size,0xa5a5a5a5u);
  VkMemoryBarrier mb{VK_STRUCTURE_TYPE_MEMORY_BARRIER};mb.srcAccessMask=VK_ACCESS_TRANSFER_WRITE_BIT|VK_ACCESS_SHADER_WRITE_BIT;mb.dstAccessMask=VK_ACCESS_SHADER_WRITE_BIT|VK_ACCESS_SHADER_READ_BIT;
  vkCmdPipelineBarrier(cb,VK_PIPELINE_STAGE_TRANSFER_BIT|VK_PIPELINE_STAGE_COMPUTE_SHADER_BIT,VK_PIPELINE_STAGE_COMPUTE_SHADER_BIT,0,1,&mb,0,nullptr,0,nullptr);
  vkCmdResetQueryPool(cb,qp,0,2);vkCmdWriteTimestamp(cb,VK_PIPELINE_STAGE_TOP_OF_PIPE_BIT,qp,0);vkCmdBindPipeline(cb,VK_PIPELINE_BIND_POINT_COMPUTE,pipeline);vkCmdBindDescriptorSets(cb,VK_PIPELINE_BIND_POINT_COMPUTE,layout,0,1,&ds,0,nullptr);vkCmdPushConstants(cb,layout,VK_SHADER_STAGE_COMPUTE_BIT,0,sizeof(pc),&pc);
  for(uint32_t j=0;j<reps;j++){
   mb.srcAccessMask=VK_ACCESS_SHADER_READ_BIT|VK_ACCESS_SHADER_WRITE_BIT;mb.dstAccessMask=VK_ACCESS_SHADER_READ_BIT|VK_ACCESS_SHADER_WRITE_BIT;
   vkCmdPipelineBarrier(cb,VK_PIPELINE_STAGE_COMPUTE_SHADER_BIT,VK_PIPELINE_STAGE_COMPUTE_SHADER_BIT,0,1,&mb,0,nullptr,0,nullptr);
   if(dynamic){
    for(uint32_t frame=0;frame<words[6];frame++){
     // Mutation always runs, including triangles missed by every ray.
     SciencePC pre{0x80000000u|frame,words[5]};vkCmdPushConstants(cb,layout,VK_SHADER_STAGE_COMPUTE_BIT,0,sizeof(pre),&pre);dispatch((words[5]+a.local*pack-1)/(a.local*pack));
     mb.srcAccessMask=VK_ACCESS_SHADER_WRITE_BIT;mb.dstAccessMask=VK_ACCESS_SHADER_READ_BIT|VK_ACCESS_SHADER_WRITE_BIT;vkCmdPipelineBarrier(cb,VK_PIPELINE_STAGE_COMPUTE_SHADER_BIT,VK_PIPELINE_STAGE_COMPUTE_SHADER_BIT,0,1,&mb,0,nullptr,0,nullptr);
     if(a.rt)tri_scene.maintain(c,cb,RtScene::address(c,scratch)+uint64_t(frame*frame_stride+boxbase)*4u,!rebuild);
     uint32_t lo=std::max(first,frame*words[4]),hi=std::min(first+count,(frame+1)*words[4]);
     if(hi>lo){SciencePC query{lo,hi-lo};vkCmdPushConstants(cb,layout,VK_SHADER_STAGE_COMPUTE_BIT,0,sizeof(query),&query);dispatch((query.count+a.local*pack-1)/(a.local*pack));}
     // Protect BVH reads from the next frame's AS write, and scratch reuse.
     if(a.rt){mb.srcAccessMask=VK_ACCESS_ACCELERATION_STRUCTURE_READ_BIT_KHR|VK_ACCESS_SHADER_READ_BIT;mb.dstAccessMask=VK_ACCESS_ACCELERATION_STRUCTURE_WRITE_BIT_KHR|VK_ACCESS_SHADER_WRITE_BIT;vkCmdPipelineBarrier(cb,VK_PIPELINE_STAGE_COMPUTE_SHADER_BIT,VK_PIPELINE_STAGE_ACCELERATION_STRUCTURE_BUILD_BIT_KHR|VK_PIPELINE_STAGE_COMPUTE_SHADER_BIT,0,1,&mb,0,nullptr,0,nullptr);}
    }
   }else{
    if(staged&&prepass_count){
     SciencePC pre{0x80000000u,prepass_count};vkCmdPushConstants(cb,layout,VK_SHADER_STAGE_COMPUTE_BIT,0,sizeof(pre),&pre);
     uint32_t pg=(prepass_count+a.local*pack-1u)/(a.local*pack);if(pg>c.prop.limits.maxComputeWorkGroupCount[0])throw std::runtime_error("prepass dispatch limit");
     dispatch(pg);mb.srcAccessMask=VK_ACCESS_SHADER_WRITE_BIT;mb.dstAccessMask=VK_ACCESS_SHADER_READ_BIT|VK_ACCESS_SHADER_WRITE_BIT;
     vkCmdPipelineBarrier(cb,VK_PIPELINE_STAGE_COMPUTE_SHADER_BIT,VK_PIPELINE_STAGE_COMPUTE_SHADER_BIT,0,1,&mb,0,nullptr,0,nullptr);
    }
    vkCmdPushConstants(cb,layout,VK_SHADER_STAGE_COMPUTE_BIT,0,sizeof(pc),&pc);dispatch(uint32_t(groups));
   }
  }
  vkCmdWriteTimestamp(cb,VK_PIPELINE_STAGE_BOTTOM_OF_PIPE_BIT,qp,1);ck(vkEndCommandBuffer(cb),"end science command");
  recorded=true;recorded_reps=reps;recorded_dispatches=dispatch_count;
  }else{dispatch_count=recorded_dispatches;command_reuses++;}
  VkSubmitInfo si{VK_STRUCTURE_TYPE_SUBMIT_INFO};si.commandBufferCount=1;si.pCommandBuffers=&cb;
  auto t=Clock::now();ck(vkQueueSubmit(c.q,1,&si,VK_NULL_HANDLE),"submit science");auto submitted=Clock::now();
  ck(vkQueueWaitIdle(c.q),"wait science");auto retired=Clock::now();
  uint64_t ts[2];ck(vkGetQueryPoolResults(c.dev,qp,0,2,sizeof(ts),ts,8,VK_QUERY_RESULT_64_BIT|VK_QUERY_RESULT_WAIT_BIT),"science timestamps read");auto end=Clock::now();
  measurement_begin_ns=std::chrono::duration_cast<std::chrono::nanoseconds>(record_begin.time_since_epoch()).count();
  measurement_end_ns=std::chrono::duration_cast<std::chrono::nanoseconds>(end.time_since_epoch()).count();
  double gpu=double((ts[1]-ts[0])&timestamp_mask)*c.prop.limits.timestampPeriod/1e6;
  if(!warm){
   double gap=have_previous_gpu_end?double((ts[0]-previous_gpu_end)&timestamp_mask)*c.prop.limits.timestampPeriod/1e6:-1.0;
   total_dispatches+=dispatch_count;queue_submissions++;
   if(gap>=0){gap_count++;gap_sum+=gap;gap_max=std::max(gap_max,gap);}
   record_total_ms+=ms_since(record_begin,t);submit_total_ms+=ms_since(t,submitted);
   retire_total_ms+=ms_since(submitted,retired);query_total_ms+=ms_since(retired,end);
   previous_gpu_end=ts[1];have_previous_gpu_end=true;
  }
  return std::pair<double,double>(ms_since(record_begin,end),gpu);
 };
 auto warmup_timing=submit(1,true);uint64_t warmup_begin_ns=measurement_begin_ns,warmup_end_ns=measurement_end_ns;
 if(sustained){
  while(double(warmup_end_ns-warmup_begin_ns)/1e6<warmup_ms){auto part=submit(repeats,true);warmup_timing.second+=part.second;warmup_end_ns=measurement_end_ns;}
  warmup_timing.first=double(warmup_end_ns-warmup_begin_ns)/1e6;
 }

 // Warmup is also returned and independently checked by the Python supervisor.
 auto dump=[&](const std::string& path){onecopy(c,pool,out.b,staging.b,output_size);ck(vkMapMemory(c.dev,staging.m,0,output_size,0,&ptr),"output map");std::ofstream file(path,std::ios::binary);file.write(static_cast<const char*>(ptr)+uint64_t(first)*words[13]*4,uint64_t(count)*words[13]*4);if(!file)throw std::runtime_error("output write");vkUnmapMemory(c.dev,staging.m);};
 auto dump_geometry=[&](const std::string& path){if(!dynamic)return;onecopy(c,pool,scratch.b,staging.b,scratch_size);ck(vkMapMemory(c.dev,staging.m,0,scratch_size,0,&ptr),"geometry audit map");std::ofstream file(path,std::ios::binary);for(uint32_t frame=0;frame<words[6];frame++)file.write(static_cast<const char*>(ptr)+uint64_t(frame)*frame_stride*4,uint64_t(words[5])*9*4);if(!file)throw std::runtime_error("geometry audit write");vkUnmapMemory(c.dev,staging.m);};
 dump(a.out+".warmup");dump_geometry(a.out+".geometry.warmup");std::pair<double,double> timing;uint64_t measurement_batches=1;
 if(sustained){
  auto begin=Clock::now();double gpu_total=0;measurement_batches=0;
  do{gpu_total+=submit(repeats,false).second;measurement_batches++;}while(ms_since(begin,Clock::now())<measurement_ms);
  auto end=Clock::now();timing={ms_since(begin,end),gpu_total};measurement_begin_ns=std::chrono::duration_cast<std::chrono::nanoseconds>(begin.time_since_epoch()).count();measurement_end_ns=std::chrono::duration_cast<std::chrono::nanoseconds>(end.time_since_epoch()).count();
 }else timing=submit(repeats,false);
 dump(a.out);dump_geometry(a.out+".geometry");
 double elapsed=ms_since(process_start,Clock::now());
 std::cout<<std::setprecision(12)<<"{\"native_evidence_schema\":\"ASTRO_NATIVE_TIMING_V2\",\"device_type\":"<<c.prop.deviceType
  <<",\"gpu_time_source\":\"VULKAN_TIMESTAMP_QUERY\",\"gpu_time_scope\":\"batch-including-barriers-and-AS-maintenance\""
  <<",\"dispatch_count\":"<<total_dispatches<<",\"queue_submit_count\":"<<queue_submissions
  <<",\"gpu_wall_ratio\":"<<timing.second/timing.first<<",\"queue_duty_pct\":"<<100.0*timing.second/timing.first
  <<",\"compute_duty\":null,\"compute_duty_status\":\"UNAVAILABLE\""
  <<",\"inter_dispatch_gaps\":{\"scope\":\"between-batches-GPU-timestamps\",\"intra_batch_status\":\"UNAVAILABLE\",\"count\":"<<gap_count<<",\"sum_ms\":"<<gap_sum<<",\"max_ms\":"<<gap_max<<"}"
  <<",\"measurement_trace_status\":\"NOT_RETAINED_ONLINE_AGGREGATES\","
  <<"\"host_cost_ms\":{\"record\":"<<record_total_ms<<",\"submit\":"<<submit_total_ms<<",\"retire\":"<<retire_total_ms<<",\"query\":"<<query_total_ms<<"},";
 std::cout<<"\"command_buffer_recordings\":"<<command_recordings<<",\"command_buffer_reuses\":"<<command_reuses<<",\"command_buffer_reuse_enabled\":"<<(reuse_commands?"true":"false")<<",";
 std::cout<<std::setprecision(12)<<"\"device\":\""<<esc(c.prop.deviceName)<<"\",\"vendor_id\":"<<c.prop.vendorID<<",\"device_id\":"<<c.prop.deviceID<<",\"driver_version\":"<<c.prop.driverVersion<<",\"backend\":\""<<(rebuild?"RT_REBUILD":a.rt?"RT_COMPUTE":"GENERIC_COMPUTE")<<"\",\"records\":"<<count<<",\"repeats\":"<<repeats<<",\"wall_ms\":"<<timing.first<<",\"gpu_ms\":"<<timing.second<<",\"setup_and_execution_ms\":"<<elapsed<<",\"as_build_ms\":"<<(triangle?tri_scene.build_ms:scene.build_ms)<<",\"records_per_s\":"<<double(count)*repeats*measurement_batches*1000/timing.first<<",\"measurement_begin_ns\":"<<measurement_begin_ns<<",\"measurement_end_ns\":"<<measurement_end_ns<<",\"warmup_begin_ns\":"<<warmup_begin_ns<<",\"warmup_end_ns\":"<<warmup_end_ns<<",\"warmup_wall_ms\":"<<warmup_timing.first<<",\"warmup_gpu_ms\":"<<warmup_timing.second<<",\"device_uuid\":\""<<uuid_text.str()<<"\",\"pci_bus_id\":\""<<pci_text.str()<<"\",\"measurement_batches\":"<<measurement_batches<<",\"timing_protocol\":\""<<(sustained?"RESIDENT_BATCH_LOOP_V1":"RESIDENT_SINGLE_BATCH_V1")<<"\"}\n";
 vkDeviceWaitIdle(c.dev);if(a.rt){if(triangle)tri_scene.destroy(c);else scene.destroy(c);}vkDestroyQueryPool(c.dev,qp,nullptr);vkDestroyPipeline(c.dev,pipeline,nullptr);vkDestroyShaderModule(c.dev,module,nullptr);vkDestroyDescriptorPool(c.dev,dp,nullptr);vkDestroyPipelineLayout(c.dev,layout,nullptr);vkDestroyDescriptorSetLayout(c.dev,dsl,nullptr);freebuf(c,in);freebuf(c,out);freebuf(c,scratch);freebuf(c,staging);vkDestroyCommandPool(c.dev,pool,nullptr);vkDestroyDevice(c.dev,nullptr);vkDestroyInstance(c.inst,nullptr);return 0;
 }catch(const std::exception& e){std::cerr<<"SCIENCE_RUNNER_ERROR: "<<e.what()<<"\n";return 2;}}
