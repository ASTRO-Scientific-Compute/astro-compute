# Robust biweight statistics — v1.17.23

One new workload, opcode63, combines the shared median/MAD pass with biweight location, midvariance and scale. These are not separate workload IDs. Contract fixed before CPU vectors and GPU code.

## Inputs and exact operation graph

encoding=binary32-hex; samples[B,N] and valid[B,N] uint0/1, B1..128, N1..256, B*N*N<=2097152. Two explicit finite binary32 tuning constants c_location and c_variance, each in [1,16]. Inputs and all executed intermediates must remain finite. Every scalar operation rounds separately to nearest-even binary32 with canonical positive zero; no FMA/reassociation or tolerance window. Every output bit must match the independent Fraction oracle.

Let n be the number of initially valid samples. Compute median M of valid values and median absolute deviation MAD=median(abs(RN32(x-M))). Numeric sorting is used. An odd median is the middle element, canonicalized; an even median is RN32(RN32(a*0.5)+RN32(b*0.5)). No normalization factor multiplies MAD.

Use original observation order for every reduction. For each location residual d=RN32(x-M), u=RN32(d/RN32(c_location*MAD)); include only abs(u)<1 (strict). t=RN32(1-RN32(u*u)); w=RN32(t*t). A=ordered_sum(RN32(d*w)), B=ordered_sum(w). Location=RN32(M+RN32(A/B)).

For variance use u=RN32(d/RN32(c_variance*MAD)) and the same strict inclusion rule. t=RN32(1-RN32(u*u)), t2=RN32(t*t), t4=RN32(t2*t2). C=ordered_sum(RN32(RN32(d*d)*t4)); D=ordered_sum(RN32(t*RN32(1-RN32(5*RN32(u*u))))). Midvariance=RN32(RN32(RN32(n)*C)/RN32(D*D)); scale=sqrt(midvariance), correctly rounded by the existing arithmetic layer. n counts all initially valid samples, including biweight-rejected ones; no modified sample-size correction.

Output nine words: [u32 status,valid_count, f32 median,MAD,location,midvariance,scale, u32 location_inliers,variance_inliers]. Status0 success. Status1 no valid values. Status2 rounded MAD=0. Status3 zero location denominator or abs(D)<=RN32(n*2^-16). Failed records retain only status and valid_count; all other fields are zero. This differs deliberately from external zero-MAD fallbacks: callers must not interpret an unidentifiable noise scale as a successful zero-noise measurement. The denominator gate is a numerical contract, not a probabilistic confidence guarantee.

## Scientific scope

[Astropy biweight location](https://docs.astropy.org/en/stable/api/astropy.stats.biweight_location.html) and [midvariance](https://docs.astropy.org/en/stable/api/astropy.stats.biweight_midvariance.html) provide the estimator equations, commonly using c_location=6 and c_variance=9. [Photutils biweight background RMS](https://photutils.readthedocs.io/en/stable/api/photutils.background.BiweightScaleBackgroundRMS.html) demonstrates the background-noise use. Accessed 2026-10-03; independently implemented, no external code copied. Our fixed finite graph/status policy is not a claim of matching Astropy's native bytes or fallback behavior.

Midvariance is a robust empirical dispersion estimate. It is not an unbiased variance guarantee for every distribution, uncertainty of the estimated mean, photon shot-noise model, or covariance matrix. A background workflow may explicitly use positive estimates as inverse-variance photometry weights; that is an assumed local independent-noise model, not universal significance calibration.

## Background composition and kernels

An adapter tiles complete nonoverlapping boxes and records input/shape/parameter hashes. It submits bounded opcode63 jobs; only full-byte-verified status0 records with sufficient valid samples and positive midvariance enter location and dispersion meshes. Empty/degenerate estimates stay invalid. Existing IDW fills missing nodes and existing bilinear interpolation expands location and midvariance separately. Photometry weights are RN32(1/interpolated_midvariance), with zero for caller-masked pixels. No automatic shot-noise contribution or correlated-noise correction is added.

Research families reviewed: sorting versus selection for median/MAD; compact insertion sort versus fixed sorting networks; serial versus parallel robust reductions. Small bounded batches retain the declared RN32 reduction order. Fresh local32/64/128/256 and pack1/2/4 candidates are compiled and validated locally; no imported winner. [Khronos subgroups](https://docs.vulkan.org/guide/latest/subgroups.html) informs portable scheduling. Full per-MathSpec QUICK<=60s; no RT or AI execution; quick rates remain informational.
