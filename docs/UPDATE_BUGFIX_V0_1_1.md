# Update / Bugfix — ASTRO GPU Demo v0.1.1

2026-10-12 · **Source-available demonstration software. Free to evaluate using the included demo. All other use requires explicit permission from the copyright holder.**

Maximum **4 fixed MathSpecs per run**. EXPERIMENTAL; not production-ready. The license, canonical mathematical contracts, DIRECT/TILED shader families and previous evidence files are unchanged.

## Fixes shipped in this demo

| Problem / previous behavior | Fix | Evidence and limits |
|---|---|---|
| Native measurement appended one timing record per submitted batch, then serialized the entire trace into Python. Short kernels could produce many records and copies. | Constant-size online totals for dispatches, submissions, gaps and host costs; no growing native batch vector or raw trace JSON. | Native build and 48 physical kernel trials passed; aggregate counter identities checked. O(1) timing-storage design, not a measured whole-process RAM reduction percentage. |
| Canonical binary32 memoization and idle allocator pages could remain between completed MathSpecs. | After each task, clear only the known pure oracle caches, collect unreachable Python objects and request local heap reclamation where available. | RSS/swap before/after and trim availability recorded. Observed small-fixture RSS changes: 53,248–348,160 bytes/task. No global cache/swap purge, GPU-memory claim or zero-RSS promise. |
| Compiler logs and artifact manifests, including temporary binding hashes, were written then deleted. | No compiler/artifact manifest writes. Source/SPIR-V bindings stay in memory, checked before and after execution using streamed file reads. | Regression verifies that only shader source and SPIR-V exist during compilation; tampered output still rejected. Input/output scratch remains transient until correctness validation. Physical SSD-write savings not measured. |
| Compact profile was normally saved only at campaign exit. | Atomically checkpoint the same compact profile after each task and its cleanup; retain final STOPPED/COMPLETE status. | Checkpoint ordering regression passes. Normal failure, Ctrl+C and SIGTERM cleanup retained; SIGKILL/host crash can still leave the active temporary workspace. Atomic replace is not a power-loss durability guarantee. |
| Command reuse existed in the native runner but was not exposed by the demo. | Optional `--runtime reuse` for FFT256, Convolution and XCORR, with actual native receipt checks; FIR stays baseline. | Default remains `baseline`. Reuse means reusing recorded commands, not merging submissions, changing kernels or enabling AI/Fusion search. All eligible physical trials executed reuse and passed full output checks. |

Only compact profile data survives normal completion. The default output path is overwritten on the next run; custom profile paths remain under the user's control. No hash inventory, raw result archive, telemetry stream or trial directory is published. Live scientific job results are a separate lifecycle and must not be deleted before a verified MainNode acknowledgement.

## Wider miner fixes — documented, not an unrestricted demo export

The current development miner additionally has:

- MathSpec-boundary job-pool/oracle/worker-cache cleanup and process RSS receipts, reducing unnecessary live references during long campaigns.
- Profile-only benchmark retention and removal of bulk hash-inventory/finalization passes; benchmark evidence is validated online before transient cleanup.
- A separate **CPU_HOST** stage between RUNTIME and WAVE_SUBGROUP: one axis per trial for reference layout, checking threads, chunk partition, async validation and legal affinity. Every output is still fully checked; shared immutable references do not share a PASS verdict.
- Explicit exploration/skip statuses, worker deadlines and sampler-ready handling, plus bounded recovery for correctness-PASS but underfed points. Diagnostic recovery does not admit invalid performance as a winner.

These search/queue/worker structures are not all present in the fixed demo and are not claimed as newly shipped public Fusion search. Targeted development CHEM checks remain performance-INVALID; no CHEM speedup or full Universal Profiler readiness is claimed. The regular miner was not modified or given the four-task cap by this release work.

## Completed validation

- **100/100 Python tests PASS**, including seven new resource/runtime regressions; independently reproduced by a separate review agent.
- Native C++/Vulkan build and all eight demo shader compilations / SPIR-V checks PASS.
- Native admission still rejects invalid local size and out-of-demo MathSpecs before Vulkan initialization.
- BC-250 / RADV GFX1013: six complete four-task runs, **48/48 kernel trials PASS / COLD ZERO**, no temporary demo workspace left. [All observations and limits](BC250_UPDATE_V0_1_1.md), [compact profile](BC250_UPDATE_V0_1_1.json).
- Canonical CPU math, contracts, input fixtures, shader mathematics, four-task limit and license checked unchanged against the prior public commit.
- CI now covers both baseline and reuse software-Vulkan modes, aggregate identities and cleanup. Actual hosted status is visible in the [workflow](https://github.com/ASTRO-Scientific-Compute/astro-compute/actions/workflows/demo-ci.yml); configuration alone is not a successful CI claim.

Independent agent code review found no blocker in this bounded change; this is not external human certification. External human review, external GPU reproduction, cross-vendor physical commissioning and sustained performance gates remain open. QUICK observations never promote a production winner.

## Magyar összefoglaló

Az SSD/RAM-éhség javítása itt a fölösleges adattárolás megszüntetését és az adatok élettartamának rövidítését jelenti: nincs növekvő natív mérési lista, nincs kiírt fordítási/hash-manifeszt, és minden matek után ürülnek a saját oracle-cache-ek és a felszabadítható processzmemória. Az ellenőrzés teljes marad; csak a kompakt profil marad meg.

A BC-250-en mind a 48 kernelpróba bitpontos PASS lett. A TILED konvolúció rövid reuse összehasonlításában +6,33% mediáneltérés látszott, de a változatlan FIR kontroll is ingadozott. Ezért nincs elfogadott általános gyorsulási vagy PERFORMANCE_IMPROVED állítás; a teljes kedvező és kedvezőtlen táblázat publikus. A demó továbbra is maximum négy matek után leáll. A rendes miner nincs korlátozva.
