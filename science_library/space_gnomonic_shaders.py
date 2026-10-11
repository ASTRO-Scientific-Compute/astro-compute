"""Integer-only RN32 gnomonic projection with explicit denominator guard."""
from .space_search_shaders import TRIG as HELPERS
BODIES={79:r'''
    uvec2 sc=sincos_turn(A(i*2u+1u)),base_sc=sincos_turn(data[9]),da=sincos_turn(sfsub(A(i*2u),data[8]));
    uint d=sfadd(sfmul(sc.x,base_sc.x),sfmul(sfmul(sc.y,base_sc.y),da.y));
    uint status=1u,xi=0u,eta=0u;
    if(!sfless(d,0x3d800000u)){
        status=0u;xi=sfdiv(sfmul(sc.y,da.x),d);
        eta=sfdiv(sfsub(sfmul(sc.x,base_sc.y),sfmul(sfmul(sc.y,base_sc.x),da.y)),d);
    }
    uint base=i*4u;result[base]=status;result[base+1u]=xi;result[base+2u]=eta;result[base+3u]=d;
'''}
