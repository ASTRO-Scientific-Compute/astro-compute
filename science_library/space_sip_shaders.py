"""Original integer-only ordered RN32 pixel distortion polynomial evaluation."""
BODIES={81:r'''
    uint u=A(i*2u),v=A(i*2u+1u),up[6],vp[6];up[0]=0x3f800000u;vp[0]=0x3f800000u;
    for(uint k=1u;k<=max(data[4],data[5]);k++){up[k]=sfmul(up[k-1u],u);vp[k]=sfmul(vp[k-1u],v);}
    uint sums[2];
    for(uint channel=0u;channel<2u;channel++){
        uint total=0u,index=0u,order=data[4u+channel],start=data[11u+channel];
        for(uint degree=2u;degree<=order;degree++){
            for(uint p=0u;p<=degree;p++){
                uint q=degree-p,term=sfmul(sfmul(data[start+index],up[p]),vp[q]);
                total=sfadd(total,term);index++;
            }
        }
        sums[channel]=total;
    }
    uint base=i*4u;result[base]=sfadd(u,sums[0]);result[base+1u]=sfadd(v,sums[1]);result[base+2u]=sums[0];result[base+3u]=sums[1];
'''}
