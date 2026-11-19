# ASTRO roadmap — 2026-11-19

Milestones have acceptance gates rather than promised dates or unbounded capacity. Current status and historical results are in [STATUS.md](STATUS.md).

| Milestone | Starting state | Evidence required to advance |
|---|---|---|
| Main Node Core | Private service IMPLEMENTED; finite checks VERIFIED | Sustained mixed load; resource and retention bounds; restart, machine reboot and failure recovery without lost or duplicate accepted work |
| Generic Graph Planner | Supported typed graphs and bounded packetized matrix route IMPLEMENTED | More operation families, legal partition boundaries and complete result reconstruction; malformed graphs rejected before execution; no per-dataset backend edits |
| Hardware routing and optimization | CUDA/Vulkan paths IMPLEMENTED; broader search EXPERIMENTAL | Clean-profile candidate discovery from actual capabilities; correctness-qualified local choice; transfer, CPU, GPU, memory and complete E2E accounting |
| Public Web / API | PLANNED; private status/API foundation exists | Separate researcher/miner/admin authorization, safe submission, quotas, real status within five seconds or explicit offline state, and deployment security review |
| WebAI serving | Private finite integration EXPERIMENTAL | Qualified trained model, isolated persistent sessions, bounded KV ownership, grouped decode, cancellation and sustained latency/throughput measurements |
| Model training and scientific quality | Private 124M training IMPLEMENTED; useful competence NOT ESTABLISHED | Broader authorized data, reproducible curriculum, untouched test set, generation and task-quality evaluation; independent numeric checks and safe checkpoint promotion |
| Low-memory execution | Specific 0.924 GiB reduction VERIFIED | Larger layers and contexts under hard resource bounds; compare complete costs; treat quantization as a separate numerical contract; no blanket 24 GB → 8 GB claim |
| Miner authentication | Trusted local operators only | External identity and credential lifecycle, revocation, replay rejection, capability checks and adversarial tests |
| P2P data plane | General deployment PLANNED | Authorized direct compressed-object exchange, integrity, resumable transport, retention and failure tests; no unsupported bandwidth-saving claims |
| Node A/B failover and state migration | PLANNED / NOT TESTED | Fenced ownership, durable receipts, state recovery and no double accounting across physical failures or network partitions |
| Fair shared service | Bounded local queues IMPLEMENTED; general fairness not qualified | Many owners with unequal job counts and long/short mixed jobs; bounded waiting and memory; research and WebAI priorities without starvation |
| Public release qualification | Existing licensed demo remains available | Explicit source allowlist, privacy/license review, clean-machine dependency closure, physical tests of the exact package and owner approval |

## Acceptance principles

1. New work expressible with supported primitives should arrive as a graph description. New compiler abilities should generalize across datasets.
2. A successful upload or accepted lease is not a completed scientific result. Count unique full workloads, internal packets and repeats separately.
3. Preserve dependencies and session isolation while keeping prepared programs, weights and state resident where safe. Optimize measured repeated work, not power draw alone.
4. Lossless compression remains required on supported production output paths. Compare eligible compressed routes and include metadata and fallback bytes.
5. Qualification budgets separately bound sessions, evaluations, worker time, GPU time and memory. Failures and untested cases remain visible.
6. A reference-tolerance PASS, same-device replay identity and byte-perfect codec restoration must retain separate labels.
7. New public releases require approval; internal progress does not automatically open the source or qualify public operations.

The [historical roadmap](https://github.com/ASTRO-Scientific-Compute/astro-compute/blob/ad6dff7c263c1a2845f604267092c68725f0c39f/docs/ROADMAP.md), [November 8 development direction](../ASTRO_DEVELOPMENT_ROADMAP_20261108.md) and [execution-map rediscovery gate](ARCHITECTURE_ROADMAP.md#clean-profile-rediscovery-acceptance-gate) remain historical references. This update does not silently close older correctness issues or promise an operational marketplace.
