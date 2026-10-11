# Contributing

ASTRO is experimental. Start with a focused issue describing the mathematical contract or execution boundary, the reproduction and the expected result. Use synthetic minimal inputs that contain no private research or personal data.

Do not modify or submit code without prior written permission from the project owner and agreement on contribution terms. You may report problems and publish attributed technical evaluations of the unmodified demo. See [LICENSE](LICENSE) and [LICENSING.md](LICENSING.md); this is source-available demonstration software, not open source.

Useful work includes independent oracle reviews, contract edge cases, clear capability gaps, portable public packaging and reproducible correctness failures. Keep changes scoped. Do not alter MathSpec mathematics as a performance shortcut. Exact contracts retain zero differing bits; bounded-FP contracts retain their explicit limits.

For software checks run `python -m unittest discover -s tests -v`. Report software checks, skipped dependencies and actual hardware measurements separately. Future GPU changes need executed-path evidence, full correctness, telemetry/performance validity and independent review before promotion. Power or occupancy is not a substitute for useful work/s.

Do not attach raw benchmark trees, hash inventories, credentials, private configs or local machine paths. A compact sanitized profile and deterministic input-generation recipe are preferable. Security issues follow [SECURITY.md](SECURITY.md), not public exploit reports.
