"""Original generic GPU kernels, after MathSpecs and CPU goldens passed."""

BODIES = {
45: r'''
    uint n=data[4],sum=0u;
    for(uint j=0u;j<n;j++)sum=sfadd(sum,A(B(i*n+j)));
    uint mean=sfdiv(sum,sfu(n)),sq=0u;
    for(uint j=0u;j<n;j++){uint d=sfsub(A(B(i*n+j)),mean);sq=sfadd(sq,sfmul(d,d));}
    result[i*2u]=mean;result[i*2u+1u]=sfdiv(sq,sfu(n-1u));
''',
46: r'''
    uint n=data[4],base=i*n,keep[512],status=2u,count=0u,mean=0u,variance=0u;
    for(uint j=0u;j<n;j++)keep[j]=B(base+j);
    for(uint iteration=0u;iteration<data[10];iteration++){
        uint sum=0u;count=0u;
        for(uint j=0u;j<n;j++)if(keep[j]!=0u){sum=sfadd(sum,A(base+j));count++;}
        if(count==0u){status=1u;break;}
        mean=sfdiv(sum,sfu(count));uint sq=0u;
        for(uint j=0u;j<n;j++)if(keep[j]!=0u){uint d=sfsub(A(base+j),mean);sq=sfadd(sq,sfmul(d,d));}
        variance=sfdiv(sq,sfu(count));uint sd=sfsqrt(variance);
        uint lo=sfsub(mean,sfmul(data[8],sd)),hi=sfadd(mean,sfmul(data[9],sd));bool changed=false;
        for(uint j=0u;j<n;j++)if(keep[j]!=0u&&(sfless(A(base+j),lo)||sfless(hi,A(base+j)))){keep[j]=0u;changed=true;}
        if(!changed){status=0u;break;}
    }
    uint sum=0u;count=0u;mean=0u;variance=0u;
    for(uint j=0u;j<n;j++)if(keep[j]!=0u){sum=sfadd(sum,A(base+j));count++;}
    if(count==0u)status=1u;
    else{
        mean=sfdiv(sum,sfu(count));uint sq=0u;
        for(uint j=0u;j<n;j++)if(keep[j]!=0u){uint d=sfsub(A(base+j),mean);sq=sfadd(sq,sfmul(d,d));}
        variance=sfdiv(sq,sfu(count));
    }
    uint dest=i*data[13];result[dest]=status;result[dest+1u]=count;result[dest+2u]=mean;result[dest+3u]=variance;
    for(uint j=0u;j<n;j++)result[dest+4u+j]=keep[j];
''',
47: r'''
    uint n=data[4],w=data[6],base=i*n,parent[1024],sizes[1024];
    for(uint j=0u;j<n;j++){parent[j]=(B(base+j)!=0u&&sfless(data[8],A(base+j)))?j:0xffffffffu;sizes[j]=0u;}
    for(uint j=0u;j<n;j++){
        if(parent[j]==0xffffffffu)continue;
        uint x=j%w,y=j/w,neighbors[4];uint count=0u;
        if(x>0u)neighbors[count++]=j-1u;
        if(y>0u){neighbors[count++]=j-w;
            if(data[10]==8u){if(x>0u)neighbors[count++]=j-w-1u;if(x+1u<w)neighbors[count++]=j-w+1u;}}
        for(uint k=0u;k<count;k++){
            uint other=neighbors[k];if(parent[other]==0xffffffffu)continue;
            uint r=j,s=other;while(parent[r]!=r)r=parent[r];while(parent[s]!=s)s=parent[s];
            if(r!=s)parent[max(r,s)]=min(r,s);
        }
    }
    for(uint j=0u;j<n;j++)if(parent[j]!=0xffffffffu){uint r=j;while(parent[r]!=r)r=parent[r];parent[j]=r;sizes[r]++;}
    for(uint j=0u;j<n;j++){uint r=parent[j];result[base+j]=(r!=0xffffffffu&&sizes[r]>=data[9])?r+1u:0u;}
''',
}
