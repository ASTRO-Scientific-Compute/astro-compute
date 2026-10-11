# Bounded elliptic Kepler state — opcode75

`SPACE_ELLIPTIC_KEPLER_STATE_F32_V1` is a direct implicit-equation solve,
followed by a two-body state conversion. It does not advance an RK4 step and
is not a renamed transform. Its state is in the right-handed perifocal plane:
+x points toward periapsis, +y follows increasing anomaly, z=0.

## Mathematical and input contract

Explicit `encoding=binary32-hex`, `angle_unit=turn`, `frame=PERIFOCAL`, nonblank
`distance_unit` and `time_unit` text of at most64 characters. `elements[N,3]`
contains `(a,e,M)`; N1..1024. Shared positive `mu` has distance_unit^3/time_unit^2.
a and mu are each in[2^-32,2^32]; eccentricity0<=e<=15/16; M is in[0,1) turns.
All words must be finite. Signed zero is accepted numerically and canonicalized
by arithmetic. No implicit angle/unit conversion, wrapping or element epoch
propagation. Hyperbolic/parabolic and nearly parabolic orbits are excluded.

In exact real notation, solve `2*pi*(E-M)-e*sin(2*pi*E)=0` for E in[0,1).
Then b=sqrt(1-e^2), d=1-e*cos(2*pi*E), r=a*d, vscale=sqrt(mu/a)/d,
position=(a*(cos(2*pi*E)-e), a*b*sin(2*pi*E),0),
velocity=(-vscale*sin(2*pi*E), vscale*b*cos(2*pi*E),0).
Output eight binary32 words per record: `[E_turns,r,x,y,z,vx,vy,vz]`.
This is an osculating unperturbed two-body state at the supplied mean anomaly;
no Julian date, frame precession or physical ephemeris is inferred.

## Canonical RN32 algorithm

Every +,-,*,/,sqrt uses independent RN-even binary32, gradual underflow,
positive zero after arithmetic, no FMA/reassociation. CPU reference uses
Fraction arithmetic and exact rounding; GPU uses integer software arithmetic.

1. Canonicalize M,e zero. For e=0, M=0, or M=1/2, set E=M exactly.
2. Otherwise set reflected=(M>1/2) and m=RN(1-M) if reflected, else M.
   Initialize lo=0, hi=1/2. Exactly32 iterations:
   mid=RN(RN(lo+hi)*1/2);
   residual=RN(RN(TAU*RN(mid-m))-RN(e*sin_turn(mid))).
   If residual<0 set lo=mid, otherwise hi=mid. Equality selects hi;
   floating-point plateau does not add unbounded iterations.
3. u=RN(RN(lo+hi)*1/2); E=RN(1-u) if reflected, else u.
4. sin_turn/cos_turn use the already published ASTRO exact fractional-turn,
   quadrant reduction and degree13/14 Taylor-Horner RN32 graph. TAU is
   binary32 word40c90fdb. Coefficients are RN32 reciprocal factorials with signs.
5. b=sqrt(RN(1-RN(e*e))); d=RN(1-RN(e*cos)); r=RN(a*d);
   vscale=RN(sqrt(RN(mu/a))/d). x=RN(a*RN(cos-e));
   y=RN(RN(a*b)*sin); vx=-RN(vscale*sin); vy=RN(RN(vscale*b)*cos).
   z=vz=+0. Full output bytes, including E and radius, require0 differing bits.

CPU input validation executes the full graph before dispatch; all intermediate
results must remain finite. The explicit a/mu bounds and eccentricity margin
avoid singular/overflowing physical states. The rounded solve is the declared
algorithm, not an exact real root or a double-precision ephemeris.

## Scientific diagnostics and scope

Independent binary64 safeguarded Newton solution of the real Kepler equation,
libm sin/cos and analytic derivatives check every output. Fixed diagnostic
thresholds: wrapped E error<=2e-6 turns, position/radius error divided by a
<=2e-5, velocity error divided by sqrt(mu/a)<=5e-5; relative specific-energy
and angular-momentum errors<=5e-5. Circular and apsis analytic anchors,
near-zero/near-one anomalies, e=15/16, signed zero, subnormal M/e and all scale
corners are exercised. These are approximation diagnostics on tested inputs,
not bit acceptance tolerances or universal precision guarantees.

Independent central-force RK4 integration with fine substeps provides a
separate orbit-trajectory check. Energy=-mu/(2a), h=sqrt(mu*a*(1-e^2)).
There are no perturbations, collisions, relativistic corrections, frame
orientation or automatic time-scale conversion. Existing Cartesian transforms
can orient an explicitly supplied perifocal frame in a later workflow.

## Primary sources

- JPL Solar System Dynamics, Standish/Williams, *Approximate Positions of the
  Planets*, steps3–4 and Kepler-equation solution: implicit eccentric anomaly
  and orbital-plane position equations. No published planet tables copied,
  no claim to their epoch/planet accuracy:
  https://ssd.jpl.nasa.gov/planets/approx_pos.html
- NASA/JPL NAIF `conics_c`: state from conic elements, two-body osculating
  interpretation and state component conventions:
  https://naif.jpl.nasa.gov/pub/naif/toolkit_docs/C/cspice/conics_c.html

Velocity equations follow differentiation using dE_rad/dt=sqrt(mu/a^3)/d.
Original ASTRO implementation; no external code copied. CPU reference,
scientific Newton and integration checks are separate from the GPU graph.
QUICK<=60seconds per MathSpec; no speed or SoC efficiency claim without release
A/B evidence. No AI executor or mathematically unsupported RT route.
