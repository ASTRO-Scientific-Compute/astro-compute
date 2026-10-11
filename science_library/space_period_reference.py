"""Independent exact-rational ordered fitting and phase-dispersion oracle."""
from . import f32 as f
from .reference import Job,MAGIC,encode,integer,array
from .float_reference import rows,values
from .space_search_reference import sincos


def basis(time,frequency,harmonics):
    phase=f.mul(time,frequency);out=[f.ONE]
    for k in range(1,harmonics+1):
        sn,cs=sincos(f.mul(phase,f.rounded(k)));out.extend([cs,sn])
    return out


def multiharmonic(samples,frequency,harmonics):
    p=2*harmonics+1;zero=[0]*(p+2)
    weights=[row[2] for row in samples];weight=f.summation(weights)
    if not weight:return [1]+zero
    mean=f.div(f.dot(weights,[row[1] for row in samples]),weight)
    gram=[[0]*p for _ in range(p)];rhs=[0]*p;chi0=0
    for time,y,w in samples:
        x=basis(time,frequency,harmonics);d=f.sub(y,mean)
        chi0=f.add(chi0,f.mul(w,f.mul(d,d)))
        for a in range(p):
            wx=f.mul(w,x[a]);rhs[a]=f.add(rhs[a],f.mul(wx,d))
            for b in range(p):gram[a][b]=f.add(gram[a][b],f.mul(wx,x[b]))
    if not chi0:return [1]+zero
    lower=[[0]*p for _ in range(p)];threshold=f.mul(weight,0x37800000)
    for i in range(p):
        for j in range(i+1):
            d=f.sub(gram[i][j],f.summation(f.mul(lower[i][k],lower[j][k]) for k in range(j)))
            if i==j:
                if f.rational(d)<=f.rational(threshold):return [2]+zero
                lower[i][j]=f.sqrt(d)
            else:lower[i][j]=f.div(d,lower[j][j])
    u=[0]*p;beta=[0]*p
    for i in range(p):u[i]=f.div(f.sub(rhs[i],f.summation(f.mul(lower[i][j],u[j]) for j in range(i))),lower[i][i])
    for i in range(p-1,-1,-1):beta[i]=f.div(f.sub(u[i],f.summation(f.mul(lower[j][i],beta[j]) for j in range(i+1,p))),lower[i][i])
    beta[0]=f.add(beta[0],mean);chi=0
    for time,y,w in samples:
        x=basis(time,frequency,harmonics);predicted=beta[0]
        for j in range(1,p):predicted=f.add(predicted,f.mul(beta[j],x[j]))
        residual=f.sub(y,predicted);chi=f.add(chi,f.mul(w,f.mul(residual,residual)))
    return [0,f.div(f.sub(chi0,chi),chi0),chi]+beta


def pdm(times,flux,period,bins):
    labels=[((t%period)*bins)//period for t in times];counts=[0]*bins;sums=[0]*bins
    for k,y in zip(labels,flux):counts[k]+=1;sums[k]=f.add(sums[k],y)
    mean=f.div(f.summation(flux),f.rounded(len(flux)))
    residuals=[f.sub(y,mean) for y in flux]
    variance=f.div(f.summation(f.mul(d,d) for d in residuals),f.rounded(len(flux)-1))
    if not variance:return [1,0,0,0,0,0]
    occupied=sum(c>0 for c in counts);dof=len(flux)-occupied
    if occupied<2 or not dof:return [2,0,0,0,0,0]
    means=[f.div(s,f.rounded(c)) if c else 0 for s,c in zip(sums,counts)]
    residuals=[f.sub(y,means[k]) for k,y in zip(labels,flux)]
    within=f.div(f.summation(f.mul(d,d) for d in residuals),f.rounded(dof))
    return [0,f.div(within,variance),variance,within,occupied,dof]


def prepare_space_period(wid,op,payload):
    if payload.get('encoding')!='binary32-hex':raise ValueError('encoding=binary32-hex required')
    a,b,c,out=[],[],[],[];n=p0=0
    if op==57:
        p0=integer(payload['harmonics'],2,4,'harmonics');p=2*p0+1
        samples=rows(payload['samples'],3,256);n=integer(len(samples),p+1,256,'observations')
        b=values(payload['frequencies'],128);records=len(b);ow=p+3
        if n*records*p*p>2097152:raise ValueError('harmonic tile work limit')
        if any(f.rational(w)<0 for t,y,w in samples) or any(f.rational(v)<=0 for v in b):raise ValueError('nonnegative weights / positive frequencies required')
        for frequency in b:
            for t,y,w in samples:
                if abs(f.rational(f.mul(f.mul(t,frequency),f.rounded(p0))))>256:raise ValueError('center times: highest harmonic phase magnitude must be <=256')
            out.extend(multiharmonic(samples,frequency,p0))
        a=[x for row in samples for x in row]
    elif op==58:
        a=array(payload['times'],0,10000000,'times',4096);n=integer(len(a),3,4096,'observations')
        b=values(payload['flux'],4096);c=array(payload['periods'],1,1000000,'periods',128);records=integer(len(c),1,128,'period count');ow=6
        if len(b)!=n or n*records>262144:raise ValueError('PDM shape/work limit')
        p0=integer(payload['bins'],2,64,'bins')
        for period in c:out.extend(pdm(a,b,period,p0))
    else:raise ValueError('unknown period-search opcode')
    assert len(out)==records*ow
    header=[MAGIC,1,op,records,n,0,0,0,p0,0,0,16+len(a),16+len(a)+len(b),ow,0,0]
    return Job(wid,payload,header+a+b+c,records,ow,encode(out))
