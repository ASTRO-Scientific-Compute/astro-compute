# Bounded GPU evaluation demo

**EXPERIMENTAL. Maximum four fixed MathSpecs per run. Not production-ready.**

This is a self-contained source package for the public demo: native Vulkan runner, fresh device-capability query, canonical oracles, shader generation, the recovered DIRECT and LDS/TILED kernel families, full warmup/final-output checks, compact diagnostic profiles and cleanup. No private development state, downloaded winner profile or canonical-directory symlink is required.

The demo does **not** include the state-bound Census / Hardware Intelligence / AI Fusion search campaign, unrestricted MinerNode, RT execution or network services. A fixed two-family evaluation must not be described as AI-driven optimization. The broader development system remains separate.

## Build and run on Linux

Requirements: Python 3.10–3.12, NumPy from `requirements.txt`, a C++17 compiler, Vulkan development headers/loader, glslangValidator, spirv-val, and a working Vulkan 1.1 compute driver with timestamps. Ubuntu/Debian build packages:

```bash
sudo apt-get install g++ libvulkan-dev glslang-tools spirv-tools
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
bash run_gpu_demo.sh --build-only
bash run_gpu_demo.sh
```

The default run stops after FFT256, Convolution, XCORR and signed-integer FIR. Each uses DIRECT and TILED on the same deterministic synthetic input and the unchanged canonical contract. All four require COLD ZERO full-output equality here. No historical observational Gaia input or historical speed record is imported.

`--tasks 1`, `--tasks 2` or `--tasks 3` shortens the fixed prefix; `--tasks 4` is the maximum. `--gpu 0` selects the enumerated Vulkan device; another nonnegative index selects another device. `--profile path.json` changes the compact report destination. There is no `--all`, arbitrary workload list, unrestricted search or limit override.

The Python launcher, generator/shader admission and native packet boundary enforce the four-task allowlist. Each MathSpec is admitted once per demo run. Source-level limits are not tamper-proof; modification and circumvention are prohibited by [LICENSE](../LICENSE).

## Reading the result

The console prints **correctness**, quick natural work units/s and available PPT diagnostics. The profile includes typed algorithmic operation counts, GPU timestamps, wall time, GPU/wall ratio, submissions, dispatches, inter-batch gaps, clock coverage and SCLK/PPT when matched through the driver's Vulkan PCI identity. Missing telemetry/resource information remains unavailable. Power is diagnostic only.

The measured interval repeatedly executes resident input. The full warmup and final output are compared; this is not per-dispatch verification of unique research jobs. These short results are always **QUICK_DIAGNOSTIC_ONLY**. They never authorize sustained-performance publication or production promotion. A correctness failure stops the demo and receives no throughput. The conservative end-to-end metric counts one validated job over preparation, compilation, warmup, repeated execution and validation.

Software Vulkan is rejected by default. `--allow-software` permits an explicitly labelled correctness run for CI; its timings are not physical GPU performance. Capability checks are runtime-based and contain no hardcoded BC-250 CU count. Other vendors are not marked hardware-verified by successful compilation.

## Resource lifetime

Builds, shader binaries, inputs, outputs, compiler binding hashes and telemetry samples are transient. Each trial is removed after validation; the temporary build directory is removed on completion, ordinary failure, Ctrl+C or SIGTERM. The demo has a five-minute outer deadline and bounded child-process deadlines. Only one compact profile is saved (the default file is overwritten on subsequent runs).

The per-user lock prevents two copies of this public demo from running concurrently. It cannot coordinate unrelated GPU applications. Force-kill, host crash or power loss can leave an `astro-demo-*` temporary directory; it contains no permanent research results and can be removed after confirming no demo is running. No automatic sweep of unrelated directories occurs.

## CI and review scope

CI runs canonical CPU tests, limit/rejection/cleanup tests, the actual native build, all eight shader compilations and a four-task software Vulkan correctness run. The workflow uses hosted runners, read-only repository permission and no secrets. It does not commission physical hardware, prove cross-vendor throughput or promote a production winner. See [publication validation](PUBLICATION.md) for actually completed checks and independent agent review scope.
