# Correctness and trust

**Policy: correctness before performance.**

## Local mathematical contract

The public CPU references preserve the canonical operation graph and strict input/output contracts. Analytic cases check entire serialized outputs. Exact integer and specified deterministic binary32 contracts require **zero differing bits**. A bounded-FP historical contract must retain its own bounds and cannot silently become an exact-contract comparator or vice versa.

A GPU candidate must execute the actual selected kernel and compare its complete output against the canonical oracle. Edge inputs, held-out inputs, partition/remainder cases and every runtime variation need coverage. Matching two executions of the same implementation is not an independent oracle.

## Two separate validation gates

### Implementation agreement

Compare the **complete numerical output** of the executed GPU kernel with the independent CPU implementation. For an exact/COLD ZERO MathSpec, acceptance requires **0 differing bits**, including status and boundary fields. Bounded-FP MathSpecs keep their stated comparator and tolerance. A checksum match or two executions of the same implementation cannot substitute for the independent reference check.

### Scientific validity

Where required by the MathSpec, separately check the numerical result against an independently derived scientific reference, analytic solution, higher-precision calculation or the original scientific error budget. The numerical operation graph and approximation budget must both be appropriate for the intended task. Extra internal precision may be necessary even when the serialized output remains binary32.

**Two implementations agreeing bit-for-bit does not prove that both implement the intended science correctly.** A scientific validity failure blocks acceptance; it is not repaired by a fast kernel or byte equality. These gates do not imply universal accuracy outside the stated inputs, model and contract.

### Historical example: Hann FFT and whitening

The [preserved zero-bit amendment](SPACE_ZERO_BIT_AMENDMENTS.md#two-separate-checks) documents a development case: the original scalar-binary32 Hann FFT matched CPU/GPU bytes on test vectors, but the CPU operation graph failed the historical whitening error budget on the full real H1 stream. It was replaced with a double-single internal window/FFT graph before that amendment was released. The external output contract still uses explicit RN32 steps.

This is a **historical internal validation example**, not a newly reproduced result from the four-task public GPU demo. Welch/whitening are outside that demo's allowlist, and the observational H1 stream and historical raw evidence are not bundled. The public analytic cases have their own finite test scope.

## Four independent questions

1. **Functional:** did the selected configuration and intended path actually run?
2. **Correctness:** did the complete output meet its unchanged MathSpec contract?
3. **Performance validity:** did wall/GPU time, queue activity and telemetry establish a valid interval?
4. **Physical/resource evidence:** did the intended hardware effect actually change, where that is claimed?

Evidence for one question does not answer the others. Unknown data remain UNAVAILABLE, UNSUPPORTED or UNVERIFIED. Power and normal temperature are diagnostics, not optimization objectives.

## Independent distributed validation — PLANNED

The design includes multiple validators, deterministic receipts, cross-validation, provenance and unpredictable challenges. Identity/ownership/network-domain separation must be explicit; two processes or two devices controlled by the same party are not automatically independent validators. Result merging must check completeness and partition semantics before returning researcher output.

Digest bindings can protect a live result/receipt exchange. They do not justify permanent benchmark hash inventories. Research results must remain available until a genuine verified MainNode ACK authorizes lifecycle progression. The current simulator is not that service.

## Public checks and limits

Run `python -m unittest discover -s tests -v`. The suite covers all 81 analytic reference cases, unchanged contract metadata, host binary32 probes, a rejected malformed job and a rejected corrupted result. The software suite does not execute a GPU. The separate bounded demo and CI software-Vulkan run check executed kernels. Neither establishes sustained throughput nor resolves the excluded development image-moments GPU defect. See [publication scope](PUBLICATION.md) for independent agent review and completed checks.

## Review provenance

- **Automated checks:** canonical CPU/selftests, native/shader build and software Vulkan correctness in CI.
- **Independent agent review:** completed for the bounded demo scope described in [DEMO_RELEASE.md](DEMO_RELEASE.md).
- **External human review:** **PENDING**. Agent review, local hardware tests and hosted CI are not external human certification.
- **Independent external hardware reproduction:** **PENDING**; use the [reproduction template](EXTERNAL_REPRODUCTIONS.md).
