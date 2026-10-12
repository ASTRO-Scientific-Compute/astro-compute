# Data lifecycle and storage

## Benchmarks — IMPLEMENTED development policy

**run → validate → profile → cleanup**

A benchmark retains compact profile data. Raw input/output dumps, per-trial hashes and hash inventories, telemetry dumps, trial workspaces and temporary compile artifacts are transient. Validation happens before cleanup; retaining less does not relax correctness. Interrupted or killed processes can leave the currently active workspace, so bounded cleanup/recovery remains necessary. The policy is not permission to indiscriminately delete researcher data.

## Public demo update — v0.1.1

The bounded demo already removed trial directories in v0.1.0. v0.1.1 also avoids writing compiler/artifact hash manifests at all, keeps native timing aggregates at constant memory size, checkpoints only compact profiles and releases pure oracle caches/idle process heap between MathSpecs. File binding is still checked in memory before and after execution. Runtime RSS observations are diagnostics, not estimated RAM savings. Scratch input/output and shader binaries still exist while needed for compilation and full correctness validation; they are deleted afterwards.

The broader miner additionally clears its job pools and worker caches between completed MathSpecs. These search-specific structures are not shipped as an unrestricted miner inside the demo. Research-result retention remains governed separately below.

## Research jobs — verified ACK integration IN DEVELOPMENT

**compute → validate → upload → verified MainNode ACK → grace → local delete**

The future ACK must bind the exact job/result, completeness and receipt identity and be authenticated under the actual MainNode protocol. A timer, local queue state or simulator marking a row UPLOADED is not proof of receipt. Until the real protocol exists, no simulated upload may authorize destruction of the only researcher result. Retries must be idempotent and partial/corrupt transfers must remain recoverable.

## Capacity planning — design guidance

Recommend at least **512 GB SSD**, with **1 TB or more** for larger workloads. Actual capacity depends on researcher datasets, in-flight jobs, caches and runtime artifacts. These are planning recommendations, not experimentally established hardware minimums. Benchmark debris must not be the reason storage fills.

No credentials, private researcher data, personal telemetry, local absolute paths or machine-specific configurations belong in this public repository.
