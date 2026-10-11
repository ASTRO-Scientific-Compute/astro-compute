# Public source preview · v1.17.52 reference foundation

**Release scope: IMPLEMENTED CPU reference export; VERIFIED software checks only.**

This package exports 96 unchanged canonical Python source modules, 81 contract metadata records and 81 small analytic vectors from the development tree. The full 94-entry registry is represented by sanitized metadata; 13 historical/runtime-only entries are not presented as extra executable CPU references. The 81 canonical references include 66 SPACE primitives.

## Reproduced software checks — 2026-10-11

Environment: Python 3.12.3, NumPy 1.26.4, Linux. From this public tree:

```bash
python -m unittest discover -s tests -v
python reference_demo.py
```

- **85 tests PASS:** 81 full analytic-output comparisons and metadata/vector checks, registry coverage, host binary32 contract probe, malformed-input rejection and corrupted/truncated-output rejection.
- CSR example: exact row outputs **(3, 0, 15)**.
- All 96 exported canonical Python modules match their development-source bytes. Their mathematical algorithms were not modified for publication.
- Public tree scanned for local absolute paths, common credential patterns, private keys and email addresses; no findings in the staged source/documents.
- No GPU execution, native build, sustained benchmark or independent code review was performed for this publication. These checks do not close those gates.

## Included

The canonical catalog, integer/Fraction/binary32 CPU oracles, deterministic arithmetic tables, analytic examples, contract metadata, original historical mathematical contracts, public software checks, full inventory, architecture, status and roadmap. Definitions of source/contract digests in mathematical metadata are not retained benchmark hash inventories.

## Deliberately outside this preview

State-bound GPU runtime/search installation, private winner profiles and seed dependencies, raw benchmark evidence, trial directories, telemetry dumps, local credentials, researcher data, game profiles and compiled artifacts. The complete GPU distribution needs an independently reviewed portable export with explicit build/runtime dependencies. A repository clone must not be represented as an installed full MinerNode.

## Contract-document context

The uppercase mathematical contract documents preserve upstream mathematical wording and historical implementation context. References to native runners, workflow adapters, validators or past hardware checks describe the wider development project, not additional included executables or newly repeated public verification. The authored architecture/status documentation is the authority for the scope of this preview.

No benchmark speed numbers are republished as a self-contained reproducible result. Current historical profiles are useful internal references, but no fake leaderboard, live network count, native low-bit capability or production-readiness claim is supplied.

Licensing remains pending an explicit project-owner decision; see [LICENSING.md](../LICENSING.md).
