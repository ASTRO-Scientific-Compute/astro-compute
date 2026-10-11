# Benchmark publication policy

**No public performance leaderboard is shipped in this preview.** Preserved local profiles and historical reports are useful development references, but without a self-contained reproduction package they are not promoted to published benchmark results. Raw benchmark evidence and hash inventories are not retained under the current storage policy.

## Primary metric

Maximize **correctly completed real mathematical work per second**. Define the natural work unit from the MathSpec: cell update, sample, distance evaluation, pair, lag, segment, ray or another precise unit. Report end-to-end time and throughput alongside the kernel measurement. Legacy Mscience/s is secondary compatibility information.

Algorithmic operations must be derived from the canonical definition and split by type: FP32, FP64, INT32, INT64, FP16 and so on. State the FMA convention (normally one multiply plus one add = two algorithmic floating-point operations when the canonical algorithm contains both), any mixed-precision convention and the measurement denominator. This is useful mathematical work, not a count of native instructions. DAG reuse, LUTs, compression and precomputation do not inflate that work count. If the operation count cannot be proved, OPS/s is **UNAVAILABLE**; natural work units/s can still be measured.

## Labels that must stay separate

| Label | Meaning |
|---|---|
| QUICK / local candidate | Short diagnostic; not a sustained claim |
| Confirmed local winner | Repeated local candidate checks in a specified scope |
| Sustained result | Valid sustained interval with complete correctness and GPU evidence |
| Certified result | Reserved for completed independent review/validation gates |
| Historical result | Earlier contract/workload/platform context; not automatically comparable |

A comparison requires identical MathSpec contract, workload, inputs, mathematical work definition and timing boundaries. A generic baseline and an optimized route must both execute and pass correctness. A catalog entry influencing no executor cannot be credited with a speedup. Only a comparable new FULL PASS measurement exceeding an earlier validated one may be marked PERFORMANCE_IMPROVED.

## Required compact profile

Record workload/contract identity, useful unit and count, algorithmic counts by type or UNAVAILABLE, runtime/kernel family, configuration, software/toolchain/device context, correctness, elapsed wall and native GPU time, GPU/wall ratio, dispatch/submission counts, available duty/gap statistics, telemetry coverage, sustained confirmation and end-to-end throughput. PPT, SCLK and engine time are diagnostics. Do not persist source/SPIR-V/input/output hash inventories or raw trial workspaces. Perform temporary execution binding and full validation before cleanup.

The profile must distinguish unavailable fields from zero. Invalid correctness never appears as accepted performance. A ~5 ms burst followed by idle time cannot be presented as sustained mathematical capacity.

## Reproduction without storage growth

Keep the public algorithm, compact configuration, deterministic input-generation recipe and validation procedure. A reproduction is a new validated run; the original transient raw output is intentionally not archived. Do not advertise an exact replay when a historical input recipe or compatible executor is missing. The current public package includes CPU reference checks and the bounded four-MathSpec Vulkan runner. Its full-output correctness checks and QUICK diagnostics are separate from any future sustained reproduction protocol.

## External reproductions

The [external reproduction template](EXTERNAL_REPRODUCTIONS.md) records the exact release, device/driver, task, kernel family, correctness, natural units and telemetry availability. It is an empty submission format, not a leaderboard. Software Vulkan correctness, physical QUICK diagnostics, sustained evidence, historical internal results and independent reproductions remain separate.
