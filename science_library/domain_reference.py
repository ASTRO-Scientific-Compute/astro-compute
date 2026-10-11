"""Cross-domain scientific CPU references using exact integers or RN32 oracle."""
from . import f32 as f
from .reference import Job, MAGIC, encode
from .float_reference import values,rows


def prepare_domain(wid, op, payload):
    if op!=25 and payload.get('encoding')!='binary32-hex':raise ValueError('explicit encoding=binary32-hex required')
    a=[];b=[];c=[];out=[];n=0;m=0;w=0;h=0;p0=0;p1=0;p2=0;ow=1
    if op==25:
        seqs=payload['sequences'];kmers=payload['kmers']
        if not isinstance(seqs,list) or not 1<=len(seqs)<=256 or not isinstance(kmers,list) or not 1<=len(kmers)<=256:raise ValueError('sequence/query count')
        if any(not isinstance(s,str) or len(s)>4096 or set(s)-set('ACGT') for s in seqs):raise ValueError('ACGT sequence required')
        if any(not isinstance(s,str) or not 1<=len(s)<=15 or set(s)-set('ACGT') for s in kmers) or len({len(s) for s in kmers})!=1:raise ValueError('uniform ACGT k-mers1..15 required')
        n=max(map(len,seqs));m=len(kmers);p0=len(kmers[0]);records=len(seqs)*m
        if records*n>4194304:raise ValueError('k-mer tile too large')
        for s in seqs:
            a.extend([len(s)]+['ACGT'.index(x) for x in s]+[0]*(n-len(s)))
            out.extend(sum(s[j:j+p0]==q for j in range(len(s)-p0+1)) for q in kmers)
        for q in kmers:
            code=0
            for ch in q:code=4*code+'ACGT'.index(ch)
            b.append(code)
    elif op==26:
        pairs=rows(payload['pairs'],6);records=len(pairs);ow=4
        p0=f.parse(payload['sigma']);p1=f.parse(payload['epsilon'])
        if f.rational(p0)<=0 or f.rational(p1)<0:raise ValueError('positive sigma, nonnegative epsilon')
        for row in pairs:
            a.extend(row);d=[f.sub(row[k],row[k+3]) for k in range(3)];s=f.dot(d,d)
            if not s:raise ValueError('coincident or underflow-distance pair')
            q=f.div(f.mul(p0,p0),s);t=f.mul(f.mul(q,q),q);tt=f.mul(t,t)
            energy=f.mul(f.mul(f.rounded(4),p1),f.sub(tt,t))
            factor=f.div(f.mul(f.mul(f.rounded(24),p1),f.sub(f.mul(f.TWO,tt),t)),s)
            out.extend([energy]+[f.mul(factor,x) for x in d])
    elif op==27:
        raw=payload['field'];h=len(raw)
        if not 3<=h<=256:raise ValueError('field height3..256')
        w=len(raw[0])
        if not 3<=w<=256:raise ValueError('field width3..256')
        field=rows(raw,w,256);p0=f.parse(payload['lambda'])
        if not 0<=f.rational(p0)<=f.rational(0x3e800000):raise ValueError('explicit heat stability requires lambda0..1/4')
        a=[x for row in field for x in row];records=w*h
        for y,row in enumerate(field):
            for x,v in enumerate(row):
                neighbors=[row[(x-1)%w],row[(x+1)%w],field[(y-1)%h][x],field[(y+1)%h][x]]
                lap=f.sub(f.summation(neighbors),f.mul(f.rounded(4),v))
                out.append(f.add(v,f.mul(p0,lap)))
    elif op==28:
        a=values(payload['xp']);b=values(payload['fp']);c=values(payload['queries']);n=len(a);records=len(c)
        if n!=len(b) or any(f.rational(x)>=f.rational(y) for x,y in zip(a,a[1:])):raise ValueError('matching strictly increasing knots required')
        for x in c:
            v=f.rational(x)
            if v<=f.rational(a[0]):out.append(0 if not f.rational(b[0]) else b[0]);continue
            if v>=f.rational(a[-1]):out.append(0 if not f.rational(b[-1]) else b[-1]);continue
            j=next(j for j in range(n-1) if f.rational(a[j])<=v<f.rational(a[j+1]))
            if v==f.rational(a[j]):out.append(0 if not f.rational(b[j]) else b[j]);continue
            weight=f.div(f.sub(x,a[j]),f.sub(a[j+1],a[j]))
            out.append(f.add(b[j],f.mul(weight,f.sub(b[j+1],b[j]))))
    elif op==29:
        left=payload['left'];right=payload['right'];n=len(left[0]);m=len(right[0])
        if not 1<=n<=128 or not 1<=m<=128:raise ValueError('matrix width1..128')
        left=rows(left,n,128);right=rows(right,m,128)
        if len(right)!=n:raise ValueError('inner dimensions differ')
        records=len(left)*m
        if records*n>1048576:raise ValueError('matrix tile too large')
        a=[x for row in left for x in row];b=[x for row in right for x in row]
        out=[f.dot(row,[right[k][j] for k in range(n)]) for row in left for j in range(m)]
    else:raise ValueError('domain opcode')
    assert len(out)==records*ow
    header=[MAGIC,1,op,records,n,m,w,h,p0,p1,p2,16+len(a),16+len(a)+len(b),ow,0,0]
    return Job(wid,payload,header+a+b+c,records,ow,encode(out))
