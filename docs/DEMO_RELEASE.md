# GPU demo release · 2026-10-11

**EXPERIMENTAL / source-available evaluation only. Not production-ready.**

## Completed local validation

- 93 Python selftests PASS: all 81 analytic canonical cases plus registry/host/rejection checks and public demo admission, actual acceptance and cleanup regressions.
- Native C++17 Vulkan runner and capability-probe build PASS.
- All eight DIRECT/TILED shader compilations and SPIR-V validation PASS.
- AMD BC-250 (RADV GFX1013): four tasks, eight executed kernels, eight complete warmup/final-output comparisons PASS; automatic stop at four tasks.
- Mesa software Vulkan: the same four-task/eight-kernel run PASS. This is software correctness evidence, not physical GPU performance.
- No persistent trial source/SPIR-V/input/output/hash or telemetry dump is kept. Only compact diagnostic profiles remain outside the source package.

The physical run used Python 3.12.3 / NumPy 1.26.4 on Linux. Inputs are deterministic synthetic fixtures (seed 271828, scale 1). These checks cover this bounded configuration, not every edge input or hardware vendor. No historical speed comparison or sustained winner is claimed.

## Review

A separate review agent checked licensing against the owner's explicit policy, mathematical-source preservation, demo admission, actual output acceptance, cleanup and release boundaries. This is an independent **agent** review, not external human certification or legal counsel.

Initial findings corrected: tests now exercise the actual canonical comparator; the cleanup test isolates its GPU lock; `--all` is explicitly rejected rather than treated as an abbreviated option; generated profiles are excluded; native local-size zero and out-of-demo packet IDs are rejected before Vulkan initialization. The portable demo has no private Census/priors dependency and does not claim to run that search integration.

Final independent agent review: no remaining software blocker found within the bounded demo scope; 93/93 Python tests independently reproduced. Hosted CI must still complete on the published revision. Passing CI is a software gate, not production approval.
