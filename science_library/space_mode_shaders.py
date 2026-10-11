"""Original insertion-sort and iterative shortest-subset_size GPU implementation."""
BODIES={64:r'''
    uint n=data[4],ordered[256],count=0u,base=9u*i;
    for(uint j=0u;j<9u;j++)result[base+j]=0u;result[base]=1u;
    for(uint j=0u;j<n;j++)if(B(i*n+j)!=0u){
        uint value=A(i*n+j),position=count;
        while(position>0u){if(!sfless(value,ordered[position-1u]))break;ordered[position]=ordered[position-1u];position--;}
        ordered[position]=value;count++;
    }
    if(count==0u)return;
    uint first=0u,size=count,rounds=0u;
    while(size>=4u){
        uint subset_size=(size+1u)/2u,best=0u,best_width=sfsub(ordered[first+subset_size-1u],ordered[first]);
        for(uint j=1u;j+subset_size<=size;j++){
            uint width=sfsub(ordered[first+j+subset_size-1u],ordered[first+j]);
            if(sfless(width,best_width)){best=j;best_width=width;}
        }
        first+=best;size=subset_size;rounds++;
    }
    if(size==3u){
        uint left=sfsub(ordered[first+1u],ordered[first]),right=sfsub(ordered[first+2u],ordered[first+1u]);
        if(sfless(left,right))size=2u;
        else if(sfless(right,left)){first++;size=2u;}
    }
    uint mode;
    if(size==2u){
        uint a=ordered[first],b=ordered[first+1u];
        if((a&0x7fffffffu)<=0x7effffffu&&(b&0x7fffffffu)<=0x7effffffu)mode=sfmul(sfadd(a,b),0x3f000000u);
        else mode=sfadd(sfmul(a,0x3f000000u),sfmul(b,0x3f000000u));
    }
    else mode=sfadd(ordered[first+size/2u],0u);
    uint low=sfadd(ordered[first],0u),high=sfadd(ordered[first+size-1u],0u);
    result[base]=0u;result[base+1u]=count;result[base+2u]=mode;result[base+3u]=low;result[base+4u]=high;
    result[base+5u]=sfsub(high,low);result[base+6u]=size;result[base+7u]=rounds;result[base+8u]=first;
'''}
