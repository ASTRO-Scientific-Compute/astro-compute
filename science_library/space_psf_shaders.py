"""Original ordered spatial PSF scan and exhaustive bounded NNLS GPU code."""
BODIES = {
59: r'''
    uint width=data[4],height=data[5],pw=data[8],ph=data[9],rx=pw/2u,ry=ph/2u;
    uint cx=i%width,cy=i/width,base=6u*i;
    for(uint k=0u;k<6u;k++)result[base+k]=0u;result[base]=2u;
    if(cx<rx||cy<ry||cx+rx>=width||cy+ry>=height)return;
    uint numerator=0u,denominator=0u,count=0u;
    for(uint y=0u;y<ph;y++)for(uint x=0u;x<pw;x++){
        uint j=(cy+y-ry)*width+cx+x-rx,w=A(3u*j+2u),p=B(y*pw+x),d=sfsub(A(3u*j),A(3u*j+1u));
        uint wp=sfmul(w,p);numerator=sfadd(numerator,sfmul(wp,d));denominator=sfadd(denominator,sfmul(wp,p));
        if(sfless(0u,w))count++;
    }
    result[base]=1u;if(denominator==0u)return;
    uint amplitude=sfdiv(numerator,denominator),variance=sfdiv(0x3f800000u,denominator),snr=sfdiv(amplitude,sfsqrt(variance)),chi=0u;
    for(uint y=0u;y<ph;y++)for(uint x=0u;x<pw;x++){
        uint j=(cy+y-ry)*width+cx+x-rx,w=A(3u*j+2u),p=B(y*pw+x),d=sfsub(A(3u*j),A(3u*j+1u));
        uint residual=sfsub(d,sfmul(amplitude,p));chi=sfadd(chi,sfmul(w,sfmul(residual,residual)));
    }
    result[base]=0u;result[base+1u]=amplitude;result[base+2u]=variance;result[base+3u]=snr;result[base+4u]=chi;result[base+5u]=count;
''',
60: r'''
    uint n=data[4],m=data[5],base=i*(m+3u),gram[25],rhs[5],best[5],scale=0u;
    for(uint k=0u;k<m+3u;k++)result[base+k]=0u;result[base]=1u;
    for(uint a=0u;a<m;a++){
        rhs[a]=0u;best[a]=0u;
        for(uint j=0u;j<n;j++)rhs[a]=sfadd(rhs[a],sfmul(sfmul(A(2u*(i*n+j)+1u),B(a*n+j)),A(2u*(i*n+j))));
        for(uint b=0u;b<=a;b++){
            uint total=0u;
            for(uint j=0u;j<n;j++)total=sfadd(total,sfmul(sfmul(A(2u*(i*n+j)+1u),B(a*n+j)),B(b*n+j)));
            gram[5u*a+b]=total;gram[5u*b+a]=total;
        }
        if(sfless(scale,gram[5u*a+a]))scale=gram[5u*a+a];
    }
    if(scale==0u)return;
    result[base]=2u;uint threshold=sfmul(scale,0x36800000u),chi=0u;
    for(uint j=0u;j<n;j++){
        uint prediction=0u;for(uint k=0u;k<m;k++)prediction=sfadd(prediction,sfmul(best[k],B(k*n+j)));
        uint d=sfsub(A(2u*(i*n+j)),prediction);chi=sfadd(chi,sfmul(A(2u*(i*n+j)+1u),sfmul(d,d)));
    }
    for(uint mask=1u;mask<(1u<<m);mask++){
        uint indices[5],q=0u,lower[25],u[5],solution[5],candidate[5];
        for(uint k=0u;k<m;k++){candidate[k]=0u;if((mask&(1u<<k))!=0u){indices[q]=k;q++;}}
        for(uint a=0u;a<q;a++){u[a]=0u;solution[a]=0u;for(uint b=0u;b<q;b++)lower[5u*a+b]=0u;}
        for(uint a=0u;a<q;a++)for(uint b=0u;b<=a;b++){
            uint total=0u;for(uint k=0u;k<b;k++)total=sfadd(total,sfmul(lower[5u*a+k],lower[5u*b+k]));
            uint d=sfsub(gram[5u*indices[a]+indices[b]],total);
            if(a==b){if(!sfless(threshold,d))return;lower[5u*a+b]=sfsqrt(d);}
            else lower[5u*a+b]=sfdiv(d,lower[5u*b+b]);
        }
        for(uint a=0u;a<q;a++){
            uint total=0u;for(uint b=0u;b<a;b++)total=sfadd(total,sfmul(lower[5u*a+b],u[b]));
            u[a]=sfdiv(sfsub(rhs[indices[a]],total),lower[5u*a+a]);
        }
        for(int aa=int(q)-1;aa>=0;aa--){
            uint a=uint(aa),total=0u;for(uint b=a+1u;b<q;b++)total=sfadd(total,sfmul(lower[5u*b+a],solution[b]));
            solution[a]=sfdiv(sfsub(u[a],total),lower[5u*a+a]);
        }
        bool feasible=true;
        for(uint k=0u;k<q;k++){if(sfless(solution[k],0u))feasible=false;candidate[indices[k]]=solution[k];}
        if(!feasible)continue;
        uint score=0u;
        for(uint j=0u;j<n;j++){
            uint prediction=0u;for(uint k=0u;k<m;k++)prediction=sfadd(prediction,sfmul(candidate[k],B(k*n+j)));
            uint d=sfsub(A(2u*(i*n+j)),prediction);score=sfadd(score,sfmul(A(2u*(i*n+j)+1u),sfmul(d,d)));
        }
        if(sfless(score,chi)){chi=score;for(uint k=0u;k<m;k++)best[k]=candidate[k];}
    }
    uint positive=0u;for(uint k=0u;k<m;k++){result[base+3u+k]=best[k];if(sfless(0u,best[k]))positive|=1u<<k;}
    result[base]=0u;result[base+1u]=positive;result[base+2u]=chi;
''',
}
