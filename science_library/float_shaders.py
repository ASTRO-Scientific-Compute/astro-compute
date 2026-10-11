"""GPU scientific algorithms for the published canonical operation order."""
from .soft32_shader import SOFT32

FFT = r'''
void transform(uint record,out uvec2 z[256]){
    uint n=data[4];uint levels=uint(findMSB(n));
    for(uint j=0u;j<n;j++){uint reverse=bitfieldReverse(j)>>(32u-levels);z[j]=uvec2(A((record*n+reverse)*2u),A((record*n+reverse)*2u+1u));}
    for(uint size=2u;size<=n;size*=2u){
        for(uint base=0u;base<n;base+=size)for(uint j=0u;j<size/2u;j++){
            uint t=j*256u/size;uvec2 tw=uvec2(B(t*2u),B(t*2u+1u)),a=z[base+j],b=z[base+j+size/2u];
            uvec2 v=uvec2(sfsub(sfmul(tw.x,b.x),sfmul(tw.y,b.y)),sfadd(sfmul(tw.x,b.y),sfmul(tw.y,b.x)));
            z[base+j]=uvec2(sfadd(a.x,v.x),sfadd(a.y,v.y));z[base+j+size/2u]=uvec2(sfsub(a.x,v.x),sfsub(a.y,v.y));
        }
    }
}
'''
BODIES={
14:r'''
    uint total=0u;for(uint j=0u;j<data[4];j++){int k=int(i)-int(j);if(k>=0&&k<int(data[5]))total=sfadd(total,sfmul(A(j),B(uint(k))));}result[i]=total;
''',
15:r'''
    uint total=0u;int lag=int(i)-int(data[5])+1;for(uint j=0u;j<data[4];j++){int k=int(j)-lag;if(k>=0&&k<int(data[5]))total=sfadd(total,sfmul(A(j),B(uint(k))));}result[i]=total;
''',
16:r'''
    uint total=0u,xx=0u,yy=0u;int lag=int(i)-int(data[5])+1;
    for(uint j=0u;j<data[4];j++){int k=int(j)-lag;if(k>=0&&k<int(data[5])){uint x=A(j),y=B(uint(k));total=sfadd(total,sfmul(x,y));xx=sfadd(xx,sfmul(x,x));yy=sfadd(yy,sfmul(y,y));}}
    uint den=sfsqrt(sfmul(xx,yy));result[i*2u]=uint(den==0u);result[i*2u+1u]=den==0u?0u:sfdiv(total,den);
''',
17:r'''
    uvec2 z[256];transform(i,z);for(uint k=0u;k<data[4];k++){uint o=(i*data[4]+k)*2u;result[o]=z[k].x;result[o+1u]=z[k].y;}
''',
18:r'''
    uint s=0u,sx=0u,sy=0u,sxx=0u,sxy=0u;
    for(uint j=0u;j<data[4];j++){uint base=(i*data[4]+j)*3u,x=A(base),y=A(base+1u),w=A(base+2u),wx=sfmul(w,x);
        s=sfadd(s,w);sx=sfadd(sx,wx);sy=sfadd(sy,sfmul(w,y));sxx=sfadd(sxx,sfmul(wx,x));sxy=sfadd(sxy,sfmul(wx,y));}
    uint d=sfsub(sfmul(s,sxx),sfmul(sx,sx)),status=uint(s==0u||d==0u||(d&0x80000000u)!=0u),slope=0u,intercept=0u;
    if(status==0u){slope=sfdiv(sfsub(sfmul(s,sxy),sfmul(sx,sy)),d);intercept=sfdiv(sfsub(sy,sfmul(slope,sx)),s);}
    result[i*3u]=status;result[i*3u+1u]=intercept;result[i*3u+2u]=slope;
''',
19:r'''
    for(uint row=0u;row<3u;row++){uint total=0u;for(uint k=0u;k<3u;k++)total=sfadd(total,sfmul(B(row*3u+k),A(i*3u+k)));result[i*3u+row]=total;}
''',
20:r'''
    uint total=0u;for(uint j=0u;j+1u<data[4];j++){uint base=(i*data[4]+j)*2u;uint dx=sfsub(A(base+2u),A(base)),ys=sfadd(A(base+1u),A(base+3u));total=sfadd(total,sfmul(sfmul(dx,ys),0x3f000000u));}result[i]=total;
''',
21:r'''
    uint acc[3]=uint[3](0u,0u,0u);
    for(uint j=0u;j<data[4];j++)if(i!=j){uint d[3],s=0u;for(uint k=0u;k<3u;k++){d[k]=sfsub(A(j*4u+k),A(i*4u+k));s=sfadd(s,sfmul(d[k],d[k]));}
        s=sfadd(s,data[8]);uint factor=sfdiv(A(j*4u+3u),sfmul(s,sfsqrt(s)));for(uint k=0u;k<3u;k++)acc[k]=sfadd(acc[k],sfmul(factor,d[k]));}
    for(uint k=0u;k<3u;k++)result[i*3u+k]=acc[k];
''',
22:r'''
    for(uint k=0u;k<3u;k++){uint vel=sfadd(A(i*9u+3u+k),sfmul(data[8],A(i*9u+6u+k)));result[i*6u+k]=sfadd(A(i*9u+k),sfmul(data[8],vel));result[i*6u+3u+k]=vel;}
''',
23:r'''
    uint total=0u,mx=0u,my=0u;for(uint y=0u;y<data[7];y++)for(uint x=0u;x<data[6];x++){
        uint v=A((i*data[7]+y)*data[6]+x);total=sfadd(total,v);mx=sfadd(mx,sfmul(sfu(x),v));my=sfadd(my,sfmul(sfu(y),v));}
    result[i*3u]=uint(total==0u);result[i*3u+1u]=total==0u?0u:sfdiv(mx,total);result[i*3u+2u]=total==0u?0u:sfdiv(my,total);
''',
24:r'''
    uvec2 z[256];transform(i,z);uint den=sfmul(data[8],sfu(data[4]));for(uint k=0u;k<data[4];k++)result[i*data[4]+k]=sfdiv(sfadd(sfmul(z[k].x,z[k].x),sfmul(z[k].y,z[k].y)),den);
''',
}


def helpers(op):
    return SOFT32+(FFT if op in (17,24) else '')

BODIES.update({
25:r'''
    uint seq=i/data[5],query=i%data[5],base=seq*(data[4]+1u),length=A(base),k=data[8],code=0u,count=0u,mask=(1u<<(2u*k))-1u;
    for(uint j=0u;j<length;j++){code=((code<<2u)|A(base+1u+j))&mask;if(j+1u>=k&&code==B(query))count++;}result[i]=count;
''',
26:r'''
    uint d[3],s=0u;for(uint k=0u;k<3u;k++){d[k]=sfsub(A(i*6u+k),A(i*6u+k+3u));s=sfadd(s,sfmul(d[k],d[k]));}
    uint q=sfdiv(sfmul(data[8],data[8]),s),t=sfmul(sfmul(q,q),q),tt=sfmul(t,t);
    uint energy=sfmul(sfmul(0x40800000u,data[9]),sfsub(tt,t));
    uint factor=sfdiv(sfmul(sfmul(0x41c00000u,data[9]),sfsub(sfmul(0x40000000u,tt),t)),s);
    result[i*4u]=energy;for(uint k=0u;k<3u;k++)result[i*4u+1u+k]=sfmul(factor,d[k]);
''',
27:r'''
    uint w=data[6],h=data[7],x=i%w,y=i/w;
    uint neighbors=sfadd(A(y*w+(x+w-1u)%w),A(y*w+(x+1u)%w));neighbors=sfadd(neighbors,A(((y+h-1u)%h)*w+x));neighbors=sfadd(neighbors,A(((y+1u)%h)*w+x));
    uint lap=sfsub(neighbors,sfmul(0x40800000u,A(i)));result[i]=sfadd(A(i),sfmul(data[8],lap));
''',
28:r'''
    uint x=C(i),n=data[4],value=0u;
    if(!sfless(A(0u),x))value=B(0u);
    else if(!sfless(x,A(n-1u)))value=B(n-1u);
    else{uint lo=0u,hi=n-1u;while(hi-lo>1u){uint mid=(lo+hi)/2u;if(sfless(x,A(mid)))hi=mid;else lo=mid;}
        if(!sfless(A(lo),x))value=B(lo);
        else{uint t=sfdiv(sfsub(x,A(lo)),sfsub(A(lo+1u),A(lo)));value=sfadd(B(lo),sfmul(t,sfsub(B(lo+1u),B(lo))));}}
    result[i]=(value&0x7fffffffu)==0u?0u:value;
''',
29:r'''
    uint row=i/data[5],col=i%data[5],sum=0u;for(uint k=0u;k<data[4];k++)sum=sfadd(sum,sfmul(A(row*data[4]+k),B(k*data[5]+col)));result[i]=sum;
''',
})
