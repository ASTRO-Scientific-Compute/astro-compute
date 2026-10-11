"""Exact rational ray/triangle oracle. GPU independently uses signed 256-bit ints."""
from fractions import Fraction
from . import f32 as f
from .reference import Job,MAGIC,encode,integer
from .triangle_offsets import OFFSETS

MISS=0x7149f2ca  # RN32(1e30), historical miss sentinel
TMIN=0x38d1b717  # RN32(0.0001)
DETEPS=0x322bcc77  # RN32(1e-8)


def vec(value):
    if not isinstance(value,list) or len(value)!=3:raise ValueError('three binary32 components required')
    words=[f.parse(v) for v in value]
    for word in words:
        a=abs(f.rational(word))
        if a and not Fraction(1,65536)<=a<=65536:raise ValueError('component outside explicit zero or [2^-16,2^16] magnitude domain; no quantization')
    return words


def normalize(words):
    length=f.sqrt(f.add(f.add(f.mul(words[0],words[0]),f.mul(words[1],words[1])),f.mul(words[2],words[2])))
    if not length:raise ValueError('zero ray direction')
    return [f.div(x,length) for x in words]


def cross(a,b):return [a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]]
def dot(a,b):return sum(x*y for x,y in zip(a,b))
def sub(a,b):return [x-y for x,y in zip(a,b)]


def hit(origin,direction,triangle):
    a,b,c=triangle;e1=sub(b,a);e2=sub(c,a);p=cross(direction,e2);det=dot(e1,p)
    if abs(det)<f.rational(DETEPS):return MISS
    s=sub(origin,a);u=dot(s,p)/det
    if not 0<=u<=1:return MISS
    q=cross(s,e1);v=dot(direction,q)/det
    if v<0 or u+v>1:return MISS
    distance=dot(e2,q)/det
    if distance<=0:return MISS
    result=f.rounded(distance)
    return result if TMIN<result<MISS else MISS


def prepare_triangle(wid,op,payload):
    if payload.get('encoding')!='binary32-hex':raise ValueError('explicit binary32-hex required')
    triangles=payload['triangles'];rays=payload['rays']
    if not isinstance(triangles,list) or not 1<=len(triangles)<=4096:raise ValueError('1..4096 triangles required')
    if not isinstance(rays,list) or not 1<=len(rays)<=4096:raise ValueError('1..4096 rays required')
    parsed=[]
    for t in triangles:
        if not isinstance(t,list) or len(t)!=3:raise ValueError('three vertices required')
        parsed.append([vec(v) for v in t])
    origins=[];directions=[];raywords=[]
    for ray in rays:
        if not isinstance(ray,dict):raise ValueError('ray object required')
        origin=vec(ray['origin']);direction=vec(ray['direction'])
        normalized=[f.rational(x) for x in normalize(direction)]
        if any(abs(x)>2 or (x*(1<<56)).denominator!=1 for x in normalized):raise ValueError('normalized direction exceeds exact arithmetic domain')
        origins.append([f.rational(x) for x in origin]);directions.append(normalized)
        raywords+=origin+direction
    frames=payload.get('frames') if op==38 else [0]
    if not isinstance(frames,list) or not 1<=len(frames)<=8:raise ValueError('1..8 explicit frame numbers required')
    frames=[integer(x,0,0xffffffff,'frame') for x in frames]
    if len(frames)*len(rays)*len(triangles)>1048576:raise ValueError('ray/triangle/frame product exceeds 1048576; split rays')
    outputs=[];geometry=[]
    for frame in frames:
        scene=[]
        for index,tri in enumerate(parsed):
            changed=[]
            for vertex in tri:
                words=list(vertex)
                if op==38:words[2]=f.add(words[2],OFFSETS[(index*17+frame*13)&1023])
                values=[f.rational(x) for x in words]
                if any(abs(x)>65536 or (x*(1<<56)).denominator!=1 for x in values):raise ValueError('mutated geometry exceeds exact arithmetic domain')
                geometry+=words;changed.append(values)
            scene.append(changed)
        for origin,direction in zip(origins,directions):outputs.append(min(hit(origin,direction,t) for t in scene))
    a=raywords;b=[v for t in parsed for vertex in t for v in vertex];c=OFFSETS+frames if op==38 else []
    n=len(rays);m=len(triangles);records=n*len(frames)
    header=[MAGIC,1,op,records,n,m,len(frames),0,0,0,0,16+len(a),16+len(a)+len(b),1,0,0]
    return Job(wid,payload,header+a+b+c,records,1,encode(outputs),encode(geometry) if op==38 else None)
