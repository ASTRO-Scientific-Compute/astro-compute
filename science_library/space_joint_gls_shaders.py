"""Original GPU joint fit, implemented independently with software binary32."""
BODIES={68:r'''
    uint n=data[4],k=data[5],m=data[6],width=2u+m+m*m,base=width*i;
    uint inv[64],g[25],lower[25],q[384],z[24],rhs[5],amps[5],invcols[25];
    for(uint j=0u;j<width;j++)result[base+j]=0u;
    for(uint j=0u;j<25u;j++)lower[j]=0u;
    for(uint j=0u;j<n;j++)inv[j]=sfdiv(0x3f800000u,C(i*n+j));
    for(uint a=0u;a<k;a++)for(uint b=0u;b<=a;b++){
        uint v=0u;
        for(uint j=0u;j<n;j++)v=sfadd(v,sfmul(sfmul(data[data[8]+(i*k+a)*n+j],inv[j]),data[data[8]+(i*k+b)*n+j]));
        v=sfadd(a==b?0x3f800000u:0u,v);g[a*5u+b]=v;g[b*5u+a]=v;
    }
    result[base]=2u;
    for(uint a=0u;a<k;a++)for(uint b=0u;b<=a;b++){
        uint v=g[a*5u+b];for(uint j=0u;j<b;j++)v=sfsub(v,sfmul(lower[a*5u+j],lower[b*5u+j]));
        if(a==b){if(!sfless(sfmul(g[a*5u+a],0x37800000u),v))return;lower[a*5u+a]=sfsqrt(v);}
        else lower[a*5u+b]=sfdiv(v,lower[b*5u+b]);
    }
    for(uint col=0u;col<=m;col++){
        uint v[4],solution[4];
        for(uint a=0u;a<k;a++){
            uint value=0u;
            for(uint j=0u;j<n;j++)value=sfadd(value,sfmul(sfmul(data[data[8]+(i*k+a)*n+j],inv[j]),col==m?A(i*n+j):B((i*m+col)*n+j)));
            for(uint j=0u;j<a;j++)value=sfsub(value,sfmul(lower[a*5u+j],v[j]));
            v[a]=sfdiv(value,lower[a*5u+a]);
        }
        for(int a=int(k)-1;a>=0;a--){
            uint value=v[a];for(uint j=uint(a)+1u;j<k;j++)value=sfsub(value,sfmul(lower[j*5u+uint(a)],solution[j]));
            solution[a]=sfdiv(value,lower[uint(a)*5u+uint(a)]);z[col*4u+uint(a)]=solution[a];
        }
        for(uint j=0u;j<n;j++){
            uint projection=0u;for(uint a=0u;a<k;a++)projection=sfadd(projection,sfmul(data[data[8]+(i*k+a)*n+j],solution[a]));
            q[col*64u+j]=sfsub(col==m?A(i*n+j):B((i*m+col)*n+j),projection);
        }
    }
    for(uint a=0u;a<m;a++){
        for(uint b=0u;b<=a;b++){
            uint value=0u;for(uint j=0u;j<n;j++)value=sfadd(value,sfmul(sfmul(q[a*64u+j],inv[j]),q[b*64u+j]));
            for(uint j=0u;j<k;j++)value=sfadd(value,sfmul(z[a*4u+j],z[b*4u+j]));
            g[a*5u+b]=value;g[b*5u+a]=value;
        }
        uint value=0u;for(uint j=0u;j<n;j++)value=sfadd(value,sfmul(sfmul(q[a*64u+j],inv[j]),q[m*64u+j]));
        for(uint j=0u;j<k;j++)value=sfadd(value,sfmul(z[a*4u+j],z[m*4u+j]));rhs[a]=value;
    }
    result[base]=1u;for(uint j=0u;j<25u;j++)lower[j]=0u;
    for(uint a=0u;a<m;a++)for(uint b=0u;b<=a;b++){
        uint value=g[a*5u+b];for(uint j=0u;j<b;j++)value=sfsub(value,sfmul(lower[a*5u+j],lower[b*5u+j]));
        if(a==b){if(!sfless(sfmul(g[a*5u+a],0x37800000u),value))return;lower[a*5u+a]=sfsqrt(value);}
        else lower[a*5u+b]=sfdiv(value,lower[b*5u+b]);
    }
    uint forward_values[5];
    for(uint a=0u;a<m;a++){
        uint value=rhs[a];for(uint j=0u;j<a;j++)value=sfsub(value,sfmul(lower[a*5u+j],forward_values[j]));
        forward_values[a]=sfdiv(value,lower[a*5u+a]);
    }
    for(int a=int(m)-1;a>=0;a--){
        uint value=forward_values[a];for(uint j=uint(a)+1u;j<m;j++)value=sfsub(value,sfmul(lower[j*5u+uint(a)],amps[j]));
        amps[a]=sfdiv(value,lower[uint(a)*5u+uint(a)]);
    }
    for(uint col=0u;col<m;col++)for(uint a=0u;a<m;a++){
        uint value=col==a?0x3f800000u:0u;
        for(uint j=0u;j<a;j++)value=sfsub(value,sfmul(lower[a*5u+j],invcols[col*5u+j]));
        invcols[col*5u+a]=sfdiv(value,lower[a*5u+a]);
    }
    for(uint a=0u;a<m;a++){
        result[base+1u+a]=amps[a];
        for(uint b=0u;b<=a;b++){
            uint value=0u;for(uint j=0u;j<m;j++)value=sfadd(value,sfmul(invcols[a*5u+j],invcols[b*5u+j]));
            result[base+1u+m+a*m+b]=value;result[base+1u+m+b*m+a]=value;
        }
    }
    uint zr[4],chi=0u;
    for(uint j=0u;j<k;j++){
        uint fit=0u;for(uint a=0u;a<m;a++)fit=sfadd(fit,sfmul(amps[a],z[a*4u+j]));zr[j]=sfsub(z[m*4u+j],fit);
    }
    for(uint j=0u;j<n;j++){
        uint fit=0u;for(uint a=0u;a<m;a++)fit=sfadd(fit,sfmul(amps[a],B((i*m+a)*n+j)));
        uint projection=0u;for(uint a=0u;a<k;a++)projection=sfadd(projection,sfmul(data[data[8]+(i*k+a)*n+j],zr[a]));
        uint qr=sfsub(sfsub(A(i*n+j),fit),projection);chi=sfadd(chi,sfmul(sfmul(qr,inv[j]),qr));
    }
    for(uint a=0u;a<k;a++)chi=sfadd(chi,sfmul(zr[a],zr[a]));
    result[base]=0u;result[base+width-1u]=chi;
'''}
