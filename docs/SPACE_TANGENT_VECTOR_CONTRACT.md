# Bounded tangent-plane to celestial unit-vector map — V1

Contract fixed before implementation. Genuine new inverse-perspective primitive opcode 80, `SPACE_TANGENT_TO_UNIT_VECTOR_F32_V1`. Given east/north gnomonic plane coordinates and a tangent point, reconstruct a normalized celestial Cartesian direction. This nonlinear inverse is distinct from forward gnomonic projection and from the existing linear matrix transform. It returns vectors, not RA/Dec or pixel WCS.

Primary reference: [ERFA inverse tangent-plane astronomical conventions and equations](https://github.com/liberfa/erfa/blob/master/src/tpsts.c), read 2026-10-04 UTC; its documented vector counterpart is eraTpstv. The accessible spherical equations independently substantiate this vector reconstruction; no ERFA/SOFA code copied and no API/bit-equivalence claim. Also [PROJ central-projection definition](https://proj.org/en/stable/operations/projections/gnom.html). ASTRO uses its own ordered RN32 vector-basis and normalization graph rather than an inverse-trig GPU implementation. ERFA BSD is reference provenance only.

## Strict payload and domain

Exactly `encoding=binary32-hex`, `angle_unit=turn`, `projection=GNOMONIC_TAN`, `axes=EAST_NORTH`, `frame`, `tangent_point`, `plane_coordinates`.

Explicit nonblank common celestial `frame` <=64 characters. `tangent_point=[alpha0,delta0]`, alpha0 in [0,1), delta0 in [-1/4,1/4] turns. `plane_coordinates[N][2]=[xi,eta]`, N1..4096; each component finite binary32 hex in [-16,16], including signed zero and subnormal values. Xi/eta are dimensionless plane coordinates, not finite angular offsets. All numbers are eight-digit hex; reject missing/extra fields, invalid shapes, nonfinite or out-of-domain values. No frame/epoch change, aberration, parallax, proper motion, distortion or hidden units.

## Canonical binary32 graph

Use separate RN32 operations throughout, no FMA, and the established unchanged exact turn-reduction/Taylor-Horner sincos. Let (sa,ca)=sincos(alpha0), (sd,cd)=sincos(delta0).

Construct canonical basis vectors with independent products:
- center = [RN(cd*ca), RN(cd*sa), sd]
- east = [-sa, ca, +0]
- north = [-RN(sd*ca), -RN(sd*sa), cd]

For each component k in order x,y,z:
`u[k] = RN(RN(center[k] + RN(xi*east[k])) + RN(eta*north[k]))`.

Compute square sum from +0, k=0,1,2 in order: `q=RN(q+RN(u[k]*u[k]))`; `r=RN(sqrt(q))`; output `v[k]=RN(u[k]/r)`.

Output N x4 binary32 words `[vx,vy,vz,r]`, where r is the norm of the canonical unnormalized vector. All four words must pass full-output zero-bit validation. The mathematical basis is orthonormal and yields r=sqrt(1+xi^2+eta^2); the stored canonical basis is rounded and the result retains those roundings. Do not silently replace the canonical norm with the ideal formula. The bounded input keeps every intermediate finite and r nonzero. This inverse's square domain is broader than the forward kernel's denominator guard; no automatic forward acceptance or bit-identical roundtrip claim.

Exact analytic golden: tangent point=(0,0), plane=(0,0) => [1,0,0,1]. At zero plane offsets, cardinal tangent points/poles give exact cardinal unit vectors according to quadrant-exact trig. Independent records share the tangent point; partition complete records only.

## Independent science and validation

The CPU byte oracle uses exact Fraction RN32 arithmetic. The separate binary64 scientific reference uses the spherical inverse equations: h=cos(delta0)-eta*sin(delta0), alpha=alpha0+atan2(xi,h), delta=atan2(sin(delta0)+eta*cos(delta0),hypot(xi,h)), then [cos(delta)cos(alpha),cos(delta)sin(alpha),sin(delta)]. It does not reuse the ordered vector-basis implementation. Compare ideal r=sqrt(1+xi^2+eta^2), reconstructed vector and unit norm.

Fixed before tests: vector Euclidean error <=2e-6, absolute unit-length error <=2e-6, relative r error <=2e-6. Independently project the output using binary64 exact tangent basis; maximum absolute recovery error for xi/eta <=2e-4. These are science diagnostic gates, never bit tolerances or universal physical astrometric precision guarantees. Require finite outputs, positive r and front-side dot product with the ideal tangent center.

Probe exact center/cardinal axes, both poles, RA near wrap, signed zero/subnormal plane components, ±16 edges/corners, tiny offsets, dense grids, cases whose recovered direction crosses a celestial pole, maximum4096 records, random/held-out centers and offsets, invalid tags/frame/shapes/NaN/Inf/bounds. Full inherited GPU/software regression and partition checks, unchanged previous MathSpecs/kernels/snapshot, real shader and every-output-field bit faults, native packet guards, fresh COLD-ZERO, worker/miner and verified source archive required. QUICK total <=60s/MathSpec. No clock/governor changes, concurrent GPU work, release speed/SoC claim without paired evidence, AI or new RT route.
