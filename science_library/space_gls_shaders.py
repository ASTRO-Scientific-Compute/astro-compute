"""Original fixed-size Cholesky and augmented-quadratic correlated fit."""
BODIES={67:r'''
    uint n=data[4],k=data[5],base=6u*i,inv[128],g[64],lower[64],bt[8],by[8],zt[8],zy[8];
    for(uint j=0u;j<6u;j++)result[base+j]=0u;
    for(uint j=0u;j<64u;j++)lower[j]=0u;
    for(uint j=0u;j<n;j++)inv[j]=sfdiv(0x3f800000u,C(i*n+j));
    for(uint a=0u;a<k;a++){
        for(uint b=0u;b<=a;b++){
            uint value=0u;
            for(uint j=0u;j<n;j++)value=sfadd(value,sfmul(sfmul(data[data[8]+(i*k+a)*n+j],inv[j]),data[data[8]+(i*k+b)*n+j]));
            value=sfadd(a==b?0x3f800000u:0u,value);g[a*8u+b]=value;g[b*8u+a]=value;
        }
        bt[a]=0u;by[a]=0u;
        for(uint j=0u;j<n;j++){
            uint ud=sfmul(data[data[8]+(i*k+a)*n+j],inv[j]);
            bt[a]=sfadd(bt[a],sfmul(ud,B(i*n+j)));by[a]=sfadd(by[a],sfmul(ud,A(i*n+j)));
        }
    }
    result[base]=2u;
    for(uint a=0u;a<k;a++)for(uint b=0u;b<=a;b++){
        uint value=g[a*8u+b];
        for(uint j=0u;j<b;j++)value=sfsub(value,sfmul(lower[a*8u+j],lower[b*8u+j]));
        if(a==b){
            if(!sfless(sfmul(g[a*8u+a],0x37800000u),value))return;
            lower[a*8u+a]=sfsqrt(value);
        }else lower[a*8u+b]=sfdiv(value,lower[b*8u+b]);
    }
    for(uint system_index=0u;system_index<2u;system_index++){
        uint v[8],z[8];
        for(uint a=0u;a<k;a++){
            uint value=system_index==0u?bt[a]:by[a];
            for(uint j=0u;j<a;j++)value=sfsub(value,sfmul(lower[a*8u+j],v[j]));
            v[a]=sfdiv(value,lower[a*8u+a]);
        }
        for(int a=int(k)-1;a>=0;a--){
            uint value=v[a];
            for(uint j=uint(a)+1u;j<k;j++)value=sfsub(value,sfmul(lower[j*8u+uint(a)],z[j]));
            z[a]=sfdiv(value,lower[uint(a)*8u+uint(a)]);
        }
        for(uint a=0u;a<k;a++){if(system_index==0u)zt[a]=z[a];else zy[a]=z[a];}
    }
    uint information=0u,numerator=0u;
    for(uint j=0u;j<n;j++){
        uint st=0u,sy=0u;
        for(uint a=0u;a<k;a++){
            uint u=data[data[8]+(i*k+a)*n+j];st=sfadd(st,sfmul(u,zt[a]));sy=sfadd(sy,sfmul(u,zy[a]));
        }
        uint qt=sfsub(B(i*n+j),st),qy=sfsub(A(i*n+j),sy),weighted=sfmul(qt,inv[j]);
        information=sfadd(information,sfmul(weighted,qt));numerator=sfadd(numerator,sfmul(weighted,qy));
    }
    for(uint a=0u;a<k;a++){
        information=sfadd(information,sfmul(zt[a],zt[a]));numerator=sfadd(numerator,sfmul(zt[a],zy[a]));
    }
    result[base]=1u;if(information==0u)return;
    uint amplitude=sfdiv(numerator,information),variance=sfdiv(0x3f800000u,information),zr[8],chi=0u;
    for(uint a=0u;a<k;a++)zr[a]=sfsub(zy[a],sfmul(amplitude,zt[a]));
    for(uint j=0u;j<n;j++){
        uint correction=0u;for(uint a=0u;a<k;a++)correction=sfadd(correction,sfmul(data[data[8]+(i*k+a)*n+j],zr[a]));
        uint residual=sfsub(A(i*n+j),sfmul(amplitude,B(i*n+j))),qr=sfsub(residual,correction);
        chi=sfadd(chi,sfmul(sfmul(qr,inv[j]),qr));
    }
    for(uint a=0u;a<k;a++)chi=sfadd(chi,sfmul(zr[a],zr[a]));
    result[base]=0u;result[base+1u]=amplitude;result[base+2u]=variance;result[base+3u]=chi;result[base+4u]=information;result[base+5u]=k;
'''}
