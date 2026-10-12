# Public package · CPU references and bounded Vulkan GPU demo

**Release scope: canonical CPU reference export plus bounded four-task Vulkan demo.**

## v0.1.1 Update / Bugfix

[Resource/runtime fixes and exact validation scope](UPDATE_BUGFIX_V0_1_1.md): 100 Python tests, native/shader build and 48 BC-250 kernel trials passed. This update has a separate independent agent code review; external human review remains pending. The [new diagnostic comparison](BC250_UPDATE_V0_1_1.md) does not replace the historical reference.

## Current published scope

The repository includes the CPU reference corpus, a maximum-four-MathSpec Vulkan demo, native C++/Vulkan build sources, DIRECT/TILED demo kernels, full-output correctness validation and CI. The workflow runs Python 3.10/3.12 software checks and native/shader builds; the Python 3.12 job also executes Mesa software Vulkan correctness and checks cleanup. Software Vulkan timing is never physical GPU evidence.

The first demo publication passed hosted CI on commit `ab3d236153c25adf14cbac067bdba818561f3fb2`: [completed run](https://github.com/ASTRO-Scientific-Compute/astro-compute/actions/runs/38161000798). The [workflow](https://github.com/ASTRO-Scientific-Compute/astro-compute/actions/workflows/demo-ci.yml) shows the status of subsequent commits. Agent review is complete for that bounded scope; external human review remains PENDING.

## Historical publication context

The first CPU-only preview is preserved below as historical publication context. Current GPU packaging, checks and limitations are in [GPU_DEMO.md](GPU_DEMO.md) and [DEMO_RELEASE.md](DEMO_RELEASE.md). The historical 85-test count below predates the expanded demo tests.

This package exports 96 unchanged canonical Python source modules, 81 contract metadata records and 81 small analytic vectors from the development tree. The full 94-entry registry is represented by sanitized metadata; 13 historical/runtime-only entries are not presented as extra executable CPU references. The 81 canonical references include 66 SPACE primitives.

## Initial CPU-only publication checks — 2026-10-11

Environment: Python 3.12.3, NumPy 1.26.4, Linux. From this public tree:

```bash
python -m unittest discover -s tests -v
python reference_demo.py
```

- **85 tests PASS:** 81 full analytic-output comparisons and metadata/vector checks, registry coverage, host binary32 contract probe, malformed-input rejection and corrupted/truncated-output rejection.
- CSR example: exact row outputs **(3, 0, 15)**.
- All 96 exported canonical Python modules match their development-source bytes. Their mathematical algorithms were not modified for publication.
- Public tree scanned for local absolute paths, common credential patterns, private keys and email addresses; no findings in the staged source/documents.
- No GPU execution, native build, sustained benchmark or independent code review was performed for the initial CPU-only publication. The later bounded demo checks are listed separately above.

## Included

The canonical catalog, integer/Fraction/binary32 CPU oracles, deterministic arithmetic tables, analytic examples, contract metadata, original historical mathematical contracts, public software checks, full inventory, architecture, status and roadmap. Definitions of source/contract digests in mathematical metadata are not retained benchmark hash inventories.

## Outside the initial CPU-only preview

State-bound GPU runtime/search installation, private winner profiles and seed dependencies, raw benchmark evidence, trial directories, telemetry dumps, local credentials, researcher data, game profiles and compiled artifacts. The complete unrestricted development runtime/search distribution remains outside the bounded portable demo. A repository clone must not be represented as an installed full MinerNode.

## Contract-document context

The uppercase mathematical contract documents preserve upstream mathematical wording and historical implementation context. References to native runners, workflow adapters, validators or past hardware checks describe the wider development project, not additional included executables or newly repeated public verification. The authored architecture/status documentation is the authority for the scope of this preview.

No benchmark speed numbers are republished as a self-contained reproducible result. Current historical profiles are useful internal references, but no fake leaderboard, live network count, native low-bit capability or production-readiness claim is supplied.

The owner has selected a source-available demonstration license; see [LICENSE](../LICENSE) and [LICENSING.md](../LICENSING.md). Evaluation through the included demo is permitted; other use requires written permission.
