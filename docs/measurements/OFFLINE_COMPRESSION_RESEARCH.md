# Offline compression research — CPU archival result

Date: **2026-11-14**. Campaign: `storage-refinement-v7 / 20261114`. Primary evidence: `FULL_RESULT.json` and `ENCODE_RESULT.json`. Later independent audit: `storage-refinement-v8 / 20261114 / AUDIT_RESULT.json`.

**Status: complete byte reconstruction verified; CPU-only research.** This archive was not produced in the CUDA/Vulkan execution path and is not the GPU QGP1 result.

## Work and size

One complete archive of the [declared scientific workset](GPU_QGP1_2026-11-19.md#full-workload-and-coverage): 10,000 PDE trajectories, five BIO models, 48 first-lead ECG records, 12 Lennard–Jones combinations and one adapted SPACE example. The 128 output records are dominated by PDE bytes. This campaign encodes already computed scientific results; it does not execute a new scientific GPU workload.

| Quantity | Measured value |
|---|---|
| Original result bytes | 16,727,640,608 |
| Complete archive bytes, including format/index/trailer | 3,284,860,953 |
| Original / stored ratio | 5.092344× |
| Stored size reduction | 80.362676% |
| Original size retained | 19.637324% |
| Outputs compared | 128 |
| Bytes compared | 16,727,640,608 |
| Differing bytes | 0 |

**The target of storing at most 10% of the original size was not met.** Approximately 19.64% remains. The smaller archive must not be described as an implemented GPU or network result.

## Cost and verification boundary

One complete encode and one complete independent inverse audit were recorded in V7. These are single observations, not repeated medians. GPU compute is not applicable: zero physical GPU sessions. Memory below is host process peak RSS, not backend allocation or full-system RAM.

| Phase | Wall time (s) | CPU time (CPU-s) |
|---|---|---|
| Encode | 198.992365 | 145.155882 |
| Independent inverse audit | 208.538886 | 168.324261 |
| Recorded full workflow | 407.532836 | 313.481235 |

Recorded peak RSS: **110,170,112 bytes**. These timings describe the recorded offline workflow, not GPU-to-researcher E2E, durable network storage or sustained disk throughput.

The independent decoder restored all 128 outputs / 16,727,640,608 bytes with zero differences. The later V8 audit independently rechecked the same archive; it is corroboration, not a second encoding sample or a smaller new format. Scientific mathematics and external references were not recomputed by either archive check.

## What this does not establish

- No production CUDA/Vulkan implementation was qualified by this research result.
- No reduction in measured PCIe traffic or observed internet traffic was demonstrated.
- The archive size is not substituted into the GPU QGP1 byte accounting or timings.
- Lossless reconstruction preserves the supplied output bytes; it does not prove scientific correctness or authenticity of an untrusted computation.
- CPU archive costs cannot be silently excluded when comparing an end-to-end delivery workflow.

Current implementation and raw evidence remain private. This report publishes measured sizes and verification boundaries, not codec internals, data, model weights or archive files. [GPU QGP1](GPU_QGP1_2026-11-19.md) · [Measurement index](MEASUREMENT_INDEX.md).
