# Data lifecycle and storage

## Benchmarks — IMPLEMENTED development policy

**run → validate → profile → cleanup**

A benchmark retains compact profile data. Raw input/output dumps, per-trial hashes and hash inventories, telemetry dumps, trial workspaces and temporary compile artifacts are transient. Validation happens before cleanup; retaining less does not relax correctness. Interrupted or killed processes can leave the currently active workspace, so bounded cleanup/recovery remains necessary. The policy is not permission to indiscriminately delete researcher data.

## Research jobs — verified ACK integration IN DEVELOPMENT

**compute → validate → upload → verified MainNode ACK → grace → local delete**

The future ACK must bind the exact job/result, completeness and receipt identity and be authenticated under the actual MainNode protocol. A timer, local queue state or simulator marking a row UPLOADED is not proof of receipt. Until the real protocol exists, no simulated upload may authorize destruction of the only researcher result. Retries must be idempotent and partial/corrupt transfers must remain recoverable.

## Capacity planning — design guidance

Recommend at least **512 GB SSD**, with **1 TB or more** for larger workloads. Actual capacity depends on researcher datasets, in-flight jobs, caches and runtime artifacts. These are planning recommendations, not experimentally established hardware minimums. Benchmark debris must not be the reason storage fills.

No credentials, private researcher data, personal telemetry, local absolute paths or machine-specific configurations belong in this public repository.
