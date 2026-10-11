# Paired complex cross-spectrum and magnitude-squared coherence — V1

Contract fixed before implementation. New primitive opcode 78, `SPACE_CROSS_SPECTRAL_COHERENCE_F32_V1`; one distinct mathematical operation, not an alias for FFT, periodogram, Welch auto-spectrum or lagged correlation. Primary equations: [SciPy coherence](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.coherence.html) and [SciPy csd](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.csd.html), browsed 2026-10-03 UTC. Original implementation of equations; no external code copied.

## Strict supplied-spectrum input

Exactly these payload fields: `encoding=binary32-hex`, `cross_convention=CONJ_X_TIMES_Y`, `replicate_contract=MATCHED_ORDERED_SEGMENTS`, `power_normalization=MEAN_SUPPLIED_BIN_PRODUCTS`, `spectrum_unit_x`, `spectrum_unit_y`, `frequency_grid_id`, `bins`.

The three labels must be nonblank strings of at most 64 characters. `bins[B][R][4]` contains `[X_real, X_imag, Y_real, Y_imag]`, with 1 <= B <= 256 and a common 2 <= R <= 64. Each component is a finite eight-digit binary32 hex word, either signed zero or magnitude in [2^-28, 2^16]. Reject other values and unknown/missing fields. No implicit rescaling, clipping, zero substitution or inferred Fourier alignment. Each record is one frequency/channel pair; the caller asserts matched ordered segment pairs and consistent Fourier normalization and grid. Correlation between segments is not tested; no significance or effective-degrees-of-freedom claim.

Units are those of the supplied complex amplitudes: auto-products have their respective squared units, cross-products the product of units, coherence is dimensionless. Input segments may already have been transformed/windowed/detrended explicitly upstream, but this primitive performs none of these operations. It does not create a PSD per Hz or apply a one-sided factor, Welch defaults, bias correction or confidence interval.

## Canonical operation order

Use separate round-to-nearest-ties-even binary32 operations for every multiply/add/subtract/divide, with the existing software-arithmetic contract and canonical arithmetic zero; no FMA. For every replicate in increasing index order:

- px = RN(RN(xr*xr) + RN(xi*xi)); py analogously.
- re = RN(RN(xr*yr) + RN(xi*yi)).
- im = RN(RN(xr*yi) - RN(xi*yr)), explicitly conj(X)*Y.
- Accumulate each of these four terms into its separate sum, starting from +0, in replicate order.

Divide each sum by exactly representable R to obtain Pxx, Pyy, RePxy and ImPxy. Let uint32 status bit 0 indicate Pxx == 0, bit 1 indicate Pyy == 0. For status != 0 coherence is the zero sentinel for an **undefined** quantity. For status == 0:

`coherence = RN(RN(RN(RePxy*RePxy) + RN(ImPxy*ImPxy)) / RN(Pxx*Pyy))`.

No clamp to one: small rounded overshoots are preserved and diagnosed. A tiny cross numerator may underflow according to the arithmetic contract; this is not hidden quantization. If a channel has any nonzero component, its mean power is at least 2^-62; therefore the nonzero power product is at least 2^-124. Maximum sum powers are bounded by 2^39 and all subsequent products remain finite. These bounds avoid a spurious zero denominator/overflow while retaining very weak absolute coherence.

Output is B x 6 uint32 words: `[status, bits(Pxx), bits(Pyy), bits(RePxy), bits(ImPxy), bits(coherence)]`. Status is an integer word, never a float. Partition only complete independent bins, preserving all replicates and their order within each bin. Exact analytic golden: R=2, both pairs X=1+0i,Y=2+0i => [0,1,4,2,0,1] with the first word status.

## Independent diagnostics and validation obligations

Full output, warmup and final, must match an independent Fraction/RN32 CPU oracle with **zero differing bits**. A second independent NumPy complex128 reference uses mean(abs(X)^2), mean(abs(Y)^2), mean(conj(X)*Y) and their exact formula at binary64 precision. Fix diagnostic limits before tests: nonzero auto-power relative error <= 2e-5; complex cross error divided by sqrt(Pxx64*Pyy64) <= 2e-5; absolute coherence error <= 2e-5; valid coherence must be in [-2e-5, 1+2e-5]. Source all-zero channels must match status exactly; undefined coherence must retain its explicit status and zero sentinel. These are scientific diagnostics, not a bit tolerance or a promise about arbitrary physical data.

Probe gain/phase, negative correlation, pure imaginary cross-spectrum, cancellation to zero, orthogonal replicate phases, zero X/Y/both, negative zero, minimum/maximum component scale, reciprocal scale changes, extreme mixed dynamic range, maximum R and B, held-out seeds, nonfinite and out-of-contract inputs, actual one-bit shader/output corruptions and invalid native packets. Verify full inherited library, partition reassembly, unchanged prior MathSpecs/kernels/snapshots, fresh COLD-ZERO and worker/miner entry points. QUICK total <= 60 s per MathSpec; no release A/B or SoC efficiency claim from QUICK.

The initial release delivers the supplied-spectrum primitive and source-bound worker summaries. A later explicit FFT-to-coherence adapter can construct bins from actual verified GPU FFT outputs. No implicit workflow or normalization is claimed in this primitive release. No AI executor or RT acceleration is introduced.
