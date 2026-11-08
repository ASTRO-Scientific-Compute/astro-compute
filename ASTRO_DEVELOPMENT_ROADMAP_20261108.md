# ASTRO independent miner — development roadmap

Date: 2026-11-08. Status: **proposed development priorities and acceptance criteria**.

[Miner package and usage](ASTRO_MINER_20261108.md) · [Measured results and reference accuracy](ASTRO_MEASUREMENTS_20261108.md)

## 1. Objective

Build a general scientific graph worker that completes independently checked research work with low total cost across CPU, GPU, PCIe, storage and, eventually, network delivery.

The first performance priority is **lower host CPU cost across all supported graphs**. The next priorities are keeping prepared work available to the GPU, proving useful concurrent execution, and selecting data movement and compression policies from complete measurements.

A research job is complete only when all required cases, time points, output values and validation conditions in its contract have been processed. Internal chunks and repeated executions must be counted separately. There is no universal one-minute limit for a complete scientific dataset.

## 2. Starting point and remaining evidence gaps

| Component | Current position | Next evidence required |
| --- | --- | --- |
| Common graph engine | Independent CUDA/Vulkan implementation; original core source included in the miner package | Rebuild and validate the extracted distribution independently |
| Persistent sessions and input residency | Implemented and used by local research campaigns | Quantify avoided uploads, allocations and program loads on successive independent jobs |
| Concurrent lanes and asynchronous host work | Implemented; a GPU may advance while the host checks retained immutable outputs | Demonstrate an E2E gain for a sustained, genuinely mixed workload with a valid physical timeline |
| Generic optimizer | Candidate search, independent budgets and per-device profiles exist in the development system | Demonstrate repeatable decisions from fresh profiles for the broader runtime/data-path search |
| QGC1 output compression | Physical GPU execution and full independent decoder checks recorded | Reduce total host cost; select compression from complete cost rather than compression ratio alone |
| Published benchmark | Small synthetic INT32 baseline with serial/concurrent modes | Build and run this newly extracted package; no benchmark score is published yet |
| Network objective | Cost model exists | Actual transfer, verified receipt, recovery and end-to-end measurements |

The full research campaigns show that GPU compression itself can be inexpensive while host reference access and independent full decoding dominate CPU or elapsed time. The RTX rerun also shows large persistence-time changes with nearly unchanged scientific GPU time. These observations justify measuring host work and storage conditions before pursuing a new kernel-only optimization.

## 3. Architecture boundaries

Maintain one reusable `engine/` implementation. Scientific domains supply kernels, input/output contracts and independent checkers through adapters. Adding BIO, CHEM, SIGNAL, SPACE or another domain must not require a new execution engine.

| Layer | Responsibility |
| --- | --- |
| Scientific adapter | Define the entire job, legal numerical transformations, reference source, tolerances, work units and complete-output validation |
| Graph compiler | Validate dependencies, accesses, shapes, data types, lane assignment and resource bounds; produce a backend-independent execution description |
| Common runtime | Own sessions, lifetimes, resident buffers, queues, completion events, safe result handoff and failure handling |
| Backend | Implement capability discovery, program loading, dispatch, event timing and transfers for its API |
| Optimizer | Search only adapter-approved configurations; measure the complete path; retain a result only under its exact device/program/input/contract identity |
| Transport and persistence | Encode, frame, transfer, store and release results while preserving byte identity and the required completion boundary |

Backend-specific execution mechanisms are expected. The public graph contract and scientific acceptance rules must remain independent of vendor names. Existing ASTRO executor code should not be copied back into this independent engine.

## 4. Priority 0 — qualify the portable miner and benchmark

The extracted package changes the launcher and build wrapper around the existing core. Qualification must cover those packaging changes explicitly.

1. Build the package in a clean directory with declared dependencies; cover Vulkan-only and CUDA-enabled builds separately.
2. Check device selection, missing capabilities, missing toolchains and driver changes. An unsupported path must report its reason before claiming a successful run.
3. Run the same synthetic workset in serial and concurrent modes on each intended device. Compare every output word with the CPU oracle.
4. Confirm finite time/memory limits, process cleanup and ownership locks. Record failures and skipped configurations as outcomes.
5. Publish compact benchmark results only after qualification. Keep these results separate from the historical research-corpus measurements.

**Acceptance:** a reproducible package build, complete correctness checks for each exercised backend, accurate resource accounting and a documented execution path. Passing software-only checks does not establish physical GPU performance.

## 5. Priority 1 — reduce general host CPU work

### Preparation and metadata

- Parse each immutable graph once per applicable identity and reuse its validated execution description.
- Reuse program and ABI bindings within the live session; rebuild only when their dependencies change.
- Replace repeated dictionary traversal, string formatting and per-dispatch allocation in hot paths with bounded prepared structures where measurement identifies a material cost.
- Keep compact summaries on the routine path. Detailed dispatch evidence should be collected with a declared measurement mode and its overhead accounted for.

### Integrity and copies

- Reuse an integrity result only while the referenced bytes remain immutable and the identity is valid. A filename, size or modification time alone is insufficient proof of content equality.
- Pass sealed descriptors through preparation, execution and validation instead of reopening and copying unchanged files at every layer.
- Measure hashing, reference reading, buffer copying, graph compilation and result serialization separately. Track bytes as well as CPU seconds.
- Prefer bounded bulk operations for large arrays. Moving work out of Python does not remove its CPU cost; include native code and child processes in the measurement.

### Reference checking

- Prepare stable reference state once within its safe lifetime and share it across independent checks.
- Keep scientific reference checks and transport-integrity checks distinct. Cached compressed packets must remain tied to the correct input, program and mathematical contract.
- A compressed checksum or byte comparison alone cannot establish the scientific correctness of a new result.
- Measure full independent decoder qualification separately from any future routine online mode. Do not derive an online-only E2E number by subtracting overlapping phases from a full audit.

**Acceptance:** on identical complete worksets and unchanged correctness rules, demonstrate lower process-tree CPU time and report any E2E, memory or I/O tradeoff. The improvement must be exercised through the common runtime by multiple graph types.

## 6. Priority 2 — sustain prepared work and control storage cost

### Session and residency policy

Use bounded caches for immutable inputs, loaded programs and reusable allocations. Track hits, misses, resident bytes, evictions and the actual upload bytes avoided. Residency must be invalidated on changed content or incompatible execution identity.

### Asynchronous service

The host should prepare the next independent job while the GPU executes, then validate a retained result while the GPU advances. Bound the queue by memory and validation capacity. Apply backpressure when output checking or persistence falls behind.

Every handoff needs explicit ownership: queued, executing, completed, retained by the checker and releasable. Cancellation, timeout and partial failure must preserve this lifetime discipline. More queued work must not permit an output buffer to be reused before its final consumer releases it.

### SSD path

Prefer a bounded number of larger sequential result containers with indexed records over a file per small codec block. Batch block sizes and offsets into a few transfers. Measure any index and framing overhead.

Record logical bytes, physical device bytes where available, I/O request sizes, queue depth, await, CPU I/O wait and dirty/writeback state. Report buffered completion and durable completion as different measurements. A constantly lit activity LED is not a throughput measurement.

TRIM, filesystem state and cache state may influence results; causal claims require an appropriately controlled comparison. A faster replay alone is not proof that one maintenance action caused the change.

**Acceptance:** fewer redundant uploads/reads/writes, bounded live data, complete results after normal completion and an E2E comparison that includes the chosen final persistence boundary.

## 7. Priority 3 — prove useful mixed execution on one GPU

Begin with correctness and the existing one/three-lane comparison. Extend to one, two, three and then five lanes only after the common runtime and evidence support each step.

1. Fix one complete workset and its natural work units before comparing modes.
2. Feed distinct, independent jobs for long enough to observe steady service and final drain. Report unique research cases and pure repeats separately.
3. Record dispatch and completion intervals on a comparable device timeline. If the backend cannot establish a common time basis, do not claim measured physical overlap from separate queue timings.
4. Compare full E2E, CPU seconds, completed work per second, per-job latency, GPU intervals, transfer bytes and peak buffers.
5. Introduce genuinely different FP64, FP32 and INT32 workloads after independent correctness is established. Three differently seeded INT32 graphs validate a runtime pattern; they do not demonstrate complementary arithmetic-unit use.
6. Measure matrix work only where the backend exposes and validates the required operation and precision. Hardware marketing names are not execution evidence.

For a fixed heterogeneous workset, report completed worksets/s plus per-domain natural throughput. Do not add unrelated units such as ECG records/s and trajectories/s into an unexplained scalar score.

**Acceptance:** complete scientific checks for every member, unchanged work quantity, valid overlap evidence where claimed, and a repeatable E2E/throughput improvement beyond observed variation. Overlap without a throughput gain is still a valid negative result.

## 8. Priority 4 — learn execution and data-path profiles

### Candidate ownership

The optimizer may explore workgroup size, work per thread, tiling, partitioning, supported execution variants, queue/lane policy, residency and output encoding. The adapter defines which candidates preserve its mathematics.

If the contract requires ZERO BIT or a fixed operation order, a faster reassociated reduction is not an admissible winner. Numerical tolerance, repeated-run bit identity, cross-device bit identity and external scientific agreement remain separate checks.

### Objective and profile identity

Choose primarily by correctly completed work per full end-to-end second under explicit CPU, memory and other resource limits. Report GPU time, CPU time, VRAM, data transfer and variation alongside the primary metric. Energy per correct work is available only when energy was actually measured.

Maintain separate profiles for standalone and mixed operation, and for local and network execution. A profile is valid only for its device identity, driver/backend, engine/program versions, input characteristics and scientific contract. RTX and each Radeon may select different policies, including different policies for different PCIe paths.

Use an explicit exploration budget, repeated finalist measurements and a declared rule for practical ties. Preserve a correct fallback when the measured difference is inconclusive. A previously saved winner must not be presented as a fresh-profile discovery.

### Independent resource accounting

Reserve and report physical sessions, candidate/graph evaluations, worker time, summed GPU intervals and memory separately. Several candidates in one process still consume several candidate evaluations. Charge warmups and retries explicitly. Unknown outcomes keep their reservation until reconciled; exhausted campaigns do not reopen automatically.

**Acceptance:** reproducible selection from a fresh profile, correct candidate rejection, independent limits respected and no stale winner reused after an invalidating change.

## 9. Priority 5 — optimize compression across PCIe, SSD and network

QGC1 is a general lossless transport component. The existing results show a strong reduction for SIGNAL, a smaller reduction for PDE, and expansion for tiny CHEM outputs. The decision must therefore account for the actual output characteristics and fixed overhead.

Candidate dimensions may include raw transfer, supported transforms, block/frame sizes, framing batches and already validated codec variants. Evaluate compressor GPU time, size/offset readback, payload transfer, metadata, fallback, checking and persistence together.

Two objectives must remain explicit:

- **Local:** time until the checked result reaches the declared local persistence boundary, with full CPU and buffer costs.
- **Network:** time until the checked result reaches the receiving service and a verified receipt is obtained, including encoding, transfer, receiver checks and any required durability.

A simple sum of phase costs is useful only where those phases are sequential. For overlapping work, score the observed schedule and final completion boundary. A bandwidth-based network estimate is a model until an actual transfer is measured. Network prices and energy costs must be supplied or measured, not invented.

Losslessness qualification must restore every original output byte with an independent decoder and compare it to the corresponding fresh raw result. Maintain separate reports for this full qualification and any proven routine compressed-domain checking mode.

**Acceptance:** exact reconstruction, correctly counted total transferred bytes, a complete E2E comparison, and an objective-specific choice that can legitimately select raw output when compression is more expensive.

## 10. Priority 6 — extend scientific coverage through adapters

Each additional adapter should provide:

1. A researcher-defined complete job and explicit completion rule.
2. Public reference provenance and the applicable numerical/error contract.
3. A supported input subset stated without extrapolating to the whole domain.
4. Kernels and graphs for the existing runtime, with required data types and capabilities declared.
5. An independent full-output checker and natural work units.
6. A finite legal candidate space plus rules for reduction order and other numerical transformations.
7. Coverage counts for unique cases, trajectories, records, time points and repeated replicas.

Expand the currently supported BIO, CHEM, SIGNAL and SPACE subsets as separate scientific work. Preserve scored ECG metrics instead of inventing a clinical PASS threshold. Keep cases with unresolved reference failures outside accepted throughput totals.

**Acceptance:** the same runtime executes the new graphs without domain-specific executor changes, and the independent checker evaluates the complete stated work.

## 11. Later platform direction

After the local worker is qualified, develop the surrounding ASTRO workflow in separately testable stages:

- **Research submission:** package a full job, inputs, scientific contract, allowed execution choices and completion criteria.
- **MainNode/control plane:** admit jobs, select compatible workers from measured capabilities, track dependencies and collect results.
- **Delivery protocol:** support resumable transfer, idempotent result identifiers, verified receipts and bounded retention. A simulated upload does not authorize deletion.
- **Independent validation:** define validator independence and scientific acceptance separately from transport integrity and ownership.
- **Scientist layer:** assist with workflow construction and interpretation while keeping mathematical acceptance under explicit contracts and review.
- **Operational service:** add isolation, recovery, version negotiation and resource limits before multi-user deployment.

These are planned platform capabilities. The current miner archive is a local development package; it is not a deployed research marketplace or distributed validation network.

## 12. Delivery order and public reporting

| Order | Deliverable | Completion evidence |
| --- | --- | --- |
| 0 | Qualified extracted miner + synthetic bench | Clean build and bounded physical checks per exercised backend |
| 1 | General host-cost reduction | Complete workset CPU/E2E comparison with unchanged reference checks |
| 2 | Sustained preparation, residency and storage path | Avoided bytes, bounded lifetimes, declared persistence boundary |
| 3 | Mixed-work execution comparison | Same workset in each mode, physical timeline where available, full correctness and variation |
| 4 | Automatic local/mixed profile selection | Fresh-profile search, separate resource ledgers, objective-specific accepted winner |
| 5 | Adaptive compression and measured delivery | Full losslessness qualification, actual bytes and complete local/network cost |
| 6 | Broader scientific adapters and service integration | Complete new cases through the same runtime and independent checkers |

This order defines dependencies rather than calendar promises. New hardware campaigns need a finite plan covering their actual session and evaluation counts before launch.

Publish measurement logs in English with exact scope, reference accuracy, relevant machine/toolchain information, and negative or inconclusive outcomes. Keep proposed work in this roadmap. The public distribution remains limited to the miner, benchmark foundation and documentation; research datasets, output arrays and hash inventories remain excluded.
