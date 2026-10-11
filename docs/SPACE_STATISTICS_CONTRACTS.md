# SPACE statistics and segmentation — v1.17.16

These three original implementations use published scientific methods. Method references are in each MathSpec. The supplied data must satisfy the explicit bounded contract; there is no silent quantization. A kernel may release results only after **zero differing bits over its complete output** against the independent CPU reference, including all masks and labels.

## Bootstrap (opcode 45)

The caller supplies a finite binary32 measurement vector and a rectangular matrix of resampling indices. Each replicate draws its specified indices with replacement, in the supplied order. An increasing-index, left-to-right RN32 sum starting at positive zero is divided by the replicate length. A second ordered pass sums squared RN32 residuals and divides by K−1, producing sample variance. The two output words are mean and sample variance. The kernel does not generate random indices, infer independence or compute confidence intervals. Research jobs must provide appropriate resampling design and RNG provenance externally; deterministic fixture seeds are test data only.

## Sigma clipping (opcode 46)

Each row is an independent patch/window with an explicit 0/1 validity mask. For current retained values, compute ordered RN32 mean, then two-pass population variance (denominator n), then RN32 square root. Compute lower and upper bounds with separate RN32 multiply and subtract/add. Values strictly outside the bounds are removed simultaneously; equality is retained. Repeat at most maxiters times, stopping when nothing changes. Removed values never return. Recompute statistics on the final mask, even after the iteration limit.

Output per row: status, retained count, mean, population variance, then **every retained flag**. Status 0 means a clipping pass removed nothing, 1 means the final mask is empty, and 2 means the last permitted pass still removed values (convergence not proved). Empty statistics are positive zero. A one-value row has zero variance. This is mean/population-standard-deviation clipping, not median/MAD clipping. Non-finite inputs and arithmetic overflow reject the entire job before dispatch, including invalid/masked input values. No implicit NaN removal.

## Segmentation (opcode 47)

Each image has its own mask. Foreground requires validity and a strict value > threshold comparison on preserved finite binary32 inputs. Connectivity is explicitly 4 or 8; the image edge has no wraparound. Remove complete connected components containing fewer than npixels foreground pixels. A surviving component receives label 1 + its smallest row-major index, identically for every member. Labels can have gaps; label identity does not claim Photutils' relabeling convention. CPU flood fill is independent of the GPU union-find traversal.

Each image is one indivisible record. Cutting a large image into independent tiles can sever a source and is **not** an equivalent partition. This bounded cutout primitive does not implement deblending, source classification or a complete survey segmentation pipeline.

## Arithmetic, execution and candidate research

Bootstrap and clipping use the existing Fraction CPU oracle and uint-only software RN32 GPU arithmetic from `BINARY32_CONTRACT.md`. Input signed zeros compare equally; arithmetic zeros are canonical positive zero. No FMA, native transcendental shortcuts, reassociated reductions or approximate tolerance passes. Segmentation uses exact finite comparisons and integer labels.

Independent replicates/patches/cutouts map to GPU invocations; search covers local sizes32/64/128/256 and record packs1/2/4 subject to actual device capability. The current kernel family uses ordered row reductions and per-cutout union-find. [NVIDIA's documented CCL family](https://developer.nvidia.com/docs/drive/drive-os/7.0.3/public/drive-os-linux-sdk/embedded-software-components/DRIVE_AGX_SoC/DriveWorks/DriveWorks_SDK/tutorials/intermediate_tutorials/imageprocessing/connectedcomponents_usecase1.html) was examined for algorithm-family research; no CUDA code or measured winner is imported. Cooperative tree reductions alter the frozen RN32 operation graph, so are not interchangeable variants of these contracts. Multi-pass global CCL is a future larger-image contract, not falsely counted in the current search.

RT has no suitable ray/BVH pruning for resampling reductions, clipping or local pixel adjacency. RT execution is explicitly unavailable for these three contracts. AI relevance remains metadata only; AI_BACKEND_UNAVAILABLE. QUICK candidate timing is informational and never version-comparison evidence. COLD-ZERO requires a fresh hardware mapping; old profiles and winners are not inherited.
