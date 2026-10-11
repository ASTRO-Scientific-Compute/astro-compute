"""Integer-only double-single arithmetic; independent from CPU residual method."""
HELPERS=r'''
uint product_error(uint a,uint b,uint hi){
    if((hi&0x7f800000u)==0u)return 0u;
    uint ma,mb,mh;int ea,eb,eh;unpack32(a,ma,ea);unpack32(b,mb,eb);unpack32(hi,mh,eh);
    uvec2 p=mul64(ma,mb);int delta=int(p.x-(mh<<uint(eh-ea-eb+23)));
    if(delta==0)return 0u;uint magnitude=uint(abs(delta));int top=findMSB(magnitude);
    uint sign=((a^b)&0x80000000u)^(delta<0?0x80000000u:0u);
    return round32(sign,ea+eb-46+top,magnitude<<uint(26-top));
}
uvec2 two_sum(uint a,uint b){uint s=sfadd(a,b),z=sfsub(s,a);return uvec2(s,sfadd(sfsub(a,sfsub(s,z)),sfsub(b,z)));}
uvec2 dsadd(uvec2 a,uvec2 b){uvec2 t=two_sum(a.x,b.x);return two_sum(t.x,sfadd(sfadd(t.y,a.y),b.y));}
uvec2 dsneg(uvec2 a){return uvec2(sfneg(a.x),sfneg(a.y));}
uvec2 dssub(uvec2 a,uvec2 b){return dsadd(a,dsneg(b));}
uvec2 dsmul(uvec2 a,uvec2 b){uint p=sfmul(a.x,b.x),e=product_error(a.x,b.x,p);uint cross=sfadd(sfmul(a.x,b.y),sfmul(a.y,b.x));return two_sum(p,sfadd(e,cross));}
void legacy_transform(uint record,out uvec2 output_z[256]){
    uvec2 re[256],im[256];
    for(uint j=0u;j<256u;j++){uint reverse=bitfieldReverse(j)>>24u;
        re[j]=dsmul(uvec2(A(record*128u+reverse),0u),uvec2(C(reverse),C(256u+reverse)));im[j]=uvec2(0u);}
    for(uint size=2u;size<=256u;size*=2u){
        for(uint base=0u;base<256u;base+=size)for(uint j=0u;j<size/2u;j++){
            uint t=j*256u/size;uvec2 wr=uvec2(B(t*4u),B(t*4u+1u)),wi=uvec2(B(t*4u+2u),B(t*4u+3u));
            uint left=base+j,right=base+j+size/2u;uvec2 ar=re[left],ai=im[left],br=re[right],bi=im[right];
            uvec2 tr=dssub(dsmul(wr,br),dsmul(wi,bi)),ti=dsadd(dsmul(wr,bi),dsmul(wi,br));
            re[left]=dsadd(ar,tr);im[left]=dsadd(ai,ti);re[right]=dssub(ar,tr);im[right]=dssub(ai,ti);
        }
    }
    for(uint k=0u;k<256u;k++)output_z[k]=uvec2(sfadd(re[k].x,re[k].y),sfadd(im[k].x,im[k].y));
}
'''
