// Included after the native runner's Ctx/Buf/copy helpers.
// API rules: https://docs.vulkan.org/guide/latest/extensions/ray_tracing.html
// Resident scene construction is outside the timed traversal interval.
struct RtScene {
    PFN_vkCreateAccelerationStructureKHR create_as=nullptr;
    PFN_vkDestroyAccelerationStructureKHR destroy_as=nullptr;
    PFN_vkGetAccelerationStructureBuildSizesKHR build_sizes=nullptr;
    PFN_vkCmdBuildAccelerationStructuresKHR cmd_build=nullptr;
    PFN_vkGetAccelerationStructureDeviceAddressKHR as_address=nullptr;
    VkAccelerationStructureKHR blas=VK_NULL_HANDLE,tlas=VK_NULL_HANDLE;
    Buf blas_storage,tlas_storage;
    uint32_t scratch_alignment=256;
    double build_ms=0;
    VkPipelineStageFlags traversal_stage=VK_PIPELINE_STAGE_COMPUTE_SHADER_BIT;

    static VkDeviceAddress address(Ctx& c, const Buf& b) {
        VkBufferDeviceAddressInfo info{};
        info.sType=VK_STRUCTURE_TYPE_BUFFER_DEVICE_ADDRESS_INFO;
        info.buffer=b.b;
        return vkGetBufferDeviceAddress(c.dev,&info);
    }

    VkAccelerationStructureKHR build(Ctx& c, VkCommandPool pool,
        VkAccelerationStructureGeometryKHR& geometry,
        VkAccelerationStructureTypeKHR type, uint32_t primitives,
        VkBuildAccelerationStructureFlagsKHR flags, Buf& storage) {
        VkAccelerationStructureBuildGeometryInfoKHR info{};
        info.sType=VK_STRUCTURE_TYPE_ACCELERATION_STRUCTURE_BUILD_GEOMETRY_INFO_KHR;
        info.type=type;
        info.flags=flags;
        info.mode=VK_BUILD_ACCELERATION_STRUCTURE_MODE_BUILD_KHR;
        info.geometryCount=1;
        info.pGeometries=&geometry;
        VkAccelerationStructureBuildSizesInfoKHR sizes{};
        sizes.sType=VK_STRUCTURE_TYPE_ACCELERATION_STRUCTURE_BUILD_SIZES_INFO_KHR;
        build_sizes(c.dev,VK_ACCELERATION_STRUCTURE_BUILD_TYPE_DEVICE_KHR,&info,&primitives,&sizes);
        storage=mkbuf(c,sizes.accelerationStructureSize,
            VK_BUFFER_USAGE_ACCELERATION_STRUCTURE_STORAGE_BIT_KHR|VK_BUFFER_USAGE_SHADER_DEVICE_ADDRESS_BIT,
            VK_MEMORY_PROPERTY_DEVICE_LOCAL_BIT);
        VkAccelerationStructureCreateInfoKHR ci{};
        ci.sType=VK_STRUCTURE_TYPE_ACCELERATION_STRUCTURE_CREATE_INFO_KHR;
        ci.buffer=storage.b; ci.size=sizes.accelerationStructureSize; ci.type=type;
        VkAccelerationStructureKHR result;
        ck(create_as(c.dev,&ci,nullptr,&result),"create acceleration structure");
        // Buffer base alignment alone does not guarantee scratch address alignment.
        Buf scratch=mkbuf(c,sizes.buildScratchSize+scratch_alignment,
            VK_BUFFER_USAGE_STORAGE_BUFFER_BIT|VK_BUFFER_USAGE_SHADER_DEVICE_ADDRESS_BIT,
            VK_MEMORY_PROPERTY_DEVICE_LOCAL_BIT);
        VkDeviceAddress raw=address(c,scratch);
        info.scratchData.deviceAddress=(raw+scratch_alignment-1)&~VkDeviceAddress(scratch_alignment-1);
        info.dstAccelerationStructure=result;
        VkAccelerationStructureBuildRangeInfoKHR range{};
        range.primitiveCount=primitives;
        const VkAccelerationStructureBuildRangeInfoKHR* ranges=&range;
        VkCommandBufferAllocateInfo ca{};
        ca.sType=VK_STRUCTURE_TYPE_COMMAND_BUFFER_ALLOCATE_INFO;
        ca.commandPool=pool;ca.level=VK_COMMAND_BUFFER_LEVEL_PRIMARY;ca.commandBufferCount=1;
        VkCommandBuffer cb;
        ck(vkAllocateCommandBuffers(c.dev,&ca,&cb),"allocate AS command");
        VkCommandBufferBeginInfo begin{};
        begin.sType=VK_STRUCTURE_TYPE_COMMAND_BUFFER_BEGIN_INFO;
        begin.flags=VK_COMMAND_BUFFER_USAGE_ONE_TIME_SUBMIT_BIT;
        ck(vkBeginCommandBuffer(cb,&begin),"begin AS build");
        VkMemoryBarrier before{};
        before.sType=VK_STRUCTURE_TYPE_MEMORY_BARRIER;
        before.srcAccessMask=VK_ACCESS_TRANSFER_WRITE_BIT|VK_ACCESS_ACCELERATION_STRUCTURE_WRITE_BIT_KHR;
        before.dstAccessMask=VK_ACCESS_SHADER_READ_BIT|VK_ACCESS_ACCELERATION_STRUCTURE_READ_BIT_KHR;
        vkCmdPipelineBarrier(cb,VK_PIPELINE_STAGE_TRANSFER_BIT|VK_PIPELINE_STAGE_ACCELERATION_STRUCTURE_BUILD_BIT_KHR,
            VK_PIPELINE_STAGE_ACCELERATION_STRUCTURE_BUILD_BIT_KHR,0,1,&before,0,nullptr,0,nullptr);
        cmd_build(cb,1,&info,&ranges);
        VkMemoryBarrier after{};
        after.sType=VK_STRUCTURE_TYPE_MEMORY_BARRIER;
        after.srcAccessMask=VK_ACCESS_ACCELERATION_STRUCTURE_WRITE_BIT_KHR;
        after.dstAccessMask=VK_ACCESS_ACCELERATION_STRUCTURE_READ_BIT_KHR;
        vkCmdPipelineBarrier(cb,VK_PIPELINE_STAGE_ACCELERATION_STRUCTURE_BUILD_BIT_KHR,
            traversal_stage|VK_PIPELINE_STAGE_ACCELERATION_STRUCTURE_BUILD_BIT_KHR,
            0,1,&after,0,nullptr,0,nullptr);
        ck(vkEndCommandBuffer(cb),"end AS build");
        VkSubmitInfo submit{};
        submit.sType=VK_STRUCTURE_TYPE_SUBMIT_INFO;
        submit.commandBufferCount=1;submit.pCommandBuffers=&cb;
        ck(vkQueueSubmit(c.q,1,&submit,VK_NULL_HANDLE),"submit AS build");
        ck(vkQueueWaitIdle(c.q),"wait AS build");
        vkFreeCommandBuffers(c.dev,pool,1,&cb);
        freebuf(c,scratch);
        return result;
    }

    void create(Ctx& c,VkCommandPool pool,const std::string& hint,bool pipeline=false) {
        traversal_stage=pipeline?VK_PIPELINE_STAGE_RAY_TRACING_SHADER_BIT_KHR:VK_PIPELINE_STAGE_COMPUTE_SHADER_BIT;
        auto start=Clock::now();
        create_as=reinterpret_cast<PFN_vkCreateAccelerationStructureKHR>(vkGetDeviceProcAddr(c.dev,"vkCreateAccelerationStructureKHR"));
        destroy_as=reinterpret_cast<PFN_vkDestroyAccelerationStructureKHR>(vkGetDeviceProcAddr(c.dev,"vkDestroyAccelerationStructureKHR"));
        build_sizes=reinterpret_cast<PFN_vkGetAccelerationStructureBuildSizesKHR>(vkGetDeviceProcAddr(c.dev,"vkGetAccelerationStructureBuildSizesKHR"));
        cmd_build=reinterpret_cast<PFN_vkCmdBuildAccelerationStructuresKHR>(vkGetDeviceProcAddr(c.dev,"vkCmdBuildAccelerationStructuresKHR"));
        as_address=reinterpret_cast<PFN_vkGetAccelerationStructureDeviceAddressKHR>(vkGetDeviceProcAddr(c.dev,"vkGetAccelerationStructureDeviceAddressKHR"));
        if(!create_as||!destroy_as||!build_sizes||!cmd_build||!as_address)
            throw std::runtime_error("RT entrypoints missing");
        VkPhysicalDeviceAccelerationStructurePropertiesKHR asp{};
        asp.sType=VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_ACCELERATION_STRUCTURE_PROPERTIES_KHR;
        VkPhysicalDeviceProperties2 prop{};
        prop.sType=VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_PROPERTIES_2;prop.pNext=&asp;
        vkGetPhysicalDeviceProperties2(c.pd,&prop);
        scratch_alignment=asp.minAccelerationStructureScratchOffsetAlignment;
        if(!scratch_alignment||asp.maxPrimitiveCount<4096||asp.maxInstanceCount<1)
            throw std::runtime_error("RT scene exceeds acceleration-structure limits");
        VkFormatProperties format{};
        vkGetPhysicalDeviceFormatProperties(c.pd,VK_FORMAT_R32G32B32_SFLOAT,&format);
        if(!(format.bufferFeatures&VK_FORMAT_FEATURE_ACCELERATION_STRUCTURE_VERTEX_BUFFER_BIT_KHR))
            throw std::runtime_error("RT vertex format unsupported");

        struct Vertex {float x,y,z;};
        std::vector<Vertex> vertices;
        for(uint32_t i=0;i<4096;i++) {
            float x=float(i&63u)*2.0f,y=float(i>>6u)*2.0f,z=float(1u+(i&3u));
            vertices.push_back({x,y,z});vertices.push_back({x+1.0f,y,z});vertices.push_back({x,y+1.0f,z});
        }
        auto upload=[&](const void* data,VkDeviceSize bytes) {
            Buf staging=mkbuf(c,bytes,VK_BUFFER_USAGE_TRANSFER_SRC_BIT,
                VK_MEMORY_PROPERTY_HOST_VISIBLE_BIT|VK_MEMORY_PROPERTY_HOST_COHERENT_BIT);
            void* ptr;ck(vkMapMemory(c.dev,staging.m,0,bytes,0,&ptr),"map RT staging");
            std::memcpy(ptr,data,size_t(bytes));vkUnmapMemory(c.dev,staging.m);
            Buf dest=mkbuf(c,bytes,VK_BUFFER_USAGE_TRANSFER_DST_BIT|
                VK_BUFFER_USAGE_ACCELERATION_STRUCTURE_BUILD_INPUT_READ_ONLY_BIT_KHR|
                VK_BUFFER_USAGE_SHADER_DEVICE_ADDRESS_BIT,VK_MEMORY_PROPERTY_DEVICE_LOCAL_BIT);
            onecopy(c,pool,staging.b,dest.b,bytes);freebuf(c,staging);return dest;
        };
        Buf verts=upload(vertices.data(),vertices.size()*sizeof(Vertex));
        VkAccelerationStructureGeometryKHR geometry{};
        geometry.sType=VK_STRUCTURE_TYPE_ACCELERATION_STRUCTURE_GEOMETRY_KHR;
        geometry.geometryType=VK_GEOMETRY_TYPE_TRIANGLES_KHR;
        geometry.flags=VK_GEOMETRY_OPAQUE_BIT_KHR;
        auto& tri=geometry.geometry.triangles;
        tri.sType=VK_STRUCTURE_TYPE_ACCELERATION_STRUCTURE_GEOMETRY_TRIANGLES_DATA_KHR;
        tri.vertexFormat=VK_FORMAT_R32G32B32_SFLOAT;tri.vertexData.deviceAddress=address(c,verts);
        tri.vertexStride=sizeof(Vertex);tri.maxVertex=uint32_t(vertices.size()-1);
        tri.indexType=VK_INDEX_TYPE_NONE_KHR;
        auto flags=hint=="fast_build"?VK_BUILD_ACCELERATION_STRUCTURE_PREFER_FAST_BUILD_BIT_KHR:
                                     VK_BUILD_ACCELERATION_STRUCTURE_PREFER_FAST_TRACE_BIT_KHR;
        blas=build(c,pool,geometry,VK_ACCELERATION_STRUCTURE_TYPE_BOTTOM_LEVEL_KHR,4096,flags,blas_storage);
        freebuf(c,verts);
        VkAccelerationStructureDeviceAddressInfoKHR ai{};
        ai.sType=VK_STRUCTURE_TYPE_ACCELERATION_STRUCTURE_DEVICE_ADDRESS_INFO_KHR;
        ai.accelerationStructure=blas;
        VkAccelerationStructureInstanceKHR instance{};
        instance.transform.matrix[0][0]=instance.transform.matrix[1][1]=instance.transform.matrix[2][2]=1.0f;
        instance.mask=0xff;instance.flags=VK_GEOMETRY_INSTANCE_TRIANGLE_FACING_CULL_DISABLE_BIT_KHR;
        instance.accelerationStructureReference=as_address(c.dev,&ai);
        Buf instances=upload(&instance,sizeof(instance));
        geometry={};geometry.sType=VK_STRUCTURE_TYPE_ACCELERATION_STRUCTURE_GEOMETRY_KHR;
        geometry.geometryType=VK_GEOMETRY_TYPE_INSTANCES_KHR;
        geometry.geometry.instances.sType=VK_STRUCTURE_TYPE_ACCELERATION_STRUCTURE_GEOMETRY_INSTANCES_DATA_KHR;
        geometry.geometry.instances.data.deviceAddress=address(c,instances);
        tlas=build(c,pool,geometry,VK_ACCELERATION_STRUCTURE_TYPE_TOP_LEVEL_KHR,1,flags,tlas_storage);
        freebuf(c,instances);
        build_ms=std::chrono::duration<double,std::milli>(Clock::now()-start).count();
    }

    void destroy(Ctx& c) {
        if(tlas)destroy_as(c.dev,tlas,nullptr);
        if(blas)destroy_as(c.dev,blas,nullptr);
        freebuf(c,tlas_storage);freebuf(c,blas_storage);
        tlas=blas=VK_NULL_HANDLE;
    }
};

static uint32_t rt_mix(uint32_t x) {
    x^=x>>16;x*=0x7feb352du;x^=x>>15;x*=0x846ca68bu;x^=x>>16;return x;
}
static uint32_t rt_fold(uint32_t h,uint32_t x) {
    return h^rt_mix(x+0x9e3779b9u+(h<<6)+(h>>2));
}
// Independent analytic oracle: rays lie strictly inside one triangle or outside
// the entire scene, with exact integer distances. No GPU baseline is trusted.
static uint32_t rt_expected(uint32_t gid,uint32_t loops,uint32_t seed,bool hybrid=false) {
    uint32_t h=0x811c9dc5u;
    for(uint32_t k=0;k<loops;k++) {
        uint32_t tri=rt_mix(gid^seed^(k*0x9e3779b9u))&4095u;
        bool miss=((gid+k)&7u)==7u;
        float distance=float(1u+(tri&3u));
        uint32_t bits;std::memcpy(&bits,&distance,sizeof(bits));
        h=rt_fold(rt_fold(h,miss?0u:tri+1u),miss?0u:bits);
        if(hybrid){
            for(uint32_t lane=0;lane<4;lane++){
                uint32_t a=rt_mix(gid^seed^(k*0x85ebca6bu)^(lane*0x9e3779b9u));
                for(uint32_t step=0;step<32;step++)a=rt_mix(a+0x6d2b79f5u+lane);
                h=rt_fold(h,a);
            }
        }
    }
    return h;
}
