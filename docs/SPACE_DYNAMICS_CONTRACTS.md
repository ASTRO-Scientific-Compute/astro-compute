# SPACE dynamics — v1.17.19

All three MathSpecs precede CPU fixtures and GPU implementation. Every output byte, including adaptive control decisions, status, accepted/rejected counts and state, requires zero differing bits. The user-supplied integration atol/rtol control a numerical local-error estimate; they never relax CPU/GPU equality. Binary32 input is preserved exactly and every operation rounds independently to nearest-even, with canonical positive zero and no FMA. The CPU preflight rejects nonfinite inputs or intermediates, including overflow and vanished denominators other than the explicitly handled singular radius.

## Shared force and potential

Parameters mu>=0, reference_radius R>=0 and finite dimensionless j2 are supplied, never inferred from a device or planet name. Position/velocity/time/mu/R must use coherent units. The z axis is the fixed symmetry axis. The physical external-field model is appropriate outside the body; no surface/collision/event or atmospheric model is implied. Negative J2 is mathematically allowed. If mu=0, force/potential are zero and the origin is permitted. Otherwise r2=ordered_sum(x*x,y*y,z*z); rounded r2=0 means singular status.

The exact force operation graph, with RN after every operator:

    r = sqrt(r2)
    base = -(mu / (r2*r))
    acceleration[k] = base * position[k]
    if j2 != 0 and R != 0:
        q = (z*z)/r2
        scale = ((1.5*j2)*mu)*(R*R) / ((r2*r2)*r)
        t = 5*q
        acceleration[k] += (scale*position[k])*(t - (3 if k==2 else 1))

Opcode54 returns [status,ax,ay,az], status0 success or1 singular (three zero values). Singularity is reported, never softened silently.

For opcode56, compute radius=sqrt(r2), speed_squared=ordered_sum(vk*vk), kinetic=0.5*speed_squared. If mu>0, potential initially equals -(mu/r); when J2 and R are nonzero:

    q = (z*z)/r2
    shape = (3*q)-1
    correction = (j2*((R*R)/r2))*(0.5*shape)
    potential = -(mu/r)*(1-correction)

Energy=kinetic+potential. Cross products use one rounded product per factor, then a rounded subtraction. Output [status,radius,speed_squared,energy,hx,hy,hz]. For singular mu>0 all six numeric values are zero. Energy and hz, not the entire angular momentum vector, are conserved in the continuous J2 model. Numerical drift must be measured; the diagnostic does not enforce conservation by overwriting state.

## Adaptive RK4 (opcode55)

Canonicalize the initial state. Start elapsed=0, h=dt_initial, last_error=0, all counters0. Standard RK4 stages use separate operations: half=h*0.5, sixth=h/6, temporary=s+(stage_step*k); final=s+sixth*(((k1+2*k2)+2*k3)+k4). Every derivative uses the shared force above. No extrapolation correction is added.

Until duration reached or max_attempts consumed:

1. Set step=min(h,RN(duration-elapsed)). If step=0 or RN(elapsed+step)<=elapsed, stop status2 without increasing attempts.
2. Increment attempts; compute coarse=RK4(s,step), mid=RK4(s,step*0.5), fine=RK4(mid,step*0.5). If half=0 stop status2. Any singular stage stops status3, preserving the accepted prefix; it is not silently accepted or retried.
3. For each of6 components form scale=atol[k]+rtol*max(abs(s[k]),abs(fine[k])); error[k]=(abs(fine[k]-coarse[k])/15)/scale. last_error=max(error[k]). Max and absolute are exact bitwise/numeric operations on finite values.
4. If last_error<=1, accept fine and increment accepted. Set elapsed=duration if step equals remaining, otherwise RN(elapsed+step). Set h=step, doubling only if error<=1/32 and step<=dt_max/2; else cap at dt_max when doubling would exceed it. Ensure next h>=dt_min. This avoids overflow from an unnecessary double near maximum finite dt.
5. Otherwise increment rejected. If step*0.5<dt_min, stop status2; keep the previous proposed h. Else set h=step*0.5 and retry from unchanged accepted state/time.

Status0 means the complete duration was reached (including zero duration),1 means max_attempts exhausted,2 insufficient allowed step/time resolution,3 singular force. Failed attempts do not advance time/state. Output13 words: status,attempts,accepted,rejected,elapsed,last_error,next_dt,state[6]. The last_error field is the most recently completed estimate (initially0), even if a later stage fails. h is the current/next proposed step as defined above. A final clipped step may be shorter than dt_min, but a rejected step is never halved below dt_min. No dense output, global error bound, stiffness support, event detection or adaptive N-body claim.

Limits: N1..64 trajectories,max_attempts1..128,N*max_attempts<=2048; common duration>=0,0<dt_min<=dt_initial<=dt_max; atol[6]>0,rtol>=0. Force and diagnostic jobs allow up to4096 records. Any impossible finite arithmetic rejects the whole job during CPU preflight instead of emitting infinities.

## Research and kernel families (2026-10-03)

Methods: [poliastro J2 acceleration](https://docs.poliastro.space/en/stable/autoapi/poliastro/core/perturbations/index.html), [GSL RK4 step doubling](https://www.gnu.org/software/gsl/doc/html/ode-initval.html), [SciPy local error scaling](https://docs.scipy.org/doc/scipy/reference/generated/scipy.integrate.RK45.html), [UT Austin conservation laws](https://farside.ph.utexas.edu/teaching/celestial/Celestial/node25.html) and [axisymmetric external potential](https://farside.ph.utexas.edu/teaching/336k/Newtonhtml/node108.html). SciPy RK45 is Dormand–Prince; this implementation is explicitly RK4 step doubling with a conservative dyadic controller, not a claim to reproduce SciPy/GSL solver outputs. No external scientific code is bundled.

Families considered: independent particle/trajectory records, stage batching across dispatches, subgroup/cooperative state updates. [Khronos subgroup capabilities](https://docs.vulkan.org/guide/latest/subgroups.html) inform portability. Independent records preserve each trajectory's adaptive history without cross-dispatch queues or noncanonical arithmetic. The local search measures local sizes32/64/128/256 and packing1/2/4, subject to capabilities. Stage batching and cooperative reductions remain unimplemented alternatives; no external benchmark is used as a hardware winner. No natural RT pruning exists for these analytic forces. AI_BACKEND_UNAVAILABLE. COLD-ZERO and informational-only QUICK policy are preserved.
