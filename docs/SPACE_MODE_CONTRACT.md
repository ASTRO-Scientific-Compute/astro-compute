# Half-sample mode — ASTRO v1.17.24

Primary source: Bickel and Fruehwirth, *On a Fast, Robust Estimator of the Mode*, [arXiv:math/0505419](https://arxiv.org/abs/math/0505419), Appendix pp.18–19, visually read on 2026-10-03. Published DOI: 10.1016/j.csda.2005.07.011. Original ASTRO implementation; no third-party source code copied. The appendix's second n=3 inequality repeats '<'; we interpret the stated closest-pair rule, using '>' for the right pair. Ties in larger windows select the first minimum, with an initialized first candidate so constant samples are defined.

## Input and partition

`SPACE_HALF_SAMPLE_MODE_F32_V1`, opcode64: `encoding=binary32-hex`, `samples[B,N]` finite binary32 and `valid[B,N]` integer0/1. B1..128,N1..256,B*N*N<=2097152. All payload values, including masked values, must be finite. Work is partitioned only by complete independent rows. Every executed arithmetic intermediate must remain finite or input preparation rejects the job. No implicit quantization, randomness, histogram binning, KDE bandwidth, or external software dependency.

## Numerical graph

RN means round-to-nearest ties-to-even binary32 after each operation; +0 is canonical. Sort valid values by numeric value. At each size n>=4 choose k=ceil(n/2) consecutive sorted values with smallest RN(last-first) width, breaking equal rounded widths by lowest sorted start index. Continue only inside that interval. Count these halvings as rounds. Stop at size <=3:

- One value: canonical value.
- Two values: RN of the exact real mean (a+b)/2. The CPU rounds an exact rational. The GPU uses RN(RN(a+b)*0.5) when both absolute values are <=0x7effffff (max_finite/2); otherwise RN(RN(a*0.5)+RN(b*0.5)). This avoids overflow and preserves constant subnormal samples.
- Three values: compare RN(b-a) and RN(c-b). Select and average the closer pair by the same exact-mean rule; on equal rounded gaps return canonical b and retain the three-value terminal interval.

The selected terminal interval supplies low/high, RN(high-low), count and global sorted start. A closest-pair termination on n=3 reduces the terminal count to2 but does not add a halving round. GPU insertion sort and iterative interval selection are independent of the CPU built-in sort and recursive oracle. RN width ties can differ from an infinite-precision half-sample estimate; this is an explicit finite-precision contract. No FMA or reassociation.

## Output and validation

Each row is nine uint32 words: `[status, valid_count, mode_f32, low_f32, high_f32, width_f32, terminal_count, halving_rounds, sorted_start]`. Status0 succeeds. Status1 has no valid sample and all eight other words zero. A constant sample is a valid mode estimate, including canonical zero; this does NOT assert zero measurement noise. All n>=1 are mathematically valid; the image adapter separately enforces minimum valid counts.

Every byte of all output fields must match the independent CPU reference (0 differing bits). Analytic vectors cover n1/n2/all n3 branches, odd/even recursive sizes, ties, masks, negative/zero/subnormal values, constant subnormal/max-finite samples,128 deterministic mean-rounding pairs, contamination and maximum dimensions. A separate NumPy float64 recursive checker validates mode, endpoints, count, rounds and sorted start on preselected exact-dyadic diagnostic inputs where rounded and exact widths agree. That diagnostic tolerance never relaxes byte correctness. Rounded-width tie edge cases are tested against the declared RN graph separately.

## Image use and limits

A provenance-bound adapter tiles complete image boxes, checks full raw GPU output and builds a valid mode mesh. Existing IDW, bilinear interpolation and weighted PSF scans consume it; no extra workload IDs are assigned. Empty or undersampled boxes remain missing and all-invalid interpolation fails. A modal sky background is useful when the background dominates each box; it is not guaranteed for multimodal images, dense sources, or contamination approaching half the sample. No bias, uncertainty, calibrated significance, photon-noise or performance advantage is claimed. Supplied photometric weights remain explicit and are not estimated from the modal interval width.
