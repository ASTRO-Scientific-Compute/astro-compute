# ASTRO miner — independent development snapshot

[Download miner + benchmark source](astro-miner-20261108.zip) · [Measured results and reference accuracy](ASTRO_MEASUREMENTS_20261108.md) · [Detailed development roadmap](ASTRO_DEVELOPMENT_ROADMAP_20261108.md)

2026-11-08. General graph execution, CUDA/Vulkan backends, persistent sessions,
independent concurrent graph lanes, bounded buffers, asynchronous host checking,
QGC1 lossless output transport and generic optimization components.

This package contains the miner and a small synthetic benchmark foundation.
It contains **no research datasets, downloaded mathematics packages, historical
output arrays, device profiles, campaign ledgers or hash inventory files**.
The benchmark generates its own input definition in memory.

The `engine/` and `autotune/` implementation files are copied unchanged from the
measured development engine. `astro.py` and `src/build.py` are packaging adapters:
NGC/corpus entry points were removed and a small INT32 benchmark was added.
`src/admission.py` preserves the shared lock and existing ownership checks.
The original development directory was not changed.

## Status and permission

Experimental development publication. The existing repository `LICENSE` applies;
this publication does not expand the bounded demo evaluation permission. The
commands below document use by the owner or another separately authorized user.
No production network, researcher submission service or automatic GPU-wide
optimization coverage is claimed.

The core has prior physical CUDA/Vulkan measurements. **This newly extracted
package and its new synthetic benchmark have not been built or GPU-tested as a
separate distribution.** The published historical science results are not scores
for this benchmark. No new hardware trials were launched to prepare the upload.

## Build

Linux, Python 3.10+, C++17, Vulkan headers/loader, OpenSSL development libraries,
glslang and SPIR-V Tools are required. CUDA additionally needs the NVIDIA driver,
CUDA toolkit and linker-visible `libcuda` development stub/library.

```bash
sudo apt-get install python3 g++ libvulkan-dev libssl-dev glslang-tools spirv-tools
cd astro-miner
# Optional CUDA SDK location; otherwise nvcc is discovered on PATH:
export INDEPENDENT_CUDA_SDK=/usr/local/cuda
python3 -B astro.py build
python3 -B astro.py devices
```

Omit the SDK export for a Vulkan-only build without CUDA. A configured missing
CUDA SDK fails explicitly. Default CUDA PTX target: `compute_75`; another
supported toolkit target can be supplied through `ASTRO_CUDA_ARCH`.

## Bounded benchmark

Replace the device address with one returned by `devices`. Select `vulkan` for
an AMD card. Each command makes one persistent session, runs three independently
seeded INT32 graphs per job, checks every output byte against a CPU oracle and
then exits. Defaults: four jobs, 65,536 values per graph, 32 integer rounds.

```bash
python3 -B bench.py --device 0000:01:00.0 --backend cuda --mode serial
python3 -B bench.py --device 0000:01:00.0 --backend cuda --mode concurrent
```

Use identical `--jobs`, `--elements` and `--rounds` for comparisons. One/three
lanes process the same three synthetic cases. More jobs are repeats, not new
research cases. This initial benchmark uses raw output; QGC1 remains available
through the graph transport API with an explicit compressed-output checker.

One invocation has a 60-second worker timeout, a 90-second worker reservation,
90/270 seconds of summed GPU intervals, 256 MiB backend buffer ceiling and at most
two 16 MiB output snapshots. No hidden warmup or retry is performed. The shared
admission lock and cumulative local `COST.json` limit remain active.

`BENCH_RESULT.json` reports full E2E, process-tree CPU time, CPU oracle preparation,
summed GPU intervals, buffer peak and correct graph evaluations/s. Per-job native
events and checker results remain local. GPU intervals can overlap; their sum
is not wall time. Serial/concurrent labels alone do not prove physical overlap
or a speedup. Writes are buffered, without an fsync completion guarantee.

## Generic graphs and optimizer integration

```bash
python3 -B astro.py run --device 0000:01:00.0 --backend cuda --graph /path/to/graph.json
```

This generic command reports `EXECUTED_NOT_DOMAIN_VALIDATED`: callers must supply
their own scientific validator. `engine/resident.py` provides the checked,
persistent-session API used by the benchmark. `autotune/` supplies generic search,
independent budgets, local/network cost objectives and packet-cache machinery;
scientific adapters and learned profiles are deliberately outside this package.
The optimizer is a library, not an automatic all-domain benchmark launcher.

Integrity checks remain in the program. Building/running creates local identity
and audit metadata; no precomputed hash files are distributed in this archive.
The admission module also checks historical ownership records on the original
host when that mounted path exists. It does not import the old ASTRO executor.
