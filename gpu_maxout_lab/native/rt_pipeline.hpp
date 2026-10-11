// Shared runner types and RtScene are defined before this header.
// SBT layout: https://docs.vulkan.org/refpages/latest/refpages/source/vkCmdTraceRaysKHR.html
struct RtPipeline {
    VkPipeline pipeline=VK_NULL_HANDLE;
    Buf sbt;
    VkStridedDeviceAddressRegionKHR raygen{},miss{},hit{},callable{};
    PFN_vkCmdTraceRaysKHR trace=nullptr;
    uint32_t max_invocations=0;

    static VkDeviceSize align_up(VkDeviceSize value,VkDeviceSize alignment) {
        return (value+alignment-1)&~(alignment-1);
    }
    void create(Ctx& c,VkPipelineLayout layout,const std::string& rgen,
                const std::string& rmiss,const std::string& rchit) {
        auto create_pipeline=reinterpret_cast<PFN_vkCreateRayTracingPipelinesKHR>(
            vkGetDeviceProcAddr(c.dev,"vkCreateRayTracingPipelinesKHR"));
        auto get_handles=reinterpret_cast<PFN_vkGetRayTracingShaderGroupHandlesKHR>(
            vkGetDeviceProcAddr(c.dev,"vkGetRayTracingShaderGroupHandlesKHR"));
        trace=reinterpret_cast<PFN_vkCmdTraceRaysKHR>(vkGetDeviceProcAddr(c.dev,"vkCmdTraceRaysKHR"));
        if(!create_pipeline||!get_handles||!trace)throw std::runtime_error("RT pipeline entrypoints missing");
        VkPhysicalDeviceRayTracingPipelinePropertiesKHR props{};
        props.sType=VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_RAY_TRACING_PIPELINE_PROPERTIES_KHR;
        VkPhysicalDeviceProperties2 p{};
        p.sType=VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_PROPERTIES_2;p.pNext=&props;
        vkGetPhysicalDeviceProperties2(c.pd,&p);
        if(!props.shaderGroupHandleSize||!props.shaderGroupHandleAlignment||
           !props.shaderGroupBaseAlignment||props.maxRayRecursionDepth<1)
            throw std::runtime_error("invalid RT pipeline limits");
        max_invocations=props.maxRayDispatchInvocationCount;
        VkShaderModule modules[3]{};
        VkPipelineShaderStageCreateInfo stages[3]{};
        VkRayTracingShaderGroupCreateInfoKHR groups[3]{};
        const std::string files[]={rgen,rmiss,rchit};
        const VkShaderStageFlagBits kinds[]={VK_SHADER_STAGE_RAYGEN_BIT_KHR,VK_SHADER_STAGE_MISS_BIT_KHR,VK_SHADER_STAGE_CLOSEST_HIT_BIT_KHR};
        for(uint32_t i=0;i<3;i++){
            auto code=read_spv(files[i]);
            VkShaderModuleCreateInfo sm{};
            sm.sType=VK_STRUCTURE_TYPE_SHADER_MODULE_CREATE_INFO;sm.codeSize=code.size()*4;sm.pCode=code.data();
            ck(vkCreateShaderModule(c.dev,&sm,nullptr,&modules[i]),"RT shader module");
            stages[i].sType=VK_STRUCTURE_TYPE_PIPELINE_SHADER_STAGE_CREATE_INFO;
            stages[i].stage=kinds[i];stages[i].module=modules[i];stages[i].pName="main";
            groups[i].sType=VK_STRUCTURE_TYPE_RAY_TRACING_SHADER_GROUP_CREATE_INFO_KHR;
            groups[i].generalShader=groups[i].closestHitShader=groups[i].anyHitShader=groups[i].intersectionShader=VK_SHADER_UNUSED_KHR;
            groups[i].type=i==2?VK_RAY_TRACING_SHADER_GROUP_TYPE_TRIANGLES_HIT_GROUP_KHR:VK_RAY_TRACING_SHADER_GROUP_TYPE_GENERAL_KHR;
            if(i==2)groups[i].closestHitShader=i;else groups[i].generalShader=i;
        }
        VkRayTracingPipelineCreateInfoKHR ci{};
        ci.sType=VK_STRUCTURE_TYPE_RAY_TRACING_PIPELINE_CREATE_INFO_KHR;
        ci.stageCount=3;ci.pStages=stages;ci.groupCount=3;ci.pGroups=groups;
        ci.maxPipelineRayRecursionDepth=1;ci.layout=layout;
        VkResult result=create_pipeline(c.dev,VK_NULL_HANDLE,VK_NULL_HANDLE,1,&ci,nullptr,&pipeline);
        for(auto module:modules)vkDestroyShaderModule(c.dev,module,nullptr);
        ck(result,"create ray tracing pipeline");

        std::vector<uint8_t> handles(size_t(props.shaderGroupHandleSize)*3);
        ck(get_handles(c.dev,pipeline,0,3,handles.size(),handles.data()),"RT group handles");
        VkDeviceSize stride=align_up(props.shaderGroupHandleSize,props.shaderGroupHandleAlignment);
        VkDeviceSize region_step=align_up(stride,props.shaderGroupBaseAlignment);
        if(stride>props.maxShaderGroupStride)throw std::runtime_error("SBT stride exceeds device limit");
        sbt=mkbuf(c,region_step*3+props.shaderGroupBaseAlignment,
            VK_BUFFER_USAGE_SHADER_BINDING_TABLE_BIT_KHR|VK_BUFFER_USAGE_SHADER_DEVICE_ADDRESS_BIT,
            VK_MEMORY_PROPERTY_HOST_VISIBLE_BIT|VK_MEMORY_PROPERTY_HOST_COHERENT_BIT);
        VkDeviceAddress raw=RtScene::address(c,sbt);
        VkDeviceAddress start=align_up(raw,props.shaderGroupBaseAlignment);
        void* data;ck(vkMapMemory(c.dev,sbt.m,0,sbt.size,0,&data),"map SBT");
        std::memset(data,0,size_t(sbt.size));
        for(uint32_t i=0;i<3;i++)
            std::memcpy(static_cast<uint8_t*>(data)+(start-raw)+region_step*i,
                        handles.data()+size_t(props.shaderGroupHandleSize)*i,props.shaderGroupHandleSize);
        vkUnmapMemory(c.dev,sbt.m);
        raygen={start,stride,stride};
        miss={start+region_step,stride,stride};
        hit={start+region_step*2,stride,stride};
    }
    void dispatch(VkCommandBuffer cb,uint32_t width) {
        if(!width||width>max_invocations)throw std::runtime_error("RT launch exceeds maxRayDispatchInvocationCount");
        trace(cb,&raygen,&miss,&hit,&callable,width,1,1);
    }
    void destroy(Ctx& c) {
        freebuf(c,sbt);
        if(pipeline)vkDestroyPipeline(c.dev,pipeline,nullptr);
        pipeline=VK_NULL_HANDLE;
    }
};
