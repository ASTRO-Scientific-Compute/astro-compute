"""Original GPU implementation using bounded integer-significand RN32 routines."""
BODIES={72:r'''
    uint n=data[4],m=data[5],width=2u+2u*n+2u*n*n+m,base=i*width;
    uint stride=2u*n+n*n+m,rec=data[11]+i*stride;
    uint F[36],Q[36],H[18],R[3],x[6],p[36],u[6],y[3];
    uint xp[6],temp[36],pp[36],c[18],s[9],e[3],l[9],k[18];
    uint post[6],aMat[36],pc[36];
    for(uint t=0u;t<width;t++)result[base+t]=0u;
    for(uint a=0u;a<n;a++){
        x[a]=data[rec+a];u[a]=data[rec+n+n*n+a];
        for(uint b=0u;b<n;b++){
            F[a*6u+b]=data[16u+a*n+b];Q[a*6u+b]=data[16u+n*n+a*n+b];p[a*6u+b]=data[rec+n+a*n+b];
        }
    }
    for(uint a=0u;a<m;a++){
        R[a]=data[16u+2u*n*n+m*n+a];y[a]=data[rec+2u*n+n*n+a];
        for(uint b=0u;b<n;b++)H[a*6u+b]=data[16u+2u*n*n+a*n+b];
    }
    for(uint a=0u;a<n;a++){
        uint v=0u;for(uint j=0u;j<n;j++)v=sfadd(v,sfmul(F[a*6u+j],x[j]));xp[a]=sfadd(v,u[a]);
        for(uint b=0u;b<n;b++){
            v=0u;for(uint j=0u;j<n;j++)v=sfadd(v,sfmul(F[a*6u+j],p[j*6u+b]));temp[a*6u+b]=v;
        }
    }
    for(uint a=0u;a<n;a++)for(uint b=0u;b<=a;b++){
        uint v=0u;for(uint j=0u;j<n;j++)v=sfadd(v,sfmul(temp[a*6u+j],F[b*6u+j]));
        v=sfadd(v,Q[a*6u+b]);pp[a*6u+b]=v;pp[b*6u+a]=v;
    }
    for(uint a=0u;a<n;a++)for(uint b=0u;b<m;b++){
        uint v=0u;for(uint j=0u;j<n;j++)v=sfadd(v,sfmul(pp[a*6u+j],H[b*6u+j]));c[a*3u+b]=v;
    }
    uint largest=0u;
    for(uint a=0u;a<m;a++){
        uint v=0u;for(uint j=0u;j<n;j++)v=sfadd(v,sfmul(H[a*6u+j],xp[j]));e[a]=sfsub(y[a],v);
        for(uint b=0u;b<=a;b++){
            v=0u;for(uint j=0u;j<n;j++)v=sfadd(v,sfmul(H[a*6u+j],c[j*3u+b]));
            v=sfadd(v,a==b?R[a]:0u);s[a*3u+b]=v;s[b*3u+a]=v;
        }
        if(sfless(largest,s[a*3u+a]))largest=s[a*3u+a];
    }
    uint threshold=sfmul(largest,0x37800000u);
    result[base]=1u;
    for(uint a=0u;a<m;a++)for(uint b=0u;b<=a;b++){
        uint v=s[a*3u+b];for(uint j=0u;j<b;j++)v=sfsub(v,sfmul(l[a*3u+j],l[b*3u+j]));
        if(a==b){if(!sfless(threshold,v))return;l[a*3u+b]=sfsqrt(v);}
        else l[a*3u+b]=sfdiv(v,l[b*3u+b]);
    }
    for(uint row=0u;row<n;row++){
        uint z[3];
        for(uint a=0u;a<m;a++){
            uint v=c[row*3u+a];for(uint j=0u;j<a;j++)v=sfsub(v,sfmul(l[a*3u+j],z[j]));z[a]=sfdiv(v,l[a*3u+a]);
        }
        for(int a=int(m)-1;a>=0;a--){
            uint v=z[a];for(uint j=uint(a)+1u;j<m;j++)v=sfsub(v,sfmul(l[j*3u+uint(a)],k[row*3u+j]));
            k[row*3u+uint(a)]=sfdiv(v,l[uint(a)*3u+uint(a)]);
        }
    }
    for(uint a=0u;a<n;a++){
        uint v=0u;for(uint j=0u;j<m;j++)v=sfadd(v,sfmul(k[a*3u+j],e[j]));post[a]=sfadd(xp[a],v);
        for(uint b=0u;b<n;b++){
            v=0u;for(uint j=0u;j<m;j++)v=sfadd(v,sfmul(k[a*3u+j],H[j*6u+b]));aMat[a*6u+b]=sfsub(a==b?0x3f800000u:0u,v);
        }
    }
    for(uint a=0u;a<n;a++)for(uint b=0u;b<n;b++){
        uint v=0u;for(uint j=0u;j<n;j++)v=sfadd(v,sfmul(aMat[a*6u+j],pp[j*6u+b]));temp[a*6u+b]=v;
    }
    for(uint a=0u;a<n;a++)for(uint b=0u;b<=a;b++){
        uint v=0u;for(uint j=0u;j<n;j++)v=sfadd(v,sfmul(temp[a*6u+j],aMat[b*6u+j]));
        uint noise=0u;for(uint j=0u;j<m;j++)noise=sfadd(noise,sfmul(sfmul(k[a*3u+j],R[j]),k[b*3u+j]));
        v=sfadd(v,noise);pc[a*6u+b]=v;pc[b*6u+a]=v;
    }
    uint z[3],chi=0u;
    for(uint a=0u;a<m;a++){
        uint v=e[a];for(uint j=0u;j<a;j++)v=sfsub(v,sfmul(l[a*3u+j],z[j]));z[a]=sfdiv(v,l[a*3u+a]);chi=sfadd(chi,sfmul(z[a],z[a]));
    }
    result[base]=0u;
    for(uint a=0u;a<n;a++){
        result[base+1u+a]=xp[a];result[base+1u+n+n*n+a]=post[a];
        for(uint b=0u;b<n;b++){
            result[base+1u+n+a*n+b]=pp[a*6u+b];result[base+1u+2u*n+n*n+a*n+b]=pc[a*6u+b];
        }
    }
    for(uint a=0u;a<m;a++)result[base+1u+2u*n+2u*n*n+a]=e[a];result[base+width-1u]=chi;
'''}
