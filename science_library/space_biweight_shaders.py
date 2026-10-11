"""Original ordered robust-statistics kernel with independent insertion sorts."""
BODIES={63:r'''
    uint n=data[4],count=0u,ordered[256],base=9u*i;
    for(uint k=0u;k<9u;k++)result[base+k]=0u;result[base]=1u;
    for(uint j=0u;j<n;j++)if(B(i*n+j)!=0u){
        uint value=A(i*n+j),position=count;
        while(position>0u){if(!sfless(value,ordered[position-1u]))break;ordered[position]=ordered[position-1u];position--;}
        ordered[position]=value;count++;
    }
    result[base+1u]=count;if(count==0u)return;
    uint middle=count/2u,center;
    if(count%2u==1u)center=sfadd(ordered[middle],0u);
    else center=sfadd(sfmul(ordered[middle-1u],0x3f000000u),sfmul(ordered[middle],0x3f000000u));
    uint seen=0u;
    for(uint j=0u;j<n;j++)if(B(i*n+j)!=0u){
        uint value=sfsub(A(i*n+j),center)&0x7fffffffu,position=seen;
        while(position>0u){if(!sfless(value,ordered[position-1u]))break;ordered[position]=ordered[position-1u];position--;}
        ordered[position]=value;seen++;
    }
    uint mad;
    if(count%2u==1u)mad=sfadd(ordered[middle],0u);
    else mad=sfadd(sfmul(ordered[middle-1u],0x3f000000u),sfmul(ordered[middle],0x3f000000u));
    result[base]=2u;if(mad==0u)return;
    uint ls=sfmul(data[8],mad),vs=sfmul(data[9],mad),a=0u,b=0u,c=0u,d=0u,nl=0u,nv=0u;
    for(uint j=0u;j<n;j++)if(B(i*n+j)!=0u){
        uint residual=sfsub(A(i*n+j),center),u=sfdiv(residual,ls);
        if(sfless(u&0x7fffffffu,0x3f800000u)){
            uint t=sfsub(0x3f800000u,sfmul(u,u)),weight=sfmul(t,t);
            a=sfadd(a,sfmul(residual,weight));b=sfadd(b,weight);nl++;
        }
        u=sfdiv(residual,vs);
        if(sfless(u&0x7fffffffu,0x3f800000u)){
            uint u2=sfmul(u,u),t=sfsub(0x3f800000u,u2),t2=sfmul(t,t),t4=sfmul(t2,t2);
            c=sfadd(c,sfmul(sfmul(residual,residual),t4));
            d=sfadd(d,sfmul(t,sfsub(0x3f800000u,sfmul(0x40a00000u,u2))));nv++;
        }
    }
    result[base]=3u;if(b==0u||!sfless(sfmul(sfu(count),0x37800000u),d&0x7fffffffu))return;
    uint location=sfadd(center,sfdiv(a,b)),variance=sfdiv(sfmul(sfu(count),c),sfmul(d,d)),scale=sfsqrt(variance);
    result[base]=0u;result[base+2u]=center;result[base+3u]=mad;result[base+4u]=location;result[base+5u]=variance;result[base+6u]=scale;result[base+7u]=nl;result[base+8u]=nv;
'''}
