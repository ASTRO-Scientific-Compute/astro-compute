# Bounded parabolic Barker state — V1

Specification fixed before implementation, v1.17.39. Genuine opcode77, `SPACE_PARABOLIC_BARKER_STATE_F32_V1`: the nonperiodic cubic Barker equation and zero-energy two-body state for exactly e=1. This fills a conic family excluded from the elliptic and hyperbolic contracts; it does not rename them or claim universal near-parabolic coverage.

## Input/output

The payload contains exactly the following tags plus distance_unit,time_unit,mu,elements; unknown or missing fields are rejected. Payload tags: `encoding=binary32-hex`, `model=PARABOLIC_E1`, `anomaly_unit=barker-dimensionless`, `frame=PERIFOCAL`; explicit nonblank distance/time unit labels<=64characters. Shared finite binary32-hex mu, elements[N,2]=[q,M],1<=N<=1024. q is periapsis distance (not semimajor axis),q/mu in[2^-32,2^32],M in[-16,16]. mu has distance^3/time^2 units. M is the supplied Barker time parameter, not an angle or periodic phase: M=(t-T)*sqrt(mu/(2q^3)). No time/calendar/unit conversion or modulo. Eccentricity is fixed exactly1 by the model and cannot be overridden; an `eccentricity` field is rejected to prevent a misleading alternate model. Finite eight-digit hex only, explicit boundaries, canonical arithmetic+0; input signed zero allowed for M.

Output N x8 words `[D,r,x,y,z,vx,vy,vz]`, D dimensionless parabolic anomaly=tan(true_anomaly/2); x points toward periapsis, y along velocity there, z=vz=+0. Units are distance and distance/time. Full GPU output must match an independent Fraction/RN32 oracle with0 differing bits.

## Exact canonical graph

Each elementary add,subtract,multiply,divide,sqrt uses software RN32 (nearest,ties-to-even), canonical zero and no FMA. Reject overflowing/out-of-contract input before execution.

M=0 gives D=0. Otherwise target=abs(M),lo=0,hi=4. Exactly32 iterations: mid=RN32(RN32(lo+hi)*1/2); square=RN32(mid*mid); cube=RN32(square*mid); residual=RN32(RN32(mid+RN32(cube/3))-target). If residual<0 set lo=mid, else hi=mid. D_abs=RN32(RN32(lo+hi)*1/2); restore sign of M. No convergence-dependent iteration count. Exact root equation D+D^3/3=M has derivative1+D²>=1; upper bracket4+64/3>16. The canonical graph approximates that real root; extremely small M can meet the fixed-iteration floor, so no relative small-anomaly precision claim is made.

Compute square=RN32(D*D),den=RN32(1+square),r=RN32(q*den),x=RN32(q*RN32(1-square)),y=RN32(RN32(2*q)*D),scale=RN32(sqrt(RN32(RN32(2*mu)/q))/den),vx=-RN32(scale*D),vy=scale,z=vz=0.

Physical derivation: r=q(1+D²),cos(nu)=(1-D²)/(1+D²),sin(nu)=2D/(1+D²); differentiating Barker's t(D) gives velocity above. Exact specific energy is0 and angular-momentum magnitude sqrt(2muq). Position is not a time-stepped copy of an existing state.

## Independent diagnostic gates fixed before tests

Binary64 closed-form root D=2*sinh(asinh(3M/2)/3), derived from the hyperbolic triple-angle identity, independently of GPU bisection; libm and direct state formulas. Absolute D error<=2e-6, position/radius error divided byq<=2e-5, velocity error divided bysqrt(mu/q)<=2e-5, root residual divided bymax(1,absM)<=5e-6. Absolute specific-energy error normalized bymu/q<=2e-5 (never divide by the exact zero energy). Relative angular-momentum error<=2e-5. These diagnostics do not relax the0-bit requirement.

Separate central-force RK4 from periapsis in both time directions: dimensionless q=mu=1, t=sqrt(2)*M,2048 substeps per Barker step1/2; independent integrated position/q and velocity/sqrt(mu/q) errors<=5e-5. Golden exact periapsis q=2,mu=1,M=0 yields[0,2,2,0,0,0,1,0]. Include ±16, sign symmetry, nonlinear anomaly interior, small/subnormal/signedzero M, allq/mu corners, maximum1024records, invalid model/eccentricity/units/shapes/nonfinite/bounds and all output-word bit corruption.

Release requires golden/random/held-out and12 edge full GPU checks, split dispatches, shader-bit and actual-output faults, native guards, fresh COLD-ZERO, worker/miner entrypoint and complete source package. Full QUICK<=60seconds/MathSpec; no release performance/SoC claims without paired A/B. One GPU job at a time, no clock/governor changes.

## Primary sources and scope

- [NASA/JPL PARTOF](https://naif.jpl.nasa.gov/pub/naif/toolkit_docs/FORTRAN/spicelib/partof.html): Barker cubic equation, anomaly and periapsis-distance time relation.
- [NASA/JPL conics_c](https://naif.jpl.nasa.gov/pub/naif/toolkit_docs/C/cspice/conics_c.html): unperturbed conic state interpretation.
- [NIST DLMF4.35](https://dlmf.nist.gov/4.35): sinh triple-angle identity underlying the independent closed-form root.

Browsed2026-10-03 UTC; original code, no external implementation copied. No e unequal1, unrestricted anomalies, continuous near-parabolic or universal-variable solver, automatic epoch/orientation conversion, perturbations, observer/relativity/light-time corrections or physical ephemeris claim. No new AI/RT execution path. SPACE remains open.
