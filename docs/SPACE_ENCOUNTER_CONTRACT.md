# Swept pair encounters — v1.17.30

## Source and scope

[REBOUND collision documentation](https://rebound.hanno-rein.de/collisions/) distinguishes endpoint overlap checks from straight-line collision searches during a step and explicitly warns that the latter can miss curved-path collisions. ASTRO implements an original closest-point projection for supplied pair chords; no REBOUND implementation is copied or required at runtime. This is an inclusive contact/closest-approach diagnostic, not an implementation of REBOUND's exact API or collision response rules.

The two endpoints of every body correspond to the same beginning/end times in a common inertial frame. Linear interpolation uses one shared fraction u in [0,1]. All coordinates and radii have consistent caller-selected length units. No automatic frame, epoch, unit or body-radius inference occurs. Radii are constant over the interval. The workload evaluates explicitly supplied pairs; the N-body adapter separately enumerates all pairs inside each system.

## 71 — SPACE_SWEPT_SPHERE_ENCOUNTER_F32_V1

Input: `encoding=binary32-hex`, `pairs[N,14]`,1<=N<=4096. Each row contains `[a0.xyz,a1.xyz,b0.xyz,b1.xyz,radius_a,radius_b]`. All values are finite binary32 and both radii are nonnegative. NaN/infinity and nonfinite executed intermediates are rejected before dispatch. Radii may be zero. Every add/subtract/multiply/divide rounds to nearest, ties to even, with gradual underflow and canonical +0; no FMA or reassociation. CPU uses independent Fraction arithmetic; GPU uses integer software binary32. Every full output word must match exactly, with zero allowed differing bits.

Packed input has a16-word header `[MAGIC,1,71,N,14,0,0,0,0,0,0,16+14*N,16+14*N,7,0,0]` followed by flattened pairs. Complete pairs are independent partition units. There is no hidden filtering, pair pruning, radius padding or RT path.

Let RN denote rounding after each operation. For axes x,y,z in that order: p=RN(b0-a0),q=RN(b1-a1),d=RN(q-p). Compute A=sum RN(d*d),B=sum RN(p*d) as ordered sums from +0. If A=0 or B>=0, choose u=0. Otherwise if -B>=A, choose u=1; otherwise u=RN(-B/A). This branch ordering avoids a potentially overflowing unconstrained ratio. The rounded stationary flag is A=0, including squared-motion underflow.

The nearest relative vector uses p directly at u=0 and q directly at u=1; for interior u it is RN(p+RN(u*d)) componentwise. Squared separations are ordered dot products of this vector, p and q. R=RN(radius_a+radius_b),R2=RN(R*R). Contact is true iff the rounded minimum squared separation is <=R2. Inclusive tangency, overlap at either endpoint, initial penetration and zero-radius point crossing count as contact.

Output7 words per pair:

`[u32 contact; f32 closest_fraction,min_distance_squared,start_distance_squared,end_distance_squared,radius_sum_squared; u32 rounded_stationary]`.

The contact word and stationary word are always0 or1. A stationary relative chord chooses the earliest minimizing fraction0. The closest fraction is **not first contact time**; for an extended-radius head-on passage, first contact precedes closest approach. No impact point, normal, velocity impulse, merging or response is computed. Rounding may affect tangency and tiny motions; this is a defined RN32 predicate, not exact-real geometry or a conservative no-miss broadphase. In particular rounded stationary need not mean mathematically zero motion.

## Verified N-body adapter

`make_job(source,raw,radii)` accepts only a full, independently checked workload69 GPU result with status0 for every system. It pairs each initial position with the exact final GPU position, preserving the shared interval. Explicit radii[B,N] must match the source systems and be finite/nonnegative; at least two bodies are required. For every system and lexicographic i<j, exactly one pair is emitted, with system/body indices in `record_pairs`. It binds upstream packed-input, whole-output, model and radii SHA256, records interval duration and labels the path model `STRAIGHT_ENDPOINT_CHORDS`, `curved_path_completeness=false`, `contact_time=false`.

Even for a nonlinear N-body trajectory, this describes its endpoint chords only. An interior gravitational close approach may be missed by a long chord. Endpoint-chord clearance must never be promoted to collision-free curved motion, an adaptive event locator or permission to skip force integration. The adapter does not change masses, resolve impacts, stop/restart integration at contact or infer physical sphere sizes.

`tools.create_encounter_jobs` reads source JSON, verified raw GPU result and an explicit JSON radius matrix. Its manifest binds all three files, the generator and each generated job. Empty/partial/corrupt trajectories are rejected. `tools.validate_space_encounter_pipeline` integrates two freely crossing bodies on the GPU (G=0), consumes their actual positions, then evaluates the encounter on the GPU. Endpoint squared separations are16, radius-sum squared is0.25 and closest separation is0 at fraction0.5: an endpoint-only test would miss this contact. One injected bit in the actual upstream result must prevent job generation.

## Evidence and limits

Analytic examples, deterministic random/heldout pairs,14 boundary cases, complete partition reassembly, shader-bit injection, five native packet guards, worker and miner integration are required. Cases include inclusive endpoint/interior tangency, complete pass-through, stationary/common translation, receding motion, point crossing, negative zero, tiny/underflowed motion and4096 records.

The independent scientific checker uses NumPy float64 SVD least-squares projection and independently evaluates interpolated separation/radius. Controlled inputs compare floating fields at rtol=atol=3e-6 and contact classification allowing1e-13 squared-distance slack only in this float64 diagnostic. This is not the GPU contract and does not allow any differing output bit. Underflow-specific edges are checked against exact RN32 CPU semantics rather than a float64 stationary-motion identity.

No universal collision completeness, earliest-contact time, curved-path root finding, collision response, trained classifier or AI backend. Existing kernels are preserved. QUICK stays informational and <=60 seconds per MathSpec; no release speed or SoC energy-per-calculation claim without paired A/B evidence.
