# Bounded celestial gnomonic tangent-plane projection — V1

Contract fixed before implementation. Genuine new primitive opcode 79, `SPACE_GNOMONIC_PROJECT_F32_V1`. It projects spherical sky directions onto a specified tangent plane; this perspective division is not supplied by the existing spherical/Cartesian conversion or linear Cartesian matrix transform.

Primary sources consulted 2026-10-03 UTC: [ERFA tangent-plane routine and astronomical conventions](https://raw.githubusercontent.com/liberfa/erfa/master/src/tpxes.c), [PROJ gnomonic definition](https://proj.org/en/stable/operations/projections/gnom.html), and [Snyder USGS Professional Paper 1395](https://pubs.usgs.gov/publication/pp1395). USGS PDF fetch returned 403; formula/convention verification uses the accessible ERFA primary source. Original ASTRO bounded RN32 graph; no ERFA/SOFA/PROJ implementation copied, no claim of identical API, statuses or bits. ERFA BSD license is reference provenance only. ERFA points to Calabretta & Greisen 2002 and Green 1987 for the astronomical derivation.

## Exact payload and domain

Exactly `encoding=binary32-hex`, `angle_unit=turn`, `projection=GNOMONIC_TAN`, `axes=EAST_NORTH`, `frame`, `tangent_point`, `directions`.

`frame` is an explicit nonblank string <=64 characters asserting that the tangent point and every direction share the same celestial coordinate frame. No epoch, proper motion, aberration, precession, observer or time conversion is inferred. `tangent_point=[alpha0,delta0]`; `directions[N][2]=[alpha,delta]`, N1..4096. Every angle is a finite eight-digit binary32 hex word; alpha,alpha0 in [0,1), delta,delta0 in [-1/4,1/4] turns. Negative zero is allowed and arithmetic canonicalizes zero. Unknown/missing fields and other domains are rejected.

The output is a dimensionless unit-sphere tangent-plane coordinate, not a finite angular displacement or a pixel coordinate. xi is east and eta north. At the tangent point their differential scale corresponds to radians. No CD/PC pixel transform, FITS header parser, lens distortion or full WCS claim.

## Canonical ordered binary32 graph

Every operation is separate RN32, no FMA. Use existing deterministic `sincos` in turns with exact fractional-turn quadrant reduction and frozen RN32 Taylor/Horner coefficients, unchanged. Compute delta_alpha=RN(alpha-alpha0); pass the signed result directly to sincos without an additional rounded wrap.

Let (s0,c0)=sincos(delta0), (s,c)=sincos(delta), (sd,cd)=sincos(delta_alpha).

- u=RN(c*c0); v=RN(u*cd); d=RN(RN(s*s0)+v).
- If d < 1/16 (exact binary32 0x3d800000), status=1 and xi=eta=+0. Preserve d even when invalid. This deliberately excludes the far hemisphere and a bounded region near the tangent-plane horizon. Never clamp the denominator or return an invented valid projection.
- Otherwise status=0, xi=RN(RN(c*sd)/d), eta=RN(RN(RN(s*c0)-RN(RN(c*s0)*cd))/d).

Output N x4 uint32 words `[status,bits(xi),bits(eta),bits(d)]`. All words have zero bit tolerance, including invalid sentinels and denominator. The exact accepted/rejected decision is the canonical rounded d, not an unrounded ideal trigonometric comparison. Partition only complete independent direction rows with the shared tangent point.

Exact analytic golden: tangent_point=(0,0), direction=(0,0) => [status0,xi0,eta0,d1]. Direction=(1/4,0) has d0 and status1; direction=(1/2,0) has d-1 and status1. At either pole aligned tangent directions project to zero with d1 under the quadrant-exact trig graph.

## Independent science and fault validation

Independent CPU byte reference uses Fraction RN32 arithmetic. Separate scientific diagnostics use binary64 libm unit vectors and tangent basis e=(-sin(alpha0),cos(alpha0),0), n=(-sin(delta0)cos(alpha0),-sin(delta0)sin(alpha0),cos(delta0)), center=(cos(delta0)cos(alpha0),cos(delta0)sin(alpha0),sin(delta0)). Dot products and perspective division are independent of the canonical spherical equation graph.

Before testing fix: denominator absolute error <=2e-6; accepted xi/eta absolute errors <=5e-4; normalized reconstructed sky direction error <=5e-6. Reconstruct direction from center+xi*e+eta*n and normalize; no inverse-angle singularity at poles. Status must match the ideal d>=1/16 when the ideal denominator is more than 2e-6 away from the threshold. Within this strip report `ROUNDING_THRESHOLD_AMBIGUITY`; retain the canonical status and bits, never silently call an ideal classification proven. Invalid xi/eta must be exact +0. These scientific bounds are diagnostic gates, not bit tolerances or universal physical astrometric precision claims.

Probe tangent centers, east/north signs, RA wrap, both poles, behind-plane points, exact horizon, neighboring binary32 angles around the 1/16 guard, signed zero/subnormal angles, endpoint centers, dense all-sky and held-out seeds, 4096 records, invalid shapes/tags/units/NaN/Inf/out-of-range angles. Include actual shader and all-output one-bit faults, native malformed packets, full inherited GPU/software regression and partition reassembly, unchanged previous MathSpecs/kernels/source snapshot, fresh COLD-ZERO, worker/miner integration and verified source ZIP. QUICK total <=60s/MathSpec; no paired release A/B or SoC-efficiency claim from quick tests. No AI executor or RT route is introduced.
