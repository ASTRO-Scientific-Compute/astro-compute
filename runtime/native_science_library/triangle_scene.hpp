// Conservative ray AABBs are candidate generators, never a distance oracle.
// Dynamic maintenance updates BOTH levels; a stale TLAS can hide moved geometry.
struct TriangleScene : RtScene {
    Buf base_boxes,instances,blas_scratch,tlas_scratch;
    uint32_t triangles=0;
    VkBuildAccelerationStructureFlagsKHR flags=VK_BUILD_ACCELERATION_STRUCTURE_PREFER_FAST_TRACE_BIT_KHR|VK_BUILD_ACCELERATION_STRUCTURE_ALLOW_UPDATE_BIT_KHR;
    VkAccelerationStructureGeometryKHR box_geometry(Ctx& c,VkDeviceAddress where) {
        VkAccelerationStructureGeometryKHR g{VK_STRUCTURE_TYPE_ACCELERATION_STRUCTURE_GEOMETRY_KHR};g.geometryType=VK_GEOMETRY_TYPE_AABBS_KHR;
        g.flags=VK_GEOMETRY_NO_DUPLICATE_ANY_HIT_INVOCATION_BIT_KHR;
        g.geometry.aabbs.sType=VK_STRUCTURE_TYPE_ACCELERATION_STRUCTURE_GEOMETRY_AABBS_DATA_KHR;
        g.geometry.aabbs.data.deviceAddress=where;g.geometry.aabbs.stride=sizeof(VkAabbPositionsKHR);return g;
    }
    VkAccelerationStructureGeometryKHR instance_geometry(Ctx& c) {
        VkAccelerationStructureGeometryKHR g{VK_STRUCTURE_TYPE_ACCELERATION_STRUCTURE_GEOMETRY_KHR};g.geometryType=VK_GEOMETRY_TYPE_INSTANCES_KHR;
        g.geometry.instances.sType=VK_STRUCTURE_TYPE_ACCELERATION_STRUCTURE_GEOMETRY_INSTANCES_DATA_KHR;
        g.geometry.instances.data.deviceAddress=address(c,instances);return g;
    }
    Buf upload(Ctx& c,VkCommandPool pool,const void* data,VkDeviceSize bytes) {
        Buf st=mkbuf(c,bytes,VK_BUFFER_USAGE_TRANSFER_SRC_BIT,VK_MEMORY_PROPERTY_HOST_VISIBLE_BIT|VK_MEMORY_PROPERTY_HOST_COHERENT_BIT);
        void* p;ck(vkMapMemory(c.dev,st.m,0,bytes,0,&p),"triangle staging map");std::memcpy(p,data,bytes);vkUnmapMemory(c.dev,st.m);
        Buf dest=mkbuf(c,bytes,VK_BUFFER_USAGE_TRANSFER_DST_BIT|VK_BUFFER_USAGE_ACCELERATION_STRUCTURE_BUILD_INPUT_READ_ONLY_BIT_KHR|VK_BUFFER_USAGE_SHADER_DEVICE_ADDRESS_BIT,VK_MEMORY_PROPERTY_DEVICE_LOCAL_BIT);
        onecopy(c,pool,st.b,dest.b,bytes);freebuf(c,st);return dest;
    }
    Buf scratch_for(Ctx& c,VkAccelerationStructureGeometryKHR& g,VkAccelerationStructureTypeKHR type,uint32_t n) {
        VkAccelerationStructureBuildGeometryInfoKHR info{VK_STRUCTURE_TYPE_ACCELERATION_STRUCTURE_BUILD_GEOMETRY_INFO_KHR};info.type=type;info.flags=flags;info.geometryCount=1;info.pGeometries=&g;
        VkAccelerationStructureBuildSizesInfoKHR sizes{VK_STRUCTURE_TYPE_ACCELERATION_STRUCTURE_BUILD_SIZES_INFO_KHR};build_sizes(c.dev,VK_ACCELERATION_STRUCTURE_BUILD_TYPE_DEVICE_KHR,&info,&n,&sizes);
        return mkbuf(c,std::max(sizes.buildScratchSize,sizes.updateScratchSize)+scratch_alignment,VK_BUFFER_USAGE_STORAGE_BUFFER_BIT|VK_BUFFER_USAGE_SHADER_DEVICE_ADDRESS_BIT,VK_MEMORY_PROPERTY_DEVICE_LOCAL_BIT);
    }
    void create_triangles(Ctx& c,VkCommandPool pool,const std::vector<uint32_t>& words) {
        auto start=Clock::now();triangles=words[5];
        create_as=reinterpret_cast<PFN_vkCreateAccelerationStructureKHR>(vkGetDeviceProcAddr(c.dev,"vkCreateAccelerationStructureKHR"));
        destroy_as=reinterpret_cast<PFN_vkDestroyAccelerationStructureKHR>(vkGetDeviceProcAddr(c.dev,"vkDestroyAccelerationStructureKHR"));
        build_sizes=reinterpret_cast<PFN_vkGetAccelerationStructureBuildSizesKHR>(vkGetDeviceProcAddr(c.dev,"vkGetAccelerationStructureBuildSizesKHR"));
        cmd_build=reinterpret_cast<PFN_vkCmdBuildAccelerationStructuresKHR>(vkGetDeviceProcAddr(c.dev,"vkCmdBuildAccelerationStructuresKHR"));
        as_address=reinterpret_cast<PFN_vkGetAccelerationStructureDeviceAddressKHR>(vkGetDeviceProcAddr(c.dev,"vkGetAccelerationStructureDeviceAddressKHR"));
        if(!create_as||!destroy_as||!build_sizes||!cmd_build||!as_address)throw std::runtime_error("triangle RT entrypoint missing");
        VkPhysicalDeviceAccelerationStructurePropertiesKHR asp{VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_ACCELERATION_STRUCTURE_PROPERTIES_KHR};VkPhysicalDeviceProperties2 props{VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_PROPERTIES_2};props.pNext=&asp;vkGetPhysicalDeviceProperties2(c.pd,&props);
        scratch_alignment=asp.minAccelerationStructureScratchOffsetAlignment;
        if(!scratch_alignment||triangles>asp.maxPrimitiveCount||asp.maxInstanceCount<1)throw std::runtime_error("triangle AS limits");
        std::vector<VkAabbPositionsKHR> boxes(triangles);
        for(uint32_t t=0;t<triangles;t++){
            float lo[3]={INFINITY,INFINITY,INFINITY},hi[3]={-INFINITY,-INFINITY,-INFINITY};
            for(uint32_t v=0;v<3;v++)for(uint32_t axis=0;axis<3;axis++){uint32_t w=words.at(words[11]+9*t+3*v+axis);float x;std::memcpy(&x,&w,4);lo[axis]=std::min(lo[axis],x);hi[axis]=std::max(hi[axis],x);}
            for(int axis=0;axis<3;axis++){float pad=std::max(0.000001f,std::max(std::abs(lo[axis]),std::abs(hi[axis]))*0.000001f);lo[axis]=std::nextafter(lo[axis]-pad,-INFINITY);hi[axis]=std::nextafter(hi[axis]+pad,INFINITY);}
            boxes[t]={lo[0],lo[1],lo[2],hi[0],hi[1],hi[2]};
        }
        base_boxes=upload(c,pool,boxes.data(),boxes.size()*sizeof(VkAabbPositionsKHR));auto geometry=box_geometry(c,address(c,base_boxes));
        blas=build(c,pool,geometry,VK_ACCELERATION_STRUCTURE_TYPE_BOTTOM_LEVEL_KHR,triangles,flags,blas_storage);blas_scratch=scratch_for(c,geometry,VK_ACCELERATION_STRUCTURE_TYPE_BOTTOM_LEVEL_KHR,triangles);
        VkAccelerationStructureDeviceAddressInfoKHR ai{VK_STRUCTURE_TYPE_ACCELERATION_STRUCTURE_DEVICE_ADDRESS_INFO_KHR};ai.accelerationStructure=blas;
        VkAccelerationStructureInstanceKHR instance{};instance.transform.matrix[0][0]=instance.transform.matrix[1][1]=instance.transform.matrix[2][2]=1.0f;instance.mask=0xff;instance.accelerationStructureReference=as_address(c.dev,&ai);
        instances=upload(c,pool,&instance,sizeof(instance));geometry=instance_geometry(c);
        tlas=build(c,pool,geometry,VK_ACCELERATION_STRUCTURE_TYPE_TOP_LEVEL_KHR,1,flags,tlas_storage);tlas_scratch=scratch_for(c,geometry,VK_ACCELERATION_STRUCTURE_TYPE_TOP_LEVEL_KHR,1);
        build_ms=std::chrono::duration<double,std::milli>(Clock::now()-start).count();
    }
    void maintain_one(Ctx& c,VkCommandBuffer cb,VkAccelerationStructureGeometryKHR& geometry,VkAccelerationStructureTypeKHR type,VkAccelerationStructureKHR object,const Buf& scratch,uint32_t n,bool update){
        VkAccelerationStructureBuildGeometryInfoKHR info{VK_STRUCTURE_TYPE_ACCELERATION_STRUCTURE_BUILD_GEOMETRY_INFO_KHR};info.type=type;info.flags=flags;info.mode=update?VK_BUILD_ACCELERATION_STRUCTURE_MODE_UPDATE_KHR:VK_BUILD_ACCELERATION_STRUCTURE_MODE_BUILD_KHR;info.srcAccelerationStructure=update?object:VK_NULL_HANDLE;info.dstAccelerationStructure=object;info.geometryCount=1;info.pGeometries=&geometry;
        VkDeviceAddress raw=address(c,scratch);info.scratchData.deviceAddress=(raw+scratch_alignment-1)&~VkDeviceAddress(scratch_alignment-1);
        VkAccelerationStructureBuildRangeInfoKHR range{};range.primitiveCount=n;const VkAccelerationStructureBuildRangeInfoKHR* ranges=&range;cmd_build(cb,1,&info,&ranges);
    }
    void maintain(Ctx& c,VkCommandBuffer cb,VkDeviceAddress boxes,bool update){
        VkMemoryBarrier mb{VK_STRUCTURE_TYPE_MEMORY_BARRIER};mb.srcAccessMask=VK_ACCESS_SHADER_WRITE_BIT|VK_ACCESS_ACCELERATION_STRUCTURE_READ_BIT_KHR|VK_ACCESS_ACCELERATION_STRUCTURE_WRITE_BIT_KHR;mb.dstAccessMask=VK_ACCESS_ACCELERATION_STRUCTURE_READ_BIT_KHR|VK_ACCESS_ACCELERATION_STRUCTURE_WRITE_BIT_KHR;
        vkCmdPipelineBarrier(cb,VK_PIPELINE_STAGE_COMPUTE_SHADER_BIT|VK_PIPELINE_STAGE_ACCELERATION_STRUCTURE_BUILD_BIT_KHR,VK_PIPELINE_STAGE_ACCELERATION_STRUCTURE_BUILD_BIT_KHR,0,1,&mb,0,nullptr,0,nullptr);
        auto geometry=box_geometry(c,boxes);maintain_one(c,cb,geometry,VK_ACCELERATION_STRUCTURE_TYPE_BOTTOM_LEVEL_KHR,blas,blas_scratch,triangles,update);
        mb.srcAccessMask=VK_ACCESS_ACCELERATION_STRUCTURE_WRITE_BIT_KHR;vkCmdPipelineBarrier(cb,VK_PIPELINE_STAGE_ACCELERATION_STRUCTURE_BUILD_BIT_KHR,VK_PIPELINE_STAGE_ACCELERATION_STRUCTURE_BUILD_BIT_KHR,0,1,&mb,0,nullptr,0,nullptr);
        geometry=instance_geometry(c);maintain_one(c,cb,geometry,VK_ACCELERATION_STRUCTURE_TYPE_TOP_LEVEL_KHR,tlas,tlas_scratch,1,update);
        mb.dstAccessMask=VK_ACCESS_ACCELERATION_STRUCTURE_READ_BIT_KHR|VK_ACCESS_SHADER_READ_BIT;vkCmdPipelineBarrier(cb,VK_PIPELINE_STAGE_ACCELERATION_STRUCTURE_BUILD_BIT_KHR,VK_PIPELINE_STAGE_COMPUTE_SHADER_BIT,0,1,&mb,0,nullptr,0,nullptr);
    }
    void destroy(Ctx& c){RtScene::destroy(c);freebuf(c,base_boxes);freebuf(c,instances);freebuf(c,blas_scratch);freebuf(c,tlas_scratch);}
};
