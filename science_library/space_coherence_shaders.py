"""Integer-only software binary32 complex cross-products on the GPU."""
BODIES={78:r'''
    uint sx=0u,sy=0u,sr=0u,si=0u,n=data[4];
    for(uint j=0u;j<n;j++){
        uint base=(i*n+j)*4u,xr=A(base),xi=A(base+1u),yr=A(base+2u),yi=A(base+3u);
        sx=sfadd(sx,sfadd(sfmul(xr,xr),sfmul(xi,xi)));
        sy=sfadd(sy,sfadd(sfmul(yr,yr),sfmul(yi,yi)));
        sr=sfadd(sr,sfadd(sfmul(xr,yr),sfmul(xi,yi)));
        si=sfadd(si,sfsub(sfmul(xr,yi),sfmul(xi,yr)));
    }
    uint count=sfu(n),px=sfdiv(sx,count),py=sfdiv(sy,count),re=sfdiv(sr,count),im=sfdiv(si,count);
    uint status=uint(px==0u)|(uint(py==0u)<<1u),coherence=0u;
    if(status==0u)coherence=sfdiv(sfadd(sfmul(re,re),sfmul(im,im)),sfmul(px,py));
    uint outbase=i*6u;result[outbase]=status;result[outbase+1u]=px;result[outbase+2u]=py;
    result[outbase+3u]=re;result[outbase+4u]=im;result[outbase+5u]=coherence;
'''}
