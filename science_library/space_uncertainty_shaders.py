"""Original per-pixel and ordered factor-projection GPU kernels."""
BODIES={65:r'''
    uint base=5u*i;
    for(uint j=0u;j<5u;j++)result[base+j]=0u;result[base]=1u;
    if(data[data[8]+i]==0u)return;
    uint signal=A(i),background=B(i),gain=C(i),source=0u;
    if(sfless(0u,signal)&&sfless(0u,gain))source=sfdiv(signal,gain);
    uint total=sfadd(background,source);result[base]=2u;if(total==0u)return;
    result[base]=0u;result[base+1u]=source;result[base+2u]=total;result[base+3u]=sfsqrt(total);result[base+4u]=sfdiv(0x3f800000u,total);
''',66:r'''
    uint n=data[4],factors=data[5],base=8u*i,active_count=0u,total_flux=0u,independent=0u,correlated=0u;
    for(uint j=0u;j<8u;j++)result[base+j]=0u;result[base]=1u;
    for(uint j=0u;j<n;j++){
        uint index=i*n+j,w=B(index);if((w&0x7fffffffu)==0u)continue;
        active_count++;total_flux=sfadd(total_flux,sfmul(w,A(index)));
        independent=sfadd(independent,sfmul(sfmul(w,w),C(index)));
    }
    if(active_count==0u)return;
    for(uint k=0u;k<factors;k++){
        uint projection=0u;
        for(uint j=0u;j<n;j++){
            uint w=B(i*n+j);if((w&0x7fffffffu)==0u)continue;
            projection=sfadd(projection,sfmul(w,data[data[8]+(i*factors+k)*n+j]));
        }
        correlated=sfadd(correlated,sfmul(projection,projection));
    }
    uint variance=sfadd(independent,correlated);result[base]=2u;result[base+1u]=active_count;result[base+2u]=total_flux;
    if(variance==0u)return;
    uint error=sfsqrt(variance);result[base]=0u;result[base+3u]=independent;result[base+4u]=correlated;result[base+5u]=variance;result[base+6u]=error;result[base+7u]=sfdiv(total_flux,error);
'''}
