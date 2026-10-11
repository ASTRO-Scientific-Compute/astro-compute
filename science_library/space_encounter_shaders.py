BODIES={71:r'''
    uint p[3],q[3],d[3],aa=0u,bb=0u,base=i*7u;
    for(uint a=0u;a<3u;a++){
        p[a]=sfsub(A(i*14u+6u+a),A(i*14u+a));q[a]=sfsub(A(i*14u+9u+a),A(i*14u+3u+a));d[a]=sfsub(q[a],p[a]);
        aa=sfadd(aa,sfmul(d[a],d[a]));bb=sfadd(bb,sfmul(p[a],d[a]));
    }
    uint t=0u;
    if(aa!=0u&&sfless(bb,0u)){uint positive=sfneg(bb);t=positive>=aa?0x3f800000u:sfdiv(positive,aa);}
    uint closest=0u,start=0u,end=0u;
    for(uint a=0u;a<3u;a++){
        uint v=t==0u?p[a]:t==0x3f800000u?q[a]:sfadd(p[a],sfmul(t,d[a]));
        closest=sfadd(closest,sfmul(v,v));start=sfadd(start,sfmul(p[a],p[a]));end=sfadd(end,sfmul(q[a],q[a]));
    }
    uint radius=sfadd(A(i*14u+12u),A(i*14u+13u)),radius2=sfmul(radius,radius);
    result[base]=closest<=radius2?1u:0u;result[base+1u]=t;result[base+2u]=closest;
    result[base+3u]=start;result[base+4u]=end;result[base+5u]=radius2;result[base+6u]=aa==0u?1u:0u;
'''}
