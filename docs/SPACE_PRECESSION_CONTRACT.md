# IAU2006 bias/precession in a declared binary32 graph — opcode74

Primary mathematical source: IERS Conventions2010 chapter5, sections5.3.1,5.4.5,5.6.4, equations(5.2),(5.40): https://iers-conventions.obspm.fr/content/chapter5/icc5.pdf . Reference numerical facts: ERFA maintained test suite `t_pmat06`, `t_pfw06`, https://raw.githubusercontent.com/liberfa/erfa/master/src/t_erfa_c.c (access2026-10-03; SHA2568a92d0099c48df31ca566bea881c19497dc295dba58dba7136cc2f8443c31f15). Only numerical test facts and published mathematical coefficients are used; no external implementation code is copied. This original ASTRO numerical realization is not a SOFA/ERFA implementation or a claim of their double-precision accuracy.

Purpose: rotate GCRS Cartesian vectors to the mean equator/equinox of a supplied date, including frame bias and IAU2006 precession. Distinct from applying an arbitrary supplied matrix: the physical epoch-dependent matrix is generated here. No nutation, Earth rotation, polar motion, aberration, parallax, proper-motion propagation, refraction or observer corrections. It is not ITRS, CIRS, true-of-date or apparent place. No RT pruning; AI relevance POSSIBLE, AI_BACKEND_UNAVAILABLE.

## Input/output

`encoding=binary32-hex`, `time_scale=TT`, `input_frame=GCRS`, `output_frame=MEAN_EQUATOR_EQUINOX_OF_DATE_IAU2006` are required exact strings. `tt_centuries` is a list of N finite binary32 values, each in[-1,+1]; `vectors` is N×3 finite binary32 values; N1..4096. T=(JD_TT-2451545)/36525. Each input vector is already in GCRS at the supplied epoch. Norm/units are preserved up to declared rounding; normalization is not implicit. All executed intermediates must remain finite, otherwise reject before GPU dispatch.

The source adapter takes two decimal-string JD parts, validates TT and both frames, forms their sum and T using exact rationals, then rounds T ONCE to binary32. It records original parts, exact T numerator/denominator, rounded bits and quantization error. No UTC/TDB/TAI conversion is inferred. The admitted exact source epoch also lies in[-1,+1] centuries: a just-outside epoch cannot round into range. Decimal fields are bounded in length to128 characters, syntactically decimal and finite; absolute value<=1e9 and decimal exponent magnitude<=32.

Output is N×16 binary32 words: `[gamma, delta_phi, psi, epsilon, R00..R22, transformed_xyz]`, angles in radians; delta_phi=phi_bar-epsilon_A, NOT phi_bar. Row-major matrix, column-vector convention. Complete independent record is partition unit. Packet header `[MAGIC,1,74,N,4,0,0,0,0,0,0,16+4*N,16+4*N,16,0,0]`, followed by record-major `[T,x,y,z]`.

## Frozen arithmetic graph

Every +,-,*,/ is RN32 nearest ties-even, gradual underflow and +0, no FMA/reassociation. Dot starts +0, increasing inner index. Coefficients are factual decimal arcseconds converted individually with exact rational `pi50/648000`, rounded once to binary32; pi50=3.14159265358979323846264338327950288419716939937510. Coefficient vectors ascending powers:

- gamma: [-.052928,10.556378,.4932044,-.00031238,-.000002788,.0000000260]
- phi: [84381.412819,-46.811016,.0511268,.00053289,-.000000440,-.0000000176]
- psi: [-.041775,5038.481484,1.5584175,-.00018522,-.000026452,-.0000000148]
- epsilon: [84381.406,-46.836769,-.0001831,.00200340,-.000000576,-.0000000434]

The delta_phi vector is obtained by subtracting the exact decimal phi and epsilon coefficients BEFORE conversion/rounding. Each angle uses descending Horner:acc=c5;acc=RN(cj+RN(T*acc)),j4..0. No large rounded phi-epsilon subtraction.

For |a|<=0.5 radians, sine and cosine are Taylor-Horner in z=RN(a*a), with individually RN32 coefficients (-1)^k/(2k+1)! for k0..6 and (-1)^k/(2k)! for k0..7. Sine is RN(a*polynomial). No phase reduction or host libm enters the exact graph. All generated angles lie in this interval for the admitted epochs.

In exact real arithmetic the IERS rotation is X(-epsilon) Z(-psi) X(phi) Z(gamma), with passive X(a)=[[1,0,0],[0,c,s],[0,-s,c]], Z(a)=[[c,s,0],[-s,c,0],[0,0,1]]. Original ASTRO stable rearrangement: R=M X(delta_phi) Z(gamma), M=X(-epsilon)Z(-psi)X(epsilon). Let se,ce=sin/cos(epsilon),sp=sin(psi),h=sin(RN(psi/2)),d=RN(2*RN(h*h)). Form:

M=[[RN(1-d), -RN(sp*ce), -RN(sp*se)],
   [RN(sp*ce), RN(1-RN(RN(ce*ce)*d)), -RN(RN(ce*se)*d)],
   [RN(sp*se), -RN(RN(ce*se)*d), RN(1-RN(RN(se*se)*d))]].

This avoids cancellation of the large obliquity rotations near J2000. Build X(delta_phi),Z(gamma) with the same trigonometric graph; compute U=M*X, R=U*Z by ordered three-term dots, then output R*v by ordered dots. Copy the four Horner angles unchanged to output. No reorthogonalization.

## Evidence and limits

Independent CPU Fraction oracle versus integer-significand GPU: ALL bits of all16 outputs, warmup/final, held-out, candidate and partition outputs. Factual ERFA test anchors validate the independent float64 implementation; its direct four-rotation/libm evaluation then checks the different stable GPU operation graph. Matrix maximum entry error target2e-7, orthogonality/determinant3e-7; vector error<=5e-7*max(1,||v||), angular error target1e-7rad for controlled vectors with norm>1e-30; smaller/zero vectors retain complete byte and scaled absolute-error checks, with no angular verdict. These are independent scientific diagnostic limits on tested vectors, not GPU byte tolerance, an all-input bound, or a microarcsecond astrometry guarantee. Binary32 epoch quantization is separately exposed. Tests cover zero/bias epoch, ±one century, signed zero, subnormal data, scaled/polar/axis vectors, maximum batch, malformed frames/time and output faults.

Source-job-summary provenance binds exact TT conversion and complete actual GPU outputs. Frame errors must reject, not silently rotate under an assumed scale. Fresh COLD-ZERO; full QUICK<=60s. No release speedup/SoC efficiency claims without paired A/B evidence.
