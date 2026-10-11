# Seven historical SPACE contracts: zero-bit amendments, v1.17.12

The original contracts in `space_domain/contracts/` remain unmodified. The seven existing public workload IDs now route through the science library with `contract_revision=ZERO_BIT_AMENDMENT_V2`. Each MathSpec binds its original contract by SHA256. This amendment retains the scientific operator and exact supplied input bits, while specifying rounding, reduction order and serialization that the old tolerance/multiset contracts did not uniquely define. Historical output bytes are not promised to be identical.

| Existing ID | Preserved operation | Deterministic amendment |
|---|---|---|
| SPACE_GWOSC_FFT256_V1 | Real, nonoverlapping FFT256, no window | Canonical radix-2 binary32 FFT, 256 interleaved complex bins |
| SPACE_GWOSC_CONVOLUTION_V1 | Symmetric FIR9 /25, edge clamp | Frozen RN32 weights, ascending nine products and additions, separate rounding |
| SPACE_GWOSC_XCORR_V1 | H1[i] × L1[i+lag], lags −64…64, valid overlap | Ascending input index RN32 dot product; retains historical lag sign |
| SPACE_GWOSC_NXCORR_V1 | Dot product divided by overlap-energy norm | Three ascending RN32 sums, RN32 product/root/division on GPU; rounded zero denominator yields +0 |
| SPACE_EXOPLANET_EARTHSIZE_FILTER_V1 | Select packed radius 1…1800, keep duplicates | Stable input order; N+1 uint32 output: count, matches, zero padding |
| SPACE_GWOSC_WELCH_PSD_V1 | Periodic Hann256, hop128, fs4096, window power96, one-sided density | Double-single window/FFT; RN32 complex bins, power/density and ascending segment mean |
| SPACE_GWOSC_WHITENING_V1 | Frequency-domain coefficients on identical Hann/Welch grid | Same double-single FFT, RN32 scale and component products; caller supplies 129 positive PSD bins |

A stream is already normalized `float32(strain*1e21)`, supplied as explicit `binary32-hex`. There is no second normalization, integer quantization, resampling or implicit PSD floor. The full 32-second stream has 131072 samples and 1023 overlapping Hann segments. Correlation also supports the 16384-sample central four seconds. The generic `_F32_` convolution/correlation contracts remain distinct: their boundary and lag conventions differ. Whitening returns frequency coefficients; it does not implement inverse FFT or full-stream whitening.

## Two separate checks

Every accepted GPU result must exactly equal its independent CPU implementation: **zero differing bits**, including padding and zero signs. Tests also compare all real-data outputs with independent double-precision scientific formulas and the original error budgets. Those diagnostic budgets do not relax byte equality.

The first scalar-binary32 Hann FFT passed CPU/GPU byte comparisons on test vectors, but its CPU graph failed the historical whitening budget for 722 complex coefficients on the full real H1 stream. It was replaced before release. Accurate cancellation-sensitive bins require additional internal precision; identical wrong scientific approximations would not be an adequate validation result.

## Canonical extended FFT

`RN` means binary32 nearest, ties to even, gradual underflow, positive arithmetic zero. Every expression below denotes a separate rounded operation. Components represent `hi + lo`; this is a defined two-component algorithm, not a claim of correctly rounded native binary64 throughout.

- `TwoSum(a,b)`: `s=RN(a+b)`, `z=RN(s-a)`, `e=RN(RN(a-RN(s-z))+RN(b-z))`; return `(s,e)`.
- Component addition: `(s,e)=TwoSum(a.hi,b.hi)`; return `TwoSum(s,RN(RN(e+a.lo)+b.lo))`.
- Component negation changes both signs, canonicalizing zero. Subtraction adds the negated pair.
- Component multiplication: `p=RN(a.hi*b.hi)`; `e=RN(exact(a.hi*b.hi)-p)`; `c=RN(RN(a.hi*b.lo)+RN(a.lo*b.hi))`; return `TwoSum(p,RN(e+c))`. The lo×lo term is deliberately absent from this defined algorithm.
- The CPU extracts the exact binary32 product residual in binary64 (at most 48 significand bits). The GPU independently forms the exact product of integer significands and rounds its residual. No GPU FP64 or tensor capability is needed.
- Frozen twiddle/window high components are RN of the nominal coefficient; low components are RN of its residual. Decimal90 generation, exact cardinal axes and source hashes make tables reproducible. Runtime transcendental functions are not used.
- Multiply `(input,0)` by the two-component Hann value, bit-reverse the inputs, then run radix-2 DIT stages 2…256. Complex butterfly products/additions use the above operations. Round each final component as `RN(hi+lo)` before PSD/whitening arithmetic.

The multi-component and Two-Sum methodology is described by [Hida, Li and Bailey](https://www.davidhbailey.com/dhbpapers/qd.pdf). ASTRO's binary32/integer implementation is original; no external source was copied. [SciPy's Welch definition](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.welch.html) documents segmented spectral density and averaging. Exact ASTRO parameters and formulas are preserved in the original local contracts.

## CPU reference and staged GPU work

Full streams use separate NumPy float32 ufuncs and ordered `cumsum(dtype=float32)`, independently of GPU integer arithmetic. Host ties, subnormals, square-root rounding and reduction order are probed against the exact Fraction oracle before preparing a job. Random operations, product residuals and a full FFT are also tested against Fraction. See [NumPy cumsum](https://numpy.org/doc/stable/reference/generated/numpy.cumsum.html); pairwise sum is not interchangeable with the specified ascending reduction.

Filter compaction uses a GPU count pass for blocks of 256 rows, followed by deterministic output-slot selection. Welch uses a GPU window/FFT/density pass per segment, followed by the ordered per-bin mean. The native runner inserts an explicit compute-write → compute-read/write barrier between these passes on every repetition. Both passes are included in dispatch timing. Splitting final output records still executes the complete required prepass; no CPU-derived offsets, FFTs or partial sums are supplied to the GPU.

CPU reference preparation rejects invalid shapes, nonfinite values and intermediate overflow. Public verification uses cached manifests with checked raw and normalized file hashes. H1 FFT/spectral data are GW150914-v2; the inherited detector-pair cache actually identifies GW150914-v3 at GPS1126259447, so the report names that version explicitly instead of repeating the old contract's v2 prose. Cached data are not described as a fresh download or credited research work.

## Remaining boundary

In v1.17.12, two historical RT triangle-hit commissioning routes remained blocked. In v1.17.13 both received independent zero-bit implementations within the bounded [triangle contract](TRIANGLE_ZERO_BIT_CONTRACT.md). The three existing exact integer radius/RDF RT paths remain available. All six scientific domains retain their existing implementations. The complete science roadmap, tensor execution, global optimality and continuous saturated node execution are not claimed by this release.
