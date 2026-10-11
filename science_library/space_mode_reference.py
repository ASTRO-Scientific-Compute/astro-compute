"""Independent recursive rational/RN32 oracle for half-sample mode."""
from . import f32 as f
from .reference import Job,MAGIC,encode
from .space_statistics_reference import rectangular_float,masks


def half_sample_mode(values):
    data=sorted(values,key=f.rational)
    if not data:return [1]+[0]*8
    def select(items,start,rounds):
        size=len(items)
        if size>=4:
            k=(size+1)//2
            widths=[f.sub(items[j+k-1],items[j]) for j in range(size-k+1)]
            first=min(range(len(widths)),key=lambda j:f.rational(widths[j]))
            return select(items[first:first+k],start+first,rounds+1)
        if size==3:
            left=f.rational(f.sub(items[1],items[0]));right=f.rational(f.sub(items[2],items[1]))
            if left<right:items=items[:2]
            elif right<left:items=items[1:];start+=1
        size=len(items)
        mode=f.rounded((f.rational(items[0])+f.rational(items[1]))/2) if size==2 else f.add(items[size//2],0)
        low=f.add(items[0],0);high=f.add(items[-1],0)
        return [0,len(data),mode,low,high,f.sub(high,low),size,rounds,start]
    return select(data,0,0)


def prepare_space_mode(wid,op,payload):
    if op!=64 or payload.get('encoding')!='binary32-hex':raise ValueError('binary32 half-sample mode contract required')
    samples,n=rectangular_float(payload['samples'],128,256);valid=masks(payload['valid'],len(samples),n);records=len(samples)
    if records*n*n>2097152:raise ValueError('half-sample sorting work limit')
    a=[v for row in samples for v in row];b=[v for row in valid for v in row];out=[]
    for row,keep in zip(samples,valid):out.extend(half_sample_mode([v for v,k in zip(row,keep) if k]))
    header=[MAGIC,1,op,records,n,0,0,0,0,0,0,16+len(a),16+len(a)+len(b),9,0,0]
    return Job(wid,payload,header+a+b,records,9,encode(out))
