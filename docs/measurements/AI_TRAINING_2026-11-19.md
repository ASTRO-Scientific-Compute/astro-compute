# ASTRO AI training evidence — 2026-11-19

**Training implementation: IMPLEMENTED. Finite training and sampled independent numerical audits: VERIFIED. General language and research competence: NOT ESTABLISHED.**

## Model and completed work

The private system trains its own 124,013,568-parameter FP32 Transformer using 512-token windows. RTX 4060 Ti / CUDA and two RX 470 / Vulkan devices train **separate replicas**. They do not aggregate gradients into one distributed model.

The closed automatic V1 run completed three rounds of 256 updates per replica: 768 updates each, continuing cumulative update 1,558 through 2,326. This is not 2,304 unique training windows; the replicas repeat the prescribed curriculum. Language and elementary scientific examples are used, with a separate held-out validation policy and checkpoint promotion only when both validation cross-entropies improve.

## Validation on the selected RTX replica

The same validation sets were used for selection in each round; they are not an untouched final test set. Cross-entropy is in natural-log units per byte, lower is better.

| Validation domain | Target bytes | Before these three rounds | After these three rounds |
|---|---:|---:|---:|
| Language | 4,096 | 3.060574 | 3.052640 |
| Elementary science | 4,096 | 3.741622 | 3.665088 |

All three round-selection checks passed; the test split was not used. Generation was **NOT RUN** in these automatic rounds. Reduced validation loss does not prove useful conversation, scientific reasoning, molecule design or autonomous research.

## Numerical audit boundary

For each of the three rounds on each GPU, the last update was checked over all 124,013,568 parameter values against an independent Float64 update based on the preceding checkpoint. The largest absolute weight error across these nine audits was 5.955433e-8; the largest fraction of allowed per-value error was below 0.250. These are nine audited updates, not all 768 gradients per replica independently recomputed.

The per-value contract was `abs(weight_error) <= 2*ulp(round32(Float64_update)) + learning_rate*(2e-5 + 5e-4*abs(Float64_gradient))`; loss tolerance was absolute `2e-5`, relative `5e-4`. All nine audits passed. Checkpoint preservation, output integrity and numerical accuracy remain separate checks. QGP1 is required on the supported GPU output path.

The [separate 512-update memory replay](MEMORY_2026-11-19.md) is a different campaign; its peaks and timings must not be presented as measurements of these automatic rounds. The small model used in the [private service qualification](MAIN_NODE_2026-11-19.md) is also a different model.

## Continuous controller V2

V2 is implemented without a default total-round or lifetime limit, while retaining explicit finite per-round resource limits. It stops on failures or rejected validation rather than silently accepting a failed candidate. It retains the accepted model and serializes ownership with the other trainer.

**77 CPU checks passed**, including simulated operation beyond 48 rounds and two hours, bounded status, epoch continuity, promotion rejection, interruption and real subprocess-lock checks. These controller checks used zero physical GPU sessions. Multi-day physical GPU training is **NOT TESTED** by that evidence. An in-progress run is not a completed long-duration qualification.

## Evidence and withheld material

Inspected private evidence: the closed automatic V1 plan/status and all three round audit/selection summaries; `auto-training-v2` CPU result, curriculum and isolation checks. Public documentation contains summary counts and metrics only. Model weights, corpora, tokenizer/training/runtime source, optimizer internals and local execution paths remain private. No trained-model release or competent assistant is announced.
