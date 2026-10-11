# Search and Runtime Fusion

**Scope: development-tree implementation, EXPERIMENTAL. This preview does not ship the GPU launcher.**

## Layered Fast Search V2

| Stage | Newly explored dimension or mechanism |
|---|---|
| BATCH | Feed size, jobs/dispatch and bounded in-flight/job-pool alternatives, evaluated separately |
| RUNTIME | Legal runtime or memory/command policy alternative, one at a time |
| WAVE_SUBGROUP | Supported wave/subgroup mode |
| ILP | Independent operation streams, only if a real adapter exists |
| LOCAL_SIZE | Workgroup size |
| TILE | Tile geometry/decomposition |
| PACK | Legal packed width |
| UNROLL | Unroll factor |
| EXECUTION_FAMILY | Ordinary kernel-family alternative |
| SPECIAL_PATH | Separately gated numeric/RT/domain-specific route |
| MINI_REFINE | Nearby previously explored settings, without a Cartesian restart |
| QUICK_CONFIRM | Short repeated checks of the top complete configurations |

Each stage inherits the best valid previous configuration. Derived resource bookkeeping can change with its governing axis; unrelated search dimensions must stay fixed. Tile, pack and unroll remain separate, as do execution family and special path. When a later family changes the resource character, only local feedback/refinement is justified.

The objective is valid natural work units/s, not occupancy, power or temperature. PPT, clock and engine time are diagnostic data. Good occupancy can explain performance; it is not itself the winner objective.

## Auditable exploration and pruning

A legal implemented axis must receive a real exploration measurement for that MathSpec before policy pruning. Protected exploration takes priority over a third or fourth marginal attempt on an already explored axis. Exhausted budget is **DEFERRED_BUDGET**, not AI insight.

Every MathSpec needs explicit stage outcomes: `MEASURED_WIN`, `MEASURED_LOSS`, `MEASURED_INVALID`, `AI_PRUNED`, `UNAVAILABLE`, `NO_ALTERNATIVE`, `ILLEGAL_FOR_FAMILY`, `DEFERRED_BUDGET`; duplicate suppression is `ALREADY_MEASURED`.

An `AI_PRUNED` record identifies the axis, reason, policy/engine and measured evidence axes. Predicted gain and confidence must be **UNAVAILABLE** when the policy has no calibrated estimator. The current measured-loss heuristic is not a trained confidence model. The audited targeted hardware run did not exercise AI_PRUNED, so that hardware gate remains open. Independent ILP and native resource receipts remain unavailable; an absent trial is not proof of pruning.

## Capability Census and actual execution

The development Census models vendor/architecture/backend/format/path separately. Storage representation, scalar/vector arithmetic, packed/dot instructions, matrix/tensor execution and emulation are separate claims. A format mentioned in vendor documentation is not a runtime pass. Candidate generation, chosen family, generated code, compiled program and actual result need to be connected by per-trial evidence while the trial is alive. Only the compact validated profile survives cleanup.

FP64, FP32, FP16, BF16, FP8, FP6, FP4, INT64/32/16/8/4 and their encodings are routed only behind legal contracts. For example, a BF16-shaped storage or integer-emulation route does not prove native BF16 ALU execution. Matrix/tensor paths remain capability-only or reserved until hardware and correctness gates pass.

## Runtime mechanism boundaries

| Mechanism | Audited development scope |
|---|---|
| STREAMING | IMPLEMENTED / EXPERIMENTAL execution mode |
| DEEP_BATCH, MULTI_INFLIGHT | IMPLEMENTED / EXPERIMENTAL on native-adapted subset |
| ASYNC_SUBMIT, ASYNC_VALIDATION | IMPLEMENTED / EXPERIMENTAL host pipeline |
| ASYNC_RETIRE | Ready-first polling exists; reordered-retirement benefit UNVERIFIED |
| PERSISTENT | Bounded per-workgroup independent-job loop; no infinite global scheduler |
| RESIDENT_DATA, BUFFER_RING | IMPLEMENTED / EXPERIMENTAL data policies |
| PRE_RECORDED_COMMANDS | IMPLEMENTED / EXPERIMENTAL command reuse |
| LDS_TILE, SUBGROUP | IMPLEMENTED only for appropriate legal families |
| RT_PIPELINE | Bounded ray-query compute; general raygen/SBT and mutable multi-inflight AS fusion RESERVED |
| LATENCY_SENSITIVE, CPU_GPU_PIPELINE | IMPLEMENTED / EXPERIMENTAL local graph mechanisms |
| OVERLAPPED_TRANSFER_COMPUTE | UNAVAILABLE as demonstrated overlap; a copy running is insufficient |
| DISTRIBUTED_PIPELINE | Protocol/loopback software checks exist; independent physical-node proof UNAVAILABLE |

Historically, 81 canonical jobs reached the common graph while native independent-job adapters covered 16; the remaining jobs using a serial executor must not be described as native batched fusion. These are distinct coverage measures. Each runtime configuration still needs its own correctness and performance gates.

## Profiler gates

**FUNCTIONAL → CORRECTNESS → PERFORMANCE_VALIDITY → RESOURCE_EVIDENCE** where resource claims are made. Native time, measurement wall time, GPU/wall ratio, dispatch count, submissions, queue/compute duty when available, inter-dispatch gaps, telemetry coverage and sustained confirmation must be explicit. Unmeasurable quantities are UNAVAILABLE/UNVERIFIED, never inferred as final allocations from SPIR-V. QUICK_SANITY is never publishable sustained performance.
