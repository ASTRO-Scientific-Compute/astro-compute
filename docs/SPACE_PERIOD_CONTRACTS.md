# SPACE period search — v1.17.20

Two MathSpecs are fixed before CPU vectors and GPU implementations. Every serialized output bit, including failure statuses and coefficients, must agree with the independent exact-rational RN32 oracle. Each operation rounds separately to nearest-even, canonical positive zero, without FMA/reassociation. Finite input/intermediate overflow is rejected before submission. The existing one-harmonic opcode 39 is unchanged.

## Multiple harmonics (opcode 57)

H2..4, p=2H+1; N>=p+1 and N<=256; F1..128; N*F*p*p<=2097152. Nonnegative inverse variances, positive trial frequencies. Relative times may be negative. phase_k=RN32(RN32(time*frequency)*RN32(k)), with abs(phase_k)<=256. The sine/cosine operation graph reuses the frozen finite-turn polynomial from SPACE_SEARCH_CONTRACTS. Basis order is [1,cos1,sin1,...,cosH,sinH]. This graph is explicitly defined; it is not a claim to reproduce native libm/Astropy bytes.

1. In observation order sum W=sum(w) and WY=sum(w*y). W=0 gives status 1. ybar=WY/W.
2. For each observation construct the basis and centered d=y-ybar. For each row a then column b: G[a,b]+=RN(RN(w*X[a])*X[b]); rhs[a]+=RN(RN(w*X[a])*d). Reference chi0+=RN(w*RN(d*d)). Every accumulation starts at 0. If chi0=0, status 1.
3. Lower-triangular Cholesky, row i then column j<=i: d=G[i,j]-ordered_sum_k<j(L[i,k]*L[j,k]). For i=j reject with status 2 if d<=RN(W*2^-16), otherwise L[i,i]=sqrt(d). For i>j, L[i,j]=d/L[j,j]. This conservative finite-precision pivot gate is not an exact rank oracle or a general condition-number certificate.
4. Forward substitution u[i]=(rhs[i]-ordered_sum_j<i(L[i,j]*u[j]))/L[i,i]. Back substitution from i=p-1..0, summing j=i+1..p-1 in increasing order: beta[i]=(u[i]-sum(L[j,i]*beta[j]))/L[i,i]. Final offset=RN(beta[0]+ybar); harmonic coefficients unchanged.
5. Rebuild each sample's basis, predicted=offset, then add beta[j]*X[j] for j=1..p-1. chi2=sum(w*RN((y-predicted)^2)). power=RN((chi0-chi2)/chi0); do not clip power to hide numerical behavior.

Output p+3 words: status,power,chi2,offset,c1,s1,... . On status 1/2 every numeric word is positive zero. No covariance, analytical false-alarm probability or multiband modeling is inferred.

## Fixed-bin PDM (opcode 58)

Times are explicit integer ticks 0..10000000; no conversion or rounding from real timestamps. N3..4096; periods1..1000000,F1..128; bins2..64;N*F<=262144. bin=((time mod period)*bins)//period uses bounded exact uint32 arithmetic. Flux stays binary32. All observations have equal statistical weight.

Accumulate per-bin count and flux sum in original observation order. Compute global mean via original-order flux sum/N; occupied is the count of nonempty bins. Global sample variance=ordered_sum((y-mean)^2)/(N-1). Rounded zero variance gives status 1. Otherwise fewer than 2 occupied bins or N<=occupied gives status 2. Both failures return five zero fields.

For each nonempty bin compute mean=sum/count. Within SSE is the original-observation-order sum of (y-bin_mean)^2, not a reordered bin-wise sum. Within variance=within_SSE/(N-occupied). theta=within_variance/global_variance. Return status 0,theta,global_variance,within_variance,occupied,N-occupied. Singleton bins contribute 0 within SSE and 0 residual degrees of freedom. theta is not clipped and may exceed 1. Lower values indicate less within-phase dispersion. This variant has one nonoverlapping equal-width cover, no automatic bin merging, no fitted Fourier shape and no built-in significance estimator.

## Frequency-grid adapter (CPU preprocessing, not a new GPU workload)

A deterministic adapter uses the exact rational span of the supplied finite binary32 relative timestamps. Caller explicitly supplies positive min/max frequency and integer samples_per_peak 1..64. Proposed spacing=1/(span*samples_per_peak), following the baseline-width heuristic. Generate min+i*spacing while <=max, round each once to binary32, reject any repeated rounded frequency; no silent deduplication or endpoint beyond max. Bound total entries before allocation, max 65536, and reject overflowing/zero/unrepresentable grids. Record timestamps hash, min/max, span, spacing, sampling factor and complete serialized grid hash. Slice into explicit tiles for workload size limits without altering global frequency order.

The user chooses scientifically meaningful bounds: an average-Nyquist heuristic is not imposed on irregular data. This grid is not a guaranteed complete peak search, especially for periods comparable to or longer than the observing baseline. No RNG or null simulation is generated.

## Sources and kernel families, 2026-10-03

Primary definitions: [Astropy multi-term model/normalization](https://docs.astropy.org/en/stable/timeseries/lombscargle.html), [Astropy frequency-grid caveats](https://docs.astropy.org/en/stable/api/astropy.timeseries.LombScargle.html), [PyAstronomy PDM](https://pyastronomy.readthedocs.io/en/latest/pyTimingDoc/pyPDMDoc/classes.html), [Stellingwerf 1978](https://articles.adsabs.harvard.edu/pdf/1978ApJ...224..953S). Original implementation; no external source code bundled.

Algorithm families reviewed: direct design-matrix fits, FFT-assisted multi-harmonic fits, QR/SVD versus bounded Cholesky normal-equation solves, per-bin reductions. [LAPACK least-squares methods](https://www.netlib.org/lapack/lug/node27.html) motivates the independent NumPy least-squares scientific check; it does not license silently replacing the declared RN32 solve order. [Khronos subgroup capabilities](https://docs.vulkan.org/guide/latest/subgroups.html) informed portable scheduling. Ordered per-trial kernels preserve the full arithmetic contract; parallel floating tree reductions/atomics would change it. Local sizes 32/64/128/256 and pack 1/2/4 are fresh local candidates; unmeasured variants stay unmeasured when QUICK expires. Total per-MathSpec QUICK<=60s. No imported benchmark winners. RT is inapplicable; AI_BACKEND_UNAVAILABLE. All timings remain informational without release A/B evidence.
