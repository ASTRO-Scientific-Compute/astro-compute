"""Integer-only RN32 bounded inverse tangent-plane direction reconstruction."""
from .space_search_shaders import TRIG as HELPERS
BODIES={80:r'''
    uvec2 a=sincos_turn(data[8]),d=sincos_turn(data[9]);
    uint center[3]=uint[3](sfmul(d.y,a.y),sfmul(d.y,a.x),d.x);
    uint east[3]=uint[3](sfneg(a.x),a.y,0u);
    uint north[3]=uint[3](sfneg(sfmul(d.x,a.y)),sfneg(sfmul(d.x,a.x)),d.y);
    uint xi=A(i*2u),eta=A(i*2u+1u),u[3],square=0u;
    for(uint k=0u;k<3u;k++){
        u[k]=sfadd(sfadd(center[k],sfmul(xi,east[k])),sfmul(eta,north[k]));
        square=sfadd(square,sfmul(u[k],u[k]));
    }
    uint r=sfsqrt(square),base=i*4u;
    for(uint k=0u;k<3u;k++)result[base+k]=sfdiv(u[k],r);
    result[base+3u]=r;
'''}
