"""Original per-record J2 gravity and adaptive trajectory GPU kernels."""
FORCE=r'''
bool dyn_force(uint x,uint y,uint z,out uint a[3]){
    uint mu=data[8],radius=data[9],j2=data[10];for(uint k=0u;k<3u;k++)a[k]=0u;
    if(mu==0u)return true;
    uint p[3]=uint[3](x,y,z),r2=0u;for(uint k=0u;k<3u;k++)r2=sfadd(r2,sfmul(p[k],p[k]));
    if(r2==0u)return false;
    uint r=sfsqrt(r2),base=sfneg(sfdiv(mu,sfmul(r2,r)));
    for(uint k=0u;k<3u;k++)a[k]=sfmul(base,p[k]);
    if(j2!=0u&&radius!=0u){
        uint q=sfdiv(sfmul(z,z),r2);
        uint scale=sfdiv(sfmul(sfmul(sfmul(0x3fc00000u,j2),mu),sfmul(radius,radius)),sfmul(sfmul(r2,r2),r));
        uint t=sfmul(0x40a00000u,q);
        for(uint k=0u;k<3u;k++)a[k]=sfadd(a[k],sfmul(sfmul(scale,p[k]),sfsub(t,k==2u?0x40400000u:0x3f800000u)));
    }
    return true;
}
'''
RK4=r'''
bool dyn_derivative(uint state[6],out uint d[6]){
    uint a[3];if(!dyn_force(state[0],state[1],state[2],a))return false;
    for(uint k=0u;k<3u;k++){d[k]=state[k+3u];d[k+3u]=a[k];}return true;
}
bool dyn_rk4(uint state[6],uint step,out uint updated[6]){
    uint tmp[6],k1[6],k2[6],k3[6],k4[6],half_step=sfmul(step,0x3f000000u),sixth=sfdiv(step,0x40c00000u);
    if(!dyn_derivative(state,k1))return false;
    for(uint k=0u;k<6u;k++)tmp[k]=sfadd(state[k],sfmul(half_step,k1[k]));
    if(!dyn_derivative(tmp,k2))return false;
    for(uint k=0u;k<6u;k++)tmp[k]=sfadd(state[k],sfmul(half_step,k2[k]));
    if(!dyn_derivative(tmp,k3))return false;
    for(uint k=0u;k<6u;k++)tmp[k]=sfadd(state[k],sfmul(step,k3[k]));
    if(!dyn_derivative(tmp,k4))return false;
    for(uint k=0u;k<6u;k++){
        uint total=sfadd(sfadd(sfadd(k1[k],sfmul(0x40000000u,k2[k])),sfmul(0x40000000u,k3[k])),k4[k]);
        updated[k]=sfadd(state[k],sfmul(sixth,total));
    }
    return true;
}
'''
BODIES={
54:r'''
    uint a[3];bool ok=dyn_force(A(i*3u),A(i*3u+1u),A(i*3u+2u),a);
    result[i*4u]=ok?0u:1u;for(uint k=0u;k<3u;k++)result[i*4u+1u+k]=a[k];
''',
55:r'''
    uint s[6],coarse[6],mid[6],fine[6];for(uint k=0u;k<6u;k++)s[k]=sfadd(A(i*6u+k),0u);
    uint duration=B(0u),h=B(1u),hmin=B(2u),hmax=B(3u),rtol=B(4u);
    uint elapsed=0u,error=0u,attempts=0u,accepted=0u,rejected=0u,status=1u;
    while(sfless(elapsed,duration)&&attempts<data[4]){
        uint remaining=sfsub(duration,elapsed),step=min(h,remaining);
        if(step==0u||!sfless(elapsed,sfadd(elapsed,step))){status=2u;break;}
        attempts++;uint half_step=sfmul(step,0x3f000000u);
        if(half_step==0u){status=2u;break;}
        if(!dyn_rk4(s,step,coarse)){status=3u;break;}
        if(!dyn_rk4(s,half_step,mid)){status=3u;break;}
        if(!dyn_rk4(mid,half_step,fine)){status=3u;break;}
        error=0u;
        for(uint k=0u;k<6u;k++){
            uint scale=sfadd(B(5u+k),sfmul(rtol,max(s[k]&0x7fffffffu,fine[k]&0x7fffffffu)));
            uint e=sfdiv(sfdiv(sfsub(fine[k],coarse[k])&0x7fffffffu,0x41700000u),scale);error=max(error,e);
        }
        if(error<=0x3f800000u){
            for(uint k=0u;k<6u;k++)s[k]=fine[k];accepted++;
            elapsed=step==remaining?duration:sfadd(elapsed,step);h=step;
            if(error<=0x3d000000u)h=step<=sfmul(hmax,0x3f000000u)?sfmul(step,0x40000000u):hmax;
            h=max(h,hmin);
        }else{
            rejected++;if(half_step<hmin){status=2u;break;}h=half_step;
        }
    }
    if(elapsed==duration)status=0u;
    uint base=i*13u;result[base]=status;result[base+1u]=attempts;result[base+2u]=accepted;result[base+3u]=rejected;
    result[base+4u]=elapsed;result[base+5u]=error;result[base+6u]=h;
    for(uint k=0u;k<6u;k++)result[base+7u+k]=s[k];
''',
56:r'''
    uint s[6];for(uint k=0u;k<6u;k++)s[k]=A(i*6u+k);
    uint r2=0u,v2=0u;for(uint k=0u;k<3u;k++){r2=sfadd(r2,sfmul(s[k],s[k]));v2=sfadd(v2,sfmul(s[k+3u],s[k+3u]));}
    uint base=i*7u;for(uint k=0u;k<7u;k++)result[base+k]=0u;
    uint mu=data[8],radius=data[9],j2=data[10];
    if(r2==0u&&mu!=0u){result[base]=1u;return;}
    uint r=sfsqrt(r2),potential=0u;
    if(mu!=0u){
        potential=sfneg(sfdiv(mu,r));
        if(j2!=0u&&radius!=0u){
            uint q=sfdiv(sfmul(s[2],s[2]),r2),shape=sfsub(sfmul(0x40400000u,q),0x3f800000u);
            uint correction=sfmul(sfmul(j2,sfdiv(sfmul(radius,radius),r2)),sfmul(0x3f000000u,shape));
            potential=sfmul(potential,sfsub(0x3f800000u,correction));
        }
    }
    result[base+1u]=r;result[base+2u]=v2;result[base+3u]=sfadd(sfmul(0x3f000000u,v2),potential);
    for(uint k=0u;k<3u;k++){uint a=(k+1u)%3u,b=(k+2u)%3u;result[base+4u+k]=sfsub(sfmul(s[a],s[b+3u]),sfmul(s[b],s[a+3u]));}
''',
}


def helpers(op):return FORCE+(RK4 if op==55 else '') if op in (54,55) else ''
