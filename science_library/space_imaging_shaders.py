"""Original GPU implementations, following the independently tested CPU oracle."""
HELPER=r'''
uint image_lerp(uint a,uint b,uint t){
    if(t==0u)return sfadd(a,0u);
    return sfadd(sfmul(sfsub(0x3f800000u,t),a),sfmul(t,b));
}
uint image_floor(uint x){
    if(x==0u)return 0u;
    uint mant;int exponent;unpack32(x,mant,exponent);
    return exponent<0?0u:mant>>uint(23-exponent);
}
'''
BODIES={
51:r'''
    uint w=data[6],h=data[7],x=B(i*2u),y=B(i*2u+1u);
    if(sfless(x,0u))x=0u;if(sfless(sfu(w-1u),x))x=sfu(w-1u);
    if(sfless(y,0u))y=0u;if(sfless(sfu(h-1u),y))y=sfu(h-1u);
    uint j=image_floor(x),k=image_floor(y),tx=sfsub(x,sfu(j)),ty=sfsub(y,sfu(k));
    uint j1=min(j+1u,w-1u),k1=min(k+1u,h-1u);
    result[i]=image_lerp(image_lerp(A(k*w+j),A(k*w+j1),tx),image_lerp(A(k1*w+j),A(k1*w+j1),tx),ty);
''',
52:r'''
    uint n=data[4],parent[512];
    for(uint j=0u;j<n;j++)parent[j]=j;
    for(uint e=0u;e<data[5];e++){
        uint a=B(e*2u),b=B(e*2u+1u);
        while(parent[a]!=a){parent[a]=parent[parent[a]];a=parent[a];}
        while(parent[b]!=b){parent[b]=parent[parent[b]];b=parent[b];}
        if(a!=b)parent[max(a,b)]=min(a,b);
    }
    uint root=i;while(parent[root]!=root)root=parent[root];
    uint canonical=0xffffffffu,total=0u;
    for(uint j=0u;j<n;j++){
        uint q=j;while(parent[q]!=q)q=parent[q];
        if(q==root){canonical=min(canonical,A(2u*j));total+=A(2u*j+1u);}
    }
    result[3u*i]=canonical;result[3u*i+1u]=total;result[3u*i+2u]=total>=data[8]?canonical:0u;
''',
53:r'''
    uint label=C(i),n=data[4],w=data[6],count=0u,flux=0u,var=0u,weight=0u,sx=0u,sy=0u;
    for(uint j=0u;j<n;j++){
        if(B(2u*j)!=label||B(2u*j+1u)==0u)continue;
        uint d=sfsub(A(3u*j),A(3u*j+1u));count++;
        flux=sfadd(flux,d);var=sfadd(var,A(3u*j+2u));
        if(!sfless(0u,d))continue;
        weight=sfadd(weight,d);sx=sfadd(sx,sfmul(d,sfu(j%w)));sy=sfadd(sy,sfmul(d,sfu(j/w)));
    }
    uint base=10u*i;for(uint k=0u;k<10u;k++)result[base+k]=0u;
    result[base]=count==0u?1u:2u;result[base+1u]=count;result[base+2u]=flux;result[base+3u]=var;
    if(weight==0u)return;
    uint cx=sfdiv(sx,weight),cy=sfdiv(sy,weight),xx=0u,xy=0u,yy=0u;
    for(uint j=0u;j<n;j++){
        if(B(2u*j)!=label||B(2u*j+1u)==0u)continue;
        uint d=sfsub(A(3u*j),A(3u*j+1u));if(!sfless(0u,d))continue;
        uint dx=sfsub(sfu(j%w),cx),dy=sfsub(sfu(j/w),cy);
        xx=sfadd(xx,sfmul(d,sfmul(dx,dx)));xy=sfadd(xy,sfmul(d,sfmul(dx,dy)));yy=sfadd(yy,sfmul(d,sfmul(dy,dy)));
    }
    result[base]=0u;result[base+4u]=weight;result[base+5u]=cx;result[base+6u]=cy;
    result[base+7u]=sfdiv(xx,weight);result[base+8u]=sfdiv(xy,weight);result[base+9u]=sfdiv(yy,weight);
''',
}


def helpers(op):return HELPER if op==51 else ''
