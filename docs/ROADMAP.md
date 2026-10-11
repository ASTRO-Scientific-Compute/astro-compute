# Roadmap · gated progress

Dates and network capacities are intentionally not promised. Each milestone has an observable exit criterion.

| Milestone | State | Exit criterion |
|---|---|---|
| Public mathematical reference foundation | IMPLEMENTED | All exported analytic contracts reproducible by public CPU checks |
| Portable GPU source release | IN DEVELOPMENT | Clean executor/build dependency closure; no local state/secret dependencies; independent review |
| Reliable local optimization | EXPERIMENTAL | Resolve intermittent image-moments failure; validate every selected runtime/configuration |
| Capability and resource evidence | IN DEVELOPMENT | Native execution tests per backend/vendor; trustworthy allocation/occupancy data or explicit UNAVAILABLE |
| Runtime Fusion expansion | IN DEVELOPMENT | Per-adapter graph/batch coverage and sustained confirmation; copy overlap proved separately |
| Universal math composition | PLANNED | Generated DAG preserves contracts, partition semantics and independent validation |
| Host Runtime Generator | PLANNED | Discover CPU/SMT/cache/SIMD/RAM/storage/network; validate thread count, affinity, task grain, cache blocking, memory placement, queues, work stealing, async I/O and validation/serialization choices |
| MainNode result protocol | IN DEVELOPMENT | Authenticated verified ACK, idempotent retry, complete result reconstruction and safe deletion |
| Independent validation network | PLANNED | Separate ownership/network domains, challenge protocol and adversarial tests on physical nodes |
| Scientist integration | PLANNED | Research task decomposition through verified end-to-end output; scientific limitations explicit |
| Heterogeneous deployment | PLANNED | Commission each CPU/GPU/APU/RT/AI/mobile backend independently |
| Engineering/realtime integration | PLANNED | Measured frame-time/latency benefits with visual correctness and rollback |
| Marketplace/accounting | PLANNED | Defined governance, job/payment contracts and validated service delivery before economic promises |

A possible ledger/accounting layer may track identity, receipts, provenance and payments. It is not the compute engine. Researcher jobs, worker compensation, validator rewards, reliability incentives, internal accounting/token concepts and fiat-denominated contracts remain design subjects. This repository announces no operational token, sale, reward rate or marketplace.

A future operational dashboard must show actual live data (approximately five seconds or fresher) or OFFLINE/UNAVAILABLE. Mock data must never appear as live network activity.
