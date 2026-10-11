# Exact static and dynamic ray queries, v1.17.13

The two historical IDs remain `RT_STATIC_NEAREST_TRIANGLE_HIT_V1` and `RT_DYNAMIC_NEAREST_TRIANGLE_HIT_V1`. Their original commissioning contracts are preserved and SHA256-linked from the new MathSpecs. `ZERO_BIT_AMENDMENT_V2` adds independent CPU proof, exact predicates and a deterministic floating-point boundary. Historical tolerance-only GPU comparisons do not establish these new output bytes.

These are geometric primitives and local RT commissioning workloads, separate from the six scientific domains. They do not create external research credit or implement a complete rendering/transport simulation. The source method is [Möller and Trumbore (1997)](https://my.eng.utah.edu/~cs6965/papers/MT97.pdf); implementation here is original, with exact determinants rather than their floating-point code.

## Input and arithmetic domain

JSON uses `encoding: binary32-hex`. Supply `triangles[M][3][3]` and `rays[N]`, each ray having `origin[3]` and `direction[3]`. Every supplied component must be zero or have magnitude between 2^-16 and 2^16 inclusive. Directions must be nonzero. There are 1…4096 triangles and 1…4096 rays. Dynamic input adds 1…8 uint32 `frames`; M×N×frames must not exceed 1,048,576. Split rays for larger jobs.

These limits bound the exact integer representation and CPU verification cost. No input is silently rounded to an integer or reduced precision. Inputs outside the declared domain are rejected. All finite binary32 patterns inside it retain their value, including signed input zeros.

Normalize directions once per query using separate canonical RN32 square/multiply/add/root/divide operations: `length=sqrt(RN(RN(dx²+dy²)+dz²))`, then `d[k]=RN(input_d[k]/length)`. The CPU uses the independent Fraction binary32 oracle; GPU normalization uses software integer significands. Accepted normalized components and mutated vertices must be exactly representable on the 2^-56 grid. This is an exact change of representation, not a quantization step.

## Exact intersection and output

For triangle a,b,c and ray o,d:

- e1=b−a, e2=c−a, p=d×e2, det=e1·p.
- If |det| < the exact value encoded by `0x322bcc77` (RN32(1e-8)), report no hit for this triangle.
- s=o−a, u=(s·p)/det, q=s×e1, v=(d·q)/det, t=(e2·q)/det.
- Require 0≤u≤1, v≥0 and u+v≤1. Both windings are accepted; edges and vertices are closed. Degenerate/parallel triangles fail the determinant test.
- Round positive t once to nearest-even binary32. Accept only if its encoding is greater than `0x38d1b717` (RN32(1e-4)) and less than `0x7149f2ca` (RN32(1e30)).
- Return the smallest accepted distance; otherwise return miss sentinel `0x7149f2ca`. Positive binary32 encodings have monotonic unsigned ordering. Duplicate candidates and equal distances cannot change the result.

The determinant and ray-origin cutoffs are inherited parameters of the geometric operation, not allowed CPU/GPU error. The output acceptance tolerance remains exactly zero bits.

The CPU evaluates geometric expressions with exact `Fraction` values. GPU predicates use signed-magnitude integers with eight uint32 limbs. Coordinates are exactly multiplied by 2^56; cross and scalar triple products are computed without truncating any significant bit. There is no GPU FP64 requirement. The final positive rational ratio is normalized by integer shifts and divided with a 27-bit significand plus sticky remainder, then passed to the existing RN32 packer.

Bound: coordinate integers have magnitude ≤2^72, differences ≤2^73, normalized direction integers ≤2^57. The largest three-coordinate scalar triple product is below 2^222. Determinants involving direction are below 2^206. These, barycentric sums, and the normalization/remainder shifts fit 256 bits. The arbitrary-precision CPU implementation and a separate GPU arithmetic stress tool validate signed carries/borrows, full products and ratio rounding.

This exact boundary can differ from the old native FP32/hardware triangle result near edges or cancellation. No identical-byte compatibility with that historical tolerant implementation is claimed. The physical operation remains nearest opaque triangle intersection within the stated numerical contract.

## Real RT path

RT enumerates conservative AABB candidates with Vulkan ray queries; it does not supply the accepted triangle distance. Each candidate runs the same exact integer triangle predicate as generic compute. The traversal bounds are expanded by at least 1e-6, or 1e-6 of coordinate scale. Extra candidates are harmless. Traversal order and duplicate candidates do not affect a minimum.

This uses the actual acceleration-structure/ray-query API, including BLAS/TLAS allocation and construction. See the [Khronos traversal specification](https://docs.vulkan.org/spec/latest/chapters/raytraversal.html). Device-specific numerical traversal behavior still must pass the full CPU comparison for every submitted job; a candidate lost by any driver is rejected, never released as a valid result.

## Dynamic mutation, frames and maintenance

For each explicit frame f, every triangle j gets the historical sine deformation along Z:

`z = RN32(base_z + OFFSETS[(17*j + 13*f) & 1023])`

`OFFSETS[k] = RN32(0.0025*sin(2*pi*k/1024))` is frozen from Decimal90 arithmetic, with exact cardinal axes. `tools/generate_triangle_offsets.py` regenerates the table. This specifies a reproducible amendment to the old device-specific sine approximation. X and Y retain their exact original input words. Every frame derives from immutable base vertices; frame order and revisiting a frame cannot accumulate drift.

The compute prepass writes all mutated vertices and their candidate AABBs on the GPU. No CPU-computed geometry, hit distances, candidate IDs or partial results are uploaded. Three measured executors are available:

| Backend | Work included in each timed repetition |
|---|---|
| GENERIC_COMPUTE | GPU mutation of every frame, then exact brute-force queries |
| RT_COMPUTE | GPU mutation, BLAS update/refit, TLAS update/refit, exact RT candidate queries |
| RT_REBUILD | GPU mutation, full BLAS rebuild, full TLAS rebuild, exact RT candidate queries |

Both acceleration-structure levels are maintained for each frame. Compute→AS, BLAS→TLAS, AS→query and query→next-frame dependencies are explicit Vulkan barriers. Initial scene construction is outside the repeated interval; all frame maintenance is inside it. See [Khronos acceleration-structure update requirements](https://docs.vulkan.org/spec/latest/chapters/accelstructures.html).

Distances are frame-major, then ray order. The runner additionally downloads every frame's complete mutated geometry after warmup and after the measured repetitions. Both snapshots are compared byte-for-byte with the CPU, including vertices missed by every ray. A geometry mismatch fails the whole job even when distances happen to agree. Geometry auditing/readback is outside throughput timing; the finite worker still pays that wall-clock cost.

Output partitioning retains the complete required geometry prepass for all frames, and emits only the requested distance interval. Partition reassembly and the complete geometry audit are independently checked.

## Search and limitations

Every search starts with fresh COLD-ZERO mapping. Each available static backend has 12 local/pack candidates; dynamic has 36 candidates across compute/update/rebuild. Rounding and predicate order are not tuning axes. The full current input is verified before and after timing, and winners receive held-out confirmation. Dynamic profiles require complete mutation evidence as well as distance evidence.

Both old pending RT IDs are now implemented within this bounded contract. Other unimplemented science families remain on the roadmap. AI/tensor execution, global optimality, production credit and continuous node saturation are not implied. Existing historical standalone launchers are retained as historical tools; the strict path is the shared science-library CLI/worker.
