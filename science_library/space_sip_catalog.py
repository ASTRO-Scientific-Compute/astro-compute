SOURCES={'sip_forward':('Shupe and Hook SIP distortion convention1.0 equations1–3','https://fits.gsfc.nasa.gov/registry/sip/SIP_distortion_v1_0.pdf','Mathematical convention reference only; original bounded RN32 implementation, no external code copied')}
DEFINITIONS=[('SPACE_SIP_FORWARD_F32_V1',81,'sip_forward','Bounded SIP forward pixel distortion',
 'Evaluate supplied degree2–5 pixel distortion polynomials before a CD/projection stage.',
 'Repeated RN32 powers up/vp; degree-ascending then p-ascending sums of RN32(RN32(coef*up[p])*vp[q]);U=RN32(u+A),V=RN32(v+B). Every rounded step explicit.',
 'Finite binary32-hex offsets[N,2] in[-1024,1024],N1..4096; independent integer a_order/b_order2..5; complete degree-ascending p-ascending coefficient arrays,abs(coef)<=2^(8-10*degree); explicit reference-relative pixel units,model id and exact fields.',
 'N x4 binary32[U,V,A_correction,B_correction],all in pixel offset units;full zero-bit output validation;no coefficient fitting,CD stage,inverse or invertibility/calibration promise.',
 'complete independent offset rows with shared supplied A/B coefficient arrays','POSSIBLE')]
