# Bounded hyperbolic Kepler state — V1

Specification fixed before implementation, v1.17.38. Genuine opcode76, `SPACE_HYPERBOLIC_KEPLER_STATE_F32_V1`: nonperiodic hyperbolic Kepler root and positive-energy two-body state. It is not the periodic elliptic solver under another name. No existing workload is replaced.

## Input/output

Finite binary32-hex payload, with explicit `encoding=binary32-hex`, `anomaly_unit=hyperbolic-radian`, `a_semantics=POSITIVE_HYPERBOLIC_MAGNITUDE`, `frame=PERIFOCAL`, nonblank distance/time labels<=64 characters. Shared `mu`, elements[N,3]=[a,e,M],1<=N<=1024. a is the positive magnitude of the conventional negative semimajor axis, NOT its signed value. Both a and mu in[2^-32,2^32], e in[5/4,4], M in[-16,16]. mu units distance^3/time^2. No phase modulo or implicit unit/epoch conversion. Reject nonfinite, out-of-bounds, missing or wrong tags. Signed zero is accepted and arithmetic zero is canonical+0.

Output N x8 words `[H,r,x,y,z,vx,vy,vz]`, H dimensionless hyperbolic anomaly (customarily radians); x points toward periapsis, y in the direction of motion there, z=vz=+0. Radius/position in distance units; velocity in distance/time. Full GPU output must equal the independent Fraction/RN32 CPU reference with0 differing bits.

## Canonical polynomial and implicit solve

Every elementary +,-,*,/,sqrt is software RN32, round-to-nearest ties-to-even, canonical zero, no FMA. Coefficients are RN32 of exact positive reciprocal factorials, not host float factorial divisions.

For argument x with|x|<=4, q=RN32(x*x):
- sinh: coefficient c_k=RN32(1/(2k+1)!), k0..10. Initialize p=c_10; for k9..0, p=RN32(c_k+RN32(q*p)); return RN32(x*p). Degree21.
- cosh: coefficient d_k=RN32(1/(2k)!), k0..11. Initialize p=d_11; for k10..0, p=RN32(d_k+RN32(q*p)); return p. Degree22.

M=0 has H=+0. Otherwise let target=abs(M), lo=0,hi=4. Exactly32 iterations: mid=RN32(RN32(lo+hi)*1/2); residual=RN32(RN32(RN32(e*sinh_poly(mid))-mid)-target). If residual<0 set lo=mid, otherwise hi=mid. Finish u=RN32(RN32(lo+hi)*1/2); H=-u for M<0, otherwise u. No adaptive floating stop condition.

The exact root satisfies e*sinh(H)-H=M. On nonnegative H, derivative=e*cosh(H)-1>=e-1>=1/4. At the upper bracket, (5/4)*sinh(4)-4>16. Thus the bounded input has one unique root and a finite safe bracket. Finite polynomial/binary32 residual differences are diagnosed independently, not claimed mathematically exact. Extremely small M can quantize to the fixed-iteration floor; the absolute diagnostic limit covers this explicitly, with no relative-anomaly precision claim.

## State graph

Compute s=sinh_poly(H), c=cosh_poly(H), beta=sqrt(RN32(e*e)-1), d=RN32(e*c)-1; r=RN32(a*d); scale=RN32(sqrt(RN32(mu/a))/d).

x=RN32(a*RN32(e-c)); y=RN32(RN32(a*beta)*s); vx=-RN32(scale*s); vy=RN32(RN32(scale*beta)*c). z=vz=0. All subtractions also RN32. The exact physical reference has energy=mu/(2a)>0 and angular-momentum magnitude=sqrt(mu*a*(e^2-1)). This follows by differentiating x=a(e-coshH), y=a*sqrt(e²-1)*sinhH with dH/dt=sqrt(mu/a³)/(e*coshH-1).

## Independent gates and validation

Thresholds fixed before numerical tests: independent binary64 safeguarded Newton using libm sinh/cosh; absolute H error<=2e-6; radius/position error divided by a<=2e-4; velocity error divided by sqrt(mu/a)<=2e-5; relative specific-energy and angular-momentum error<=2e-4. Separately polynomial error/ max(1,abs(libm_value))<=1e-6 on[-4,4]. Test the implicit residual independently, scaled by max(1,abs(M)),<=5e-6. These are scientific diagnostic limits; output bit tolerance stays exactly zero.

Separate central-force RK4 integration from periapsis forward and backward in dimensionless time t=M,2048 substeps per1/2 time unit; comparison position/a<=2e-4,velocity/sqrt(mu/a)<=5e-5. Include analytic periapsis anchor e=5/4,a=mu=1 -> H0,r=x=1/4,y=vx=0,vy=3; sign symmetry, M±16, e endpoints, signedzero/subnormal M, all a/mu scale corners and1024 records. Reject elliptic/parabolic and near-parabolic e, wrong anomaly units or signed a, overflow/nonfinite inputs. Golden/random/held-out/edge complete GPU outputs and true split dispatches, injected shader and actual output bits, native guards, fresh COLD-ZERO, worker/miner and source package required.

Full QUICK<=60seconds/MathSpec; no release speedup or SoC-efficiency claim without paired A/B evidence. GPU jobs serial; no governor/clock writes.

## Sources and limits

- [NASA/JPL HYPTOF](https://naif.jpl.nasa.gov/pub/naif/toolkit_docs/FORTRAN/spicelib/hyptof.html): hyperbolic Kepler equation and time relation using conventional signed negative semimajor axis.
- [NASA/JPL conics_c](https://naif.jpl.nasa.gov/pub/naif/toolkit_docs/C/cspice/conics_c.html): unperturbed conic state interpretation.
- [NIST DLMF4.33](https://dlmf.nist.gov/4.33): hyperbolic Maclaurin series.
- [NIST DLMF4.35](https://dlmf.nist.gov/4.35): hyperbolic identities.

Sources browsed2026-10-03; original implementation, no external source code copied. No e near1, parabolic/universal-variable solver, unrestricted anomaly or range claim, automatic time/orientation workflow, perturbations, observer/relativistic/light-time effects, or physical ephemeris claim. No new AI/RT execution path.
