# Linear Kalman predict/update — opcode 72

Original implementation, no external code copied. Primary mathematical sources:
- R. E. Kalman (1960), *A New Approach to Linear Filtering and Prediction Problems*, https://www.cs.cmu.edu/~./motionplanning/papers/sbp_papers/k/Kalman1960.pdf . Linear prediction and measurement estimation.
- T. M. Chin, JPL IPN Progress Report 42-233 (2023), https://ipnpr.jpl.nasa.gov/progress_report/42-233/42-233A-orig.pdf , equations (1–2),(5–10),(14). Transition/observation model and Joseph covariance update. Accessed 2026-10-03.

Scientific use: bounded batches of independent linear state estimates, e.g. local constant-velocity tracking of measured positions. One MathSpec `SPACE_LINEAR_KALMAN_STEP_F32_V1` combines prediction and one measurement correction. This adds sequential estimation, not another name for least squares. No RT pruning exists for these dense small matrices. AI relevance POSSIBLE; AI_BACKEND_UNAVAILABLE.

## Input and assumptions

All numbers are finite eight-digit binary32 hex strings, `encoding=binary32-hex`. Row-major matrices. Shared `transition` F[n,n], `process_covariance` Q[n,n], `observation` H[m,n], `measurement_variance` R[m]. Per-record `states` x[B,n], `covariances` P[B,n,n], `controls` u[B,n], `measurements` y[B,m]. B=1..64,n=1..6,m=1..3, uniform dimensions, no implicit controls. Host validates exact-rational symmetry and positive semidefiniteness of each P and Q by LDL elimination including zero-pivot residual checks. Each R entry strictly positive. The complete executed RN32 graph must remain finite; overflow/divide-by-zero rejects the whole job before dispatch.

F includes the explicitly chosen time step and units. u is an additive deterministic state increment, not a control matrix. Process and measurement noises are assumed zero mean, mutually independent and independent of the initial error. R is diagonal only. F,H,Q,R and units are supplied by the caller; this primitive does not fit, validate or calibrate them. Gaussian assumptions are needed to interpret the linear estimate as a conditional mean; no automatic posterior calibration or coverage claim.

## Frozen operation graph

RN denotes binary32 nearest ties-even, gradual underflow, canonical positive zero. Every add, subtract, multiply, divide and square root rounds separately; no FMA/reassociation. Dot product starts at +0 and visits inner index in increasing order. Matrix multiplication is row-major ordered dots. Symmetric products calculate only entries a>=b in that order then copy each to [b,a]; there is no averaging.

1. xp[a]=RN(dot(F[a],x)+u[a]); T=F P; Pp[a,b]=RN(dot(T[a],F[b])+Q[a,b]), a>=b, mirrored.
2. C=Pp H^T; S[a,b]=RN(dot(H[a],C[:,b])+(R[a] if a=b else 0)), a>=b, mirrored. e[a]=RN(y[a]-dot(H[a],xp)).
3. Set threshold=RN(max(0,S[0,0],...,S[m-1,m-1])*2^-16). Unpivoted lower Cholesky visits a=0..m-1,b=0..a. Residual starts S[a,b], subtracts RN(L[a,j]*L[b,j]) for j=0..b-1. Diagonal residual <=threshold returns status1 with EVERY numeric output +0. Otherwise diagonal=sqrt(residual), offdiagonal=residual/L[b,b]. This is a declared numerical guard, not a condition-number proof.
4. For each state row a, solve S K[a,:]^T=C[a,:]^T using L forward then L^T backward substitution. Each substitution starts rhs[a], subtracts products in increasing j (back solve j=a+1..m-1), then divides by diagonal. xp correction: xpost[a]=RN(xp[a]+dot(K[a],e)).
5. A=I-KH with separately rounded dot/subtract; V=A Pp. Ppost[a,b]=RN(dot(V[a],A[b])+sum_j RN(RN(K[a,j]*R[j])*K[b,j])), a>=b, mirrored (Joseph form).
6. z=forward_solve(L,e). chi2=dot(z,z). It is the innovation quadratic in the stated rounded graph, not a p-value or outlier rejection rule.

Status0 output: `[uint32 status; xp[n],Pp[n*n],xpost[n],Ppost[n*n],e[m],chi2]`, width=2+2n+2n*n+m, row-major little-endian uint32 words. Status1 uses identical width with all numeric words zero. No partial successful prediction is published for status1.

Packed input header: `[MAGIC,1,72,B,n,m,0,0,0,0,0,offset_records,offset_records,width,0,0]`; after 16 words F,Q,H,R, then record-major x,P,u,y. offset_records=16+2*n*n+m*n+m; record_stride=2*n+n*n+m. One whole record is the partition unit.

## Validation and scope

Independent CPU oracle uses unbounded Fractions and exact rounding; GPU uses integer-significand software binary32. ALL output bits, statuses, warmup, partition reassembly and held-out outputs must match. Independent float64 NumPy matrix multiplication and direct solves check the scientific equations on well-conditioned fixtures; their numerical thresholds do not permit ANY GPU bit difference. Analytic scalar and covariance/innovation checks supplement them. Boundary and deliberately singular-in-RN32 cases test status semantics; invalid non-PSD input is rejected before execution.

Joseph form and explicit symmetry do not guarantee positive semidefiniteness after finite-precision rounding. No hidden jitter, clipping, regularization or repair is performed. Continuation must revalidate the complete returned Ppost exactly; an indefinite rounded result blocks continuation. The adapter accepts only complete zero-bit-verified, all-status0 upstream output and binds job/input/output hashes. No nonlinear/EKF/UKF, smoothing, missing measurements, full R or long-term filter stability certification.

QUICK is informational and <=60 seconds per MathSpec in total. No release-performance or SoC efficiency claim without policy-compliant paired A/B evidence.
