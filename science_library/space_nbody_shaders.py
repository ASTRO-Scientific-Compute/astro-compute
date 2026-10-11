"""Original coupled-array RK4 GPU implementation with software binary32."""
INTEGRATOR=r'''
bool nb_derivative(uint state[48],uint mass[8],out uint derivative[48]){
    uint n=data[4];for(uint a=0u;a<48u;a++)derivative[a]=0u;
    for(uint p=0u;p<n;p++){
        uint acceleration[3]=uint[3](0u,0u,0u);
        if(data[8]!=0u)for(uint q=0u;q<n;q++){
            if(p==q)continue;uint gm=sfmul(data[8],mass[q]);if(gm==0u)continue;
            uint delta[3],distance=0u;
            for(uint a=0u;a<3u;a++){delta[a]=sfsub(state[q*6u+a],state[p*6u+a]);distance=sfadd(distance,sfmul(delta[a],delta[a]));}
            distance=sfadd(distance,data[9]);if(distance==0u)return false;
            uint scale=sfdiv(gm,sfmul(distance,sfsqrt(distance)));
            for(uint a=0u;a<3u;a++)acceleration[a]=sfadd(acceleration[a],sfmul(scale,delta[a]));
        }
        for(uint a=0u;a<3u;a++){derivative[p*6u+a]=state[p*6u+3u+a];derivative[p*6u+3u+a]=acceleration[a];}
    }
    return true;
}
bool nb_rk4(uint state[48],uint step,uint mass[8],out uint updated[48]){
    uint tmp[48],k1[48],k2[48],k3[48],k4[48],count=data[4]*6u;
    uint half_step=sfmul(step,0x3f000000u),sixth=sfdiv(step,0x40c00000u);
    for(uint a=0u;a<48u;a++){tmp[a]=0u;updated[a]=0u;}
    if(!nb_derivative(state,mass,k1))return false;
    for(uint a=0u;a<count;a++)tmp[a]=sfadd(state[a],sfmul(half_step,k1[a]));
    if(!nb_derivative(tmp,mass,k2))return false;
    for(uint a=0u;a<count;a++)tmp[a]=sfadd(state[a],sfmul(half_step,k2[a]));
    if(!nb_derivative(tmp,mass,k3))return false;
    for(uint a=0u;a<count;a++)tmp[a]=sfadd(state[a],sfmul(step,k3[a]));
    if(!nb_derivative(tmp,mass,k4))return false;
    for(uint a=0u;a<count;a++){
        uint value=sfadd(sfadd(sfadd(k1[a],sfmul(0x40000000u,k2[a])),sfmul(0x40000000u,k3[a])),k4[a]);
        updated[a]=sfadd(state[a],sfmul(sixth,value));
    }
    return true;
}
'''
BODIES={
69:r'''
    uint n=data[4],count=n*6u,width=7u+count,base=width*i,state[48],mass[8],coarse[48],mid[48],fine[48];
    for(uint a=0u;a<48u;a++)state[a]=0u;for(uint a=0u;a<count;a++)state[a]=sfadd(A(i*count+a),0u);
    for(uint a=0u;a<8u;a++)mass[a]=0u;for(uint a=0u;a<n;a++)mass[a]=B(i*n+a);
    uint duration=C(0u),h=C(1u),hmin=C(2u),hmax=C(3u),rtol=C(4u);
    uint elapsed=0u,error=0u,attempts=0u,accepted=0u,rejected=0u,status=1u;
    while(sfless(elapsed,duration)&&attempts<data[5]){
        uint remaining=sfsub(duration,elapsed),step=min(h,remaining);
        if(step==0u||!sfless(elapsed,sfadd(elapsed,step))){status=2u;break;}
        attempts++;uint half_step=sfmul(step,0x3f000000u);if(half_step==0u){status=2u;break;}
        if(!nb_rk4(state,step,mass,coarse)){status=3u;break;}
        if(!nb_rk4(state,half_step,mass,mid)){status=3u;break;}
        if(!nb_rk4(mid,half_step,mass,fine)){status=3u;break;}
        error=0u;
        for(uint a=0u;a<count;a++){
            uint scale=sfadd(C(5u+a%6u),sfmul(rtol,max(state[a]&0x7fffffffu,fine[a]&0x7fffffffu)));
            uint value=sfdiv(sfdiv(sfsub(fine[a],coarse[a])&0x7fffffffu,0x41700000u),scale);error=max(error,value);
        }
        if(error<=0x3f800000u){
            for(uint a=0u;a<count;a++)state[a]=fine[a];accepted++;
            elapsed=step==remaining?duration:sfadd(elapsed,step);h=step;
            if(error<=0x3d000000u)h=step<=sfmul(hmax,0x3f000000u)?sfmul(step,0x40000000u):hmax;
            h=max(h,hmin);
        }else{
            rejected++;if(half_step<hmin){status=2u;break;}h=half_step;
        }
    }
    if(elapsed==duration)status=0u;
    result[base]=status;result[base+1u]=attempts;result[base+2u]=accepted;result[base+3u]=rejected;
    result[base+4u]=elapsed;result[base+5u]=error;result[base+6u]=h;
    for(uint a=0u;a<count;a++)result[base+7u+a]=state[a];
''',
70:r'''
    uint n=data[4],base=i*15u,total=0u,kinetic=0u,potential=0u,minimum=0u;
    uint momentum[3]=uint[3](0u,0u,0u),angular[3]=uint[3](0u,0u,0u),center[3]=uint[3](0u,0u,0u);
    for(uint a=0u;a<15u;a++)result[base+a]=0u;
    for(uint p=0u;p<n;p++)total=sfadd(total,B(i*n+p));
    if(total==0u){result[base]=2u;return;}
    for(uint p=0u;p<n;p++){
        uint mass=B(i*n+p);if(mass==0u)continue;uint state[6],v2=0u;
        for(uint a=0u;a<6u;a++)state[a]=A((i*n+p)*6u+a);
        for(uint a=0u;a<3u;a++)v2=sfadd(v2,sfmul(state[3u+a],state[3u+a]));
        kinetic=sfadd(kinetic,sfmul(sfmul(0x3f000000u,mass),v2));
        for(uint a=0u;a<3u;a++){
            momentum[a]=sfadd(momentum[a],sfmul(mass,state[3u+a]));center[a]=sfadd(center[a],sfmul(mass,state[a]));
            uint b=(a+1u)%3u,c=(a+2u)%3u;
            uint cross=sfsub(sfmul(state[b],state[3u+c]),sfmul(state[c],state[3u+b]));
            angular[a]=sfadd(angular[a],sfmul(mass,cross));
        }
    }
    bool have_pair=false;
    for(uint p=0u;p<n;p++)for(uint q=p+1u;q<n;q++){
        uint distance=0u;
        for(uint a=0u;a<3u;a++){uint delta=sfsub(A((i*n+q)*6u+a),A((i*n+p)*6u+a));distance=sfadd(distance,sfmul(delta,delta));}
        minimum=have_pair?min(minimum,distance):distance;have_pair=true;
        uint coupling=sfmul(sfmul(data[8],B(i*n+p)),B(i*n+q));if(coupling==0u)continue;
        uint softened=sfadd(distance,data[9]);if(softened==0u){result[base]=1u;return;}
        potential=sfsub(potential,sfdiv(coupling,sfsqrt(softened)));
    }
    result[base+1u]=total;result[base+2u]=kinetic;result[base+3u]=potential;result[base+4u]=sfadd(kinetic,potential);
    for(uint a=0u;a<3u;a++){result[base+5u+a]=momentum[a];result[base+8u+a]=angular[a];result[base+11u+a]=sfdiv(center[a],total);}
    result[base+14u]=minimum;
'''}


def helpers(op):return INTEGRATOR if op==69 else ''
