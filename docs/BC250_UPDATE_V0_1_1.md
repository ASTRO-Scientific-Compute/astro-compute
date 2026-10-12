# BC-250 Reference Run — v0.1.1 Update / Bugfix

**QUICK_DIAGNOSTIC_ONLY. 48/48 complete warmup/final-output checks PASS / COLD ZERO. Sustained: NO. Independent external reproduction: NO.**

Reference hardware: AMD BC-250, **24 active CUs**, **2000 MHz target**, Vulkan / RADV GFX1013. CU count comes from runtime KFD SIMD topology, not a kernel constant. Actual clocks and PPT are recorded for every observation in the [compact report](BC250_UPDATE_V0_1_1.json).

Environment: Linux Mint 22.3; kernel `7.0.0-38-generic`; Mesa 26.2.4 - kisak-mesa PPA; Mesa 26.2.4 - kisak-mesa PPA (LLVM 21.1.8); Python 3.12.3; NumPy 1.26.4.

## What was compared

A: original public source at `6850a05fe116cbaa9a74f7791933f89248bbf2f4` (same demo runtime as v0.1.0). B: v0.1.1 resource fixes with baseline command recording. C: v0.1.1 with optional command-buffer reuse for FFT256, Convolution and XCORR. FIR stays baseline and is a noise/control observation, not an optimized path.

Two runs per arm, in **A → B → C → C → B → A** order. Each run stops at four fixed MathSpecs / eight DIRECT–TILED trials. Inputs use seed 271828, scale 1; local=64, pack=1, eight dispatches per batch; warmup 2000 ms, measurement 1000 ms. Canonical math and shader-generating code are byte-equivalent. The one changing host-policy axis B/C is command reuse; no workload, pack, local-size or mathematical work-count change.

## All natural-work observations

Rates below are medians of two runs, in the stated **units/s** (no legacy science/s scaling). Ratios are descriptive QUICK observations, not accepted or statistically established speedups.

| MathSpec | Family | Unit/s | A: old | B: update | C: reuse | B/A | C/B |
|---|---|---|---:|---:|---:|---:|---:|
| SPACE_GWOSC_FFT256_V1 | DIRECT | FFT256_window/s | 1,632.65 | 1,620.69 | 1,625.48 | 0.9927× | 1.0030× |
| SPACE_GWOSC_FFT256_V1 | TILED | FFT256_window/s | 59,535.11 | 60,129.45 | 61,606.23 | 1.0100× | 1.0246× |
| SPACE_GWOSC_CONVOLUTION_V1 | DIRECT | convolution_sample/s | 67,467,569.33 | 69,540,878.29 | 70,841,270.04 | 1.0307× | 1.0187× |
| SPACE_GWOSC_CONVOLUTION_V1 | TILED | convolution_sample/s | 69,519,470.17 | 67,788,259.04 | 72,078,785.11 | 0.9751× | 1.0633× |
| SPACE_GWOSC_XCORR_V1 | DIRECT | cross_correlation_lag/s | 347,308.96 | 343,917.92 | 347,518.87 | 0.9902× | 1.0105× |
| SPACE_GWOSC_XCORR_V1 | TILED | cross_correlation_lag/s | 684,311.61 | 688,809.83 | 686,651.75 | 1.0066× | 0.9969× |
| SIGNAL_FIR_ACCUMULATE_I16_V1 | DIRECT | filtered_sample/s | 23,586,680.51 | 23,455,380.03 | 22,372,552.05 | 0.9944× | 0.9538× |
| SIGNAL_FIR_ACCUMULATE_I16_V1 | TILED | filtered_sample/s | 24,583,983.59 | 23,921,357.50 | 25,060,064.72 | 0.9730× | 1.0476× |

TILED Convolution has a +6.33% C/B median difference in this short sample. The unchanged FIR control also moves by about −4.62% / +4.76%; this is evidence of run variability. Therefore **PERFORMANCE_IMPROVED is not assigned**, no general speedup is claimed, and reuse remains opt-in. Repeated sustained A/B with the full performance gates and independent reproduction is still required.

## GPU and host evidence

Each retained trial includes measured native GPU time, measurement wall time, GPU/wall ratio, dispatch/submission counts, inter-batch timestamp gaps, telemetry coverage, SCLK and PPT, natural work and typed algorithmic operation rates. New trials also retain native command-recording/reuse counters and measurement-only record/submit/retire/query totals. Queue submissions matched measurement batches and dispatch count was eight times submissions in every run. Native reuse receipts passed on all eligible C trials; FIR receipts confirm reuse disabled.

PPT is a driver diagnostic, not an isolated SoC power rail or optimization objective. VGPR/SGPR/scratch/spill/occupancy remain UNAVAILABLE. Complete per-batch traces, raw outputs and benchmark hash inventories are not retained. Correctness is checked before cleanup; no sampling or cached PASS is substituted.

The new task-boundary cleanup receipts observed **53,248–348,160 bytes** of Python-process RSS reduction per task in these small fixtures. This is a measured local change, not total process savings, a GPU-memory measurement or a prediction for large research jobs. The earlier native per-batch vector is structurally eliminated; a physical peak-RAM or SSD-write-volume A/B measurement was not collected, so no percentage savings is claimed.

The JSON preserves every run including conservative one-job end-to-end rate, typed mathematical operations and legacy science/s. These metrics are different scopes: the natural resident-work rate must not be described as end-to-end unique research throughput. Historical v0.1.0 reference files are unchanged.

## Reproduce the bounded modes

```bash
bash run_gpu_demo.sh --runtime baseline --profile demo-baseline.json
bash run_gpu_demo.sh --runtime reuse --profile demo-reuse.json
```

Run one GPU benchmark at a time. Only compact profiles are retained; no unrestricted search or extra MathSpec is enabled.
