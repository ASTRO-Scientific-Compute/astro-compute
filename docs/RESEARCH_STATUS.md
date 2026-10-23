# ASTRO research progress — 2026-10-23

> **Research disclosure, NOT a public software release.** The repository currently ships a **four-MathSpec bounded Vulkan demonstration** plus the published CPU reference corpus. The items below summarize **separate, privately run research** reported by the project owner. Their full implementations, raw laboratory evidence and locally learned device profiles are **not included in this repository**, and readers cannot independently reproduce these measurements from the public demo alone.
>
> **No production MinerNode, MainNode, distributed AI model, marketplace, universal GPU kernel generator or deployed independent validation network is claimed.** No research science credit was issued for the repeated lab benchmarks.

This page reports both positive and negative evidence. MathSpec correctness, packet bit-exactness, CPU-codec throughput, physical GPU performance and production readiness are **distinct** properties.

## Current GPU Execution Map limitation — acceptance still open

**The current GPU Execution Map is not a completed universal optimizer.** In the private research described by the project owner, important paths still required manual investigation: `CPU_SORT_COPY` on the RTX 4060 Ti, and output/readback memory-path and QBC choices on the RX 470. Those improvements demonstrate gaps in automatic candidate discovery and execution integration. They do not demonstrate that the present search independently discovers the same paths on a new device.

**New MinerNode acceptance requirement — NOT DEMONSTRATED:** starting with a clean device profile, the system must use a versioned, sourced architecture database and native capability measurements to automatically rediscover applicable versions of those paths. The implemented adapters may be reused, but their selection must arise from the measured search; a preloaded winner, GPU-name shortcut, manually forced route or imported profile does not satisfy this requirement.

The rediscovered routes must then execute on their bound devices and pass independent CPU FULL checking and an end-to-end comparison on identical MathSpec/input/work. Include preprocessing and sorting, upload, GPU compute/encoding, readback, CPU decode/check, synchronization and final drain. Report cold setup separately from amortized reuse. A smaller packet, faster kernel, higher busy percentage or lower isolated stage time alone cannot satisfy the gate.

The public four-task demo does not exercise this acceptance test. Automatic rediscovery, correctness, measurement integrity, sustained confirmation and profile activation retain separate statuses. Negative and unavailable paths must remain visible. See the [clean-profile acceptance protocol](ARCHITECTURE_ROADMAP.md#clean-profile-rediscovery-acceptance-gate).

## What is publicly reproducible today?

- Public source: the [bounded four-MathSpec Vulkan demo](GPU_DEMO.md), CPU references and correctness tests; historical BC-250 public demonstration checks are documented in [the v0.1.1 update](BC250_UPDATE_V0_1_1.md).
- This public preview is **experimental** and is distributed under the [source-available demonstration license](../LICENSE), **not** an OSI-approved open-source license. The four-workload evaluation limit remains unchanged.
- No unrestricted MinerNode, private QLAB codec, compiled device-specific winner, or user/worker credential is being published with this research note.

## Selected private-laboratory results (reported scope only)

| Work / checkpoint | Reported finding | What is **not** established |
|---|---|---|
| Gaia / RX 470, PCIe **Gen1 x1**, QBC Universal Fusion V0.2 | `QBC2_PREFIX` approximately **167.19 million FULL-checked source–angle counts/s** in repeated QUICK controls; **0.581026 logical D→H bytes/output**, about **97.14 MB/s** at that rate. About **4.10x** the corresponding RAW end-to-end quick control. | Not sustained, production, a physical PCIe transaction measurement, or an RTX 5090 result. Repeated output checks are not newly credited science. |
| Gaia / QBC V0.4 | CPU-only hybrid `plan11/B128`: **0.493003 B/output** on canonical data, approximately **15.15%** smaller than the comparable QBC2 packet representation. Three-corpus size advantage approximately **18.03%** in the frozen study. Packet-only inverse and scoped agent review reported PASS. | **No V0.4 GPU codec port, GPU E2E speedup or shared 400–450 M/s at <=100 MB/s achievement.** |
| Cross-math / BLACKHOLE V0.5 | XOR/modulo prediction, integer lifting, byte/bitplane transforms, dictionary bitpacking/rANS and bounded selection tested on Gaia, Ising, Heat, Leapfrog and static/dynamic RT. Ising and static RT showed scoped size advantages. | **No generally winning selector**: the six-family bounded selector produced more bytes in aggregate than the older per-case offline minimum; decoder gates failed on its size wins. |
| Ising / AUTO-004-R1 | Frozen two-component dictionary encoder, **same packet bytes**, with a **2.790x** full CPU encode→decode→FULL-cycle speedup for fixed 109 on four new holdout cases (2.185x for fixed 110). Scoped packet-only FULL and review PASS. | No new compression ratio, no GPU/PCIe performance and no release promotion. |
| Ising / AUTO-005 | One read-only dictionary per SIZE950 invocation shared by two actually executed serializers; complete packet bytes unchanged. **1.271x** full CPU-codec throughput improvement on four new holdouts, after validation and review. | No new G2/G3 claim or GPU execution proof. |
| Ising / AUTO-007 retrospective classic baselines | On **26 exposed cases**, classic offline minimum **322,040 B**; SIZE950 **235,236 B** (**26.95% smaller**); SIZE954 **218,676 B** (**32.10% smaller**). Missing baseline coverage was completed retrospectively. | An offline per-case minimum is not a zero-cost online selector; the historical AUTO-006 missing-coverage status was not retroactively altered. |
| Ising / AUTO-006 and AUTO-009 | SIZE954 lowered bytes compared with SIZE950 but reduced measured **CPU-codec throughput to ~0.210x** on 26 exposed cases and **~0.242x** on four initially fresh cases. Evidence-only AUTO-009 attributed roughly **95–96% of measured CPU-codec time to encoding** in that implementation. | **SIZE954 failed decode/performance acceptance**; the CPU transfer model does not predict GPU encode or PCIe x1 execution. |
| Ising / AUTO-012 **SPIN1** | Mathematically checked compression: reconstruct local `(energy, spin)` values from a complete one-bit-per-spin grid only when **every original record** satisfies the exact static Ising identity, otherwise exact fallback. Release and ASan/UBSan, packet-only inverse, fault tests, **518 canonical regressions** and **four new holdouts** reported PASS. On one **257×255 random grid**, a **524,280 B** raw result became an **8,280 B** full packet (**~63.3x raw/packet**). | **Data-family-specific, not a general 64x compressor.** Several structured cases lost to older codecs; inverse speed and joint G2/G3 did not qualify for promotion. No GPU version. |
| Verification Atlas / AUTO-010 and AUTO-011 | Static audit of one-step `PHYSICS_ISING_OBSERVABLES_I32_V1` and `PHYSICS_HEAT_STEP_F32_V1` found **no proven order-of-magnitude cheaper exact validator** for those primitives. A fused full Ising CPU verifier was built and FULL-correctness tested, but overall performance acceptance **failed** across required large holdouts. | No deployed proof-based validator, no claim that a probabilistic check is zero-error, no 100:5 miner/validator capacity claim. |

### Important interpretation boundaries

- **COLD ZERO names commissioning with no inherited performance profile. Exact correctness is a separate gate requiring zero differing bits for exact contracts.** A losslessly decoded packet can still encode a scientifically wrong result: packet roundtrip is not independent science validation.
- A **MathSpec-specific compact representation** may exploit output dependencies. A correct Ising `SPIN1` packet does **not** establish that a remote miner actually performed the energy calculation. Receipt integrity, independence and work accounting are separate problems.
- `FULL`, `QUICK`, fresh holdout, packet-only CPU inverse, agent code review, native GPU execution, sustained testing and external reproduction **must not be interchanged**.
- The 100 MB/s Gaia target is a **total logical GPU-to-host D→H design budget** (packet, headers, guards, receipts, etc.), **not** observed physical PCIe capacity. At 400–450 M results/s it requires about **0.250–0.222 B/output**; this shared goal is **not achieved**.
- No performance numbers on this page refer to the shipped public four-MathSpec demo unless explicitly labeled as such. Hardware configurations and source evidence for the private experiments have not yet been released for independent reproduction.

## Status by workstream

| Workstream | Current disclosure |
|---|---|
| Public four-MathSpec demo | **SHIPPED / EXPERIMENTAL**, bounded correctness and short diagnostic scope; see [status](STATUS.md) |
| BLACKHOLE codec research | **CPU-LAB / PARTIAL SUCCESS**, multiple scoped bit-exact tests; GPU codec **NOT_RUN** |
| Fully autonomous GPU Architecture Atlas and E2E execution generation | **INCOMPLETE / AUTOMATIC REDISCOVERY NOT DEMONSTRATED**; manually investigated RTX 4060 Ti CPU_SORT_COPY and RX 470 memory/QBC paths expose current coverage gaps |
| Exact Verification Atlas | **STATIC RESEARCH / LOCAL CPU EXPERIMENT**, no generally cheaper per-MathSpec verifier established |
| MainNode, independent validator network, distributed AI model, marketplace/payments | **PLANNED / NOT DEPLOYED** |
| Production admission and global profile promotion | **NOT AUTHORIZED** |

## Next publication gates

1. Rebuild the **local MinerNode hardware execution map** around sourced architecture families, backend exposure, native-unit evidence and correct per-device runtime search. Include CPU feed, GPU encode, PCIe readback, CPU decode and final drain; do not hardcode existing GPU winners.
2. Independently reproduce **complete, correctly checked end-to-end performance** on a clean-profile older AMD GPU and a modern NVIDIA GPU before promising portability or operational throughput.
3. Keep the BLACKHOLE GPU encoder/decoder, exact verification proofs and independent multi-owner DEVNET behind separate admission gates. Preserve negative controls and publish sanitized reproduction packages before using them as public benchmark claims.

For architectural ownership and milestones, see [Architecture roadmap](ARCHITECTURE_ROADMAP.md), [Existing public roadmap](ROADMAP.md), and [benchmark methodology](BENCHMARKS.md).
