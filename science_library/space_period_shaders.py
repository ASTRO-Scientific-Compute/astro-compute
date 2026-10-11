"""Original ordered design-matrix/Cholesky and phase-bin GPU implementations."""
from .space_search_shaders import TRIG
HARMONIC=r'''
void period_basis(uint time,uint frequency,uint harmonics,out uint x[9]){
    x[0]=0x3f800000u;uint phase=sfmul(time,frequency);
    for(uint k=1u;k<=harmonics;k++){uvec2 sc=sincos_turn(sfmul(phase,sfu(k)));x[2u*k-1u]=sc.y;x[2u*k]=sc.x;}
}
'''
BODIES={
57:r'''
    uint n=data[4],harmonics=data[8],p=2u*harmonics+1u,base=i*(p+3u),frequency=B(i),weight=0u,wy=0u;
    for(uint k=0u;k<p+3u;k++)result[base+k]=0u;result[base]=1u;
    for(uint j=0u;j<n;j++){uint w=A(3u*j+2u);weight=sfadd(weight,w);wy=sfadd(wy,sfmul(w,A(3u*j+1u)));}
    if(weight==0u)return;
    uint mean=sfdiv(wy,weight),gram[81],lower[81],rhs[9],u[9],beta[9],x[9],chi0=0u;
    for(uint a=0u;a<p;a++){rhs[a]=0u;u[a]=0u;beta[a]=0u;for(uint b=0u;b<p;b++){gram[9u*a+b]=0u;lower[9u*a+b]=0u;}}
    for(uint j=0u;j<n;j++){
        uint y=A(3u*j+1u),w=A(3u*j+2u),d=sfsub(y,mean);period_basis(A(3u*j),frequency,harmonics,x);
        chi0=sfadd(chi0,sfmul(w,sfmul(d,d)));
        for(uint a=0u;a<p;a++){
            uint wx=sfmul(w,x[a]);rhs[a]=sfadd(rhs[a],sfmul(wx,d));
            for(uint b=0u;b<p;b++)gram[9u*a+b]=sfadd(gram[9u*a+b],sfmul(wx,x[b]));
        }
    }
    if(chi0==0u)return;
    result[base]=2u;uint threshold=sfmul(weight,0x37800000u);
    for(uint a=0u;a<p;a++)for(uint b=0u;b<=a;b++){
        uint total=0u;for(uint k=0u;k<b;k++)total=sfadd(total,sfmul(lower[9u*a+k],lower[9u*b+k]));
        uint d=sfsub(gram[9u*a+b],total);
        if(a==b){if(!sfless(threshold,d))return;lower[9u*a+b]=sfsqrt(d);}
        else lower[9u*a+b]=sfdiv(d,lower[9u*b+b]);
    }
    for(uint a=0u;a<p;a++){
        uint total=0u;for(uint b=0u;b<a;b++)total=sfadd(total,sfmul(lower[9u*a+b],u[b]));
        u[a]=sfdiv(sfsub(rhs[a],total),lower[9u*a+a]);
    }
    for(int aa=int(p)-1;aa>=0;aa--){
        uint a=uint(aa),total=0u;for(uint b=a+1u;b<p;b++)total=sfadd(total,sfmul(lower[9u*b+a],beta[b]));
        beta[a]=sfdiv(sfsub(u[a],total),lower[9u*a+a]);
    }
    beta[0]=sfadd(beta[0],mean);uint chi=0u;
    for(uint j=0u;j<n;j++){
        period_basis(A(3u*j),frequency,harmonics,x);uint predicted=beta[0];
        for(uint a=1u;a<p;a++)predicted=sfadd(predicted,sfmul(beta[a],x[a]));
        uint residual=sfsub(A(3u*j+1u),predicted);chi=sfadd(chi,sfmul(A(3u*j+2u),sfmul(residual,residual)));
    }
    result[base]=0u;result[base+1u]=sfdiv(sfsub(chi0,chi),chi0);result[base+2u]=chi;
    for(uint a=0u;a<p;a++)result[base+3u+a]=beta[a];
''',
58:r'''
    uint n=data[4],bins=data[8],period=C(i),counts[64],sums[64],means[64],total=0u;
    for(uint k=0u;k<bins;k++){counts[k]=0u;sums[k]=0u;means[k]=0u;}
    for(uint j=0u;j<n;j++){uint k=((A(j)%period)*bins)/period;counts[k]++;sums[k]=sfadd(sums[k],B(j));total=sfadd(total,B(j));}
    uint mean=sfdiv(total,sfu(n)),sse=0u;
    for(uint j=0u;j<n;j++){uint d=sfsub(B(j),mean);sse=sfadd(sse,sfmul(d,d));}
    uint variance=sfdiv(sse,sfu(n-1u)),base=6u*i;for(uint k=0u;k<6u;k++)result[base+k]=0u;result[base]=1u;
    if(variance==0u)return;
    uint occupied=0u;for(uint k=0u;k<bins;k++)if(counts[k]>0u)occupied++;
    result[base]=2u;if(occupied<2u||occupied==n)return;
    for(uint k=0u;k<bins;k++)if(counts[k]>0u)means[k]=sfdiv(sums[k],sfu(counts[k]));
    uint within=0u;
    for(uint j=0u;j<n;j++){uint k=((A(j)%period)*bins)/period,d=sfsub(B(j),means[k]);within=sfadd(within,sfmul(d,d));}
    within=sfdiv(within,sfu(n-occupied));result[base]=0u;result[base+1u]=sfdiv(within,variance);
    result[base+2u]=variance;result[base+3u]=within;result[base+4u]=occupied;result[base+5u]=n-occupied;
''',
}


def helpers(op):return TRIG+HARMONIC if op==57 else ''
