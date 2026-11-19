# ASTRO status — 2026-11-19

**Overall: EXPERIMENTAL.** This page distinguishes the public demo from later private development. A passed check covers only the named work, hardware, numerical contract and lifetime.

## Labels

| Label | Meaning |
|---|---|
| IMPLEMENTED | Concrete implementation exists in the stated public or private scope |
| VERIFIED | A named physical or software check passed within its stated bounds |
| EXPERIMENTAL | Research implementation with open qualification or integration limits |
| PLANNED | Intended capability, not a working service claim |
| UNAVAILABLE / NOT TESTED | Evidence is absent or the described check was not performed |

## Current evidence

| Component | Scope and status | Qualification boundary |
|---|---|---|
| Canonical references and fixed GPU demo | Public; IMPLEMENTED / VERIFIED | Historical analytic tests and fixed-task demo evidence; [publication scope](PUBLICATION.md) and [v0.1.1](UPDATE_BUGFIX_V0_1_1.md) |
| November 8 miner archive | Historical public source snapshot; EXPERIMENTAL | Extracted launcher/bench NOT TESTED on GPU as a standalone package; existing source exposure does not imply a current private runtime release |
| Typed mathematical graph engine | Private; IMPLEMENTED / VERIFIED on tested graphs | CUDA/Vulkan, resource limits and independent numerical contracts; arbitrary unsupported mathematics is not claimed |
| GPU-side QGP1 output | Private; IMPLEMENTED / VERIFIED on tested paths | Lossless output packaging required on current supported paths; raw fallback may occur inside the format; compression integrity is not scientific correctness |
| Dependency-driven packet queue | Private; IMPLEMENTED / VERIFIED | Two hosts, four workers, 12 synthetic complete DAGs; [measurements](measurements/MAIN_NODE_2026-11-19.md) |
| Main Node Core/API and private WebAI integration | Private; IMPLEMENTED / VERIFIED in finite tests / EXPERIMENTAL | Later service qualification includes lifecycle tests and short GPU generation on a separate 426,688-parameter model; no public endpoint or always-on GPU fleet claim |
| Generic memory reduction | Private; VERIFIED on the 124M training replay | Approximately 0.924 GiB fewer backend allocations; same-device replay identity; [memory report](measurements/MEMORY_2026-11-19.md) |
| 124M FP32 model training | Private; IMPLEMENTED / VERIFIED within the training audit | 512-token windows, three separate replicas, held-out validation; [training report](measurements/AI_TRAINING_2026-11-19.md) |
| Continuous training controller V2 | Private; IMPLEMENTED / VERIFIED by 77 CPU checks | Simulated lifecycle and real process-lock checks; multi-day physical GPU operation NOT TESTED |
| Public Web / WebAI and researcher onboarding | PLANNED | No verified public service, authentication lifecycle or external-miner trust qualification |
| Scientific AI planning and useful conversation | EXPERIMENTAL / NOT ESTABLISHED | Training loss improvements do not establish reasoning, research competence or chatbot quality |
| General graph partitioning / universal local optimization | EXPERIMENTAL; broader coverage PLANNED | All-Transformer network decomposition and universal automatic optimal-route discovery are not established |
| Cross-node failover / stateful migration / adversarial validation | PLANNED / NOT TESTED | Service restart checks do not qualify machine loss, Node A/B failover or untrusted miners |

The first network campaign closed its qualification workers and server. A **separate later** private Core/API campaign deployed a continuing service and closed its finite GPU workers. These are different snapshots, not contradictory lifetime claims. A two-minute availability probe is not a multi-hour or multi-day serving qualification.

## Measurement rules

- Worker E2E is wall time inside its named worker boundary; it is not automatically full researcher-to-result latency.
- Process-tree CPU time and GPU event intervals measure different work. Neither their difference nor E2E minus GPU time is automatically CPU waste.
- Backend buffer allocation is distinct from host RAM and total driver-reported VRAM.
- Numeric PASS against a Float64 oracle does not imply bit identity across devices.
- Same-device checkpoint replay identity does not imply all intermediate gradients were independently recomputed.
- QGP1 ZERO BIT concerns restoration of encoded bytes. It does not certify an untrusted miner's mathematics.
- QGC1 remains the format named in the November 8 historical report. Its results are not relabeled QGP1.

## Historical limitations remain visible

The [October status at its original commit](https://github.com/ASTRO-Scientific-Compute/astro-compute/blob/ad6dff7c263c1a2845f604267092c68725f0c39f/docs/STATUS.md) records an intermittent image-moments runtime mismatch and missing execution-map evidence. This documentation update does not close that issue or qualify those historical paths. The [clean-profile rediscovery gate](ARCHITECTURE_ROADMAP.md#clean-profile-rediscovery-acceptance-gate) remains open without new route-specific proof.

GitHub Actions tests the **public demo**. Its green status does not certify the nested miner archive or the private Main Node, AI and training implementations. New measurements below were checked against local reports and structured summaries; private raw evidence and implementations are not included, so public independent reproduction of those later runs is unavailable from this repository alone.
