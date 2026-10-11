# SPACE inference — v1.17.17

All three are original implementations of published scientific methods, with explicit finite-operation contracts. Complete output acceptance requires zero differing CPU/GPU bits. Separate binary64 science diagnostics never relax that rule. Binary32-hex is mandatory; non-finite input and overflowing arithmetic reject the job before dispatch. No trained AI or invented RT backend is used.

## Percentile bootstrap interval (48)

Each input row is a complete distribution of supplied bootstrap statistic replicates, not original observations. Sort numerically, canonicalizing signed zeros. For confidence c compute alpha=RN32(RN32(1-c)*0.5) and upper probability RN32(1-alpha). For each probability q, h=RN32((N-1)*q), j=floor(h), g=RN32(h-j). If g=0 return the sorted value at j; otherwise return RN32(RN32(RN32(1-g)*x[j])+RN32(g*x[min(j+1,N-1)])). Every arithmetic node rounds separately to nearest-even binary32. Output is [lower,upper]. Repeated values, negative values, odd lengths and confidence1 are valid. No data-dependent reduction reassociation.

Sources: [SciPy percentile bootstrap](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.bootstrap.html), [NumPy type7 quantile definition](https://numpy.org/doc/stable/reference/generated/numpy.quantile.html). CPU uses rational comparisons and sorting; GPU uses an independently written padded bitonic sorting network. Padding is the largest finite binary32 value and does not change the first N numeric order statistics. Research considered [GPU sorting networks](https://developer.nvidia.com/gpugems/gpugems2/part-vi-simulation-and-numerical-algorithms/chapter-46-improved-gpu-sorting) and radix/selection families; only the stated bitonic implementation is included in this release's local/pack search. No external benchmark winner is imported.

This is the equal-tailed percentile method, not BCa or basic-bootstrap intervals. Resampling design, correlation assumptions and coverage calibration are external responsibilities. The existing bootstrap mean/variance output can supply its mean column as replicates; no extra kernel ID is invented for that data conversion.

## Monte Carlo tail (49)

For each supplied observed statistic, count every supplied null statistic greater than or numerically equal to it. Return four exact uint32 words: b,N,b+1,N+1. The final two are the rational conservative randomized upper-tail estimate, following [SciPy's plus-one convention](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.permutation_test.html). No floating division loses probability bits. There is no approximate-equality window; equal signed zeros tie. This is a randomized-sample contract, not enumeration of the exact permutation distribution.

For periodogram maxima, observed and null values must use the same frequency search and observation model; see [Astropy's significance discussion](https://docs.astropy.org/en/stable/timeseries/lombscargle.html). Required model and grid identifiers are bound into the binary input by a SHA-256 digest of their canonical JSON. They are provenance, not proof that the null model is appropriate. The kernel neither generates null simulations nor interprets a tail probability as the probability that a source is real. Null shards must add raw b,N first and apply the correction once; observed-threshold records can be independently dispatched unchanged.

## Two-template SED fit (50)

For each object and supplied template pair, accumulate in increasing band order:

`g00 += (w*t0)*t0; g01 += (w*t0)*t1; g11 += (w*t1)*t1; u += (w*t0)*y; v += (w*t1)*y`.

All multiply/add nodes are separate RN32 operations. Let product=g00*g11 and det=product-g01*g01. If det<=RN32(product*2^-18), output status1 and three positive zeros, with no accepted fit. This includes zero weights, rank deficiency and poor conditioning; it never silently promotes a boundary-only approximation.

Otherwise enumerate candidates in fixed order: (0,0); (max(0,u/g00),0); (0,max(0,v/g11)); and ((u*g11-v*g01)/det,(v*g00-u*g01)/det) if both interior coefficients are nonnegative. For each candidate, compute predicted=(a*t0)+(b*t1), residual=y-predicted, chi2=ordered_sum(w*(residual*residual)), again RN32 at each node. Keep the first candidate with minimum rounded chi2 (strict improvement only). Output [status0,a,b,chi2]. Arithmetic zero is positive zero. This frozen finite computation is bit reproducible; binary64 constrained fits are independent scientific diagnostics, not identical-byte targets.

Sources: [EAZY analytic two-template fits](https://github.com/gbrammer/eazy-photoz/blob/master/doc/eazy_manual.tex), [SciPy/NNLS constrained least squares](https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.nnls.html). The finite two-variable active sets are exhaustively enumerated. General active-set N-template methods and iterative solvers remain future scope. The caller supplies redshifted/bandpass-integrated template pairs and inverse-variance weights; no redshift grid, prior or posterior is invented.

## Search and partitioning

Independent distributions, observed thresholds and object/template pairs map to independent GPU records. Capability-legal local sizes32/64/128/256 and packs1/2/4 form the12 candidates per workload. No new RT route: none of these operators benefits from ray/BVH pruning without changing its contract. AI relevance is metadata only. COLD-ZERO and the paired release-benchmark policy remain mandatory; quick rates are INFORMATIONAL.
