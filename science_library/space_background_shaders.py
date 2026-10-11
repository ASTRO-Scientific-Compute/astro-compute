"""Original bounded neighbor insertion and masked median insertion kernels."""
BODIES = {
61: r'''
    uint n=data[4],limit=data[8],qx=B(2u*i),qy=B(2u*i+1u),distances[16],indices[16],used=0u,base=4u*i;
    for(uint k=0u;k<4u;k++)result[base+k]=0u;result[base]=1u;
    for(uint j=0u;j<n;j++){
        if(A(4u*j+3u)==0u)continue;
        int dx=int(A(4u*j))-int(qx),dy=int(A(4u*j+1u))-int(qy);
        uint d=uint(dx*dx+dy*dy),position=0u;
        while(position<used){if(d<distances[position]||(d==distances[position]&&j<indices[position]))break;position++;}
        if(position>=limit)continue;
        uint next_count=min(used+1u,limit);
        for(int k=int(next_count)-1;k>int(position);k--){distances[k]=distances[k-1];indices[k]=indices[k-1];}
        distances[position]=d;indices[position]=j;used=next_count;
    }
    if(used==0u)return;
    result[base]=0u;
    if(distances[0]==0u){result[base+1u]=sfadd(A(4u*indices[0]+2u),0u);result[base+2u]=1u;return;}
    uint numerator=0u,denominator=0u;
    for(uint k=0u;k<used;k++){
        uint weight=sfdiv(0x3f800000u,sfu(distances[k]));
        numerator=sfadd(numerator,sfmul(weight,A(4u*indices[k]+2u)));denominator=sfadd(denominator,weight);
    }
    result[base+1u]=sfdiv(numerator,denominator);result[base+2u]=used;result[base+3u]=distances[0];
''',
62: r'''
    uint width=data[4],height=data[5],radius=data[8]/2u,minimum=data[9],cy=i/width,cx=i%width,count=0u,ordered[49];
    int top=max(0,int(cy)-int(radius)),bottom=min(int(height)-1,int(cy+radius));
    int left=max(0,int(cx)-int(radius)),right=min(int(width)-1,int(cx+radius));
    for(int y=top;y<=bottom;y++)for(int x=left;x<=right;x++){
        uint j=uint(y)*width+uint(x);if(B(j)==0u)continue;
        uint value=A(j),position=count;
        while(position>0u){if(!sfless(value,ordered[position-1u]))break;ordered[position]=ordered[position-1u];position--;}
        ordered[position]=value;count++;
    }
    uint base=3u*i;result[base]=1u;result[base+1u]=count;result[base+2u]=0u;
    if(count<minimum)return;
    uint middle=count/2u;
    result[base]=0u;result[base+2u]=(count%2u)==1u?sfadd(ordered[middle],0u):sfadd(sfmul(ordered[middle-1u],0x3f000000u),sfmul(ordered[middle],0x3f000000u));
''',
}
