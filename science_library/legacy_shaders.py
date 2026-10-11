"""Exact historical operators; staged Welch/compaction keep all work on GPU."""
from .float_shaders import FFT
from .spectral_shader import HELPERS as SPECTRAL_HELPERS

BODIES={
30:r'''
    uvec2 z[256];legacy_transform(i,z);for(uint k=0u;k<256u;k++){result[i*512u+k*2u]=z[k].x;result[i*512u+k*2u+1u]=z[k].y;}
''',
31:r'''
    uint sum=0u;for(uint j=0u;j<9u;j++){uint idx=uint(clamp(int(i)+int(j)-4,0,int(data[4])-1));sum=sfadd(sum,sfmul(A(idx),B(j)));}result[i]=sum;
''',
32:r'''
    int lag=int(i)-64;uint sum=0u,begin=uint(max(0,-lag)),end=min(data[4],uint(int(data[4])-max(0,lag)));
    for(uint j=begin;j<end;j++)sum=sfadd(sum,sfmul(A(j),B(uint(int(j)+lag))));result[i]=sum;
''',
33:r'''
    int lag=int(i)-64;uint xy=0u,xx=0u,yy=0u,begin=uint(max(0,-lag)),end=min(data[4],uint(int(data[4])-max(0,lag)));
    for(uint j=begin;j<end;j++){uint x=A(j),y=B(uint(int(j)+lag));xy=sfadd(xy,sfmul(x,y));xx=sfadd(xx,sfmul(x,x));yy=sfadd(yy,sfmul(y,y));}
    uint den=sfsqrt(sfmul(xx,yy));result[i]=den==0u?0u:sfdiv(xy,den);
''',
34:r'''
    uint count=0u;
    if(i==0u){for(uint block=0u;block<data[5];block++)count+=seen[block];result[0]=count;return;}
    uint target=i-1u;
    for(uint block=0u;block<data[5];block++){
        uint next=count+seen[block];
        if(target<next){for(uint j=block*256u;j<min((block+1u)*256u,data[4]);j++){uint value=A(j),r=value&65535u;
            if(r>=1u&&r<=1800u){if(count==target){result[i]=value;return;}count++;}}}
        count=next;
    }
    result[i]=0u;
''',
35:r'''
    uint sum=0u;for(uint s=0u;s<data[5];s++)sum=sfadd(sum,seen[s*129u+i]);result[i]=sfdiv(sum,sfu(data[5]));
''',
36:r'''
    uvec2 z[256];legacy_transform(i,z);for(uint k=0u;k<129u;k++){
        uint q=(k==0u||k==128u)?0x3f800000u:0x40000000u;
        uint scale=sfsqrt(sfdiv(q,sfmul(0x48c00000u,C(512u+k))));
        result[i*258u+2u*k]=sfmul(z[k].x,scale);result[i*258u+2u*k+1u]=sfmul(z[k].y,scale);
    }
''',
}


def helpers(op):
    if op==34:
        return r'''
void run_prepass(uint block){uint count=0u;for(uint j=block*256u;j<min((block+1u)*256u,data[4]);j++){uint r=A(j)&65535u;count+=uint(r>=1u&&r<=1800u);}seen[block]=count;}
'''
    if op not in (30,35,36):return ''
    transform=FFT.replace('void transform(', 'void legacy_transform(')
    transform=transform.replace('A((record*n+reverse)*2u+1u)','0u')
    transform=transform.replace('A((record*n+reverse)*2u)', 'A(record*256u+reverse)' if op==30 else 'sfmul(A(record*128u+reverse),C(reverse))')
    if op in (35,36):transform=SPECTRAL_HELPERS
    if op==35:
        transform+=r'''
void run_prepass(uint segment){
    uvec2 z[256];legacy_transform(segment,z);
    for(uint k=0u;k<129u;k++){uint q=(k==0u||k==128u)?0x3f800000u:0x40000000u;
        uint p=sfdiv(sfmul(q,sfadd(sfmul(z[k].x,z[k].x),sfmul(z[k].y,z[k].y))),0x48c00000u);seen[segment*129u+k]=p;}
}
'''
    return transform
