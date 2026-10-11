"""GPU integer-only RN32 Barker cubic solve and parabolic state."""
BODIES={77:r'''
    uint q=A(i*2u),mean=sfadd(A(i*2u+1u),0u),d=0u;
    if(mean!=0u){
        bool negative=sfless(mean,0u);uint target=negative?sfneg(mean):mean,lo=0u,hi=0x40800000u;
        for(uint step=0u;step<32u;step++){
            uint mid=sfmul(sfadd(lo,hi),0x3f000000u),cube=sfmul(sfmul(mid,mid),mid);
            uint residual=sfsub(sfadd(mid,sfdiv(cube,0x40400000u)),target);
            if(sfless(residual,0u))lo=mid;else hi=mid;
        }
        d=sfmul(sfadd(lo,hi),0x3f000000u);if(negative)d=sfneg(d);
    }
    uint square=sfmul(d,d),den=sfadd(0x3f800000u,square),radius=sfmul(q,den);
    uint x=sfmul(q,sfsub(0x3f800000u,square)),y=sfmul(sfmul(0x40000000u,q),d);
    uint scale=sfdiv(sfsqrt(sfdiv(sfmul(0x40000000u,data[8]),q)),den),base=i*8u;
    result[base]=d;result[base+1u]=radius;result[base+2u]=x;result[base+3u]=y;result[base+4u]=0u;
    result[base+5u]=sfneg(sfmul(scale,d));result[base+6u]=scale;result[base+7u]=0u;
'''}
