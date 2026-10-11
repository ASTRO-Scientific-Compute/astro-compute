# Engineering → Realtime / Game

**ENGINEERING is a first-class science branch.** Its current reference primitives include sparse matrix-vector operations and numerical geometry. Simulation, dense/sparse workflows and automatic realtime composition are broader planned directions.

## Existing separate prototype — EXPERIMENTAL

A local Linux game-optimizer prototype has GPU/API/process observation, per-game profiles, CLI/GUI entry points, frame-time statistics and controlled launch-setting experiments. It can reason about p99 frame time, 1% low and stutter where actual measurements are supplied. Restricted candidates include Mesa cache/threading choices, child-process scheduling and an opt-in queue setting. Regressions can cause rollback on the next launch; already-running launch flags are not magically rewritten.

This is not automatic engine binary modification, shader rewriting, per-pass counter access or a verified game-speedup result. Synthetic examples are not measured wins. The separate prototype and its personal game settings/telemetry are not included in this public source export.

## ASTRO integration — PLANNED

- **ANALYZE:** observe frame pacing, API paths, compute/physics/RT workloads and bottlenecks.
- **RECOMMEND:** propose legal runtime changes with evidence and explicit expected effects.
- **AUTO-APPLY:** apply only validated, reversible changes within an agreed scope, with a correctness/visual-quality gate and rollback.

Future frame-graph analysis, shader analysis, Vulkan/DXVK/VKD3D path selection, engine-level workload rewriting and automatic physics/RT scheduling need their own implementation and validation. Scientific throughput and realtime latency are different objectives; a faster average that worsens stutter is not automatically a better realtime profile.
