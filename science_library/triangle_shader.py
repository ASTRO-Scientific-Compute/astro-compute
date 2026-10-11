"""Exact signed 256-bit determinants and correctly rounded rational distance."""
ARITHMETIC=r'''
struct Big {uint w[8]; bool neg;};
Big bz(){Big a;for(int k=0;k<8;k++)a.w[k]=0u;a.neg=false;return a;}
bool bzero(Big a){uint v=0u;for(int k=0;k<8;k++)v|=a.w[k];return v==0u;}
int bcmp(Big a,Big b){for(int k=7;k>=0;k--){if(a.w[k]<b.w[k])return -1;if(a.w[k]>b.w[k])return 1;}return 0;}
Big bshift(Big a,int n){Big r=bz();int words=n/32,bits=n%32;for(int k=7;k>=0;k--){int j=k-words;if(j>=0){r.w[k]=a.w[j]<<uint(bits);if(bits!=0&&j>0)r.w[k]|=a.w[j-1]>>uint(32-bits);}}r.neg=a.neg;return r;}
Big bmagadd(Big a,Big b){Big r=bz();uint carry=0u;for(int k=0;k<8;k++){uint s=a.w[k]+b.w[k],c=uint(s<a.w[k]);uint t=s+carry;c+=uint(t<s);r.w[k]=t;carry=c;}return r;}
Big bmagsub(Big a,Big b){Big r=bz();uint borrow=0u;for(int k=0;k<8;k++){uint s=a.w[k]-b.w[k],c=uint(a.w[k]<b.w[k]);uint t=s-borrow;c+=uint(s<borrow);r.w[k]=t;borrow=c;}return r;}
Big bneg(Big a){if(!bzero(a))a.neg=!a.neg;return a;}
Big badd(Big a,Big b){Big r;if(a.neg==b.neg){r=bmagadd(a,b);r.neg=a.neg;}else if(bcmp(a,b)>=0){r=bmagsub(a,b);r.neg=a.neg;}else{r=bmagsub(b,a);r.neg=b.neg;}if(bzero(r))r.neg=false;return r;}
Big bsub(Big a,Big b){return badd(a,bneg(b));}
Big bmul(Big a,Big b){Big r=bz();for(int i=0;i<8;i++){uint carry=0u;for(int j=0;j<8-i;j++){uint hi,lo;umulExtended(a.w[i],b.w[j],hi,lo);uint s=lo+r.w[i+j];hi+=uint(s<lo);uint t=s+carry;hi+=uint(t<s);r.w[i+j]=t;carry=hi;}}r.neg=(a.neg!=b.neg)&&!bzero(r);return r;}
Big bfloat(uint word){Big r=bz();if((word&0x7fffffffu)==0u)return r;uint mant;int exponent;unpack32(word,mant,exponent);int shift=exponent+33;r.w[0]=shift<0?mant>>uint(-shift):mant;if(shift>0)r=bshift(r,shift);r.neg=(word&0x80000000u)!=0u;return r;}
int btop(Big a){for(int k=7;k>=0;k--)if(a.w[k]!=0u)return 32*k+findMSB(a.w[k]);return -1;}
uint bratio(Big num,Big den){if(bzero(num))return 0u;int e=btop(num)-btop(den);if(e>=0)den=bshift(den,e);else num=bshift(num,-e);if(bcmp(num,den)<0){num=bshift(num,1);e--;}
 uint q=0u;for(int j=0;j<27;j++){q<<=1u;if(bcmp(num,den)>=0){num=bmagsub(num,den);q|=1u;}if(j<26)num=bshift(num,1);}if(!bzero(num))q|=1u;return round32(0u,e,q);}
struct BVec {Big x;Big y;Big z;};
BVec bv(uvec3 w){return BVec(bfloat(w.x),bfloat(w.y),bfloat(w.z));}
BVec vsub(BVec a,BVec b){return BVec(bsub(a.x,b.x),bsub(a.y,b.y),bsub(a.z,b.z));}
BVec vcross(BVec a,BVec b){return BVec(bsub(bmul(a.y,b.z),bmul(a.z,b.y)),bsub(bmul(a.z,b.x),bmul(a.x,b.z)),bsub(bmul(a.x,b.y),bmul(a.y,b.x)));}
Big vdot(BVec a,BVec b){return badd(badd(bmul(a.x,b.x),bmul(a.y,b.y)),bmul(a.z,b.z));}
uvec3 ray_direction(uint ray){uvec3 d=uvec3(A(ray*6u+3u),A(ray*6u+4u),A(ray*6u+5u));uint length=sfsqrt(sfadd(sfadd(sfmul(d.x,d.x),sfmul(d.y,d.y)),sfmul(d.z,d.z)));return uvec3(sfdiv(d.x,length),sfdiv(d.y,length),sfdiv(d.z,length));}
uint triangle_word(uint frame,uint index){
#ifdef DYNAMIC_TRIANGLES
 uint stride=((9u*data[5]+1u)&~1u)+6u*data[5];return seen[frame*stride+index];
#else
 return B(index);
#endif
}
uint triangle_hit(uint frame,uint triangle,BVec origin,BVec direction){
 uint j=triangle*9u;BVec a=bv(uvec3(triangle_word(frame,j),triangle_word(frame,j+1u),triangle_word(frame,j+2u)));
 BVec b=bv(uvec3(triangle_word(frame,j+3u),triangle_word(frame,j+4u),triangle_word(frame,j+5u)));
 BVec c=bv(uvec3(triangle_word(frame,j+6u),triangle_word(frame,j+7u),triangle_word(frame,j+8u)));
 BVec e1=vsub(b,a),e2=vsub(c,a),p=vcross(direction,e2);Big det=vdot(e1,p);
 Big eps=bshift(bfloat(0x322bcc77u),112);if(bcmp(det,eps)<0)return 0x7149f2cau;
 BVec s=vsub(origin,a);Big un=vdot(s,p);BVec q=vcross(s,e1);Big vn=vdot(direction,q),tn=vdot(e2,q);
 if(det.neg){un=bneg(un);vn=bneg(vn);tn=bneg(tn);}det.neg=false;
 if(un.neg||vn.neg||tn.neg||bcmp(un,det)>0||bcmp(badd(un,vn),det)>0)return 0x7149f2cau;
 uint distance=bratio(tn,det);return distance>0x38d1b717u&&distance<0x7149f2cau?distance:0x7149f2cau;
}
#ifdef DYNAMIC_TRIANGLES
void run_prepass(uint triangle){
 uint frame_index=pc.first&0x7fffffffu,frame=C(1024u+frame_index),offset=C((triangle*17u+frame*13u)&1023u);
 uint boxbase=(9u*data[5]+1u)&~1u,stride=boxbase+6u*data[5],base=frame_index*stride;
 vec3 lower=vec3(1e30),upper=vec3(-1e30);
 for(uint vertex=0u;vertex<3u;vertex++){uint j=triangle*9u+vertex*3u;uvec3 w=uvec3(B(j),B(j+1u),sfadd(B(j+2u),offset));
  seen[base+j]=w.x;seen[base+j+1u]=w.y;seen[base+j+2u]=w.z;vec3 p=uintBitsToFloat(w);lower=min(lower,p);upper=max(upper,p);}
 // Larger than coordinate rounding error; boxes decide candidates only.
 vec3 pad=max(vec3(0.000001),max(abs(lower),abs(upper))*0.000001);
 lower-=pad;upper+=pad;
 for(uint axis=0u;axis<3u;axis++){seen[base+boxbase+triangle*6u+axis]=floatBitsToUint(lower[axis]);seen[base+boxbase+triangle*6u+3u+axis]=floatBitsToUint(upper[axis]);}
}
#endif
'''


def body(rt):
    common='uint ray=i%data[4],frame=i/data[4];uvec3 ow=uvec3(A(ray*6u),A(ray*6u+1u),A(ray*6u+2u)),dw=ray_direction(ray);BVec origin=bv(ow),direction=bv(dw);uint best=0x7149f2cau;'
    if rt:
        common+='''rayQueryEXT query;rayQueryInitializeEXT(query,scene,0u,0xffu,uintBitsToFloat(ow),0.0,uintBitsToFloat(dw),1e30);
while(rayQueryProceedEXT(query)){if(rayQueryGetIntersectionTypeEXT(query,false)==gl_RayQueryCandidateIntersectionAABBEXT){uint j=rayQueryGetIntersectionPrimitiveIndexEXT(query,false);if(j<data[5])best=min(best,triangle_hit(frame,j,origin,direction));}}'''
    else:common+='for(uint j=0u;j<data[5];j++)best=min(best,triangle_hit(frame,j,origin,direction));'
    return common+'result[i]=best;'
