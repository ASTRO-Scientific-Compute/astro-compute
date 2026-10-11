"""Original stabilized RTS GPU graph using integer software binary32."""
BODIES={73:r'''
    uint n=data[4],width=1u+2u*n+3u*n*n,base=i*width,rec=data[11]+i*(3u*n+2u*n*n);
    uint F[36],Q[36],p[36],np[36],x[6],u[6],nx[6],xp[6],temp[36],pp[36],l[36],g[36],xs[6];
    uint aa[36],bb[36],uu[36],vv[36],ps[36];
    for(uint t=0u;t<width;t++)result[base+t]=0u;
    for(uint a=0u;a<n;a++){
        x[a]=data[rec+a];u[a]=data[rec+n+n*n+a];nx[a]=data[rec+2u*n+n*n+a];
        for(uint b=0u;b<n;b++){
            F[a*6u+b]=data[16u+a*n+b];Q[a*6u+b]=data[16u+n*n+a*n+b];p[a*6u+b]=data[rec+n+a*n+b];np[a*6u+b]=data[rec+3u*n+n*n+a*n+b];
        }
    }
    for(uint a=0u;a<n;a++){
        uint v=0u;for(uint j=0u;j<n;j++)v=sfadd(v,sfmul(F[a*6u+j],x[j]));xp[a]=sfadd(v,u[a]);
        for(uint b=0u;b<n;b++){
            v=0u;for(uint j=0u;j<n;j++)v=sfadd(v,sfmul(F[a*6u+j],p[j*6u+b]));temp[a*6u+b]=v;
        }
    }
    uint largest=0u;
    for(uint a=0u;a<n;a++){
        for(uint b=0u;b<=a;b++){
            uint v=0u;for(uint j=0u;j<n;j++)v=sfadd(v,sfmul(temp[a*6u+j],F[b*6u+j]));v=sfadd(v,Q[a*6u+b]);pp[a*6u+b]=v;pp[b*6u+a]=v;
        }
        if(sfless(largest,pp[a*6u+a]))largest=pp[a*6u+a];
    }
    uint threshold=sfmul(largest,0x37800000u);result[base]=1u;
    for(uint a=0u;a<n;a++)for(uint b=0u;b<=a;b++){
        uint v=pp[a*6u+b];for(uint j=0u;j<b;j++)v=sfsub(v,sfmul(l[a*6u+j],l[b*6u+j]));
        if(a==b){if(!sfless(threshold,v))return;l[a*6u+b]=sfsqrt(v);}else l[a*6u+b]=sfdiv(v,l[b*6u+b]);
    }
    for(uint row=0u;row<n;row++){
        uint z[6];
        for(uint a=0u;a<n;a++){
            uint v=0u;for(uint j=0u;j<n;j++)v=sfadd(v,sfmul(p[row*6u+j],F[a*6u+j]));
            for(uint j=0u;j<a;j++)v=sfsub(v,sfmul(l[a*6u+j],z[j]));z[a]=sfdiv(v,l[a*6u+a]);
        }
        for(int a=int(n)-1;a>=0;a--){
            uint v=z[a];for(uint j=uint(a)+1u;j<n;j++)v=sfsub(v,sfmul(l[j*6u+uint(a)],g[row*6u+j]));g[row*6u+uint(a)]=sfdiv(v,l[uint(a)*6u+uint(a)]);
        }
    }
    for(uint a=0u;a<n;a++){
        uint v=0u;for(uint j=0u;j<n;j++)v=sfadd(v,sfmul(g[a*6u+j],sfsub(nx[j],xp[j])));xs[a]=sfadd(x[a],v);
        for(uint b=0u;b<n;b++){
            v=0u;for(uint j=0u;j<n;j++)v=sfadd(v,sfmul(g[a*6u+j],F[j*6u+b]));aa[a*6u+b]=sfsub(a==b?0x3f800000u:0u,v);bb[a*6u+b]=sfadd(np[a*6u+b],Q[a*6u+b]);
        }
    }
    for(uint a=0u;a<n;a++)for(uint b=0u;b<n;b++){
        uint uval=0u,vval=0u;
        for(uint j=0u;j<n;j++){uval=sfadd(uval,sfmul(g[a*6u+j],bb[j*6u+b]));vval=sfadd(vval,sfmul(aa[a*6u+j],p[j*6u+b]));}
        uu[a*6u+b]=uval;vv[a*6u+b]=vval;
    }
    for(uint a=0u;a<n;a++)for(uint b=0u;b<=a;b++){
        uint uval=0u,vval=0u;
        for(uint j=0u;j<n;j++){uval=sfadd(uval,sfmul(uu[a*6u+j],g[b*6u+j]));vval=sfadd(vval,sfmul(vv[a*6u+j],aa[b*6u+j]));}
        uint v=sfadd(uval,vval);ps[a*6u+b]=v;ps[b*6u+a]=v;
    }
    result[base]=0u;
    for(uint a=0u;a<n;a++){
        result[base+1u+a]=xp[a];result[base+1u+n+n*n+a]=xs[a];
        for(uint b=0u;b<n;b++){
            result[base+1u+n+a*n+b]=pp[a*6u+b];result[base+1u+2u*n+n*n+a*n+b]=ps[a*6u+b];result[base+1u+2u*n+2u*n*n+a*n+b]=g[a*6u+b];
        }
    }
'''}
