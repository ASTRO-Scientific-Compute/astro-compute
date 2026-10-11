"""Independent Fraction/RN32 inverse perspective via tangent basis and normalization."""
from fractions import Fraction
from . import f32 as f
from .reference import Job,MAGIC,encode
from .float_reference import rows,values
from .space_search_reference import sincos
WID='SPACE_TANGENT_TO_UNIT_VECTOR_F32_V1'


def reconstruct(xi,eta,alpha,delta):
    sa,ca=sincos(alpha);sd,cd=sincos(delta)
    center=[f.mul(cd,ca),f.mul(cd,sa),sd];east=[f.neg(sa),ca,0];north=[f.neg(f.mul(sd,ca)),f.neg(f.mul(sd,sa)),cd]
    u=[f.add(f.add(c,f.mul(xi,e)),f.mul(eta,n)) for c,e,n in zip(center,east,north)]
    r=f.sqrt(f.dot(u,u))
    return [f.div(x,r) for x in u]+[r]


def prepare_space_tangent_vector(wid,payload):
    tags=dict(encoding='binary32-hex',angle_unit='turn',projection='GNOMONIC_TAN',axes='EAST_NORTH')
    if set(payload)!=set(tags)|{'frame','tangent_point','plane_coordinates'} or any(payload.get(k)!=v for k,v in tags.items()):raise ValueError('exact inverse tangent fields and explicit projection/axes/angle tags required')
    frame=payload['frame']
    if not isinstance(frame,str) or not frame.strip() or len(frame)>64:raise ValueError('bounded explicit common celestial frame required')
    point=values(payload['tangent_point'],2,2);plane=rows(payload['plane_coordinates'],2,4096)
    if not 0<=f.rational(point[0])<1 or not -Fraction(1,4)<=f.rational(point[1])<=Fraction(1,4):raise ValueError('tangent point angles outside bounded turns')
    if any(abs(f.rational(w))>16 for row in plane for w in row):raise ValueError('plane coordinate outside[-16,16]')
    n=len(plane);end=16+2*n;header=[MAGIC,1,80,n,2,0,0,0,*point,0,end,end,4,0,0]
    out=[w for row in plane for w in reconstruct(*row,*point)]
    return Job(wid,payload,header+sum(plane,[]),n,4,encode(out))
