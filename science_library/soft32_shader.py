"""Original finite RN32 arithmetic using portable uint32 significands.

Three guard/round/sticky bits retain rounding information. Multiplication uses
umulExtended; division is restoring long division; square root is restoring
base-4 digit extraction. No native float instructions or shaderInt64 required.
"""
SOFT32 = r'''
uint sjam(uint v,int s){if(s<=0)return v;if(s>=32)return uint(v!=0u);return (v>>s)|uint((v<<(32-s))!=0u);}
uint sjam64(uvec2 v,int s){ // callers use20 or21
    return (v.x>>s)|(v.y<<(32-s))|uint((v.x<<(32-s))!=0u);
}
void unpack32(uint bits,out uint m,out int e){
    uint field=(bits>>23)&255u;m=bits&0x7fffffu;e=int(field)-127;
    if(field!=0u)m|=0x800000u;
    else{e=-126;while(m!=0u&&m<0x800000u){m<<=1;e--;}}
}
uint round32(uint sign,int e,uint z){
    if(z==0u)return 0u;
    if(e < -126){z=sjam(z,-126-e);e=-126;}
    uint tail=z&7u,m=z>>3;
    if(tail>4u||(tail==4u&&(m&1u)!=0u))m++;
    if(m==0u)return 0u;
    if(m>=0x1000000u){m>>=1;e++;}
    if(e>127)return sign|0x7f800000u;
    uint field=m>=0x800000u?uint(e+127):0u;
    return sign|(field<<23)|(m&0x7fffffu);
}
uint sfneg(uint a){return (a&0x7fffffffu)==0u?0u:a^0x80000000u;}
uint sfadd(uint a,uint b){
    if((a&0x7fffffffu)<(b&0x7fffffffu)){uint t=a;a=b;b=t;}
    if((b&0x7fffffffu)==0u)return (a&0x7fffffffu)==0u?0u:a;
    uint x,y;int ex,ey;unpack32(a,x,ex);unpack32(b,y,ey);
    uint z=x<<3,t=sjam(y<<3,ex-ey),sign=a&0x80000000u;
    if(((a^b)&0x80000000u)==0u){z+=t;if(z>=0x8000000u){z=sjam(z,1);ex++;}}
    else{z-=t;if(z==0u)return 0u;while(z<0x4000000u){z<<=1;ex--;}}
    return round32(sign,ex,z);
}
uint sfsub(uint a,uint b){return sfadd(a,sfneg(b));}
uint sfmul(uint a,uint b){
    if((a&0x7fffffffu)==0u||(b&0x7fffffffu)==0u)return 0u;
    uint x,y;int ex,ey;unpack32(a,x,ex);unpack32(b,y,ey);
    uvec2 product=mul64(x,y);bool high=(product.y&0x8000u)!=0u;
    return round32((a^b)&0x80000000u,ex+ey+int(high),sjam64(product,high?21:20));
}
uint sfdiv(uint a,uint b){
    if((b&0x7fffffffu)==0u)return 0x7fc00000u;
    if((a&0x7fffffffu)==0u)return 0u;
    uint x,y;int ex,ey;unpack32(a,x,ex);unpack32(b,y,ey);
    int e=ex-ey;if(x<y){x<<=1;e--;}
    uint q=0u;
    for(int bit=26;bit>=0;bit--){if(x>=y){x-=y;q|=1u<<bit;}if(bit!=0)x<<=1;}
    if(x!=0u)q|=1u;
    return round32((a^b)&0x80000000u,e,q);
}
uint sfsqrt(uint a){
    if((a&0x7fffffffu)==0u)return 0u;
    if((a&0x80000000u)!=0u)return 0x7fc00000u;
    uint m;int e;unpack32(a,m,e);if((e&1)!=0){m<<=1;e--;}
    uvec2 rad=uvec2(m<<29,m>>3);uint root=0u,rem=0u;
    for(int digit=26;digit>=0;digit--){int bit=2*digit;uint pair=bit>=32?(rad.y>>(bit-32))&3u:(rad.x>>bit)&3u;
        rem=(rem<<2)|pair;uint trial=(root<<2)|1u;root<<=1;
        if(rem>=trial){rem-=trial;root|=1u;}
    }
    if(rem!=0u)root|=1u;
    return round32(0u,e/2,root);
}
uint sfu(uint n){if(n==0u)return 0u;int e=findMSB(n);return round32(0u,e,n<<uint(26-e));} // n<=4096
'''
SOFT32 += r'''
bool sfless(uint a,uint b){
    if((a&0x7fffffffu)==0u)a=0u;if((b&0x7fffffffu)==0u)b=0u;
    if(((a^b)&0x80000000u)!=0u)return (a&0x80000000u)!=0u;
    return (a&0x80000000u)!=0u?a>b:a<b;
}
'''
