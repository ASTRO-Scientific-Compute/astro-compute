# BC-250 Reference Demo Results

**Reference hardware: AMD BC-250 — 24 CU active — 2000 MHz target — Vulkan / RADV / GFX1013.**

> These are short diagnostic reference measurements from the public bounded demo, not sustained production benchmarks.

**Result class: QUICK_DIAGNOSTIC_ONLY · Sustained: NO / NOT_TESTED · Independent external reproduction: NO.**

This is one maintainer-operated reference run of the four-task public demo, including all eight DIRECT/TILED trials. Every row passed the complete warmup/final-output COLD ZERO check (0 differing bits). This is not a leaderboard, an ASTRO peak-capacity claim or a production promotion.

## Software and hardware identity

| Field | Recorded value |
|---|---|
| Demo release | [`v0.1.0-demo`](https://github.com/ASTRO-Scientific-Compute/astro-compute/releases/tag/v0.1.0-demo) |
| Executed source commit | [`48a9ddc5ff00cd174b8f7cb58f9933af22f1df72`](https://github.com/ASTRO-Scientific-Compute/astro-compute/tree/48a9ddc5ff00cd174b8f7cb58f9933af22f1df72) |
| Source binding | All 377 release files matched before and after the run; compilation/job binding checked transiently by the demo |
| Run interval (UTC) | 2026-10-11 18:59:59.804734 – 19:00:30.708638 |
| GPU | AMD BC-250 (RADV GFX1013), vendor/device `0x1002:0x13fe`; physical integrated GPU |
| Active CUs | 24: runtime KFD `simd_count=48`, `simd_per_cu=2`; not a hardcoded architecture maximum or an occupancy measurement |
| GPU clock target | 2000 MHz; runtime KFD maximum agrees with the operator target. Measured averages appear below; the clock was not held constant |
| OS / kernel | Linux Mint 22.3 / Linux `7.0.0-38-generic`, x86_64 |
| Mesa / backend | Mesa `26.2.4 - kisak-mesa PPA`, RADV, Vulkan |
| Vulkan | Device API `1.4.354`; instance `1.3.275` |
| Python / NumPy | `3.12.3` / `1.26.4` |
| Native compiler | `c++ (Ubuntu 13.3.0-6ubuntu2~24.04.1) 13.3.0` |
| Workload | Synthetic fixture seed `271828`, scale `1`; same input/contract for both families |
| Trial configuration | Local size `64`, pack `1`, eight dispatches/submission; 2000 ms warmup then approximately 1000 ms measurement per family |
| Whole demo wall time | 30.724 s, including native build and all four tasks |

The development Fast Search was stopped before this run. The desktop remained active; exclusive use by all OS/graphics clients was not established. No clock or power policy was changed for this run. Telemetry was matched through Vulkan PCI identity. SCLK is the time-weighted average of clock samples; PPT is the average of available driver power samples, not an isolated SoC-rail measurement.

## Measured natural work throughput

The denominator is **measurement wall time**, not GPU time alone. Each trial repeats resident input. Full-output correctness is checked after warmup and at completion, not on every repeated dispatch as unique research work. All rows are short observations; a single run supplies no statistical confidence interval or sustained winner.

| MathSpec | Family | Correctness | Natural work units/s | Unit | Mean SCLK MHz | Mean PPT W |
|---|---|---|---:|---|---:|---:|
| FFT256 | DIRECT | PASS / COLD ZERO | 1,619.825 | FFT256 windows/s | 2000.00 | 73.02 |
| FFT256 | TILED | PASS / COLD ZERO | 59,942.040 | FFT256 windows/s | 2000.00 | 73.28 |
| Convolution | DIRECT | PASS / COLD ZERO | 68,713,122.768 | convolution samples/s | 1967.55 | 74.74 |
| Convolution | TILED | PASS / COLD ZERO | 69,194,198.985 | convolution samples/s | 1920.00 | 73.08 |
| XCORR | DIRECT | PASS / COLD ZERO | 345,307.682 | correlation lags/s | 2000.00 | 73.66 |
| XCORR | TILED | PASS / COLD ZERO | 687,193.613 | correlation lags/s | 2000.00 | 80.25 |
| Integer FIR | DIRECT | PASS / COLD ZERO | 22,580,247.350 | filtered samples/s | 1969.27 | 74.96 |
| Integer FIR | TILED | PASS / COLD ZERO | 25,045,559.324 | filtered samples/s | 1920.00 | 73.66 |

## Exact tasks and useful work

| Display name | MathSpec ID | One dispatched job |
|---|---|---|
| FFT256 | `SPACE_GWOSC_FFT256_V1` | Four 256-point FFT windows from 1024 synthetic samples |
| Convolution | `SPACE_GWOSC_CONVOLUTION_V1` | 1024 output samples, nine clamped taps/sample |
| XCORR | `SPACE_GWOSC_XCORR_V1` | Two 513-sample streams; 129 output lags, −64 through +64 |
| Integer FIR | `SIGNAL_FIR_ACCUMULATE_I16_V1` | 257 samples, 37 signed-int16 coefficients; 257 filtered outputs |

`natural units/s = completed dispatches × natural units per job / measurement wall seconds`.

Fixture and kernel generators are included in the linked source revision. Both families execute the same canonical mathematical task; the fixed two-family comparison does not run Census/AI Fusion search. These small default fixtures do not demonstrate the maximum throughput of the GPU or of the full development executor.

## GPU and measurement evidence

| MathSpec / family | Native GPU ms | Wall ms | GPU/wall | Dispatches | Submissions | Telemetry coverage | Samples |
|---|---:|---:|---:|---:|---:|---:|---:|
| FFT256 / DIRECT | 983.574 | 1007.516 | 97.62% | 408 | 51 | 98.95% | 96 |
| FFT256 / TILED | 845.661 | 1000.433 | 84.53% | 14,992 | 1,874 | 99.44% | 96 |
| Convolution / DIRECT | 577.885 | 1000.020 | 57.79% | 67,104 | 8,388 | 98.55% | 95 |
| Convolution / TILED | 584.973 | 1000.052 | 58.49% | 67,576 | 8,447 | 98.66% | 96 |
| XCORR / DIRECT | 947.587 | 1001.194 | 94.65% | 2,680 | 335 | 99.42% | 97 |
| XCORR / TILED | 929.764 | 1000.172 | 92.96% | 5,328 | 666 | 98.95% | 95 |
| Integer FIR / DIRECT | 478.211 | 1000.035 | 47.82% | 87,864 | 10,983 | 99.05% | 97 |
| Integer FIR / TILED | 451.431 | 1000.025 | 45.14% | 97,456 | 12,182 | 98.97% | 97 |

GPU/wall is a timestamp ratio, **not the fraction of active CUs or a hardware occupancy counter**. It is approximately 45–48% for Integer FIR here. The remaining wall time is outside the measured GPU intervals; no sustained-performance PASS is implied. Clock averages range from 1920 to 2000 MHz. Temperature and power do not determine the optimization objective.

The [compact profile](BC250_REFERENCE_RUN_V0_1.json) includes measured between-submission GPU gaps (count, sum and maximum), typed useful-work counts, legacy science/s and the exact recorded values behind the rounded tables. Intra-batch per-dispatch gaps, hardware queue/compute duty counters, occupancy and register/scratch/spill receipts are UNAVAILABLE. Telemetry coverage is the sampled clock time span over the measurement window, not a proof of continuous GPU activity.

## Algorithmic operations and end-to-end scope

Useful algorithmic counts per dispatched job: FFT256 **40,960 FP32** operations; Convolution **18,432 FP32**; XCORR **123,905 FP32**; Integer FIR **8,843 INT32 products and 8,843 INT64 additions**, kept separate. These count canonical arithmetic, not native GPU instructions. Multiply plus add counts as two useful operations; the RN32 contract rounds them separately, with no claim that a fused hardware FMA executed. Addressing, control, packing and comparisons are excluded. A faster implementation does not increase these counts.

| MathSpec / family | Effective FP32 ops/s | Effective INT32 ops/s | Effective INT64 ops/s | One-job end-to-end natural units/s |
|---|---:|---:|---:|---:|
| FFT256 / DIRECT | 16,587,004.988 | — | — | 1.210 |
| FFT256 / TILED | 613,806,490.844 | — | — | 1.206 |
| Convolution / DIRECT | 1,236,836,209.828 | — | — | 313.093 |
| Convolution / TILED | 1,245,495,581.732 | — | — | 312.738 |
| XCORR / DIRECT | 331,669,366.876 | — | — | 40.118 |
| XCORR / TILED | 660,052,128.859 | — | — | 40.179 |
| Integer FIR / DIRECT | — | 776,953,802.772 | 776,953,802.772 | 78.305 |
| Integer FIR / TILED | — | 861,781,638.534 | 861,781,638.534 | 78.575 |

“—” means that type is not part of the stated counted arithmetic subset; it is not a measured zero hardware-instruction rate. The last column follows the demo’s conservative **one validated job** convention: one job’s natural units divided by preparation, candidate compilation, warmup, repeated execution, readback and validation time. It does not count all repeated resident dispatches as unique research completions and excludes the once-per-demo native build. It must not be confused with the measurement-window throughput above.

## Reproduce this public demo

Install the [documented dependencies](GPU_DEMO.md), then use a clean checkout:

```bash
git clone --branch v0.1.0-demo --depth 1 https://github.com/ASTRO-Scientific-Compute/astro-compute.git
cd astro-compute
git rev-parse HEAD
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
bash run_gpu_demo.sh --gpu 0 --profile reference-demo.json
```

The commit must be `48a9ddc5ff00cd174b8f7cb58f9933af22f1df72`. This run used the exact Python/NumPy versions above. Select the physical Vulkan device index appropriate to your host and stop competing GPU benchmarks before measuring. `--gpu 0` selected the BC-250 in this run. The demo itself does not set a 2000 MHz target on another computer. Different driver, clock, input, device or host activity requires its own reported context; no particular rate is guaranteed.

The four-MathSpec limit remains enforced. The demo builds temporary binaries, validates complete outputs and removes temporary data on normal completion. This run left no temporary demo workspace. Only the compact profile and this report are published; no raw input/output, shader/source hash inventory, telemetry stream, local state tree or historical benchmark result is attached.

External human review and independent external hardware reproduction remain **PENDING**. An external run can use the [reproduction template](EXTERNAL_REPRODUCTIONS.md). [Licence terms](../LICENSE) and the distinction between [QUICK and sustained results](BENCHMARKS.md) remain unchanged.
