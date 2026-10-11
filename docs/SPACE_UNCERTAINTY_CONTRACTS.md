# Photometric uncertainty contracts — v1.17.25

Primary sources read 2026-10-03:

- [Photutils calc_total_error](https://photutils.readthedocs.io/en/stable/api/photutils.utils.calc_total_error.html): background-only uncertainty plus source Poisson noise, effective gain, negative-signal and zero-gain conventions.
- [NIST: combining uncertainty components](https://physics.nist.gov/cuu/Uncertainty/combination.html): covariance-aware propagation for a linear combination. ASTRO uses the identity w^T(D+U^TU)w = sum_i(w_i^2 D_i) + sum_k(sum_i w_i U_ki)^2.

Original ASTRO implementation; no external source code copied. These two models are new library algorithms, not alternate names for previous workloads. No implicit physical-unit conversion or parameter fitting is performed.

## Common arithmetic and validation

All numerical inputs use eight-digit `binary32-hex` strings and `encoding=binary32-hex`. RN32 is round-to-nearest, ties-to-even after each specified operation, with gradual underflow and canonical positive zero. No FMA/reassociation. Every input, including masked values, must be finite; all executed intermediates must remain finite or CPU preparation rejects the job before dispatch. Full output bytes, including statuses and all diagnostic fields, require zero differing bits. Separate NumPy float64 equations are scientific diagnostics, never permission for output mismatch.

## 65 — SPACE_SOURCE_NOISE_MAP_F32_V1

Flat arrays `signal`, `background_variance`, `gain`, `valid`, equal length N1..65536; valid is integer0/1. Background variance and effective gain are nonnegative. Signal is in declared image units after background subtraction; background variance is in squared image units and excludes the source's Poisson term. Gain is countable events per image unit; callers must handle exposure and unit conversion explicitly. ASTRO accepts variance directly, whereas Photutils accepts standard deviation.

For each valid pixel, source_variance=RN32(signal/gain) only if signal>0 and gain>0, otherwise zero. Then total=RN32(background_variance+source_variance); error=RN32(sqrt(total)); inverse_variance=RN32(1/total). Negative signal adds no source Poisson term. Zero gain explicitly disables that term; it is not inferred gain. Masked pixels produce status1 and zero numerical output without evaluating divisions. If rounded total is zero, status2 and zero error/inverse are returned; no infinite weight is manufactured.

Five output words: `[u32 status, f32 source_variance,total_variance,error,inverse_variance]`; status0 succeeds,1 masked,2 zero total variance. On status2, source and total are zero. Partition by complete pixels. Analytic example: signal12,background_variance1,gain4 gives source3,total4,error2,inverse0.25. A negative signal with background4 gives total4; gain0 with background9 gives total9.

The formula is a supplied or plug-in noise model. An observed positive residual used as signal is not an unbiased estimator of source intensity, nor does it validate a likelihood or significance. Empirical background dispersion requires its own calibration. Background/source/correlation terms must not be double-counted.

## 66 — SPACE_LINEAR_FLUX_COVARIANCE_F32_V1

Input `flux[B,N]`, signed `weights[B,N]`, nonnegative `diagonal_variance[B,N]`, signed `factors[B,K,N]`. B1..128,N1..256,K0..16, with B*N*(K+1)<=262144. All rows use the same N and K; K0 is represented by one empty list per row. Weights are fixed coefficients of a linear estimator, not automatically inverse variances or normalized aperture areas. Zero weight omits a pixel without altering the remaining coefficients.

The real-valued covariance model is C=diag(D)+U^TU: D is the independent component in squared flux units; each U row is a loading in flux units for a standardized, mutually independent latent component. This representation guarantees positive semidefinite covariance over the real numbers without an approximate eigenvalue acceptance test. It is bounded to at most16 factors and does not estimate them from data.

Ordered numerical graph, increasing pixel index i and factor index k:

- F=sum RN32(w_i*f_i), with RN32 after each addition.
- Vd=sum RN32(RN32(w_i*w_i)*D_i), ordered RN32 additions.
- For each k: p_k=sum RN32(w_i*U_ki), ordered RN32 additions. Vc=sum RN32(p_k*p_k), ordered RN32 additions.
- V=RN32(Vd+Vc); error=RN32(sqrt(V)); standardized_flux=RN32(F/error).

Zero coefficients are skipped in all three reductions. Output eight words: `[u32 status,active_count,f32 flux,diagonal_variance,correlated_variance,total_variance,error,standardized_flux]`. Status0: active coefficients and positive rounded variance. Status1: no active coefficient; all other fields zero. Status2: active coefficients but rounded variance0; flux and active_count retained, other fields zero. Status2 is a valid degenerate-model diagnostic, never a finite-significance measurement. Nonzero model terms can underflow to zero under this explicit arithmetic contract. Partition only by whole observation rows.

Analytic case: flux[4,8], weights[1,1], D[2,2], U[[1,1],[1,1],[1,1]] gives F12,Vd4,Vc12,V16,error4,standardized_flux3. With weights[1,-1], the same common factors cancel: F-4,Vd4,Vc0,V4,error2,standardized_flux-2. Fractional weights square in variance propagation because this is a fixed linear combination of measured whole-pixel values; it is not a model of subdivided Poisson counting areas.

For a linear estimator, covariance propagation is exact in real arithmetic for the supplied covariance, without requiring a Gaussian distribution. Gaussian coverage or false-alarm probabilities do require additional assumptions and are not claimed. Common background offsets, flat-field modes or other low-rank correlations can be supplied; arbitrary survey covariance, fitted weights, nuisance estimation and physical calibration remain outside this contract.

## Adapter and integration

A provenance-bound adapter prepares complete image noise jobs, requires full raw GPU equality before producing variance/error/weight maps, and zeros unusable PSF weights. A separate adapter extracts explicitly supplied linear-statistic coordinates and signed coefficients from verified GPU variance maps. It checks unique in-bounds coordinates, explicit factor dimensions, complete inputs and hashes; invalid/zero-variance pixels cannot silently be included with nonzero coefficients. It does not infer apertures, factors or calibration.

The pipeline uses actual GPU noise outputs both for an existing PSF scan and for the new covariance-aware linear flux statistic. Its controlled common-mode example tests variance addition and cancellation. The PSF scan remains diagonal-weighted; the correlated uncertainty is computed for the separate fixed linear statistic, not silently attributed to a generalized least-squares PSF fit.

COLD-ZERO and the <=60s total per-MathSpec QUICK contract remain mandatory. Quick rates are INFORMATIONAL, with no release speedup, energy/record or SoC-efficiency claim. Neither new workload has a ray/BVH or AI execution path.
