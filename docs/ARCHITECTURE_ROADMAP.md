# ASTRO Universal — architectural research roadmap

**2026-10-23 · DESIGN, not a released system.** The current [public scope](STATUS.md) is a bounded four-MathSpec demonstration. This document describes proposed architecture and the evidence gates needed to turn ongoing laboratory work into dependable features.

## One hardware knowledge base, local authority

ASTRO plans a versioned, sourced **Hardware Architecture Knowledge Base** covering major AMD (GCN/Polaris, Vega, RDNA, CDNA), NVIDIA (Pascal, Volta, Turing, Ampere, Ada, Hopper, Blackwell) and Intel (Xe variants) architecture families. Consumer, workstation and datacenter devices are all relevant, but marketing family names alone are not reliable silicon identifiers.

Each record must distinguish **physical or documented capability**, **driver/backend exposure**, **native execution proof**, **MathSpec correctness**, and **performance-valid evidence**. Where precise registers, cache controls, tensor/RT instructions or internal engine paths are unavailable, record `UNKNOWN` rather than inventing a capability. Vendor and driver documentation must be attributed and versioned.

The database is **not a table of global performance winners**. Local devices may learn different legal executors because of specific silicon, enabled units, memory topology, firmware, host CPU, driver and loaded PCIe link. Private learned profiles remain local and must be invalidated or revalidated after material changes.

## MinerNode: optimize the entire local execution chain

**Target sequence:** architecture candidate → physical device identification → backend probes → native capability evidence → MathSpec-legal kernel and host-route generation → FULL correctness → end-to-end benchmark with final drain → trusted local profile.

The search space includes CPU preprocessing, feed/backpressure, host-to-device transfer, workgroup/subgroup geometry, registers/spills, memory policy, queues/dispatch, kernel compute, GPU-side compression, device-to-host readback, CPU inverse and verification. Pipeline overlap requires evidence; timestamped subphases may overlap and must not be naively added together.

**First acceptance demonstration:** on a fresh local profile, automatically rediscover applicable known improvements (including CPU-side feed choices), and compare complete validated outputs on an older AMD and a modern NVIDIA GPU. A short QUICK PASS is not a sustained result. The primary PCIe research target is **Gen1 x1**, with **Gen3 x1** a possible fallback profile if the actual hardware and link support it. This is an engineering goal, not proof of RTX 5090 utilization on x1.

## Clean-profile rediscovery acceptance gate

**Required for the new MinerNode; not yet demonstrated by the current GPU Execution Map.** Known private-lab improvements still needed manual discovery: RTX 4060 Ti `CPU_SORT_COPY` and RX 470 output/readback-memory and QBC paths. This is an explicit implementation limitation, not evidence of a completed universal optimizer.

1. **Clean start and identity.** Create an isolated COLD ZERO profile with no inherited winners. Bind native receipts and plans to stable device identity, driver/backend version and measured link/topology; a reused PCI address or Vulkan index is insufficient. Preserve existing profiles and evidence.
2. **Architecture-to-candidate trace.** Record sourced architecture-record versions, live native capability results, legal MathSpec constraints, candidate-generation decisions and unavailable/rejected alternatives. The database suggests legal possibilities; it supplies neither assumed support nor a global performance winner.
3. **Automatic rediscovery.** Through the ordinary search entry point, independently admit and try the relevant CPU_SORT_COPY route on RTX 4060 Ti and memory/readback/QBC alternatives on RX 470 where native probes permit them. Existing legal adapters may be reused. Manual route forcing, seeded device winners or hardcoded device-name selection fail this gate. Functional discovery is reported separately if local measurements favor another route.
4. **Actual execution and FULL correctness.** Bind the selected execution plan to generated source/SPIR-V and actual worker receipts, including memory types, data transforms, input/job identity and final drain. Every claimed route must run natively and pass the unchanged independent CPU FULL-oracle contract; catalog entries and importable modules are insufficient. COLD ZERO is profile commissioning, not the name of the zero-bit correctness test.
5. **Comparable end-to-end evidence.** Use identical MathSpec, input sequence, useful work, numerical contract and external conditions, with repeated alternating baseline/candidate windows. Change one principal route at a time. Count all preprocessing/sort, upload, compute/encode, readback, decode, FULL validation, waits and final drain; report cold setup and reused execution separately. Account for overlap without adding overlapping intervals. The objective is fully verified natural work per elapsed time, with logical bytes and native GPU timings reported separately.
6. **Admission remains separate.** Publish discovered/rejected paths and losses, distinguish QUICK from sustained evidence, and require scoped independent review and sustained confirmation before profile activation. Missing hardware, counters or tests remain UNAVAILABLE/UNVERIFIED. A local success covers only its actual device/driver/workload scope; it is not automatically a profile for another GPU or proof of universal coverage.

The acceptance artifact must show the complete trace from architecture data and native probes through candidate generation, executed worker and FULL-validated E2E comparison. Until that trace is demonstrated on the stated AMD and NVIDIA controls, public documentation must continue to describe the map as incomplete.

## BLACKHOLE: storage, wire and device-boundary research

- `BHC-CORE`: lossless, packet-only, bounded parsing/inverse; candidate transforms and mathematical dependencies are retained only if reversible under the exact contract.
- `BHC-STREAM`: streaming/chunking, explicit accounting for encoder time, payload+metadata, latency, verified receipts and network/PCIe bytes.
- `BHC-STORE`: temporary scientific data retention and exact reconstruction, with correct cleanup only after an authenticated receiving acknowledgement.

For a narrow PCIe link, **compression must happen on the GPU before D→H** to reduce the miner's PCIe output traffic. CPU compression after RAW readback may save network bytes but not the already spent GPU→CPU bytes. Compute/encode, transfer and validation must be compared together; a smaller packet that takes substantially longer to produce is not a stream winner. The [research status](RESEARCH_STATUS.md) documents both improvements and costly negative selectors.

## Verification Atlas: independent correctness at viable cost

For each MathSpec, document **input, complete output, numeric semantics, current FULL-recompute cost, any exact certificate/proof and all producer/validator/proof/transfer costs**.

Validating a packet's integrity is not scientific verification. Full recomputation by an independent trusted implementation remains the default until a stronger or equivalently trustworthy alternative is proven. Deterministic exact certificates, probabilistic algebraic checks and sampled verification have **different guarantees** and cannot silently replace a zero-error contract. A correct output also does not automatically prove the claimed worker performed the computation; accounting/attestation is separate.

Independent validation requires independent physical and operational trust domains under the future protocol. MainNode-operated GPUs may perform validation **when appropriately independent of the miner**; GPU–GPU agreement using identical buggy kernels is not itself sufficient. Any proposed proof and receipt must be bound to exact MathSpec version, input, job, range, owner and sequence and independently audited.

## MainNode: coordinate, not remotely tune worker GPUs

MainNode is a separate control/coordination and service role. It can optimize **its own** CPU, GPU, network, storage and hosting environment through the same shared architecture knowledge, and coordinate validated job placement and payments. **It does not generate or overwrite the private local execution maps of MinerNodes.** All hardware commissioning, scheduling within the host and per-GPU winner selection remain local to each node.

A public production network, distributed model inference across heterogeneous nodes, verified settlement, worker/validator compensation and Scientist AI are **future stages**. They are not present in the public demo.

## Gated implementation sequence

| Phase | Status now | Gate before expanding |
|---|---|---|
| Public mathematical reference and bounded four-task demo | **EXPERIMENTAL PUBLIC DEMO** | Preserve build, correctness and evaluation license |
| Architecture-family records and runtime capability probes | **PLANNED REBUILD** | Versioned source provenance; device/driver identity; `UNKNOWN` permitted |
| Automatic kernel **and full host-feed** route generation | **PLANNED / PARTIAL PRIVATE RESEARCH** | Automatic clean-profile rediscovery of RTX 4060 Ti CPU_SORT_COPY and RX 470 memory/QBC routes; bound native execution and FULL E2E A/B, with review and separate activation |
| GPU-resident BLACKHOLE encoding and packet drain | **NOT VERIFIED** | Packet-only inverse, exact GPU science comparison, host transfer accounting, correct final drain |
| MathSpec-specific lower-cost independent validation | **RESEARCH** | Proven mathematical guarantee and measured producer+proof+verifier cost, with fraud tests |
| Multi-owner DEVNET and reliable MainNode ACK | **PLANNED** | Authenticated integrity, isolated physical domains, rollback/retry, multi-day operation |
| Distributed AI/marketplace and billing | **PLANNED** | Contract, permission, privacy, payment and operating security review |

The platform should publish **negative findings** and failure gates alongside positive evidence. No new private lab result is automatically promoted to a public, general or production claim.
