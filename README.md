# ASTRO — Scientific Compute

**Scientific workloads. Heterogeneous hardware. Checked results.**

Discover hardware. Optimize execution. Validate the science.

ASTRO develops hardware-aware execution of mathematical workloads, with canonical reference checks. Start with the public four-MathSpec Vulkan demo.

**[Run the GPU demo →](#try-it)** · **[See measured BC-250 results →](docs/BC250_UPDATE_V0_1_1.md)**

### GPU Execution Map: current limitation

**Not a completed universal optimizer.** Private RTX 4060 Ti `CPU_SORT_COPY` and RX 470 memory/readback/QBC improvements still required manual investigation. Automatic rediscovery from a clean device profile has **not been demonstrated**.

The new MinerNode must derive legal candidates from sourced architecture data and native measurements, execute them and pass **FULL-validated end-to-end comparisons**, including host work, transfers and final drain. Preloaded winners and manually forced routes do not satisfy this gate. [Required acceptance protocol](docs/ARCHITECTURE_ROADMAP.md#clean-profile-rediscovery-acceptance-gate).

[Private research status, including negative results](docs/RESEARCH_STATUS.md) · [Architecture roadmap](docs/ARCHITECTURE_ROADMAP.md). These are research disclosures and requirements; the shipped software remains the bounded four-MathSpec demo.

### Current public evidence

| Evidence | Public scope |
|---|---|
| **48/48 physical Vulkan kernel trials PASS / COLD ZERO** | [v0.1.1 bounded comparison](docs/BC250_UPDATE_V0_1_1.md): six runs, four MathSpecs, DIRECT + TILED; complete warmup/final outputs checked. |
| **AMD BC-250 · 24 active CUs · RADV GFX1013** | Physical reference device; 2000 MHz target, measured clocks reported separately. |
| **81 canonical CPU reference primitives** | [Reference corpus](docs/SCIENCE_MAP.md), including 66 SPACE primitives. |
| **94-entry registry inventory** | [Complete inventory](registry_inventory.json); the other 13 entries are not extra executable CPU references. |
| **4 fixed public GPU-demo MathSpecs** | FFT256, Convolution, XCORR and signed-integer FIR; at most four per run. |
| **CPU tests + native/shader build + software Vulkan CI** | [Passing v0.1.1 release run](https://github.com/ASTRO-Scientific-Compute/astro-compute/actions/runs/38276734313); hosted software Vulkan is not physical GPU evidence. |

[![Demo CI](https://github.com/ASTRO-Scientific-Compute/astro-compute/actions/workflows/demo-ci.yml/badge.svg?branch=main)](https://github.com/ASTRO-Scientific-Compute/astro-compute/actions/workflows/demo-ci.yml)

> **EXPERIMENTAL · Active development · Not production-ready**
>
> Physical results are **QUICK_DIAGNOSTIC_ONLY**, not sustained benchmarks. Independent external hardware reproduction is pending. [Status](docs/STATUS.md) · [Validation and audit scope](docs/PUBLICATION.md)

### Try it

Linux, Python 3.10–3.12, and a working physical Vulkan 1.1 compute driver with timestamps are required. On Ubuntu/Debian, install the build dependencies and run the tagged demo:

```bash
sudo apt-get install git python3-venv g++ libvulkan-dev glslang-tools spirv-tools
git clone --branch v0.1.1-demo --depth 1 https://github.com/ASTRO-Scientific-Compute/astro-compute.git
cd astro-compute
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
bash run_gpu_demo.sh
```

The demo builds its native runner, executes DIRECT and TILED for the same four fixed tasks, checks the complete warmup/final outputs against canonical CPU oracles, then stops. It saves one compact diagnostic profile. [Device selection, dependencies and result interpretation](docs/GPU_DEMO.md).

**Source-available demonstration software. Free to evaluate using the included demo. All other use requires explicit permission from the copyright holder.** [LICENSE](LICENSE) · [Evaluation scope](LICENSING.md). This is not an open-source or OSI-approved license.

[v0.1.1 Update / Bugfix](docs/UPDATE_BUGFIX_V0_1_1.md) covers SSD/RAM lifetime fixes and opt-in `--runtime reuse`. The default remains baseline. The public demo is a fixed two-family evaluation; unrestricted Census/Fusion search and a full MinerNode are separate development work.

For the CPU references and software selftests, in the same environment:

```bash
python -m unittest discover -s tests -v
python reference_demo.py
```

### Why ASTRO?

- **Measure the execution path.** A GPU name or advertised capability is not proof of working hardware execution.
- **Search the runtime and kernel path.** The experimental development system searches configurations; the public demo exposes fixed DIRECT/TILED paths and bounded runtime comparison.
- **Check the mathematics first.** Each contract keeps its exact or bounded-FP requirements before performance can be accepted.
- **Route by demonstrated strengths.** Heterogeneous distributed work routing is the planned direction, not a deployed network capability.

### Real demo profile

**2026-10-12 · v0.1.1 comparison · arm B, first baseline run · QUICK_DIAGNOSTIC_ONLY.** Exact fields from `runs[1].profile.trials[1]` in the [published compact profiles](docs/BC250_UPDATE_V0_1_1.json), not a simulated terminal transcript:

```json
{
  "workload_id": "SPACE_GWOSC_FFT256_V1",
  "config": {
    "family": "TILED",
    "local_size": 64,
    "pack": 1
  },
  "CORRECTNESS": "PASS",
  "PERFORMANCE_VALIDITY": "QUICK_DIAGNOSTIC_ONLY",
  "diagnostic_work_units_per_s": 59606.96847135116,
  "unit": "FFT256_window/s",
  "SUSTAINED_PERFORMANCE": "NOT_TESTED"
}
```

This is one short observation on repeated resident input. Full warmup/final output checks do not establish per-dispatch validation of unique research jobs. [All eight paths, both repeated runs per arm, and unfavorable comparisons](docs/BC250_UPDATE_V0_1_1.md) remain public; no general speedup is claimed.

### Run ASTRO on another GPU

Current physical public reference: **AMD BC-250 / RADV**. Run the unmodified bounded four-MathSpec demo on another AMD, NVIDIA or Intel system and [submit a hardware reproduction report](https://github.com/ASTRO-Scientific-Compute/astro-compute/issues/new?template=hardware-reproduction.yml) with its sanitized compact profile. Other devices are not yet hardware-verified here. Correctness evidence is required before performance comparison; failed or unsupported runs are useful reports too.

Technical evaluation and attributed publication are within the [evaluation license](LICENSING.md). [Reporting guide and evidence requirements](docs/EXTERNAL_REPRODUCTIONS.md). Code changes, limit bypass and service operation are outside that permission.

### Explore the system

[Architecture](docs/ARCHITECTURE.md) · [Search & runtime](docs/SEARCH_AND_RUNTIME.md) · [Mathematical corpus](docs/SCIENCE_MAP.md) · [Validation](docs/VALIDATION.md) · [Data lifecycle](docs/DATA_LIFECYCLE.md) · [Roadmap](docs/ROADMAP.md)

The detailed implementation boundaries and planned platform follow below.

## 1. What is ASTRO?

**PLANNED platform; EXPERIMENTAL local execution.** ASTRO connects a research problem to a mathematical contract, a hardware-compatible execution plan and a checked result. “MinerNode” means a compute worker. Scientific work, rather than cryptocurrency proof-of-work, is the purpose of the system.

## 2. Why heterogeneous scientific compute?

**PLANNED network architecture.** Different devices have different strengths. An older GPU may handle FFT, reduction, geometry or data preparation while an AI accelerator handles an appropriate matrix workload. CPUs, APUs, AMD/NVIDIA/Intel GPUs, RT-capable devices and, eventually, mobile/edge devices should be routed by measured capabilities. A device name or advertised feature never proves a working execution path.

## 3. Architecture

![ASTRO architecture with explicit implementation boundaries](assets/architecture.svg)

The complete Researcher → Scientist → MainNode → worker → independent validation loop is **PLANNED / IN DEVELOPMENT**, not a deployed production network. The solid local block identifies the experimental development implementation; it does not imply that the whole GPU runtime ships in this public preview. [Read the boundaries](docs/ARCHITECTURE.md).

## 4. MinerNode

**Automatic clean-profile rediscovery remains an open acceptance gate.** The manually investigated NVIDIA CPU_SORT_COPY and AMD memory/QBC paths reveal missing search coverage; the execution map is not a completed universal optimizer.

**IMPLEMENTED / EXPERIMENTAL in the development tree:** local capability inspection, candidate generation, kernel execution, correctness checks and local profile selection. There is no universal hardcoded GPU winner. The reference development device is AMD BC-250 / RADV GFX1013; its active CU count is a runtime capability, not a cross-device constant. Full cross-vendor execution coverage is **UNAVAILABLE** as a verified claim.

## 5. Runtime Fusion

**EXPERIMENTAL.** A job can combine batching, in-flight work, resident data, command reuse and asynchronous host work. Correctness belongs to the complete runtime configuration. Native independent-job fusion currently covers a smaller subset than the canonical reference corpus. Bounded persistent job loops are not an unlimited GPU scheduler. Transfer/compute overlap and independent multi-machine execution are not established. [Mechanism-by-mechanism status](docs/SEARCH_AND_RUNTIME.md).

## 6. Hardware profiling

**IMPLEMENTED catalog and search-path model; EXPERIMENTAL execution integration.** Capability Census distinguishes storage, scalar, vector, packed/dot, matrix/tensor and emulated paths across numeric formats. FP64/32/16, BF16, FP8/6/4 and INT64/32/16/8/4 are not interchangeable claims. Documentation, backend exposure, an executed kernel and trustworthy measurement are separate evidence levels. Resource measurements such as final VGPR/SGPR allocation, scratch/spill and occupancy remain **UNAVAILABLE** where the driver supplies no reliable receipt. SPIR-V is not a register-allocation oracle.

## 7. Layered search

**IMPLEMENTED / EXPERIMENTAL in the development tree.**

`BATCH → RUNTIME → CPU_HOST → WAVE_SUBGROUP → ILP → LOCAL_SIZE → TILE → PACK → UNROLL → EXECUTION_FAMILY → SPECIAL_PATH → MINI_REFINE → QUICK_CONFIRM`

Each layer builds on the previous correctness-PASS configuration and introduces one new search dimension. Legal unexplored axes get an exploration trial before policy pruning; unavailable axes are reported explicitly. ILP is currently unavailable as an independent axis in the audited Fast V2 adapter set. A QUICK winner remains a local candidate, not a production promotion. [Audit rules](docs/SEARCH_AND_RUNTIME.md).

## 8. Universal Mathematics

**IMPLEMENTED reference corpus; PLANNED general composition.** The development registry has 94 entries; this preview includes 81 canonical CPU reference primitives, including 66 SPACE entries. Those numbers describe different scopes. The remaining 13 entries are listed explicitly in the [inventory](registry_inventory.json).

The long-term goal is to compose reductions, transforms, sparse/dense operations, scans, gather/scatter, integration, geometry, tensor operations and spatial traversal into research workflows. The corpus is a reference and regression foundation, not a promise to solve science by accumulating hundreds of unrelated handwritten recipes.

## 9. Science domains

| Domain | Implemented reference examples | Planned direction beyond the bounded primitives |
|---|---|---|
| SPACE | Image moments, catalog geometry, FFT/correlation, photometry, orbital primitives | Composed astronomy, Gaia/catalog workflows, gravitational-wave processing |
| BIO | Alignment scores, contact analysis, numerical primitives | Larger biological workflows |
| CHEM | Squared pair distances, radial counts, geometry | Composed molecular/spatial analysis |
| PHYSICS | Ising observables, bounded numerical primitives | Simulation and field/particle workflows |
| SIGNAL | FIR and spectral/numerical building blocks | Composed filtering and signal pipelines |
| ENGINEERING | Sparse matrix-vector products, orientation, numerical geometry | Simulation, optimization and realtime workloads |

Two additional canonical RT commissioning contracts are categorized separately. A primitive is not a complete scientific application. [Full 94-entry inventory and scope](docs/SCIENCE_MAP.md).

## 10. Validation

**Correctness before performance.** Exact contracts require zero differing bits; bounded-FP contracts retain their own explicit bounds. An optimization cannot silently change the mathematical problem, rounding graph or input representation.

Two separate gates matter: **implementation agreement** checks the entire GPU output against the independent CPU implementation (zero differing bits for exact contracts); **scientific validity** checks the numerical result against the required scientific reference, higher internal precision or original error budget where the MathSpec requires it. Two implementations agreeing bit-for-bit does not prove that both implement the intended science correctly. The documented [Hann FFT / whitening amendment](docs/VALIDATION.md#historical-example-hann-fft-and-whitening) illustrates why.

The public CPU checks are **VERIFIED only within their stated test scope**. Development GPU results need their own oracle comparison, executed-path evidence and performance-validity gates. Independent network validation is **PLANNED**: nodes sharing an ownership or network domain do not automatically count as independent validators. [Validation policy](docs/VALIDATION.md).

## 11. RT compute

**EXPERIMENTAL local paths.** Ray query and BLAS/TLAS traversal can serve conservative spatial broadphases. A candidate hit must still satisfy the MathSpec's exact narrowphase. RT is not assumed to accelerate every workload. Ray-query commissioning does not establish general raygen/SBT support or an application-wide speedup.

## 12. AI / Tensor

ASTRO is scientific compute first. AI/Tensor execution, Scientist AI and orchestration are components within that system, not its primary definition.

**PLANNED execution integration.** Tensor/matrix work, inference, preparation and distributed reasoning support belong behind capability and correctness gates. Cataloging FP4 or BF16 does not mean that a given GPU executes it natively. Legacy GPUs remain useful for suitable classic compute tasks; modern accelerators must prove their own paths. No production inference/training backend is claimed here.

## 13. Engineering / Realtime / Game

**EXPERIMENTAL separate prototype; PLANNED ASTRO integration.** An existing Linux game-optimizer prototype observes launch/API paths and frame-time metrics, stores per-game profiles and supports restricted launch-setting experiments and rollback on a later launch. No verified game-speedup claim is published here.

The ASTRO direction is **ANALYZE → RECOMMEND → AUTO-APPLY**, with explicit validation and rollback. Automatic frame-graph reconstruction, engine/shader rewriting and physics/RT pipeline optimization are planned. [Prototype boundary](docs/ENGINEERING.md).

## 14. MainNode

**PLANNED / IN DEVELOPMENT.** The control plane is responsible for DAG dependencies, routing, data distribution, validation coordination, result collection, receipts, node management and researcher interfaces. The local uploader simulator is not a real result-receipt service. No unmeasured node-capacity claim is made.

## 15. Scientist

**PLANNED / IN DEVELOPMENT.** Scientist AI would interpret the research task, propose a mathematical workflow, dispatch compute through MainNode, assess validated outputs and reconstruct a researcher-facing answer. Mathematical correctness and scientific interpretation remain distinct responsibilities.

## 16. Storage and data lifecycle

**IMPLEMENTED benchmark retention policy; research ACK integration IN DEVELOPMENT.**

- Benchmark: **run → validate → profile → cleanup**. Retain the compact profile, not raw outputs, hash inventories, telemetry dumps or trial workspaces.
- Research work: **compute → validate → upload → verified MainNode ACK → grace period → local delete**. A simulated upload never authorizes deletion.

Storage planning guidance: **512 GB SSD minimum recommendation; 1 TB+ recommended**, depending on researcher data and workload. This is not a measured minimum requirement or a reason to accumulate benchmark debris. [Lifecycle details](docs/DATA_LIFECYCLE.md).

## 17. Current status

**EXPERIMENTAL, not production-ready.** Fast Search works on bounded adapters in the development tree; Runtime Fusion is under active development. The image-moments runtime path has an unresolved intermittent correctness failure; successful replays do not prove it fixed. Native resource receipts, full cross-vendor execution validation and independent review remain open. [Dated status table](docs/STATUS.md).

## 18. Benchmarks

This preview publishes **no GPU performance leaderboard**. Historical local profiles are not self-contained public reproduction packages. Primary metrics must be correctly completed natural work units/s and end-to-end time; legacy science/s is secondary. QUICK, confirmed local, sustained, certified and historical results must remain distinct. [Required methodology](docs/BENCHMARKS.md) · [External reproduction template](docs/EXTERNAL_REPRODUCTIONS.md).

## 19. Roadmap

**NEXT milestones:** broader portable GPU search integration and external human review; broader hardware commissioning; resource evidence; reliable runtime composition; a real MainNode ACK and independent validation protocol; Scientist integration; host-runtime generation; heterogeneous network commissioning; engineering/realtime integration. Marketplace, compensation, accounting/token and fiat-denominated research contracts are long-term design topics, not operational products. [Gated roadmap](docs/ROADMAP.md).

## 20. Contributing

Start with [CONTRIBUTING.md](CONTRIBUTING.md). Small reproducible correctness cases, independent reviews, precise capability gaps and portable packaging improvements are useful. Code modification and contribution require prior written permission; contribution terms must be agreed before incorporating third-party code.

## 21. Security

Read [SECURITY.md](SECURITY.md). Never submit credentials, private researcher data or raw local state in a public issue. Security reporting must use a confirmed private channel. This preview starts no network service and does not expose a production compute network.

