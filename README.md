# ASTRO — Scientific Research & Compute

ASTRO is developing two services on one mathematical graph and GPU execution foundation:

- **Scientific Research Lab:** AI-assisted problem understanding, planning, simulation, verification and evaluation. WebAI is one interface to this lab.
- **Scientific Compute Network:** execution of researcher-submitted scientific, mathematical and supported AI workloads on heterogeneous GPU miners, with or without AI assistance.

**Status · 2026-11-19:** experimental development. A bounded public demo is available. Later private implementations have passed defined local GPU and two-host tests; a production public research network and a competent scientific assistant are not established.

## What has been demonstrated?

| Scope | Observed result | Evidence and limits |
|---|---|---|
| Public `v0.1.1-demo` | Four fixed GPU tasks; 100 historical Python tests | [Release and diagnostic boundaries](docs/UPDATE_BUGFIX_V0_1_1.md) |
| Private two-host execution | BC-250, RTX 4060 Ti and two RX 470 workers; 12 complete synthetic DAGs, 36 packets | [Network measurements](docs/measurements/MAIN_NODE_2026-11-19.md) |
| Private 124M-model memory replay | RTX backend peak 2.984 → 2.060 GiB; RX 470 3.031 → 2.107 GiB | [Memory measurements](docs/measurements/MEMORY_2026-11-19.md); no general E2E speedup |
| Private model training | 124,013,568 FP32 parameters; 512-token windows; three independent GPU replicas | [Training evidence](docs/measurements/AI_TRAINING_2026-11-19.md); language competence not established |
| Full image inference | MobileNetV2, 100,000 images/card on RTX and two RX 470s | [Inference measurements](docs/measurements/IMAGE_INFERENCE_2026-11-19.md); sampled CPU oracle, historical FP16 Tensor rejection retained |
| GPU QGP1 scientific output | 16.73 GB logical output → 5.35 GB packets; complete lossless reconstruction | [GPU compression measurements](docs/measurements/GPU_QGP1_2026-11-19.md); automatic application did not establish E2E gain |
| Offline CPU archival research | 16.73 GB → 3.285 GB complete archive | [Separate CPU research](docs/measurements/OFFLINE_COMPRESSION_RESEARCH.md); not the production GPU path, 10% size target not met |
| Private Core/API integration | Bounded service, lifecycle and GPU checks | [Status](docs/STATUS.md); not a public WebAI deployment |

These are owner-retained laboratory results summarized for publication, not independently reproduced public runtime releases. Numerical tolerance, same-device replay identity and lossless QGP1 restoration are separate claims.

[Measurement index](docs/measurements/MEASUREMENT_INDEX.md) groups the dated campaigns and defines timing, memory, byte accounting and correctness limits. Image inference is distinct from image generation and language-model training; its QGP1 packets were slightly larger than the raw logits.

## Public demo

The reproducible public demo remains the tagged, fixed four-task evaluation. Install the Linux build/Vulkan prerequisites in the [setup guide](docs/GPU_DEMO.md) first:

```bash
git clone --branch v0.1.1-demo https://github.com/ASTRO-Scientific-Compute/astro-compute.git
cd astro-compute
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
bash run_gpu_demo.sh
```

Read [v0.1.1 results](docs/BC250_UPDATE_V0_1_1.md), [original BC-250 results](docs/REFERENCE_DEMO_RESULTS.md) and [hardware reporting guidance](CONTRIBUTING.md). No new physical GPU test was run for this documentation update.

## Public and private scope

This repository uses the restricted, source-available [ASTRO Demonstration License](LICENSE), explained in [LICENSING.md](LICENSING.md). It is not an unrestricted open-source release.

The historical [2026-11-08 miner snapshot](ASTRO_MINER_20261108.md) contains engine and optimizer source. Its extracted launcher and benchmark were explicitly **not independently GPU-qualified**. It is not a release of the current private Main Node, AI runtime or training system. Existing license terms are unchanged.

Current private runtime source, compiler and optimizer internals, model weights, researcher datasets and deployment configuration are outside this documentation update. The historical [QGC1 measurements](ASTRO_MEASUREMENTS_20261108.md) remain unchanged; later QGP1 results are dated separately.

## Development map

- [Status and evidence boundaries](docs/STATUS.md)
- [Shared Main Node / miner architecture](docs/ARCHITECTURE.md)
- [Roadmap with acceptance gates](docs/ROADMAP.md)
- [Changelog](CHANGELOG.md)
- [Historical research limitations](docs/RESEARCH_STATUS.md)
- [GPU execution-map acceptance protocol](docs/ARCHITECTURE_ROADMAP.md#clean-profile-rediscovery-acceptance-gate)
- [Security](SECURITY.md) · [Contribution policy](CONTRIBUTING.md)

The [previous README at its original commit](https://github.com/ASTRO-Scientific-Compute/astro-compute/blob/ad6dff7c263c1a2845f604267092c68725f0c39f/README.md) preserves the earlier project presentation and links. Historical tests and releases retain their original scope.
