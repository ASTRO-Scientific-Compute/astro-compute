"""Original stable bias/precession graph with independent Fraction RN32 oracle."""
from fractions import Fraction
from math import factorial
from . import f32 as f
from .reference import Job,MAGIC,encode
from .float_reference import values,rows
WID='SPACE_IAU2006_BIAS_PRECESSION_F32_V1'
OUTPUT_FRAME='MEAN_EQUATOR_EQUINOX_OF_DATE_IAU2006'
DECIMAL={
 'gamma':('-.052928','10.556378','.4932044','-.00031238','-.000002788','.0000000260'),
 'phi':('84381.412819','-46.811016','.0511268','.00053289','-.000000440','-.0000000176'),
 'psi':('-.041775','5038.481484','1.5584175','-.00018522','-.000026452','-.0000000148'),
 'epsilon':('84381.406','-46.836769','-.0001831','.00200340','-.000000576','-.0000000434')}
ARCSEC=Fraction('3.14159265358979323846264338327950288419716939937510')/648000
COEFF={name:tuple(f.rounded(Fraction(v)*ARCSEC) for v in coeff) for name,coeff in DECIMAL.items() if name!='phi'}
COEFF['delta_phi']=tuple(f.rounded((Fraction(a)-Fraction(b))*ARCSEC) for a,b in zip(DECIMAL['phi'],DECIMAL['epsilon']))
SIN=tuple(f.rounded(Fraction((-1)**k,factorial(2*k+1))) for k in range(7))
COS=tuple(f.rounded(Fraction((-1)**k,factorial(2*k))) for k in range(8))


def horner(t,coeff):
    acc=coeff[-1]
    for c in reversed(coeff[:-1]):acc=f.add(c,f.mul(t,acc))
    return acc


def trig(a):
    if abs(f.rational(a))>Fraction(1,2):raise ValueError('small-angle trigonometric range')
    z=f.mul(a,a);return f.mul(a,horner(z,SIN)),horner(z,COS)


def mm(a,b):return [[f.dot(row,col) for col in zip(*b)] for row in a]


def precess(t,vector):
    gamma,delta,psi,eps=[horner(t,COEFF[name]) for name in ('gamma','delta_phi','psi','epsilon')]
    se,ce=trig(eps);sp,_=trig(psi);h,_=trig(f.mul(psi,f.HALF));d=f.mul(f.TWO,f.mul(h,h))
    a=f.mul(sp,ce);b=f.mul(sp,se);c=f.neg(f.mul(f.mul(ce,se),d))
    M=[[f.sub(f.ONE,d),f.neg(a),f.neg(b)],[a,f.sub(f.ONE,f.mul(f.mul(ce,ce),d)),c],[b,c,f.sub(f.ONE,f.mul(f.mul(se,se),d))]]
    sd,cd=trig(delta);sg,cg=trig(gamma)
    X=[[f.ONE,0,0],[0,cd,sd],[0,f.neg(sd),cd]];Z=[[cg,sg,0],[f.neg(sg),cg,0],[0,0,f.ONE]]
    R=mm(mm(M,X),Z);return [gamma,delta,psi,eps]+sum(R,[])+[f.dot(row,vector) for row in R]


def prepare_space_precession(wid,payload):
    if payload.get('encoding')!='binary32-hex' or payload.get('time_scale')!='TT' or payload.get('input_frame')!='GCRS' or payload.get('output_frame')!=OUTPUT_FRAME:raise ValueError('explicit binary32 TT/GCRS/mean-of-date contract required')
    t=values(payload['tt_centuries'],4096);v=rows(payload['vectors'],3,4096)
    if len(t)!=len(v):raise ValueError('matching epoch/vector records required')
    if any(abs(f.rational(x))>1 for x in t):raise ValueError('TT centuries outside[-1,1]')
    flat=[];out=[]
    for epoch,vector in zip(t,v):flat+=[epoch]+vector;out+=precess(epoch,vector)
    N=len(t);header=[MAGIC,1,74,N,4,0,0,0,0,0,0,16+4*N,16+4*N,16,0,0]
    return Job(wid,payload,header+flat,N,16,encode(out))
