# External demo reproductions

**No external reproduction results are recorded here yet. This is a submission template, not a leaderboard.** External human review and independent physical-hardware reproduction remain PENDING until a verifiable report is accepted.

Run the unmodified [bounded GPU demo](GPU_DEMO.md) from a named ASTRO release or exact commit. It stops after at most four fixed MathSpecs. Record each DIRECT/TILED trial separately, using the same task input and contract. A result applies only to that documented configuration.

## Record template

Copy this block into a technical report or an issue. Replace every placeholder; use UNAVAILABLE for missing observations. Do not publish a rate as accepted performance when correctness is FAIL or unverified.

```yaml
contributor: <public handle or attribution>
astro_release: <tag, or UNAVAILABLE>
astro_commit: <exact source commit>
run_date: <YYYY-MM-DD>
os: <distribution/version/architecture>
python_numpy: <versions>
gpu: <reported device name>
vendor: <reported vendor>
driver: <driver/version>
vulkan_implementation: <for example RADV, proprietary driver, or llvmpipe>
device_kind: <PHYSICAL_GPU or SOFTWARE_VULKAN>
mathspec: <exact allowed MathSpec ID>
execution_family: <DIRECT or TILED>
input: <demo seed/scale; default seed 271828, scale 1>
correctness: <PASS, FAIL, or UNVERIFIED>
validation_scope: <full warmup/final output comparison>
differing_bits: <observed integer or UNAVAILABLE>
measurement_class: QUICK_DIAGNOSTIC_ONLY
natural_unit: <unit reported by this MathSpec>
quick_natural_work_units_per_s: <observed rate or UNAVAILABLE>
measurement_wall_time: <value and unit, or UNAVAILABLE>
measured_gpu_time: <value and unit, or UNAVAILABLE>
gpu_wall_ratio: <observed value or UNAVAILABLE>
hardware_telemetry_availability: <available fields or UNAVAILABLE>
notes: <limitations, failures, setup and reproducible steps>
```

The source commit identifies the release; it is not a benchmark hash inventory. Raw inputs/outputs, shader hashes and telemetry dumps are not requested. A sanitized compact profile may accompany the report if it contains no private paths, researcher data, secrets or unrelated machine information.

## Interpretation and review

- **SOFTWARE_VULKAN:** execution/correctness evidence on a software implementation. Its timings are never physical GPU measurements.
- **PHYSICAL_GPU + QUICK_DIAGNOSTIC_ONLY:** a short device observation, not sustained or certified performance. Describe telemetry that is actually available; missing sensors are not estimated.
- **Correctness FAIL:** retain the failure description, with the accepted rate UNAVAILABLE. Do not rank it against passing runs.
- **Independent reproduction:** requires an identifiable external report tied to a release/commit and reproducible setup. Local maintainer runs and independent agent review do not establish external hardware reproduction.
- **Sustained/certified evidence:** requires a separate appropriate protocol and review. It cannot be inferred from this demo or obtained by changing the label.
- **Historical internal results:** remain reference context, not automatically comparable public scores. No internal winner/profile is imported here.

Technical evaluation and attributed publication of unmodified-demo results are permitted under [LICENSE](../LICENSE). This template does not grant permission to modify the code, bypass the four-MathSpec limit or operate a service.
