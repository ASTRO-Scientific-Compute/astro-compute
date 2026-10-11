"""Independent Fraction/RN32 bounded forward SIP distortion oracle."""
from fractions import Fraction
from . import f32 as f
from .reference import Job,MAGIC,encode
from .float_reference import rows,values
WID='SPACE_SIP_FORWARD_F32_V1'
TAGS=dict(encoding='binary32-hex',offset_unit='pixel',offset_origin='REFERENCE_PIXEL',term_order='DEGREE_ASCENDING_P_ASCENDING')


def terms(order):return [(degree,p,degree-p) for degree in range(2,order+1) for p in range(degree+1)]


def coefficient_limit(degree):return Fraction(1,1<<(10*degree-8))


def distort(u,v,a,b,oa,ob):
    up=[f.ONE];vp=[f.ONE]
    for k in range(max(oa,ob)):
        up.append(f.mul(up[-1],u));vp.append(f.mul(vp[-1],v))
    sums=[]
    for coefficients,order in ((a,oa),(b,ob)):
        total=0
        for coefficient,(_,p,q) in zip(coefficients,terms(order)):
            total=f.add(total,f.mul(f.mul(coefficient,up[p]),vp[q]))
        sums.append(total)
    return [f.add(u,sums[0]),f.add(v,sums[1]),*sums]


def prepare_space_sip(wid,payload):
    if not isinstance(payload,dict) or set(payload)!=set(TAGS)|{'model_id','a_order','b_order','a_coefficients','b_coefficients','offsets'} or any(payload.get(k)!=v for k,v in TAGS.items()):raise ValueError('exact SIP fields and explicit offset/term tags required')
    label=payload['model_id']
    if not isinstance(label,str) or not label.strip() or len(label)>64:raise ValueError('bounded explicit distortion model id required')
    orders=[payload['a_order'],payload['b_order']]
    if any(type(order) is not int or not 2<=order<=5 for order in orders):raise ValueError('independent polynomial orders2..5 required')
    coefficients=[]
    for key,order in zip(('a_coefficients','b_coefficients'),orders):
        tt=terms(order);parsed=values(payload[key],len(tt),len(tt))
        if any(abs(f.rational(word))>coefficient_limit(degree) for word,(degree,_,_) in zip(parsed,tt)):raise ValueError('degree-specific SIP coefficient bound exceeded')
        coefficients.append(parsed)
    offsets=rows(payload['offsets'],2,4096)
    if any(abs(f.rational(word))>1024 for row in offsets for word in row):raise ValueError('reference-relative pixel offset outside[-1024,1024]')
    n=len(offsets);astart=16+2*n;bstart=astart+len(coefficients[0]);header=[MAGIC,1,81,n,*orders,0,0,0,0,0,astart,bstart,4,0,0]
    output=[word for row in offsets for word in distort(*row,*coefficients,*orders)]
    return Job(wid,payload,header+sum(offsets,[])+coefficients[0]+coefficients[1],n,4,encode(output))
