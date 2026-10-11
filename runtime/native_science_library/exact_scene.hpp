// Uses the shared Max Out AS build/allocation helpers; custom user-input AABBs.
struct ExactScene : RtScene {
    void create_exact(Ctx& c,VkCommandPool pool,const std::vector<uint32_t>& words) {
        auto start=Clock::now();
        create_as=reinterpret_cast<PFN_vkCreateAccelerationStructureKHR>(vkGetDeviceProcAddr(c.dev,"vkCreateAccelerationStructureKHR"));
        destroy_as=reinterpret_cast<PFN_vkDestroyAccelerationStructureKHR>(vkGetDeviceProcAddr(c.dev,"vkDestroyAccelerationStructureKHR"));
        build_sizes=reinterpret_cast<PFN_vkGetAccelerationStructureBuildSizesKHR>(vkGetDeviceProcAddr(c.dev,"vkGetAccelerationStructureBuildSizesKHR"));
        cmd_build=reinterpret_cast<PFN_vkCmdBuildAccelerationStructuresKHR>(vkGetDeviceProcAddr(c.dev,"vkCmdBuildAccelerationStructuresKHR"));
        as_address=reinterpret_cast<PFN_vkGetAccelerationStructureDeviceAddressKHR>(vkGetDeviceProcAddr(c.dev,"vkGetAccelerationStructureDeviceAddressKHR"));
        if(!create_as||!destroy_as||!build_sizes||!cmd_build||!as_address)throw std::runtime_error("RT entrypoints missing");
        VkPhysicalDeviceAccelerationStructurePropertiesKHR asp{VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_ACCELERATION_STRUCTURE_PROPERTIES_KHR};
        VkPhysicalDeviceProperties2 prop{VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_PROPERTIES_2};prop.pNext=&asp;vkGetPhysicalDeviceProperties2(c.pd,&prop);
        scratch_alignment=asp.minAccelerationStructureScratchOffsetAlignment;
        uint32_t count=words[5],base=words[11];
        if(!scratch_alignment||asp.maxPrimitiveCount<std::max(count,1u)||asp.maxInstanceCount<1)throw std::runtime_error("RT scene limits");
        uint64_t r2;
        if(words[2]==9){size_t end=words[12]+2*words[8];r2=uint64_t(words.at(end))|(uint64_t(words.at(end+1))<<32);}
        else r2=uint64_t(words[8])|(uint64_t(words[9])<<32);
        // |integer coordinates|<=1e9. Float origin/box errors are far below1024
        // coordinate ticks even with maximum radius sqrt(12e18). Widening never
        // decides a match: exact64 squared distance is the only narrowphase.
        double radius=std::ceil(std::sqrt(double(r2)))+1024.0;
        std::vector<VkAabbPositionsKHR> boxes(std::max(count,1u));
        for(uint32_t i=0;i<count;i++){
            double x=int32_t(words.at(base+3*i)),y=int32_t(words.at(base+3*i+1)),z=int32_t(words.at(base+3*i+2));
            boxes[i]={std::nextafter(float(x-radius),-INFINITY),std::nextafter(float(y-radius),-INFINITY),std::nextafter(float(z-radius),-INFINITY),std::nextafter(float(x+radius),INFINITY),std::nextafter(float(y+radius),INFINITY),std::nextafter(float(z+radius),INFINITY)};
        }
        if(!count)boxes[0]={1e20f,1e20f,1e20f,1.00001e20f,1.00001e20f,1.00001e20f};
        auto upload=[&](const void* data,VkDeviceSize bytes){
            Buf staging=mkbuf(c,bytes,VK_BUFFER_USAGE_TRANSFER_SRC_BIT,VK_MEMORY_PROPERTY_HOST_VISIBLE_BIT|VK_MEMORY_PROPERTY_HOST_COHERENT_BIT);
            void* ptr;ck(vkMapMemory(c.dev,staging.m,0,bytes,0,&ptr),"map AS input");std::memcpy(ptr,data,size_t(bytes));vkUnmapMemory(c.dev,staging.m);
            Buf dest=mkbuf(c,bytes,VK_BUFFER_USAGE_TRANSFER_DST_BIT|VK_BUFFER_USAGE_ACCELERATION_STRUCTURE_BUILD_INPUT_READ_ONLY_BIT_KHR|VK_BUFFER_USAGE_SHADER_DEVICE_ADDRESS_BIT,VK_MEMORY_PROPERTY_DEVICE_LOCAL_BIT);
            onecopy(c,pool,staging.b,dest.b,bytes);freebuf(c,staging);return dest;
        };
        Buf input=upload(boxes.data(),boxes.size()*sizeof(VkAabbPositionsKHR));
        VkAccelerationStructureGeometryKHR geometry{VK_STRUCTURE_TYPE_ACCELERATION_STRUCTURE_GEOMETRY_KHR};geometry.geometryType=VK_GEOMETRY_TYPE_AABBS_KHR;
        geometry.flags=VK_GEOMETRY_NO_DUPLICATE_ANY_HIT_INVOCATION_BIT_KHR;
        geometry.geometry.aabbs.sType=VK_STRUCTURE_TYPE_ACCELERATION_STRUCTURE_GEOMETRY_AABBS_DATA_KHR;
        geometry.geometry.aabbs.data.deviceAddress=address(c,input);geometry.geometry.aabbs.stride=sizeof(VkAabbPositionsKHR);
        auto flags=VK_BUILD_ACCELERATION_STRUCTURE_PREFER_FAST_TRACE_BIT_KHR;
        blas=build(c,pool,geometry,VK_ACCELERATION_STRUCTURE_TYPE_BOTTOM_LEVEL_KHR,uint32_t(boxes.size()),flags,blas_storage);freebuf(c,input);
        VkAccelerationStructureDeviceAddressInfoKHR ai{VK_STRUCTURE_TYPE_ACCELERATION_STRUCTURE_DEVICE_ADDRESS_INFO_KHR};ai.accelerationStructure=blas;
        VkAccelerationStructureInstanceKHR instance{};instance.transform.matrix[0][0]=instance.transform.matrix[1][1]=instance.transform.matrix[2][2]=1;instance.mask=0xff;instance.accelerationStructureReference=as_address(c.dev,&ai);
        Buf instances=upload(&instance,sizeof(instance));
        geometry={VK_STRUCTURE_TYPE_ACCELERATION_STRUCTURE_GEOMETRY_KHR};geometry.geometryType=VK_GEOMETRY_TYPE_INSTANCES_KHR;geometry.geometry.instances.sType=VK_STRUCTURE_TYPE_ACCELERATION_STRUCTURE_GEOMETRY_INSTANCES_DATA_KHR;geometry.geometry.instances.data.deviceAddress=address(c,instances);
        tlas=build(c,pool,geometry,VK_ACCELERATION_STRUCTURE_TYPE_TOP_LEVEL_KHR,1,flags,tlas_storage);freebuf(c,instances);
        build_ms=std::chrono::duration<double,std::milli>(Clock::now()-start).count();
    }
};
