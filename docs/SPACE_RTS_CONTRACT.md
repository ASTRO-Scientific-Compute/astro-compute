# Stabilized Rauch–Tung–Striebel backward step — opcode 73

Primary source: T. M. Chin, JPL IPN Progress Report42-233 (2023), https://ipnpr.jpl.nasa.gov/progress_report/42-233/42-233A-orig.pdf , equations(9–13),(20), sectionIII.C, accessed2026-10-03. Original ASTRO implementation of published equations, no external code copied.

Scientific purpose: fixed-interval smoothing revises a past filtered state using a later smoothed estimate. This is distinct from forward Kalman filtering: later observations can inform earlier states. One new ID `SPACE_RTS_SMOOTHER_STEP_F32_V1`. Dense matrix solves have no RT pruning; AI relevance POSSIBLE, AI_BACKEND_UNAVAILABLE.

## Input

Finite eight-digit binary32-hex values. Shared transition F[n,n] and process covariance Q[n,n]; per-record filtered `states` x[B,n], `covariances` P[B,n,n], additive deterministic `controls` u[B,n], next-time `next_states` xs_next[B,n], `next_covariances` Ps_next[B,n,n]. n1..6,B1..64. Row-major. Q,P,Ps_next must be exactly symmetric positive semidefinite, checked by exact-rational LDL residual elimination. Every executed rounded intermediate must remain finite; otherwise host rejects before dispatch. Units/time step/noise model explicit in supplied F,Q,u; no implicit physical constants.

The next smoothed estimate must correspond to the supplied linear transition and same scientific trajectory for the probabilistic interpretation. A standalone primitive cannot prove that interpretation. The adapter verifies the entire adjacent forward Kalman job/result pair, its actual posterior handoff and any later smoothing job/result. It carries explicit temporal hashes. The terminal state equals the last filtered state by an explicit caller choice. Model validity, time-series completeness, independence assumptions and noise calibration are not inferred.

## Frozen RN32 graph

Every arithmetic operation including sqrt is binary32 nearest ties-even, gradual underflow, canonical +0, separately rounded, no FMA. Matrix products use increasing inner-index dot products starting at +0. Symmetric outputs compute a>=b then mirror; no averaging. Exact CPU uses Fractions; GPU uses independent bounded integer-significand arithmetic.

1. xp=F*x+u, with dot then add. T=F*P. Pp[a,b]=dot(T[a],F[b])+Q[a,b], lower triangle mirrored.
2. Threshold=RN(max(0,diag(Pp))*2^-16). Lower unpivoted Cholesky with increasing a,b,j; residual starts Pp[a,b], subtracts each rounded product. Diagonal residual<=threshold returns status1 and every numeric output +0; otherwise sqrt or division by diagonal. It is a declared numerical guard, not a condition-number guarantee.
3. C=P*F^T. Solve Pp*G[a,:]^T=C[a,:]^T separately for every state row. Forward substitution increasing a,j; backward decreasing a and increasing j>a. Each starts the rhs, subtracts rounded products, divides by diagonal. d=xs_next-xp; xs=x+G*d (dot then add).
4. A=I-G*F (dot then subtract). B=Ps_next+Q elementwise. U=G*B; V=A*P. Ps[a,b]=RN(dot(U[a],G[b])+dot(V[a],A[b])), lower triangle mirrored. This is the stabilized JPL equation(20), algebraically equivalent in real arithmetic to the usual RTS covariance update for the stated linear model. No subtraction of covariance matrices, no hidden regularization.

Output width=1+2n+3n*n: `[uint32 status;xp[n],Pp[n*n],xs[n],Ps[n*n],G[n*n]]`, little-endian words, row-major. Status0 means completed graph, not calibrated uncertainty. Status1 has all other words +0. Partition unit is the full independent record.

Packet header `[MAGIC,1,73,B,n,0,0,0,0,0,0,offset,offset,width,0,0]`. F,Q follow the16-word header, offset=16+2*n*n. Then record-major x,P,u,xs_next,Ps_next; stride=3*n+2*n*n.

## Evidence and limitations

Complete zero-bit equality covers status, all predictions, smoothed means/covariances and gain, warmup and final, every candidate and held-out confirmation, and partition reassembly. Float64 direct linear solves separately check equations on accepted fixtures. A six-observation GPU forward/backward workflow additionally compares ALL smoothed means/covariances to an independently conditioned joint Gaussian block model (no RTS recursion). Those diagnostic thresholds never permit GPU bit differences.

Boundary cases include singular/ill-conditioned prediction rejection, semidefinite input, correlated covariances, no-information smoothing, signed zero, subnormals and maximal batch/dimensions. One-bit shader/output faults must be rejected. Rounded covariance PSD is not universally guaranteed; continuation rechecks it exactly, and blocks instead of silently repairing. Supplied arbitrary next covariance does not imply variance reduction. No nonlinear smoothing, singular pseudoinverse, variable-size infinite timeline, automatic calibration or physical accuracy certification.

Fresh COLD-ZERO per used MathSpec; full QUICK<=60s each. No release speedup or SoC efficiency statement without benchmark-policy paired A/B evidence.
