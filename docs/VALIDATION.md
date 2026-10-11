# Correctness and trust

**Policy: correctness before performance.**

## Local mathematical contract

The public CPU references preserve the canonical operation graph and strict input/output contracts. Analytic cases check entire serialized outputs. Exact integer and specified deterministic binary32 contracts require **zero differing bits**. A bounded-FP historical contract must retain its own bounds and cannot silently become an exact-contract comparator or vice versa.

A GPU candidate must execute the actual selected kernel and compare its complete output against the canonical oracle. Edge inputs, held-out inputs, partition/remainder cases and every runtime variation need coverage. Matching two executions of the same implementation is not an independent oracle.

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
