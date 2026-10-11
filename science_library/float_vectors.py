"""Hand-derived scientific vectors, before GPU implementation."""
import random
from .f32 import hex32


def floats(x):
    return [floats(v) for v in x] if isinstance(x,list) else hex32(x)


def job(**kw):
    return dict(encoding='binary32-hex',**{k:floats(v) for k,v in kw.items()})


def bits(xs):
    return [int(hex32(x),16) for x in xs]


GOLDEN = {
    14:(job(x=[1,2,3],kernel=[1,-1]),bits([1,1,1,-3])),
    15:(job(x=[1,2],y=[3,4]),bits([4,11,6])),
    16:(job(x=[1,0],y=[1,0]),[1,0,0,0x3f800000,1,0]),
    17:(job(signals=[[[1,0],[0,0],[0,0],[0,0]]]),bits([1,0]*4)),
    18:(job(samples=[[[0,1,1],[1,3,1],[2,5,1]],[[1,2,0],[1,4,0],[1,6,0]]]),[0]+bits([1,2])+[1,0,0]),
    19:(job(vectors=[[1,2,3]],matrix=[[0,-1,0],[1,0,0],[0,0,1]]),bits([-2,1,3])),
    20:(job(curves=[[[0,0],[1,1],[2,2]],[[2,2],[1,1],[0,0]]]),bits([2,-2])),
    21:(job(bodies=[[0,0,0,16],[1,1,1,8]],epsilon_squared=1),bits([1,1,1,-2,-2,-2])),
    22:(job(states=[[1,2,3,4,5,6,2,-2,0]],dt=.5),bits([3.5,4,6,5,4,6])),
    23:(job(images=[[[1,1],[1,1]],[[0,0],[0,0]]]),[0]+bits([.5,.5])+[1,0,0]),
    24:(job(signals=[[1,1,1,1]],fs=1),bits([4,0,0,0])),
}

GOLDEN.update({
    25:({'sequences':['AAAAA','ACGTACGT',''],'kmers':['AA','AC','CG']},[4,0,0,0,2,2,0,0,0]),
    26:(job(pairs=[[1,0,0,0,0,0]],sigma=1,epsilon=1),bits([0,24,0,0])),
    27:(job(field=[[4]*3 for _ in range(3)],**{'lambda':.25}),bits([4]*9)),
    28:(job(xp=[0,1,2],fp=[1,3,1],queries=[-1,0,.5,1,1.5,2,3]),bits([1,1,2,3,2,1,1])),
    29:(job(left=[[1,2],[3,4]],right=[[5,6],[7,8]]),bits([19,22,43,50])),
})

def fixture(op,seed=271828,scale=1):
    r=random.Random(seed);count=5*scale
    def seq(n):return [r.randint(-127,127)/16 for _ in range(n)]
    if op in (14,15,16):return job(**dict(x=seq(61*scale),**{'kernel' if op==14 else 'y':seq(17)}))
    if op==17:return job(signals=[[[x,y] for x,y in zip(seq(32),seq(32))] for _ in range(count)])
    if op==18:return job(samples=[[[x,3*x+1+r.randint(-4,4)/16,1+r.randrange(4)] for x in seq(31)] for _ in range(count)])
    if op==19:return job(vectors=[seq(3) for _ in range(31*scale)],matrix=[seq(3) for _ in range(3)])
    if op==20:return job(curves=[[[j/4,v] for j,v in enumerate(seq(61))] for _ in range(count)])
    if op==21:return job(bodies=[seq(3)+[1+r.randrange(4)/4] for _ in range(11*scale)],epsilon_squared=.25)
    if op==22:return job(states=[seq(9) for _ in range(31*scale)],dt=.0625)
    if op==23:return job(images=[[[r.randrange(128)/16 for x in range(7)] for y in range(5)] for _ in range(count)])
    if op==24:return job(signals=[seq(32) for _ in range(count)],fs=4)
    if op==25:return dict(sequences=[''.join(r.choice('ACGT') for _ in range(97)) for _ in range(count)],kmers=[''.join(r.choice('ACGT') for _ in range(3)) for _ in range(13)])
    if op==26:return job(pairs=[seq(3)+[20+x for x in seq(3)] for _ in range(31*scale)],sigma=2,epsilon=.5)
    if op==27:return job(field=[seq(17) for _ in range(11*scale)],**{'lambda':.125})
    if op==28:return job(xp=[j/2 for j in range(31)],fp=seq(31),queries=[r.randrange(-8,136)/8 for _ in range(31*scale)])
    if op==29:return job(left=[seq(13) for _ in range(11*scale)],right=[seq(17) for _ in range(13)])
    raise ValueError(op)
