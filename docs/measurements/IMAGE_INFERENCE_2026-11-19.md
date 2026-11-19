# Full image inference — measurements through 2026-11-19

**Workload: MobileNetV2 image inference, 100,000 STL-10 images, 1,000 output logits per image.** The model uses pretrained ImageNet weights; this is image inference, not image generation or the ASTRO-trained 124M language model. Each full pass processes the same 100,000 distinct unlabeled images and produces 100,000,000 FP32 logits (400,000,000 bytes). Three cards processing them means 300,000 image-instances, not 300,000 different images.

Status: private laboratory measurements, with scoped correctness evidence. The faster historical FP16 Tensor route was subsequently **rejected**. No full-corpus independent oracle or ground-truth classification accuracy is claimed.

## Measurement contract

All times below are seconds; CPU time is aggregate process-tree CPU-seconds. Backend peak is tracked backend buffer allocation in bytes, not total GPU VRAM or host RAM. GPU event intervals are not occupancy and cannot be subtracted from E2E to infer CPU waste. Independent audits and offline compilation are outside these timed E2E boundaries. Buffered output persistence is included; durable `fsync`, network transit, installation and system boot are not measured. See [common definitions](MEASUREMENT_INDEX.md#definitions).

RTX uses CUDA; the two RX 470 cards use Vulkan on the same Linux rig. ×8 and ×1 identify PCIe link widths, not different chip architectures. The three-card campaigns below run concurrently and share host CPU, RAM and storage. These are not isolated GPU rankings. V17 is the explicitly noted single-RTX exception. Times printed to six decimals do not imply microsecond repeatability.

## V13 — generic matrix optimization

Date: **2026-11-14**. Campaign: `matrix-stride-v13 / 20261114T173908Z`. Primary evidence: `SUMMARY.json`, paired `SESSION_RESULT.json`, group results and full-output comparisons. Each row is one complete baseline pass and one selected pass per GPU, baseline first; three GPUs run together in each arm.

| GPU / backend | Baseline E2E (s) | Selected E2E (s) | Observed ratio |
|---|---|---|---|
| RTX 4060 Ti / CUDA | 41.679451 | 41.205929 | 1.0115× |
| RX 470 ×8 / Vulkan | 320.383835 | 135.555483 | 2.3635× |
| RX 470 ×1 / Vulkan | 344.017103 | 159.930082 | 2.1510× |

| GPU / backend | Process-tree CPU (CPU-s), baseline → selected | GPU interval (s), baseline → selected | Backend peak (bytes), baseline → selected |
|---|---|---|---|
| RTX 4060 Ti / CUDA | 18.514826 → 14.822520 | 33.973092 → 35.478783 | 881,704,452 → 2,269,462,020 |
| RX 470 ×8 / Vulkan | 24.055252 → 15.594561 | 290.561623 → 122.840636 | 700,743,184 → 1,394,621,968 |
| RX 470 ×1 / Vulkan | 24.846164 → 16.634389 | 290.319862 → 125.640605 | 700,743,184 → 1,394,621,968 |

Rig wall time: **344.077703 → 160.083171 s**. These are full-pass timings, not the many small tuning samples. The search screened 13 candidates per card on 2,048 images, then confirmed three finalists three times on 8,192 images. There was no extra hidden warm-up. The approximately 192.866 s offline precompile is excluded from the reported full-pass E2E.

The change used the generic compiler matrix route; the campaign reported no handwritten GPU backend source changes. This does not establish an equivalent gain on other networks, datasets or devices. The selected backend memory increase is part of the cost, not hidden by the speed ratio.

**Correctness boundary:** 36 independently checked images per card and pass, with `abs(actual-reference) <= 0.05 + 0.005*abs(reference)`. All 100 million logits were finite. Within each card, baseline and selected full logits were byte-identical across all 400,000,000 bytes; this is implementation equivalence, not an independent full-corpus oracle. The original sample passed, but the historical RTX FP16 route must be read with the later V17 rejection below.

## V16 — generic index optimization

Date: **2026-11-14**. Campaign: `index-ir-v16 / 20261114T183849Z`. Primary evidence: `SUMMARY.json`, paired `SESSION_RESULT.json` and full-output comparisons. Again, one full baseline and one full selected pass per GPU, three GPUs concurrently, same 100,000 images per pass.

| GPU / backend | Baseline E2E (s) | Selected E2E (s) | Observed ratio |
|---|---|---|---|
| RTX 4060 Ti / CUDA | 35.936470 | 33.498841 | 1.0728× |
| RX 470 ×8 / Vulkan | 108.147579 | 86.946199 | 1.2438× |
| RX 470 ×1 / Vulkan | 131.407849 | 109.335274 | 1.2019× |

| GPU / backend | Process-tree CPU (CPU-s), baseline → selected | GPU interval (s), baseline → selected | Backend peak (bytes), baseline → selected |
|---|---|---|---|
| RTX 4060 Ti / CUDA | 14.100387 → 14.160009 | 30.399504 → 27.767974 | 2,269,462,020 → 2,269,462,020 |
| RX 470 ×8 / Vulkan | 14.906458 → 14.806935 | 96.766507 → 76.418181 | 1,394,621,968 → 1,394,621,968 |
| RX 470 ×1 / Vulkan | 15.976683 → 15.409425 | 99.137438 → 78.613696 | 1,394,621,968 → 1,394,621,968 |

Rig wall time: **131.478794 → 109.407135 s**. The selected static assignment completed **2742.051501 image-instances/s** across the rig. This divides 300,000 repeated image-instances by the group wall time; it is not the rate for unique images or a general scheduler capacity.

The search screened six candidates per card on 2,048 images and confirmed two finalists three times on 8,192 images. The full-pass reference boundary remained 36 images; same-device baseline/selected full logits were byte-identical. Historical RTX FP16 qualification was later revoked after V17 found counterexamples. Its timing remains a historical observation, not an accepted current numerical speedup. Radeon results retain their stated sample-limited qualification.

V13 and V16 use their own contemporary baselines. Comparing their selected timings across campaigns is not a controlled paired experiment.

## V17 — real Tensor instructions, failed numerical gate

Date: **2026-11-14**. Campaign: `tensor-ab-v17 / 20261114T190637Z`. Sources: `SUMMARY.json`, `extended-reference/RESULT.json` and full-run `HARDWARE_PROOF.json`. Hardware: one RTX 4060 Ti, CUDA. Each mode ran the complete 100,000-image task three times in the order Tensor, SIMT, SIMT, Tensor, Tensor, SIMT. Four additional 2,048-image screening passes are separate from the full-run medians.

| Execution | Median E2E (s) | Full E2E range (s), n=3 | Median CPU (CPU-s) | Median GPU (s) | Backend peak (bytes) |
|---|---|---|---|---|---|
| FP16 Tensor | 33.426835 | 33.268515–33.661727 | 14.139868 | 28.010627 | 2,269,462,020 |
| FP32 SIMT | 39.237896 | 39.192189–39.518654 | 14.497581 | 33.235920 | 2,269,462,020 |

FP16 matrix operands with FP32 accumulation and FP32 SIMT were held to the **same numerical tolerance**, not identical operand precision. Loaded program identities were joined to dispatch evidence: each full pass had 51,612 dispatches; the Tensor pass had 27,370 dispatches to entries containing HMMA instructions, while the SIMT pass had zero. This proves execution of the identified programs; it does not measure Tensor occupancy or the fraction of total arithmetic performed by HMMA.

The original 36-image sample passed. After inspecting cross-mode disagreements, an expanded **214-image diagnostic sample** was checked against an independent CPU model oracle. It was selected deliberately, not randomly. The same tolerance `0.05 + 0.005*abs(reference)` was retained.

| Execution | Failed images / 214 | Tolerance-violating logits | Maximum absolute logit error | Expanded audit |
|---|---|---|---|---|
| TENSOR | 3 | 6 | 0.1046419144 | FAIL |
| SIMT | 0 | 0 | 4.100799561e-05 | PASS |

**The faster FP16 Tensor configuration is rejected.** Its timing advantage is not an accepted correctness-preserving speedup. The prior RTX profile was revoked. FP32 SIMT passed this expanded sample, not a full 100,000-image independent CPU proof. Same-mode full-output repetitions were byte-identical; cross-mode byte identity was not expected and was not achieved. Top-1 agreement with a model oracle is distinct from labeled classification accuracy.

Later TF32x3 work is outside this campaign and is not used to repair or relabel this failed FP16 result.

## November 19 — complete inference with mandatory GPU QGP1

Date: **2026-11-19**. Timing source: `codec_autobench_v1 / 20261119T051339Z`, `MEASUREMENT_SUMMARY.json`, phase `images-auto`. Reference provenance: `dispatch_corpus_v1 / 20261119T032516Z`, `images-1` per-device `OFFLINE_AUDIT.json`.

One complete pass per GPU, three cards concurrently. Each card processed all 100,000 images and all 100 million logits. These three timings come from the codec application campaign, not from the earlier dispatch audit.

| GPU / backend | E2E (s) | Process-tree CPU (CPU-s) | GPU total (s) | GPU mathematics (s) | Backend peak (bytes) |
|---|---|---|---|---|---|
| RTX 4060 Ti / CUDA | 43.992579 | 18.412865 | 34.141981 | 33.330214 | 2,328,199,176 |
| RX 470 ×8 / Vulkan | 98.947483 | 18.343602 | 83.020770 | 76.358070 | 1,453,359,136 |
| RX 470 ×1 / Vulkan | 120.515500 | 17.706052 | 85.376101 | 78.715257 | 1,453,359,136 |

For each GPU:

- Raw logits: **400,000,000 bytes**; with execution counters: **400,000,032 bytes**.
- QGP1 packets: **400,025,056 bytes**. All 391 frames used raw fallback inside the mandatory lossless format. The encoder still ran.
- D2H API transfer accounting: **400,025,304 bytes**, including additional transfer metadata. H2D API accounting: **2,778,824,192 bytes**.
- Thus packets are 25,056 bytes larger than the logits, or 25,024 bytes larger than logits plus counters. **No compression saving was obtained on this output.** This is not a network transfer measurement.
- Image work had no matching learned science profile and used conservative fallback; it was not an image-specific tuning success.

Independent restoration checked all 400,000,032 bytes against retained audited output identities, with zero differing bytes. The separate inverse audit took approximately 3.1–3.3 s per device and is excluded from the table.

The matching earlier audit checked 217 images / 217,000 logits per GPU against retained independent CPU reference values. That audit reported:

| GPU / backend | Reference images | Maximum absolute logit error | Reference top-1 agreement |
|---|---|---|---|
| RTX 4060 Ti / CUDA | 217 | 4.100799561e-05 | 217/217 |
| RX 470 ×8 / Vulkan | 217 | 4.291534424e-05 | 217/217 |
| RX 470 ×1 / Vulkan | 217 | 4.291534424e-05 | 217/217 |

The current run **inherits** that numerical result through identity of every restored output byte; it did not calculate a new 217-image CPU oracle. All 100 million logits were finite. The remaining images do not have independent CPU-oracle coverage. A 217/217 top-1 match is not STL-10 ground-truth accuracy, and the diagnostic sample does not provide a population confidence interval.

The earlier `dispatch_corpus_v1` full A/B campaign itself found no general E2E improvement from the host dispatch-cache change. Its same-work output audit is valuable evidence without turning that timing result into a speedup claim.

## Reproduction and publication limits

These summaries were checked against owner-retained structured evidence, not newly benchmarked during publication. The private current engine, profiles, weights, input corpus, output arrays and local evidence manifests are not included. Campaign identifiers and evidence basenames above allow the owner to trace each result, but do not enable independent reproduction from this repository alone. Public-demo CI verifies the public demo only.

No result here establishes general GPU rankings, language-model token throughput, universal memory reduction, network throughput or scientific reasoning ability. [Measurement index](MEASUREMENT_INDEX.md) · [GPU QGP1 report](GPU_QGP1_2026-11-19.md).
