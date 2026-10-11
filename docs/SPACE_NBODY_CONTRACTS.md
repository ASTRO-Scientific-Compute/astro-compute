# Coupled N-body contracts — v1.17.29

## Scope and primary sources

The [GSL ODE documentation](https://www.gnu.org/software/gsl/doc/html/ode-initval.html) describes classical RK4 with step-doubling error estimation and the two-half-step solution. The [REBOUND gravity variables](https://pyodide.hanno-rein.de/simulation/variables/) define a constant gravitational coefficient and uniform softened inverse-square interactions. ASTRO implements its own bounded numerical graph; no GSL/REBOUND code was copied and neither is a runtime dependency. The controller below is explicitly ASTRO's controller, not a claim of GSL compatibility.

Both new workloads describe isolated systems with fixed masses, constant G and one uniform constant softening squared. Inputs have caller-consistent units; there is no implicit astronomical constant, unit conversion, coordinate frame or epoch. Positions and velocities belong to the same inertial frame and instant. Bodies in one record are mutually coupled and may never be partitioned into independent records.

## Exact numerical contract

All physical values are finite binary32 hex words. Every add, subtract, multiply, divide and square root rounds to nearest, ties to even (RN32); subnormals are retained and zero results canonicalized to +0. No FMA, reassociation or native float shortcuts. Ordered sums begin at +0 and follow ascending body/component indices. Exact CPU Fraction arithmetic and independent GPU integer/software-binary32 implementations must agree on every output bit. NaN/infinity inputs or nonfinite executed intermediates are rejected by host preparation before GPU dispatch. Numerical underflow remains defined by RN32. The six controller tolerances never relax output-bit equality.

Common payload: `encoding=binary32-hex`, `states[B,N,6]` in x,y,z,vx,vy,vz order; `masses[B,N]`; `gravitational_constant>=0`; `softening_squared>=0`; masses>=0. All systems have the same N; masses may differ. Native input consists of a16-word header, flattened states A, flattened masses B and, for integration, shared controls C. Header: `[MAGIC,1,opcode,systems,bodies,max_attempts,0,0,G,eps2,0,16+len(A),16+len(A)+len(B),output_width,0,0]`. The header's B offset doubles as A end; C offset doubles as B end. Native packet entry is an internal executor boundary; public jobs must pass host preparation.

## 69 — SPACE_ADAPTIVE_NBODY_RK4_F32_V1

Bounds:1<=B<=16,1<=N<=8,1<=max_attempts<=64 and B*N*N*max_attempts<=16384. Shared controls C are `duration,dt_initial,dt_min,dt_max,rtol,atol[6]`; duration>=0,0<dt_min<=dt_initial<=dt_max,rtol>=0,each atol>0. Absolute tolerances repeat for each body's six components.

For each body i, dr_i/dt=v_i. For j ascending excluding i: gm=RN(G*m_j); skip rounded-zero gm. G=0 skips all interactions. delta=RN(r_j-r_i); d2=RN(ordered sum RN(delta_axis^2)+eps2). If d2=0, return singular-force status. scale=RN(gm/RN(d2*RN(sqrt(d2)))); acceleration accumulates RN(scale*delta) in j order. A massless particle feels massive sources but supplies no acceleration to others.

Classical RK4 uses half=RN(h/2),sixth=RN(h/6); k1 at the full current state, k2 at state+half*k1, k3 at state+half*k2, k4 at state+h*k3. Every stage recalculates all mutual forces from that stage's complete coupled state. The update is RN(state+RN(sixth*RN(RN(RN(k1+RN(2*k2))+RN(2*k3))+k4))). Each inner arithmetic operation is also RN32.

An attempt computes coarse=one full step and fine=two half steps. Per-component error is RN(RN(abs(RN(fine-coarse))/15)/RN(atol_axis+RN(rtol*max(abs(old),abs(fine))))). The maximum over all6N components controls the whole system. Accept iff error<=1, using fine without Richardson extrapolation. The next step doubles if error<=1/32, bounded by dt_max; otherwise it retains the used step, then is clamped at least dt_min. A rejected attempt halves the step; if the half is below dt_min, fail. Steps clip to remaining duration, so the terminal accepted step may be smaller than dt_min. On accepting it, elapsed is set exactly to duration. A step unable to advance rounded time, or a zero rounded half step, fails. Zero duration skips force evaluation and returns the canonicalized initial state.

Output per record: `[u32 status,attempts,accepted,rejected; f32 elapsed,last_error,next_dt,final_states[N,6]]`, width7+6N. Status0 complete,1 attempt budget,2 minimum/unrepresentable step,3 singular force. Failure retains the last accepted state and time. Attempts include a failed force attempt; accepted+rejected can be less than attempts. A failed force or half-step evaluation retains the previous last_error. next_dt is the current controller step, not necessarily a successful recommendation after failure.

## 70 — SPACE_NBODY_INVARIANTS_F32_V1

Bounds:1<=B<=64,1<=N<=64,B*N*N<=65536. Output15 words: `[u32 status; f32 M,T,U,E,Px,Py,Pz,Lx,Ly,Lz,COMx,COMy,COMz,min_distance_squared]`.

M is ordered sum of masses. Rounded M=0 yields status2 and14 numeric zero words immediately. For each nonzero-mass body: T accumulates RN(RN(.5*m)*ordered_dot(v,v)); P sums m*v; L sums m*(r cross v), with each cross component the RN subtraction of two RN products; weighted position sums m*r, then divides each component by M. Zero-mass bodies are skipped in these sums.

For pairs i<j in ascending order, delta=r_j-r_i, unsoftened r2=ordered_dot(delta,delta); minimum includes all pairs, even massless ones, and equals0 for N=1. Coupling=RN(RN(G*m_i)*m_j). Rounded-zero coupling skips potential. Otherwise softened=RN(r2+eps2); zero softened distance yields status1 and14 numeric zeros. Potential sequentially subtracts RN(coupling/RN(sqrt(softened))). E=RN(T+U). No partial numeric diagnostics escape on failure.

A massless coincident particle may have a valid potential diagnostic and a singular acceleration in workload69: these statuses answer different questions. Continuous static softened gravity conserves E,P,L; its COM is constant only when P=0, otherwise moves linearly. Numerical RK4 does not guarantee exact conservation.

## Verified downstream workflow

`space_nbody_adapter` reconstructs all final state words only after comparing the complete upstream output with its independently prepared reference and requiring status0 for every system. It preserves masses,G,eps2 and binds upstream packed-input, full-output and model SHA256. The diagnostic job consumes these exact words. A continuation requires an explicit new duration and restarts the original shared dt_initial/min/max/tolerances; it does not silently reuse per-record next_dt. It describes the next interval in the same static model, not an absolute epoch or a promise of a bit-identical single long integration.

`tools.create_nbody_followup_jobs` reads a source JSON job and raw GPU output, writes a diagnostic job and optionally a continuation, plus source/output/generator/job hashes. Its CPU verification is outside GPU timing. `tools.validate_space_nbody_pipeline` runs initial invariants, integration, actual-output invariants, continuation and continued-output invariants on the GPU. A controlled circular binary checks short-interval energy/angular-momentum drift (<3e-5 absolute), momentum and COM (<2e-6). These are test-specific diagnostics, not universal integration tolerances.

## Evidence and limits

Golden analytic examples, deterministic random/heldout systems,27 edge cases across both workloads, complete whole-system partition reconstruction, shader-bit corruption and malformed native-packet guards are required. Independent scientific checking uses float64 velocity-Verlet at2048/4096 steps with <1e-7 refinement change, and separately vectorized invariants. Controlled trajectory comparisons use rtol=atol=3e-5; invariants use8e-6. These physical diagnostics are separate from mandatory0-bit CPU/GPU comparison and do not prove arbitrary long-term accuracy.

No adaptive/per-body softening, collision or surface event localization, merging, drag/radiation, external J2 field, symplectic long-term behavior or unlimited body count. No AI executor or new RT path. QUICK is informational, at most60 seconds per MathSpec including baseline/confirmation. Release speed and SoC energy-per-calculation claims require paired A/B evidence with complete timing/input/kernel/clock provenance under the existing benchmark policy.
