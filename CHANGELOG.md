# Changelog

## Performance evidence V2 · 2026-11-19

- Add complete MobileNetV2 / 100,000-image inference measurements for V13, V16 and the later QGP1 application, with CPU, GPU, memory and sampled-reference boundaries.
- Retain the V17 negative result: real FP16 Tensor execution was faster but failed the expanded numerical contract; it is not an accepted speedup.
- Add full scientific GPU QGP1 size, serial/overlap timing and automatic-selection evidence; distinguish packet, D2H API and stored-container bytes.
- Report storage backpressure and the absence of an automatic-application E2E gain without attributing a proven SSD fault.
- Document the smaller CPU-only archive separately, including encoding/audit cost and the unmet 10% target.
- Add a measurement index. Preserve all runtime, CI, license, release and historical measurement files; no new private source or raw evidence is published.

## Documentation preparation · 2026-11-19

- Present the Scientific Research Lab and direct Scientific Compute Network as two services on one Main Node / graph / miner foundation.
- Add scoped private-laboratory summaries for two-host execution, the later private Core/API qualification, 124M memory replay and model training.
- Distinguish implementation, finite verification, experimental work, planned services and missing evidence.
- Preserve numeric tolerances, same-device replay identity and QGP1 restoration as separate claims; retain historical QGC1 reports unchanged.
- Keep the licensed public demo, old releases, tests, source archive and license files unchanged. No current private implementation, weights or data are added.
- This is a documentation update, not a new GPU-qualified release, public WebAI launch or general performance claim.

## Presentation update · 2026-10-12

- Lead the README with scoped public evidence, a tagged quick start and an exact published profile excerpt.
- Add a bounded-demo hardware reproduction issue form and refresh the social preview.
- Preserve all runtime, mathematical, licensing and historical evidence bytes; technical status and acceptance gates are unchanged.

## v0.1.1-demo — Update / Bugfix · 2026-10-12

- Bound native timing memory with online aggregates instead of per-batch trace retention.
- Release pure oracle caches and idle local heap between MathSpecs; record actual RSS/swap observations.
- Stop writing compiler/artifact hash manifests; preserve in-memory source/SPIR-V binding checks with streamed hashing.
- Save compact atomic per-task checkpoints and retain normal interruption cleanup.
- Add opt-in command-buffer reuse with native execution receipts; baseline remains default, fixed four-task cap unchanged.
- Add resource regressions and baseline/reuse software-Vulkan CI checks.
- Publish all BC-250 diagnostic A/B observations, including regressions and unchanged-path variability. No sustained or general speedup claim.
- Document the separate development miner CPU_HOST, storage-retention and memory-lifetime fixes without claiming the unrestricted search ships in the demo.

[Detailed Update / Bugfix notes](docs/UPDATE_BUGFIX_V0_1_1.md) · [BC-250 comparison](docs/BC250_UPDATE_V0_1_1.md)

## v0.1.0-demo — historical

The original bounded DIRECT/TILED demo, owner-selected evaluation license, canonical references and CI. [Original release notes](docs/releases/PUBLIC_GPU_DEMO_V0_1.md) and [unchanged BC-250 reference](docs/REFERENCE_DEMO_RESULTS.md).
