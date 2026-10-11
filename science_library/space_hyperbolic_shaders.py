"""Integer-only GPU hyperbolic polynomial and fixed32-step implicit solve."""
HELPERS=r'''
const uint HYP_SINH[11]=uint[11](0x3f800000u,0x3e2aaaabu,0x3c088889u,0x39500d01u,0x3638ef1du,0x32d7322bu,0x2f309231u,0x2b573f9fu,0x274a963cu,0x2317a4dau,0x1eb8dc78u);
const uint HYP_COSH[12]=uint[12](0x3f800000u,0x3f000000u,0x3d2aaaabu,0x3ab60b61u,0x37d00d01u,0x3493f27eu,0x310f76c7u,0x2d49cba5u,0x29573f9fu,0x253413c3u,0x20f2a15du,0x1c8671cbu);
uint hyper_sinh(uint x){uint q=sfmul(x,x),v=HYP_SINH[10];for(int k=9;k>=0;k--)v=sfadd(HYP_SINH[k],sfmul(q,v));return sfmul(x,v);}
uint hyper_cosh(uint x){uint q=sfmul(x,x),v=HYP_COSH[11];for(int k=10;k>=0;k--)v=sfadd(HYP_COSH[k],sfmul(q,v));return v;}
'''
BODIES={76:r'''
    uint a=A(i*3u),e=A(i*3u+1u),mean=sfadd(A(i*3u+2u),0u),h=0u;
    if(mean!=0u){
        bool negative=sfless(mean,0u);uint target=negative?sfneg(mean):mean,lo=0u,hi=0x40800000u;
        for(uint step=0u;step<32u;step++){
            uint mid=sfmul(sfadd(lo,hi),0x3f000000u);
            uint residual=sfsub(sfsub(sfmul(e,hyper_sinh(mid)),mid),target);
            if(sfless(residual,0u))lo=mid;else hi=mid;
        }
        h=sfmul(sfadd(lo,hi),0x3f000000u);if(negative)h=sfneg(h);
    }
    uint s=hyper_sinh(h),c=hyper_cosh(h),beta=sfsqrt(sfsub(sfmul(e,e),0x3f800000u));
    uint d=sfsub(sfmul(e,c),0x3f800000u),radius=sfmul(a,d),scale=sfdiv(sfsqrt(sfdiv(data[8],a)),d),base=i*8u;
    result[base]=h;result[base+1u]=radius;
    result[base+2u]=sfmul(a,sfsub(e,c));result[base+3u]=sfmul(sfmul(a,beta),s);result[base+4u]=0u;
    result[base+5u]=sfneg(sfmul(scale,s));result[base+6u]=sfmul(sfmul(scale,beta),c);result[base+7u]=0u;
'''}
