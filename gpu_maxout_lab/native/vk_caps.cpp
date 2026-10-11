#include <vulkan/vulkan.h>
#include <algorithm>
#include <cstdint>
#include <cstdlib>
#include <cstring>
#include <iomanip>
#include <iostream>
#include <set>
#include <sstream>
#include <string>
#include <vector>

static void ck(VkResult r, const char* what) {
    if (r != VK_SUCCESS) { std::cerr << what << " failed: " << int(r) << "\n"; std::exit(2); }
}
static std::string esc(const char* s) {
    std::ostringstream o;
    for (; *s; ++s) {
        unsigned char c=*s;
        if (c=='"' || c=='\\') o << '\\' << char(c);
        else if (c=='\n') o << "\\n";
        else if (c>=32) o << char(c);
    }
    return o.str();
}
static bool has(const std::set<std::string>& e, const char* n){ return e.find(n)!=e.end(); }
int main(int argc,char**argv){
    int gpu=0;
    for(int i=1;i<argc;i++) if(std::string(argv[i])=="--gpu" && i+1<argc) gpu=std::atoi(argv[++i]);
    VkApplicationInfo ai{};ai.sType=VK_STRUCTURE_TYPE_APPLICATION_INFO; ai.pApplicationName="ASTRO GPU Max-Out Caps"; ai.apiVersion=VK_API_VERSION_1_1;
    VkInstanceCreateInfo ici{};ici.sType=VK_STRUCTURE_TYPE_INSTANCE_CREATE_INFO; ici.pApplicationInfo=&ai;
    VkInstance inst=VK_NULL_HANDLE; ck(vkCreateInstance(&ici,nullptr,&inst),"vkCreateInstance");
    uint32_t nd=0; ck(vkEnumeratePhysicalDevices(inst,&nd,nullptr),"vkEnumeratePhysicalDevices(count)");
    if(!nd || gpu<0 || gpu>=int(nd)){ std::cerr<<"GPU index out of range\n"; return 3; }
    std::vector<VkPhysicalDevice> ds(nd); ck(vkEnumeratePhysicalDevices(inst,&nd,ds.data()),"vkEnumeratePhysicalDevices");
    VkPhysicalDevice pd=ds[gpu];

    uint32_t ne=0; ck(vkEnumerateDeviceExtensionProperties(pd,nullptr,&ne,nullptr),"ext count");
    std::vector<VkExtensionProperties> ex(ne); ck(vkEnumerateDeviceExtensionProperties(pd,nullptr,&ne,ex.data()),"ext list");
    std::set<std::string> ext; for(auto &x:ex) ext.insert(x.extensionName);

    VkPhysicalDeviceIDProperties ids{};ids.sType=VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_ID_PROPERTIES;
    VkPhysicalDeviceProperties2 idp{};idp.sType=VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_PROPERTIES_2;idp.pNext=&ids;
    vkGetPhysicalDeviceProperties2(pd,&idp);
    auto hex_uuid=[](const uint8_t* a){const char* h="0123456789abcdef";std::string s;for(int i=0;i<VK_UUID_SIZE;++i){s+=h[a[i]>>4];s+=h[a[i]&15];}return s;};
    VkPhysicalDeviceSubgroupProperties sub{};sub.sType=VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_SUBGROUP_PROPERTIES;
#ifdef VK_EXT_subgroup_size_control
    VkPhysicalDeviceSubgroupSizeControlPropertiesEXT subctl{};subctl.sType=VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_SUBGROUP_SIZE_CONTROL_PROPERTIES_EXT;
    sub.pNext=&subctl;
#endif
    VkPhysicalDeviceProperties2 p2{};p2.sType=VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_PROPERTIES_2;
#ifdef VK_EXT_pci_bus_info
    VkPhysicalDevicePCIBusInfoPropertiesEXT pci{};pci.sType=VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_PCI_BUS_INFO_PROPERTIES_EXT;
    bool pci_info=has(ext,VK_EXT_PCI_BUS_INFO_EXTENSION_NAME);pci.pNext=&sub;p2.pNext=pci_info?static_cast<void*>(&pci):static_cast<void*>(&sub);
#else
    bool pci_info=false;p2.pNext=&sub;
#endif
#ifdef VK_AMD_shader_core_properties2
    VkPhysicalDeviceShaderCoreProperties2AMD cores{};cores.sType=VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_SHADER_CORE_PROPERTIES_2_AMD;
    bool core_info=has(ext,VK_AMD_SHADER_CORE_PROPERTIES_2_EXTENSION_NAME);
    if(core_info){cores.pNext=p2.pNext;p2.pNext=&cores;}
#endif
    vkGetPhysicalDeviceProperties2(pd,&p2);
#ifdef VK_EXT_subgroup_size_control
    VkPhysicalDeviceSubgroupSizeControlFeaturesEXT subfeat{};subfeat.sType=VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_SUBGROUP_SIZE_CONTROL_FEATURES_EXT;
    VkPhysicalDeviceFeatures2 f2{};f2.sType=VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_FEATURES_2; f2.pNext=&subfeat; vkGetPhysicalDeviceFeatures2(pd,&f2);
#endif
    auto &p=p2.properties;
    VkPhysicalDeviceMemoryProperties mp{}; vkGetPhysicalDeviceMemoryProperties(pd,&mp);
    uint32_t nq=0; vkGetPhysicalDeviceQueueFamilyProperties(pd,&nq,nullptr); std::vector<VkQueueFamilyProperties> q(nq); vkGetPhysicalDeviceQueueFamilyProperties(pd,&nq,q.data());
    int compute_q=-1; for(uint32_t i=0;i<nq;i++) if(q[i].queueFlags & VK_QUEUE_COMPUTE_BIT){ compute_q=int(i); break; }

    bool subgroup_ctl=has(ext,VK_EXT_SUBGROUP_SIZE_CONTROL_EXTENSION_NAME)
#ifdef VK_EXT_subgroup_size_control
        && subfeat.subgroupSizeControl
#endif
        ;
    VkPhysicalDeviceFeatures2 rt_features{};rt_features.sType=VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_FEATURES_2;
    VkPhysicalDeviceBufferDeviceAddressFeatures bda{};bda.sType=VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_BUFFER_DEVICE_ADDRESS_FEATURES;
    VkPhysicalDeviceAccelerationStructureFeaturesKHR asf{};asf.sType=VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_ACCELERATION_STRUCTURE_FEATURES_KHR;
    VkPhysicalDeviceRayQueryFeaturesKHR rq{};rq.sType=VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_RAY_QUERY_FEATURES_KHR;
    VkPhysicalDeviceRayTracingPipelineFeaturesKHR rtf{};rtf.sType=VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_RAY_TRACING_PIPELINE_FEATURES_KHR;
    auto chain=[&](auto& f){f.pNext=rt_features.pNext;rt_features.pNext=&f;};
    bool api12=p.apiVersion>=VK_API_VERSION_1_2;
    if(api12)chain(bda);
    if(has(ext,"VK_KHR_acceleration_structure"))chain(asf);
    if(has(ext,"VK_KHR_ray_query"))chain(rq);
    if(has(ext,"VK_KHR_ray_tracing_pipeline"))chain(rtf);
    vkGetPhysicalDeviceFeatures2(pd,&rt_features);
    bool address=api12&&bda.bufferDeviceAddress;
    bool accel=asf.accelerationStructure&&address&&has(ext,"VK_KHR_deferred_host_operations");
    bool ray_query=rq.rayQuery&&accel&&compute_q>=0;
    bool rtp=rtf.rayTracingPipeline&&accel&&compute_q>=0;
    bool coop_khr=has(ext,"VK_KHR_cooperative_matrix");
    bool coop_nv=has(ext,"VK_NV_cooperative_matrix");
    bool float16int8=has(ext,"VK_KHR_shader_float16_int8");
    bool storage16=has(ext,"VK_KHR_16bit_storage");

    std::cout << "{";
    std::cout << "\"schema\":\"ASTRO_GPU_MAXOUT_CAPS_V1\",";
    std::cout << "\"gpu_index\":"<<gpu<<",";
    std::cout << "\"device\":{\"name\":\""<<esc(p.deviceName)<<"\",\"vendor_id\":"<<p.vendorID<<",\"device_id\":"<<p.deviceID<<",\"device_type\":"<<p.deviceType<<",\"api_version\":"<<p.apiVersion<<",\"driver_version\":"<<p.driverVersion<<"},";
    std::cout << "\"device_uuid\":\""<<hex_uuid(ids.deviceUUID)<<"\",\"driver_uuid\":\""<<hex_uuid(ids.driverUUID)<<"\",";
#ifdef VK_EXT_pci_bus_info
    if(pci_info) std::cout << "\"pci_bus_id\":\""<<std::hex<<std::setfill('0')<<std::setw(4)<<pci.pciDomain<<":"<<std::setw(2)<<pci.pciBus<<":"<<std::setw(2)<<pci.pciDevice<<"."<<pci.pciFunction<<"\",";
    else std::cout << "\"pci_bus_id\":null,";
#else
    std::cout << "\"pci_bus_id\":null,";
#endif
    std::cout << std::dec;
#ifdef VK_AMD_shader_core_properties2
    if(core_info)std::cout << "\"topology\":{\"active_compute_units\":"<<cores.activeComputeUnitCount<<",\"source\":\"VK_AMD_shader_core_properties2\",\"status\":\"CAPABILITY_ONLY\"},";
    else
#endif
    std::cout << "\"topology\":{\"active_compute_units\":null,\"status\":\"UNAVAILABLE\"},";
    std::cout << "\"limits\":{";
    std::cout << "\"max_compute_workgroup_invocations\":"<<p.limits.maxComputeWorkGroupInvocations<<",";
    std::cout << "\"max_compute_shared_memory_size\":"<<p.limits.maxComputeSharedMemorySize<<",";
    std::cout << "\"max_storage_buffer_range\":"<<p.limits.maxStorageBufferRange<<",";
    std::cout << "\"timestamp_period_ns\":"<<p.limits.timestampPeriod<<",";
    std::cout << "\"subgroup_size\":"<<sub.subgroupSize;
#ifdef VK_EXT_subgroup_size_control
    std::cout << ",\"min_subgroup_size\":"<<(subgroup_ctl?subctl.minSubgroupSize:sub.subgroupSize);
    std::cout << ",\"max_subgroup_size\":"<<(subgroup_ctl?subctl.maxSubgroupSize:sub.subgroupSize);
    std::cout << ",\"max_compute_workgroup_subgroups\":"<<(subgroup_ctl?subctl.maxComputeWorkgroupSubgroups:0);
#else
    std::cout << ",\"min_subgroup_size\":"<<sub.subgroupSize<<",\"max_subgroup_size\":"<<sub.subgroupSize<<",\"max_compute_workgroup_subgroups\":0";
#endif
    std::cout << "},";
    std::cout << "\"features\":{";
    std::cout << "\"compute_queue\":"<<(compute_q>=0?"true":"false")<<",";
    std::cout << "\"subgroup_size_control\":"<<(subgroup_ctl?"true":"false")<<",";
    std::cout << "\"ray_query\":"<<(ray_query?"true":"false")<<",";
    std::cout << "\"acceleration_structure\":"<<(accel?"true":"false")<<",";
    std::cout << "\"buffer_device_address\":"<<(address?"true":"false")<<",";
    std::cout << "\"ray_tracing_pipeline\":"<<(rtp?"true":"false")<<",";
    std::cout << "\"cooperative_matrix_khr\":"<<(coop_khr?"true":"false")<<",";
    std::cout << "\"cooperative_matrix_nv\":"<<(coop_nv?"true":"false")<<",";
    std::cout << "\"matrix_any\":"<<((coop_khr||coop_nv)?"true":"false")<<",";
    std::cout << "\"shader_float16_int8\":"<<(float16int8?"true":"false")<<",";
    std::cout << "\"storage16\":"<<(storage16?"true":"false");
    std::cout << "},";
    std::cout << "\"queue\":{\"compute_family\":"<<compute_q<<",\"family_count\":"<<nq<<"},";
    std::cout << "\"memory_heaps\":[";
    for(uint32_t i=0;i<mp.memoryHeapCount;i++){ if(i) std::cout<<","; std::cout<<"{\"bytes\":"<<uint64_t(mp.memoryHeaps[i].size)<<",\"flags\":"<<mp.memoryHeaps[i].flags<<"}"; }
    std::cout << "],\"extensions\":[";
    bool first=true; for(auto &x:ext){ if(!first) std::cout<<","; first=false; std::cout<<"\""<<esc(x.c_str())<<"\""; }
    std::cout << "]}" << std::endl;
    vkDestroyInstance(inst,nullptr); return 0;
}
