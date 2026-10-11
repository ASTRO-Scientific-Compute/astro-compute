"""GPU fixed-step implicit solve, separate from the Fraction reference."""
from .space_search_shaders import TRIG
HELPERS = TRIG
BODIES = {75:r'''
    uint a=A(i*3u),e=sfadd(A(i*3u+1u),0u),mean=sfadd(A(i*3u+2u),0u),ecc=mean;
    if(e!=0u&&mean!=0u&&mean!=0x3f000000u){
        bool reflected=sfless(0x3f000000u,mean);
        uint target=reflected?sfsub(0x3f800000u,mean):mean,lo=0u,hi=0x3f000000u;
        for(uint step=0u;step<32u;step++){
            uint mid=sfmul(sfadd(lo,hi),0x3f000000u);uvec2 trig=sincos_turn(mid);
            uint residual=sfsub(sfmul(0x40c90fdbu,sfsub(mid,target)),sfmul(e,trig.x));
            if(sfless(residual,0u))lo=mid;else hi=mid;
        }
        uint u=sfmul(sfadd(lo,hi),0x3f000000u);ecc=reflected?sfsub(0x3f800000u,u):u;
    }
    uvec2 trig=sincos_turn(ecc);
    uint beta=sfsqrt(sfsub(0x3f800000u,sfmul(e,e))),d=sfsub(0x3f800000u,sfmul(e,trig.y));
    uint radius=sfmul(a,d),scale=sfdiv(sfsqrt(sfdiv(data[8],a)),d),base=i*8u;
    result[base]=ecc;result[base+1u]=radius;
    result[base+2u]=sfmul(a,sfsub(trig.y,e));result[base+3u]=sfmul(sfmul(a,beta),trig.x);result[base+4u]=0u;
    result[base+5u]=sfneg(sfmul(scale,trig.x));result[base+6u]=sfmul(sfmul(scale,beta),trig.y);result[base+7u]=0u;
'''}
