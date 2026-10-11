# ASTRO Public GPU Demo v0.1

**Experimental prerelease · source-available evaluation software · not production-ready.**

This is the first bounded public Vulkan GPU demo, accompanied by ASTRO's canonical CPU reference corpus. It is not a full MinerNode release.

## Included

- Four fixed MathSpecs: `SPACE_GWOSC_FFT256_V1`, `SPACE_GWOSC_CONVOLUTION_V1`, `SPACE_GWOSC_XCORR_V1` and `SIGNAL_FIR_ACCUMULATE_I16_V1`.
- Actual DIRECT and TILED kernels on the same deterministic synthetic input; native C++17/Vulkan sources, shader generation and portable setup instructions.
- Complete warmup/final-output comparison against the canonical independent CPU oracle. All four demo contracts require COLD ZERO: **0 differing bits**. A failed correctness check stops execution and has no accepted throughput.
- A maximum of four distinct allowed MathSpecs per run, enforced at launcher/generator/native admission. No unrestricted search or supported limit override.
- Compact diagnostic profiles and automatic removal of temporary build/trial data on normal completion and handled interruptions.
- 81 CPU reference primitives (66 SPACE), analytic vectors and a sanitized 94-entry registry inventory; these are different scopes from the four GPU demo tasks.

## Try it

Follow [GPU setup and dependencies](../GPU_DEMO.md), then run from the repository:

```bash
bash run_gpu_demo.sh
```

The sources require Linux, Python 3.10–3.12, NumPy, a C++17 compiler, Vulkan headers/loader, shader tools and a working compute driver with timestamps. No prebuilt executables or private development state are required.

## Validation scope

The published demo implementation passed 93 Python tests, native builds and all eight shader/SPIR-V checks. A local AMD BC-250 / RADV GFX1013 run completed all four tasks and eight DIRECT/TILED correctness checks. A separate Mesa software-Vulkan run also passed; its timing is not physical GPU performance. Hosted CI covers Python 3.10/3.12, native/shader builds, software-Vulkan correctness and cleanup; see the [workflow](https://github.com/ASTRO-Scientific-Compute/astro-compute/actions/workflows/demo-ci.yml).

Every demo timing is **QUICK_DIAGNOSTIC_ONLY**, in the MathSpec's natural work units/s. There is no sustained leaderboard claim, historical speedup claim or certified cross-vendor performance claim. Power/clock readings are diagnostic; unavailable telemetry remains UNAVAILABLE.

Implementation agreement and scientific validity are separate gates: byte-identical implementations can still share an inadequate numerical approximation. See the [validation model and historical Hann FFT/whitening example](../VALIDATION.md). The historical example is not a new public-demo reproduction.

## Known limitations

- Physical hardware commissioning in this public scope is currently limited to the documented BC-250 run. Broader AMD/NVIDIA/Intel hardware results require new evidence.
- No unrestricted Census/Hardware Intelligence/AI Fusion search, RT executor, tensor/inference backend or full MinerNode is shipped as an operational demo feature.
- No production network, MainNode receipt service, Scientist service or independent distributed validation network.
- Native register allocation/occupancy evidence is unavailable in this demo. No claim that every internal development feature is portable or commissioned.
- Abrupt host failure or SIGKILL can leave temporary files; normal/handled cleanup cannot prevent that.
- Independent agent review is complete for the bounded demo scope. **External human review is PENDING.**

## License and external results

**Source-available demonstration software. Free to evaluate using the included demo. All other use requires explicit permission from the copyright holder.** See [LICENSE](../../LICENSE). This is not an open-source or OSI-approved license. Modification, commercial/service use, integration, relicensing and limit circumvention require written permission.

External contributors can report unmodified-demo results with the [reproduction template](../EXTERNAL_REPRODUCTIONS.md). No external scores have been invented or imported from internal benchmark profiles.
