"""Independent original GPU stable bias/precession operation graph."""
HELPERS=r'''
const uint prec_coeff[24]=uint[24](
 0xb489c323u,0x3856a8c8u,0x3620772cu,0xb0d0255cu,0xad6dc961u,0x2a0debe3u,
 0x330dfd3eu,0x34060fa0u,0x34858cf5u,0xb1f4f567u,0x2b3996eeu,0x2a0cd469u,
 0xb4597746u,0x3cc81ba7u,0x36fd8493u,0xb076d528u,0xaf0d012cu,0xa9a19275u,
 0x3ed17496u,0xb96e19edu,0xb07401e7u,0x3226dd29u,0xac4481b1u,0xaa6ce64eu);
uint prec_angle(uint t,uint row){uint v=prec_coeff[row*6u+5u];for(int j=4;j>=0;j--)v=sfadd(prec_coeff[row*6u+uint(j)],sfmul(t,v));return v;}
const uint prec_sin[7]=uint[7](SIN_WORDS);
const uint prec_cos[8]=uint[8](COS_WORDS);
uvec2 prec_trig(uint a){
 uint z=sfmul(a,a),s=prec_sin[6],c=prec_cos[7];
 for(int j=5;j>=0;j--)s=sfadd(prec_sin[j],sfmul(z,s));
 for(int j=6;j>=0;j--)c=sfadd(prec_cos[j],sfmul(z,c));
 return uvec2(sfmul(a,s),c);
}
'''
# Frozen factorial coefficients; verified independently by CPU/float64 tests.
from .space_search_reference import SIN_COEFF,COS_COEFF
HELPERS=HELPERS.replace('SIN_WORDS',','.join(f'0x{v:08x}u' for v in SIN_COEFF)).replace('COS_WORDS',','.join(f'0x{v:08x}u' for v in COS_COEFF))

BODIES={74:r'''
    uint epoch=A(i*4u),base=i*16u,angles[4];
    for(uint a=0u;a<4u;a++){angles[a]=prec_angle(epoch,a);result[base+a]=angles[a];}
    uvec2 eps=prec_trig(angles[3]),psi=prec_trig(angles[2]),halfpsi=prec_trig(sfmul(angles[2],0x3f000000u));
    uint d=sfmul(0x40000000u,sfmul(halfpsi.x,halfpsi.x));
    uint a=sfmul(psi.x,eps.y),b=sfmul(psi.x,eps.x),c=sfneg(sfmul(sfmul(eps.y,eps.x),d));
    uint M[9],X[9],Z[9],U[9],R[9];
    M[0]=sfsub(0x3f800000u,d);M[1]=sfneg(a);M[2]=sfneg(b);M[3]=a;M[4]=sfsub(0x3f800000u,sfmul(sfmul(eps.y,eps.y),d));M[5]=c;M[6]=b;M[7]=c;M[8]=sfsub(0x3f800000u,sfmul(sfmul(eps.x,eps.x),d));
    uvec2 dp=prec_trig(angles[1]),ga=prec_trig(angles[0]);
    for(uint j=0u;j<9u;j++){X[j]=0u;Z[j]=0u;}
    X[0]=0x3f800000u;X[4]=dp.y;X[5]=dp.x;X[7]=sfneg(dp.x);X[8]=dp.y;
    Z[0]=ga.y;Z[1]=ga.x;Z[3]=sfneg(ga.x);Z[4]=ga.y;Z[8]=0x3f800000u;
    for(uint row=0u;row<3u;row++)for(uint col=0u;col<3u;col++){
        uint value=0u;for(uint j=0u;j<3u;j++)value=sfadd(value,sfmul(M[row*3u+j],X[j*3u+col]));U[row*3u+col]=value;
    }
    for(uint row=0u;row<3u;row++)for(uint col=0u;col<3u;col++){
        uint value=0u;for(uint j=0u;j<3u;j++)value=sfadd(value,sfmul(U[row*3u+j],Z[j*3u+col]));R[row*3u+col]=value;result[base+4u+row*3u+col]=value;
    }
    for(uint row=0u;row<3u;row++){
        uint value=0u;for(uint j=0u;j<3u;j++)value=sfadd(value,sfmul(R[row*3u+j],A(i*4u+1u+j)));result[base+13u+row]=value;
    }
'''}
