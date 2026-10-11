# Status · public preview, 2026-10-11

**Overall: EXPERIMENTAL / IN DEVELOPMENT. Not production-ready.**

The public preview and the broader development tree are different scopes. This table is a source audit, not a certification of every runtime path.

| Label | Meaning |
|---|---|
| IMPLEMENTED | Concrete code exists in the stated scope; not proof of hardware behavior |
| EXPERIMENTAL | Research implementation with open correctness, portability or review gates |
| VERIFIED | A named check passed; only its exact scope is covered |
| IN DEVELOPMENT | Work is incomplete or integration remains open |
| PLANNED | Design intent; no working integration claimed |
| UNAVAILABLE | Required path, data or trustworthy evidence is absent |

`CODE_PRESENT != WORKING != MEASURED != TRUSTED`

| Component | Public preview | Development-tree assessment |
|---|---|---|
| 81 canonical CPU references / 66 SPACE | IMPLEMENTED; analytic tests in this repo | Existing canonical corpus, not all 94 registry entries |
| Full 94-entry inventory | IMPLEMENTED, sanitized metadata | Includes 13 historical/runtime-only entries |
| Layered Fast Search V2 | Documentation; GPU executor unavailable here | IMPLEMENTED / EXPERIMENTAL; bounded adapter support |
| Census and Search-Path Registry | Design and evidence boundaries documented | IMPLEMENTED catalog; EXPERIMENTAL candidate integration |
| Runtime Fusion | Documentation | EXPERIMENTAL; native independent-job subset is narrower than corpus |
| RT scientific compute | Canonical CPU references for commissioning | EXPERIMENTAL, bounded ray-query paths |
| Native VGPR/SGPR/scratch/spill/occupancy | UNAVAILABLE | Reliable final-allocation receipts unavailable in audited path |
| Independent ILP Fast V2 axis | UNAVAILABLE | Not wired as an independent legal axis in audited adapter set |
| Transfer/compute overlap | UNAVAILABLE | Copy execution alone did not establish overlap |
| Distributed execution | PLANNED full deployment | Loopback transport tests do not prove independent physical nodes |
| MainNode and Scientist end-to-end | PLANNED / IN DEVELOPMENT | No complete production researcher-to-result integration |
| AI/tensor backend; mobile execution | PLANNED | Capability records are not backend execution proof |
| Host Runtime Generator | PLANNED | No general CPU/host optimizer claimed |
| Realtime/game integration | PLANNED | Separate local optimizer prototype is EXPERIMENTAL |
| Benchmark profile-only cleanup | Policy documented | IMPLEMENTED; abnormal termination may leave current transient files |
| Public standalone GPU distribution | IN DEVELOPMENT | Runtime depends on state-bound inputs that need a separate clean export |
| Independent release review | UNAVAILABLE as completed evidence | PENDING |

## Known correctness issue

An intermittent image-moments runtime result mismatch remains open in development evidence. A later successful replay is not a fix. A CPU oracle passing the public analytic case does not certify that GPU runtime. Any failing configuration is excluded from accepted performance results.

## Evidence boundary

The source audit consulted v1.17.52 status, Runtime Fusion, Layered Fast V2, capability-census, RT and retention reports, plus the separate game-optimizer source. Those local reports and raw state are not uploaded. Historical local measurements are not relabeled VERIFIED public benchmarks. Public software-check results and their reproduction command are recorded in [PUBLICATION.md](PUBLICATION.md).
