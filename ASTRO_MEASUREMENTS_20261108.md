# ASTRO — measured results and reference accuracy

Date: 2026-11-08. Physical local runs: RTX 4060 Ti using CUDA and two RX 470 cards using Vulkan.
These measurements cover complete research worksets in the development engine. They are not results from the newly packaged synthetic benchmark.
All numbers below come from saved execution and verification records. Times are seconds; decimal points and comma thousands separators are used throughout.

## 1. Complete workset processed in each run

| Domain | Fully processed scope per workset |
| --- | --- |
| BIO / SBML | 5 distinct models; all 51 requested time points, both species and all 128 replicas per model |
| SIGNAL / MIT-BIH | The complete first lead of all 48 records; 31,200,000 samples |
| CHEM / NIST Lennard–Jones | All 4 configurations × 3 schemes = 12 combinations |
| SPACE | 1 adapted Kepler orbit with 128 replicas |
| PDEBench / Burgers | 10,000 distinct trajectories × 201 time points × 1,024 cells = 2,058,240,000 values |

Each workset required 64 internal chunks and 69 graph evaluations. A chunk is a partition of the complete work, not a separate completed research job.
The first campaign processed the same workset six times; the RTX rerun added two executions.
Total: **8 complete executions, 1 distinct workset, 7 comparison repeats and 552 internal graph evaluations**.

The first chunk combined several scientific domains in one persistent session on one physical GPU. Subsequent chunks were PDE work. This is not evidence of a balanced multi-domain mixture throughout the entire run.
Coverage is limited to the supported cases listed above; it does not cover the full SBML suite or a complete Basilisk workflow. SPC/E is excluded from accepted work because its reference check failed.

## 2. First full campaign: six physical sessions

CPU time covers the process tree. GPU time is the sum of recorded GPU event intervals.

| GPU | Output mode | Full E2E (s) | Process-tree CPU (s) | Scientific GPU compute (s) | GPU compression (s) |
| --- | --- | ---: | ---: | ---: | ---: |
| RTX 4060 Ti | raw | 376.669036 | 104.632438 | 93.191197 | 0.000000 |
| RTX 4060 Ti | qgc1 | 787.385656 | 264.157173 | 94.110800 | 1.489654 |
| RX 470 ×8 | raw | 394.860040 | 148.740429 | 34.864394 | 0.000000 |
| RX 470 ×8 | qgc1 | 250.895690 | 291.114153 | 35.020317 | 2.217084 |
| RX 470 ×1 | raw | 250.562766 | 160.009426 | 34.252381 | 0.000000 |
| RX 470 ×1 | qgc1 | 248.467996 | 288.192059 | 34.257332 | 2.110674 |

Whole campaign: **3,149.743729 s wall time; 1,514.892634 s process-tree CPU time**.
This includes initial compressed-reference construction and the cost of interrupted CPU preparation. Resuming that preparation did not repeat GPU work.
Peak backend buffer allocation was **1,300,558,192 bytes on RTX** and **1,325,724,144 bytes on Radeon**, both below 2 GiB. These are backend buffers, not total driver/context VRAM.

Full audited compression consumed more CPU time on all three cards. These observations do not establish a universal E2E speedup or a stable device ranking.

## 3. Complete RTX rerun

| Output mode | Full E2E (s) | Process-tree CPU (s) | Scientific GPU compute (s) | GPU compression (s) |
| --- | ---: | ---: | ---: | ---: |
| raw | 170.713195 | 93.219888 | 91.431878 | 0.000000 |
| qgc1 | 270.267095 | 255.255319 | 94.130787 | 1.476443 |

Both sessions together: **442.612778 s wall time; 350.033850 s process-tree CPU time**.
All 128 raw output files and all 128 compressed output files matched the corresponding previous RTX outputs.

| RTX host phase | Earlier measurement (s) | Rerun (s) |
| --- | ---: | ---: |
| Raw output persistence | 255.100641 | 17.861920 |
| Compressed output persistence | 21.513768 | 4.408518 |
| Compressed-reference reading, integrity checking and sealing | 470.862260 | 105.9175 |
| Independent full decoding and bit comparison | 195.814723 | 145.3641 |

Host waiting time decreased. The experiment does not isolate TRIM as the cause from cache, writeback and other system-state changes.
Phase intervals can overlap and are not additive. Persistence uses operating-system buffering; E2E does not guarantee completion of an fsync-based durable write.
Canonical-reference preparation recorded **128 cache hits and 0 misses**, taking **1.294022 s wall time and 1.244084 s process-tree CPU time**.

## 4. Data transfer and compression

GPU-to-host counts include codec metadata and raw fallback bytes.

| Domain | Original bytes | Actual QGC1 GPU-to-host bytes | Original / transferred |
| --- | ---: | ---: | ---: |
| BIO | 522,240 | 503,528 | 1.037162 |
| SIGNAL | 260,000,000 | 23,466,920 | 11.079426 |
| SPACE | 1,198,080 | 1,198,144 | 0.999947 |
| CHEM | 288 | 1,056 | 0.272727 |
| PDE | 16,465,920,000 | 15,160,452,192 | 1.086110 |

Total: **16,727,640,608 → 15,185,621,840 bytes; 9.218388% less transferred data**.
Each session recorded 13,015 scientific dispatches; each QGC1 session added 12,189 compression dispatches.
Across all eight sessions: **104,120 scientific dispatches and 48,756 compression dispatches**.
Internet transfer and energy consumption were not measured in these runs.

## 5. Accuracy against reference data

These are full-output checks. Numerical error figures below are the largest observed across the three cards.

| Workload | Reference and acceptance rule | Measured error or detection accuracy | Result |
| --- | --- | --- | --- |
| SBML | Published per-case absolute + relative tolerance | Maximum absolute error 6.2198279513×10⁻¹¹; maximum fraction of allowed tolerance 6.1336633375×10⁻⁷ | 5/5 models PASS; no reference ZERO BIT claim |
| NIST Lennard–Jones | Tolerance derived from the precision of the published numbers | Maximum absolute difference 0.049650713200; maximum fraction of allowed tolerance 0.993014240855 | 12/12 combinations PASS; no reference ZERO BIT claim |
| MIT-BIH ECG | Beat annotations, ±150 ms matching window | TP 108,461; FP 672; FN 1,007; sensitivity 99.0800965%; positive predictive value 99.3842376% | SCORED; no clinical PASS claim |
| Kepler | Independent analytic solution evaluated to 60 decimal digits | Position error ≤0.030468298706 m; velocity error ≤0.000032957061143 m/s; relative energy drift ≤5.0835240153×10⁻¹¹ | Engineering limits PASS: 0.1 m / 0.0001 m/s / 10⁻⁸; no Basilisk certification |
| PDEBench Burgers | Complete downloaded reference tensor; predefined engineering tolerances | Maximum relative L2 error 0.00107073951812; maximum absolute error 0.0297906912121 | All 10,000 trajectories PASS; limits 0.01 and 0.05 respectively |
| QGC1 losslessness | Independent decoder compared with fresh raw results from the same card | Every one of the 16,727,640,608 original bytes checked in each complete compressed run; zero differing bits | ZERO BIT |

The ECG implementation-equivalence check is ZERO BIT. This is a separate result from accuracy against cardiologist annotations.
Between RTX and Radeon, 123 of 128 raw outputs were bit-identical; five differed. General cross-device ZERO BIT has not been established.
QGC1 E2E and CPU figures include both online compressed comparison and the separate complete decoder audit.

## 6. Measurement provenance and scope

Saved local records: `full-run-20261108T174516Z`, `FULL_AUDITED_RESULT.json`,
`rtx-rerun-20261108T184513Z/results/SUMMARY.json`, `HOST_COMPARISON.json`,
per-job `VERIFICATION.json` records and native event traces.

This public log is a measurement summary. Research data, output arrays and hash inventories are excluded from publication.
Independent external reproduction is not part of this report. No additional physical runs were performed for the English translation.
