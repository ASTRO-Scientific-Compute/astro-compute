# SPACE background meshes — v1.17.22

Contracts defined before CPU vectors and GPU implementation. All binary32 arithmetic uses the existing finite RN32 operation graph: separate nearest-even rounding, canonical positive zero, no FMA/reassociation. Entire output bytes, including statuses, counts and integer distances, require exact CPU/GPU equality. Non-finite input/intermediate values are rejected before submission.

## Opcode 61: inverse squared-distance interpolation

Inputs: unique integer source positions [M,2] and query positions [Q,2], coordinates in 0..32767 explicit coordinate ticks; M1..256, Q1..4096. Values[M] are finite binary32; valid[M] are uint0/1. neighbors K1..16; M*Q*K<=4194304. No implicit rounding from real coordinates. No unit conversion, smoothing constant or periodic distance.

For each query compute exact d2=(qx-sx)^2+(qy-sy)^2 for valid sources. Its maximum is 2147352578, fitting uint32. Select min(K,valid_count) nearest sources ordered by (exact d2, original source index). The CPU oracle uses integer distances and sorting; GPU keeps an ordered bounded insertion list. All-invalid input returns [status1,0,0,0]. An exact valid coordinate match returns [status0,canonical_value,1,0], even if K>1. Invalid coincident sources are ignored.

Otherwise traverse selected sources in increasing (d2,index) order. weight=RN32(1/RN32(d2)); numerator=ordered_sum(RN32(weight*value)); denominator=ordered_sum(weight); value=RN32(numerator/denominator). No sqrt or native reciprocal shortcut. Output [u32 status,f32 value,u32 contributors,u32 nearest_d2]. Negative values are valid. This is bounded Shepard inverse-distance weighting with power=2, no regularization; not the default behavior or exact bytes of any external package. It provides a local interpolant, not calibrated uncertainty or a guarantee of reconstructing large missing regions.

## Opcode 62: masked local median

Inputs: mesh[H,W] finite binary32 and valid[H,W] uint0/1, H,W1..64; odd square window1/3/5/7, minimum_valid1..window^2. Each output center gathers only valid in-bounds cells in its centered square. Boundaries truncate the window; no padding or reflection. The center itself need not be valid. No output value becomes an input to another center.

Sort gathered values numerically. If count<minimum_valid, output [status1,count,0]. Otherwise odd count selects the middle value, canonicalized. For even count a,b, median=RN32(RN32(a*0.5)+RN32(b*0.5)). Output [status0,count,median]. The half-before-add graph avoids overflow from a+b, but has explicitly different subnormal rounding from a single exact rational average. Comparison treats signed zeros as equal; output zero is positive. This conventional averaged-even median differs from SciPy ndimage.median_filter's upper-middle convention for even footprints. CPU sorting and GPU insertion sorting are independently implemented.

## Background adapter and pipeline

A CPU adapter tiles a finite image and explicit valid mask into complete, nonoverlapping boxes. H,W<=128, box dimensions1..32 with area<=512; image dimensions must divide exactly; mesh height/width2..16. No silent edge padding/cropping. It submits existing opcode46 mean-centered sigma-clipping jobs in tiles of at most128 boxes, preserving row-major global cell order. Explicit lower/upper sigmas, iteration count and minimum retained count are required.

Only complete byte-verified GPU outputs with status0 (stable) and retained_count>=minimum_retained enter the measured mesh. Empty and iteration-capped cells become invalid, not measured zero. The adapter verifies input hashes, source provenance, tile coverage and entire output bytes before assembling. Cell positions use doubled pixel coordinates, (2*column+1)*box_width-1 and the analogous y, preserving rectangular box aspect ratio without half-pixel rounding. Source values remain the actual verified GPU means.

Opcode61 fills missing cell centers, opcode62 optionally smooths the complete mesh, and existing opcode51 bilinearly expands it. Per-pixel query coordinates are independently RN32((2*x-(box_width-1))/(2*box_width)), likewise y; the existing bilinear contract clamps outside the center grid. Background estimation does not create an RMS, variance or uncertainty map. Supplied valid masks describe samples excluded from statistics; no-coverage handling for downstream photometry remains an explicit caller decision. A controlled end-to-end trial feeds the expanded background to opcode59 PSF scanning.

## Research and candidate families, 2026-10-03

[Photutils Background2D](https://photutils.readthedocs.io/en/stable/api/photutils.background.Background2D.html) motivates clipped box statistics, missing-cell handling and mesh filtering. [ShepardIDWInterpolator](https://photutils.readthedocs.io/en/stable/api/photutils.utils.ShepardIDWInterpolator.html) describes neighbor-based inverse-distance weights. [SciPy median filtering](https://docs.scipy.org/doc/scipy/reference/generated/scipy.ndimage.median_filter.html) documents boundary/median choices that this contract explicitly distinguishes. These are published method references; no external source code is copied, imported or required. Photutils 3's deprecated BkgIDWInterpolator wrapper is not adopted as a dependency.

Reviewed families: direct scan versus spatial trees for neighbor selection; insertion sorting versus sorting networks/histograms/selection for local medians; scalar versus tiled neighborhood gathers. Fixed small neighborhoods and exact ordered RN32 reductions permit fresh local32/64/128/256 and pack1/2/4 candidates. [Khronos subgroup capabilities](https://docs.vulkan.org/guide/latest/subgroups.html) inform scheduling portability. No global device winner is hardcoded. Full per-MathSpec QUICK<=60s; unmeasured candidates remain unmeasured. No RT or AI execution is claimed; timing remains informational without release A/B evidence.
