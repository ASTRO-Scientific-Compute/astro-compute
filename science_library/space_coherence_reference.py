"""Independent Fraction/RN32 paired complex products and coherence."""
from fractions import Fraction
from . import f32 as f
from .reference import Job, MAGIC, encode
from .float_reference import rows
WID='SPACE_CROSS_SPECTRAL_COHERENCE_F32_V1'
TAGS=dict(encoding='binary32-hex',cross_convention='CONJ_X_TIMES_Y',replicate_contract='MATCHED_ORDERED_SEGMENTS',power_normalization='MEAN_SUPPLIED_BIN_PRODUCTS')
LABELS=('spectrum_unit_x','spectrum_unit_y','frequency_grid_id')


def prepare_space_coherence(wid,payload):
    if set(payload)!=set(TAGS)|set(LABELS)|{'bins'} or any(payload.get(k)!=v for k,v in TAGS.items()):
        raise ValueError('exact coherence fields and explicit matched complex spectrum contract required')
    for key in LABELS:
        label=payload[key]
        if not isinstance(label,str) or not label.strip() or len(label)>64:raise ValueError('bounded explicit spectrum/grid labels required')
    bins=payload['bins']
    if not isinstance(bins,list) or not 1<=len(bins)<=256:raise ValueError('coherence bin count')
    bins=[rows(b,4,64) for b in bins];n=len(bins[0])
    if n<2 or any(len(b)!=n for b in bins):raise ValueError('common replicate count2..64 required')
    lo,hi=Fraction(1,1<<28),Fraction(1<<16)
    output=[];a=[]
    for records in bins:
        totals=[0]*4
        for xr,xi,yr,yi in records:
            for word in (xr,xi,yr,yi):
                value=abs(f.rational(word))
                if value and not lo<=value<=hi:raise ValueError('coherence component outside bounded scale')
            a.extend((xr,xi,yr,yi))
            terms=[f.add(f.mul(xr,xr),f.mul(xi,xi)),f.add(f.mul(yr,yr),f.mul(yi,yi)),
                   f.add(f.mul(xr,yr),f.mul(xi,yi)),f.sub(f.mul(xr,yi),f.mul(xi,yr))]
            totals=[f.add(s,t) for s,t in zip(totals,terms)]
        px,py,re,im=[f.div(s,f.rounded(n)) for s in totals]
        status=int(px==0)|(int(py==0)<<1)
        coherence=0 if status else f.div(f.add(f.mul(re,re),f.mul(im,im)),f.mul(px,py))
        output.extend((status,px,py,re,im,coherence))
    records=len(bins);end=16+len(a)
    header=[MAGIC,1,78,records,n,0,0,0,0,0,0,end,end,6,0,0]
    return Job(wid,payload,header+a,records,6,encode(output))
