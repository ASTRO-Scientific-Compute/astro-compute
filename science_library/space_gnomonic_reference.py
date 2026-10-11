"""Independent Fraction/RN32 bounded gnomonic projection."""
from fractions import Fraction
from . import f32 as f
from .reference import Job,MAGIC,encode
from .float_reference import rows,values
from .space_search_reference import sincos
WID='SPACE_GNOMONIC_PROJECT_F32_V1'


def project(alpha,delta,alpha0,delta0):
    s,c=sincos(delta);s0,c0=sincos(delta0);sd,cd=sincos(f.sub(alpha,alpha0))
    d=f.add(f.mul(s,s0),f.mul(f.mul(c,c0),cd))
    if f.rational(d)<Fraction(1,16):return [1,0,0,d]
    xi=f.div(f.mul(c,sd),d)
    eta=f.div(f.sub(f.mul(s,c0),f.mul(f.mul(c,s0),cd)),d)
    return [0,xi,eta,d]


def prepare_space_gnomonic(wid,payload):
    tags=dict(encoding='binary32-hex',angle_unit='turn',projection='GNOMONIC_TAN',axes='EAST_NORTH')
    if set(payload)!=set(tags)|{'frame','tangent_point','directions'} or any(payload.get(k)!=v for k,v in tags.items()):raise ValueError('exact gnomonic fields and explicit projection/axes/angle tags required')
    frame=payload['frame']
    if not isinstance(frame,str) or not frame.strip() or len(frame)>64:raise ValueError('bounded explicit common sky frame required')
    point=values(payload['tangent_point'],2,2);directions=rows(payload['directions'],2,4096)
    for alpha,delta in [point]+directions:
        if not 0<=f.rational(alpha)<1 or not -Fraction(1,4)<=f.rational(delta)<=Fraction(1,4):raise ValueError('spherical turn angles outside bounds')
    n=len(directions);end=16+2*n;header=[MAGIC,1,79,n,2,0,0,0,*point,0,end,end,4,0,0]
    out=[word for row in directions for word in project(*row,*point)]
    return Job(wid,payload,header+sum(directions,[]),n,4,encode(out))
