"""Original inference GPU code, following independent CPU reference vectors."""
CI_HELPER = r'''
uint ci_quantile(uint sorted_values[512],uint n,uint q){
    uint h=sfmul(sfu(n-1u),q),mant;int exponent;unpack32(h,mant,exponent);
    uint j=exponent<0?0u:mant>>uint(23-exponent),g=sfsub(h,sfu(j));
    if(g==0u)return sorted_values[j];
    return sfadd(sfmul(sfsub(0x3f800000u,g),sorted_values[j]),sfmul(g,sorted_values[min(j+1u,n-1u)]));
}
'''
SED_HELPER = r'''
uint pair_chi(uint object_index,uint pair_index,uint aa,uint bb){
    uint n=data[4],chi=0u;
    for(uint k=0u;k<n;k++){
        uint predicted=sfadd(sfmul(aa,B(pair_index*2u*n+k)),sfmul(bb,B(pair_index*2u*n+n+k)));
        uint residual=sfsub(A((object_index*n+k)*2u),predicted);
        chi=sfadd(chi,sfmul(A((object_index*n+k)*2u+1u),sfmul(residual,residual)));
    }
    return chi;
}
'''
BODIES = {
48:r'''
    uint n=data[4],padded=1u,ordered[512];while(padded<n)padded*=2u;
    for(uint k=0u;k<padded;k++)ordered[k]=k<n?sfadd(A(i*n+k),0u):0x7f7fffffu;
    for(uint span=2u;span<=padded;span*=2u)for(uint stride=span/2u;stride>0u;stride/=2u){
        for(uint j=0u;j<padded;j++){uint other=j^stride;if(other<=j)continue;
            bool ascending=(j&span)==0u;
            if(ascending?sfless(ordered[other],ordered[j]):sfless(ordered[j],ordered[other])){
                uint value=ordered[j];ordered[j]=ordered[other];ordered[other]=value;}
        }
    }
    uint alpha=sfmul(sfsub(0x3f800000u,data[8]),0x3f000000u);
    result[i*2u]=ci_quantile(ordered,n,alpha);result[i*2u+1u]=ci_quantile(ordered,n,sfsub(0x3f800000u,alpha));
''',
49:r'''
    uint value=A(i),count=0u,n=data[4];
    for(uint j=0u;j<n;j++)if(!sfless(B(j),value))count++;
    result[i*4u]=count;result[i*4u+1u]=n;result[i*4u+2u]=count+1u;result[i*4u+3u]=n+1u;
''',
50:r'''
    uint n=data[4],object_index=i/data[5],pair_index=i%data[5],g00=0u,g01=0u,g11=0u,u=0u,v=0u;
    for(uint k=0u;k<n;k++){
        uint y=A((object_index*n+k)*2u),w=A((object_index*n+k)*2u+1u);
        uint t0=B(pair_index*2u*n+k),t1=B(pair_index*2u*n+n+k),wt0=sfmul(w,t0),wt1=sfmul(w,t1);
        g00=sfadd(g00,sfmul(wt0,t0));g01=sfadd(g01,sfmul(wt0,t1));g11=sfadd(g11,sfmul(wt1,t1));
        u=sfadd(u,sfmul(wt0,y));v=sfadd(v,sfmul(wt1,y));
    }
    uint base=i*4u,product=sfmul(g00,g11),det=sfsub(product,sfmul(g01,g01));
    result[base]=1u;for(uint k=1u;k<4u;k++)result[base+k]=0u;
    if(!sfless(sfmul(product,0x36800000u),det))return;
    uint axis_a=sfdiv(u,g00),axis_b=sfdiv(v,g11);
    if(sfless(axis_a,0u))axis_a=0u;if(sfless(axis_b,0u))axis_b=0u;
    uint aa=sfdiv(sfsub(sfmul(u,g11),sfmul(v,g01)),det),bb=sfdiv(sfsub(sfmul(v,g00),sfmul(u,g01)),det);
    uint best_a=0u,best_b=0u,best=pair_chi(object_index,pair_index,0u,0u);
    uint trial=pair_chi(object_index,pair_index,axis_a,0u);
    if(sfless(trial,best)){best=trial;best_a=axis_a;}
    trial=pair_chi(object_index,pair_index,0u,axis_b);
    if(sfless(trial,best)){best=trial;best_a=0u;best_b=axis_b;}
    if(!sfless(aa,0u)&&!sfless(bb,0u)){
        trial=pair_chi(object_index,pair_index,aa,bb);
        if(sfless(trial,best)){best=trial;best_a=aa;best_b=bb;}
    }
    result[base]=0u;result[base+1u]=best_a;result[base+2u]=best_b;result[base+3u]=best;
''',
}


def helpers(op):
    return CI_HELPER if op == 48 else SED_HELPER if op == 50 else ''
