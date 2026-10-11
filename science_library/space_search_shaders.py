"""Original GPU implementations; uint-only RN32 arithmetic, no native trig."""
from .space_search_reference import SIN_COEFF,COS_COEFF

TRIG=r'''
uint trunc_positive(uint a){uint m;int e;unpack32(a,m,e);return e<0?0u:m>>uint(23-e);}
uvec2 sincos_turn(uint a){
    uint mag=a&0x7fffffffu;uint whole=trunc_positive(mag);
    uint phase=sfsub(mag,sfu(whole));uint quadrant=trunc_positive(sfmul(phase,0x40800000u));
    uint residual=sfsub(phase,sfmul(sfu(quadrant),0x3e800000u));
    uint x=sfmul(residual,0x40c90fdbu),z=sfmul(x,x);
    const uint sc[7]=uint[7](SIN_COEFF);const uint cc[8]=uint[8](COS_COEFF);
    uint sn=sc[6],cn=cc[7];for(int k=5;k>=0;k--)sn=sfadd(sc[k],sfmul(z,sn));
    for(int k=6;k>=0;k--)cn=sfadd(cc[k],sfmul(z,cn));sn=sfmul(x,sn);
    uvec2 r=quadrant==0u?uvec2(sn,cn):quadrant==1u?uvec2(cn,sfneg(sn)):quadrant==2u?uvec2(sfneg(sn),sfneg(cn)):uvec2(sfneg(cn),sn);
    if((a&0x80000000u)!=0u)r.x=sfneg(r.x);return r;
}
'''.replace('SIN_COEFF',','.join(f'0x{x:08x}u' for x in SIN_COEFF)).replace('COS_COEFF',','.join(f'0x{x:08x}u' for x in COS_COEFF))

RK4=r'''
void derivative(uint state[6],out uint d[6]){
    uint mu=data[8],factor=0u;
    if(mu!=0u){uint r2=0u;for(uint k=0u;k<3u;k++)r2=sfadd(r2,sfmul(state[k],state[k]));factor=sfneg(sfdiv(mu,sfmul(r2,sfsqrt(r2))));}
    for(uint k=0u;k<3u;k++){d[k]=state[k+3u];d[k+3u]=sfmul(factor,state[k]);}
}
'''

BODIES={
39:r'''
    uint n=data[4],freq=B(i),weight=0u,wy=0u,wc=0u,ws=0u;uvec2 trig[512];
    for(uint j=0u;j<n;j++){uint w=A(j*3u+2u);trig[j]=sincos_turn(sfmul(A(j*3u),freq));weight=sfadd(weight,w);wy=sfadd(wy,sfmul(w,A(j*3u+1u)));wc=sfadd(wc,sfmul(w,trig[j].y));ws=sfadd(ws,sfmul(w,trig[j].x));}
    uint base=i*6u;for(uint k=0u;k<6u;k++)result[base+k]=0u;
    if(weight==0u){result[base]=1u;return;}
    uint ym=sfdiv(wy,weight),cm=sfdiv(wc,weight),sm=sfdiv(ws,weight),cc=0u,ss=0u,cs=0u,yc=0u,ys=0u,yy=0u;
    for(uint j=0u;j<n;j++){
        uint c=sfsub(trig[j].y,cm),s=sfsub(trig[j].x,sm),y=sfsub(A(j*3u+1u),ym),w=A(j*3u+2u);
        uint ww_c=sfmul(w,c),ww_s=sfmul(w,s),ww_y=sfmul(w,y);
        cc=sfadd(cc,sfmul(ww_c,c));ss=sfadd(ss,sfmul(ww_s,s));cs=sfadd(cs,sfmul(ww_c,s));
        yc=sfadd(yc,sfmul(ww_y,c));ys=sfadd(ys,sfmul(ww_y,s));yy=sfadd(yy,sfmul(ww_y,y));
    }
    if(yy==0u){result[base]=1u;return;}
    uint product=sfmul(cc,ss),det=sfsub(product,sfmul(cs,cs));
    if(!sfless(sfmul(product,0x36800000u),det)){result[base]=2u;return;}
    uint ac=sfdiv(sfsub(sfmul(yc,ss),sfmul(ys,cs)),det),bs=sfdiv(sfsub(sfmul(ys,cc),sfmul(yc,cs)),det);
    uint offset=sfsub(sfsub(ym,sfmul(ac,cm)),sfmul(bs,sm)),chi=0u;
    for(uint j=0u;j<n;j++){uint residual=sfsub(A(j*3u+1u),sfadd(sfadd(offset,sfmul(ac,trig[j].y)),sfmul(bs,trig[j].x)));chi=sfadd(chi,sfmul(A(j*3u+2u),sfmul(residual,residual)));}
    result[base+1u]=sfdiv(sfsub(yy,chi),yy);result[base+2u]=offset;result[base+3u]=ac;result[base+4u]=bs;result[base+5u]=chi;
''',
40:r'''
    uint n=data[4],bins=data[8],period=C(i),cnt[64],sums[64];
    for(uint k=0u;k<bins;k++){cnt[k]=0u;sums[k]=0u;}
    for(uint j=0u;j<n;j++){uint bin=((A(j)%period)*bins)/period;cnt[bin]++;sums[bin]=sfadd(sums[bin],B(j));}
    uint total=0u;for(uint k=0u;k<bins;k++)total=sfadd(total,sums[k]);
    uint base=i*6u;result[base]=1u;for(uint k=1u;k<6u;k++)result[base+k]=0u;uint best=0u;
    for(uint start=0u;start<bins;start++){
        uint ni=0u,yi=0u;
        for(uint width=1u;width<=data[10];width++){
            uint bin=(start+width-1u)%bins;ni+=cnt[bin];yi=sfadd(yi,sums[bin]);uint no=n-ni;
            if(width<data[9]||ni==0u||no==0u)continue;
            uint outer=sfdiv(sfsub(total,yi),sfu(no)),depth=sfsub(outer,sfdiv(yi,sfu(ni)));
            if(!sfless(0u,depth))continue;
            uint score=sfdiv(sfmul(sfmul(sfmul(depth,depth),sfu(ni)),sfu(no)),sfu(n));
            if(sfless(best,score)){best=score;result[base]=0u;result[base+1u]=start;result[base+2u]=width;result[base+3u]=depth;result[base+4u]=outer;result[base+5u]=score;}
        }
    }
''',
41:r'''
    uint value=A(i);bool peak=B(i)!=0u&&sfless(data[8],value);int w=int(data[6]),h=int(data[7]),r=int(data[9]),x=int(i)%w,y=int(i)/w;
    for(int dy=-r;dy<=r;dy++)for(int dx=-r;dx<=r;dx++){
        int xx=x+dx,yy=y+dy;uint other=0u;
        if(xx>=0&&xx<w&&yy>=0&&yy<h){uint j=uint(yy*w+xx);if(B(j)==0u)continue;other=A(j);}
        if(sfless(value,other))peak=false;
    }
    result[i]=uint(peak);
''',
42:r'''
    uint n=data[4],obs=i/data[5],model=i%data[5],num=0u,den=0u;
    for(uint k=0u;k<n;k++){uint y=A((obs*n+k)*2u),w=A((obs*n+k)*2u+1u),t=B(model*n+k),wt=sfmul(w,t);num=sfadd(num,sfmul(wt,y));den=sfadd(den,sfmul(wt,t));}
    uint amp=0u,chi=0u;
    if(den!=0u){amp=sfdiv(num,den);if(sfless(amp,0u))amp=0u;
        for(uint k=0u;k<n;k++){uint residual=sfsub(A((obs*n+k)*2u),sfmul(amp,B(model*n+k)));chi=sfadd(chi,sfmul(A((obs*n+k)*2u+1u),sfmul(residual,residual)));}}
    result[i*3u]=uint(den==0u);result[i*3u+1u]=amp;result[i*3u+2u]=chi;
''',
43:r'''
    uint radius=A(i*3u);uvec2 lat=sincos_turn(A(i*3u+1u)),lon=sincos_turn(A(i*3u+2u));uint rc=sfmul(radius,lat.y);
    result[i*3u]=sfmul(rc,lon.y);result[i*3u+1u]=sfmul(rc,lon.x);result[i*3u+2u]=sfmul(radius,lat.x);
''',
44:r'''
    uint state[6],tmp[6],k1[6],k2[6],k3[6],k4[6],base=i*data[13],dt=data[9],half_dt=sfmul(dt,0x3f000000u),sixth=sfdiv(dt,0x40c00000u);
    for(uint k=0u;k<6u;k++){state[k]=sfadd(A(i*6u+k),0u);result[base+k]=state[k];}
    for(uint step=0u;step<data[4];step++){
        derivative(state,k1);for(uint k=0u;k<6u;k++)tmp[k]=sfadd(state[k],sfmul(half_dt,k1[k]));
        derivative(tmp,k2);for(uint k=0u;k<6u;k++)tmp[k]=sfadd(state[k],sfmul(half_dt,k2[k]));
        derivative(tmp,k3);for(uint k=0u;k<6u;k++)tmp[k]=sfadd(state[k],sfmul(dt,k3[k]));derivative(tmp,k4);
        for(uint k=0u;k<6u;k++){uint sum=sfadd(sfadd(sfadd(k1[k],sfmul(0x40000000u,k2[k])),sfmul(0x40000000u,k3[k])),k4[k]);state[k]=sfadd(state[k],sfmul(sixth,sum));result[base+(step+1u)*6u+k]=state[k];}
    }
''',
}


def helpers(op):return (TRIG if op in (39,43) else '')+(RK4 if op==44 else '')
