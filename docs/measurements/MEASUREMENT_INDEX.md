# ASTRO measurement index

This index groups **dated, scoped observations**, not a universal GPU leaderboard. The current private runtime and raw evidence are not published. The tagged public demo remains independently runnable within its own limits; private campaigns below cannot be reproduced from the public repository alone.

## Campaigns added in this update

Every image full pass uses the same 100,000 STL-10 images / 100 million MobileNetV2 logits. Every science full pass produces the same 16,727,640,608 logical output bytes / 128 records. Repeated passes and replicas do not add unique research cases. Exact evidence basenames, timing boundaries, resource costs and audit scope are in the linked reports.

| Date / campaign ID | Work and hardware / backend | Full measurement samples | Result and qualification | Report |
|---|---|---|---|---|
| 2026-11-14 · `matrix-stride-v13 / 20261114T173908Z` | Full image inference; RTX CUDA + RX 470 ×8/×1 Vulkan concurrently | One baseline + one selected pass/card | RX observed E2E ratios 2.3635× / 2.1510×; 36-image reference sample and complete same-device byte comparisons. Historical RTX FP16 path later rejected | [Image inference](IMAGE_INFERENCE_2026-11-19.md#v13--generic-matrix-optimization) |
| 2026-11-14 · `index-ir-v16 / 20261114T183849Z` | Same image corpus; three concurrent cards | One baseline + one selected pass/card | Selected rig 109.407135 s, 2742.051501 image-instances/s for this static assignment. Historical RTX numerical qualification later revoked | [Image inference](IMAGE_INFERENCE_2026-11-19.md#v16--generic-index-optimization) |
| 2026-11-14 · `tensor-ab-v17 / 20261114T190637Z` | Full image inference; RTX CUDA only | Three full passes/mode | Real HMMA execution; FP16 Tensor rejected on expanded 214-image audit, FP32 SIMT passed the sample | [Tensor negative result](IMAGE_INFERENCE_2026-11-19.md#v17--real-tensor-instructions-failed-numerical-gate) |
| 2026-11-19 · `dispatch_corpus_v1 / 20261119T032516Z` | Full science and image work; three concurrent cards | One control + one enabled pass/workload/card | Full output identity; image evidence covers 217 CPU-reference images/card. No general host-cache E2E gain | [Audit provenance](IMAGE_INFERENCE_2026-11-19.md#november-19--complete-inference-with-mandatory-gpu-qgp1) |
| 2026-11-19 · `codec_autobench_v1 / 20261119T051339Z`, image application | Full image inference; three concurrent cards | One pass/card | E2E 43.992579 / 98.947483 / 120.515500 s; all bytes restored; inherited 217-image audit. QGP1 packet slightly larger than raw logits | [Image inference](IMAGE_INFERENCE_2026-11-19.md#november-19--complete-inference-with-mandatory-gpu-qgp1) |
| 2026-11-14 · `gpu-pipeline-v1 / physical-20261114T064656Z` | Complete scientific work; RTX CUDA only | One RAW + three serial QGP1 + three overlap QGP1 | 5.35 GB packets, full lossless inverse audit. Overlap median 116.467256 s; RAW has only one timing | [GPU QGP1](GPU_QGP1_2026-11-19.md#november-14--rtx-serial-and-overlap-execution) |
| 2026-11-19 · `codec_autobench_v1 / 20261119T051339Z`, science calibration/application | Complete scientific work; three concurrent cards | Two full passes/setting/card, then one application/card | Setting 1 selected for smaller packets; Radeon measured-profile reuse, RTX conservative fallback. Application did not establish E2E gain | [Automatic codec selection](GPU_QGP1_2026-11-19.md#november-19--automatic-codec-selection-on-three-concurrent-gpus) |
| 2026-11-14 · `storage-refinement-v7 / 20261114`, V8 audit | Previously computed complete scientific output; CPU only, no GPU backend | One full archive encode; V7 inverse plus later V8 inverse | 3,284,860,953 bytes, zero differing restored bytes. 10%-retained-size goal not met; not a production GPU path | [Offline compression research](OFFLINE_COMPRESSION_RESEARCH.md) |

## Previously documented evidence

These earlier documents keep their original qualification boundaries:

- [124M model memory replay](MEMORY_2026-11-19.md): backend allocation savings on a defined replay; not universal 24 GB → 8 GB compatibility.
- [Model training](AI_TRAINING_2026-11-19.md): independent replicas and finite numerical checks; not established language competence.
- [Main Node and two-host execution](MAIN_NODE_2026-11-19.md): finite network and service qualification; not an open worldwide miner fleet.
- [Public demo results](../REFERENCE_DEMO_RESULTS.md) and [v0.1.1 changes](../BC250_UPDATE_V0_1_1.md).
- [Historical QGC1 measurements](../../ASTRO_MEASUREMENTS_20261108.md): preserved under their original format name and date.

## Definitions

- **E2E / wall time:** elapsed time within the report's stated run boundary. Offline compilation, reference preparation/audits, durable disk flush and actual network delivery are not automatically included. Compare only like boundaries.
- **Process-tree CPU-s:** CPU time aggregated over the included process tree. It can exceed wall time through parallel execution; GPU interval differences do not identify CPU waste.
- **GPU time:** instrumented device intervals. Total, mathematics and codec subsets are labeled separately. Overlap can make interval sums differ from wall duration. A device-utilization percentage does not measure useful arithmetic throughput.
- **Backend peak bytes:** tracked backend buffer allocations. This is neither total driver VRAM nor host RSS. Offline CPU research reports host RSS explicitly instead.
- **Packet bytes:** complete encoded format payload, including raw fallback and in-format metadata. **D2H API bytes:** bytes accounted at device-to-host transfer APIs, including transfer metadata. **Stored file bytes:** packet payload plus container/index/framing. None by itself is measured internet traffic.
- **Numerical reference PASS:** the named mathematical tolerance or detector metric on the stated sample/corpus. It does not mean bit identity or ground-truth classification accuracy.
- **Replay identity:** full output equivalence between the compared executions. It is not an independent mathematical oracle.
- **ZERO BIT / lossless restoration:** every decoded byte equals the original byte supplied to the encoder, within the explicitly tested output set. This does not certify the original computation.
- **Units:** seconds (s), CPU-seconds (CPU-s), exact byte counts; decimal GB = 10^9 bytes, MiB = 2^20 bytes, GiB = 2^30 bytes. Ratios use original bytes / complete stored or packet bytes as labeled; reduction = 1 − encoded/original.

## Evidence and reproduction policy

Tables derive from retained structured campaign records, not from new GPU runs for this update. Campaign IDs and filenames are traceability labels, not links to publicly released evidence files. No private source, data, weights, raw result archive, local path, credentials or hash inventory is added. An independent developer can inspect these reported boundaries and run the existing public demo, but cannot independently reproduce the current private campaigns from this documentation alone.

A pass applies only to the named work, contract, hardware and measurement lifetime. Failures, fallback behavior and negative performance findings remain visible. GitHub Actions verifies the unchanged public demo, not the private runtime behind these measurements.
