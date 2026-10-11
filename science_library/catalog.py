"""Research-backed contracts, defined before the CPU and GPU implementations."""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
DOMAINS = ('SPACE', 'BIO', 'CHEM', 'PHYSICS', 'SIGNAL', 'ENGINEERING', 'RT')
SOURCES = {
    'moments': ('Photutils center-of-mass centroid', 'https://photutils.readthedocs.io/en/stable/api/photutils.centroids.centroid_com.html', 'BSD-3-Clause'),
    'aperture': ('Photutils aperture photometry, center mask', 'https://photutils.readthedocs.io/en/stable/user_guide/aperture.html', 'BSD-3-Clause'),
    'fold': ('Astropy Box Least Squares: phase-folded light curves', 'https://docs.astropy.org/en/stable/timeseries/bls.html', 'BSD-3-Clause'),
    'linear': ('GSL weighted linear least squares', 'https://www.gnu.org/software/gsl/doc/html/lls.html', 'GPL-3.0-or-later; documentation/reference only, no copied implementation'),
    'match': ('Astropy catalog matching and angular separation', 'https://docs.astropy.org/en/stable/coordinates/matchsep.html', 'BSD-3-Clause'),
    'smith': ('Biopython pairwise local alignment', 'https://biopython.org/docs/latest/Tutorial/chapter_pairwise.html', 'Biopython License/BSD-3-Clause; independent recurrence implementation'),
    'contact': ('MDAnalysis native contacts / radius cutoff', 'https://docs.mdanalysis.org/stable/documentation_pages/analysis/contacts.html', 'LGPL-2.1-or-later/GPL-2.0-or-later by version; reference only'),
    'rdf': ('LAMMPS pair-distance histogram for radial distribution functions', 'https://docs.lammps.org/compute_rdf.html', 'GPL-2.0; reference only'),
    'distance': ('MDAnalysis distance arrays', 'https://docs.mdanalysis.org/stable/documentation_pages/lib/distances.html', 'reference only; no source copied'),
    'ising': ('Rutgers computational physics: nearest-neighbor Ising model J=1', 'https://web.physics.rutgers.edu/grad/509/Ising%20model.html', 'University teaching reference; no code copied'),
    'fir': ('Arm CMSIS-DSP FIR definition and fixed-point accumulator', 'https://arm-software.github.io/CMSIS-DSP/latest/group__FIR.html', 'Apache-2.0; independent implementation'),
    'csr': ('Netlib Templates: compressed row storage', 'https://netlib.org/linalg/html_templates/node91.html', 'reference only; no source copied'),
    'orient': ('Shewchuk robust geometric predicates', 'https://www.cs.cmu.edu/~quake/robust.html', 'public-domain reference implementation; no code copied'),
}
# Inputs are natively integer/fixed-point. Float data are rejected, never rounded.
# Scientific scope is the stated primitive, not a full downstream application.
DEFINITIONS = [
 ('SPACE_IMAGE_MOMENTS_U16_V1', 1, 'moments', 'Raw image moments through order two', 'Centroid and shape sufficient statistics on detector-count image cutouts.',
  'M_pq=sum(x^p*y^q*I[y,x]); (p,q)=(0,0),(1,0),(0,1),(2,0),(1,1),(0,2)',
  'images[B,H,W], 1<=H,W<=64; integer detector counts 0..65535', 'B x 6 unsigned64 moments, low word then high word; centroid is M10/M00,M01/M00 downstream; empty flux has zero moments', 'image cutouts', 'POSSIBLE'),
 ('SPACE_APERTURE_SUM_I32_V1', 2, 'aperture', 'Circular center-mask aperture photometry', 'Background-subtracted source flux and aperture pixel count.',
  'F=sum((I[y,x]-b)*1[(x-cx)^2+(y-cy)^2<=r^2]); A=sum(mask)',
  'image[H,W], H,W<=64, pixel/background -65535..65535; apertures[N]=[cx,cy,r,b], centers inside image, integer r 0..64', 'N x [signed32 flux, uint32 area]; clipping at image edge; no fractional pixel weighting', 'aperture queries with shared image', 'NONE'),
 ('SPACE_TRANSIT_FOLD_STATS_I32_V1', 3, 'fold', 'Trial-period phase-bin sufficient statistics', 'Preprocessing for binned transit/variability searches; not the complete BLS optimizer.',
  'bin(t,P)=floor((t mod P)*K/P); outputs per (P,bin): count,sum(y),sum(y^2)',
  'times[N] integer ticks 0..10000000, flux[N] -1000..1000, N<=8192; periods[T] 1..1000000; bins K 1..256', 'T*K x [u32 count,i64 flux sum,u64 square sum]; empty bins exactly zero', 'trial periods and bins; all observations shared', 'POSSIBLE'),
 ('SPACE_WEIGHTED_LINEAR_STATS_I32_V1', 4, 'linear', 'Weighted linear-fit normal-equation statistics', 'Exact sufficient statistics for weighted intercept/slope fitting; solve and covariance are downstream.',
  '[sum(w),sum(w*x),sum(w*y),sum(w*x*x),sum(w*x*y),sum(w*y*y)]',
  'samples[B,N,3]=(x,y,w), N<=1024, |x|,|y|<=1000, w integer 0..100', 'B x 6 signed64 statistics; singular and zero-weight inputs yield statistics, not an invented fitted solution', 'independent fits; sample shards may be summed with checked64 accumulators', 'STRONG_CANDIDATE'),
 ('SPACE_CATALOG_CHORD_MATCH_I32_V1', 5, 'match', 'Fixed-point catalog radius match and bounded nearest source', 'Cross-match two catalogs represented as integer Cartesian coordinates; unit-sphere chord queries require an explicitly pre-encoded sphere catalog.',
  'd2(q,p)=sum((q_k-p_k)^2); count=sum(d2<=R2); nearest=argmin(d2,index) within cutoff',
  'queries[N,3], catalog[M,3], |coordinate|<=1000000000; squared_radius integer0..12000000000000000000; declared coordinate_unit; no RA/Dec conversion inside this primitive',
  'N x [u32 count,u32 nearest_index,u64 squared_distance]; no match => [0,0xffffffff,0xffffffffffffffff]', 'query rows; catalog shards merge counts and min(distance,global index)', 'NONE'),
 ('BIO_SMITH_WATERMAN_I32_V1', 6, 'smith', 'Smith-Waterman local alignment score', 'Exact DNA local similarity score for independent sequence pairs.',
  'H[i,j]=max(0,H[i-1,j-1]+(2 if A[i-1]==B[j-1] else -1),H[i-1,j]-2,H[i,j-1]-2); score=max(H)',
  'pairs[B]=[DNA_A,DNA_B], A/C/G/T only, lengths0..128; match2,mismatch-1,linear gap-2', 'B x signed32 optimal local score; no traceback or affine-gap claim', 'independent sequence pairs', 'POSSIBLE'),
 ('BIO_CONTACT_COUNTS_I32_V1', 7, 'contact', 'Cross-group molecular contact counts', 'Count contacts between two atom groups using a hard distance cutoff; no periodic boundary wrapping.',
  'C(q)=sum_p [sum_k(q_k-p_k)^2<=R2]',
  'queries[N,3], catalog[M,3] integer coordinate ticks in +/-1000000000, squared_radius0..12000000000000000000, explicit coordinate_unit; cross-group coincidences included',
  'N x u32 counts; full input precision is retained', 'query atoms; add counts across disjoint catalog shards', 'NONE'),
 ('CHEM_PAIR_DISTANCE_SQUARED_I64_V1', 8, 'distance', 'Molecular pair squared-distance matrix', 'Geometric primitive for distance restraints and molecular structural analysis.',
  'D[i,j]=sum_k(A[i,k]-B[j,k])^2',
  'queries[N,3], catalog[M,3], integer coordinate ticks in +/-1000000000, explicit coordinate_unit', 'N*M x u64 exact squared distances; no sqrt or periodic wrapping', 'pair tiles', 'STRONG_CANDIDATE'),
 ('CHEM_RADIAL_HISTOGRAM_I64_V1', 9, 'rdf', 'Cross-group radial pair-count histogram', 'Raw shell counts for RDF analysis; volume/density normalization is downstream.',
  'H[q,b]=sum_p [E2[b]<=d2(q,p)<E2[b+1]]',
  'queries,catalog: integer coordinate ticks in +/-1000000000; strictly increasing squared_edges[2..65] in0..12000000000000000000; coordinate_unit required',
  'N*B x u32 shell counts, lower inclusive/upper exclusive; catalog groups not implicitly deduplicated', 'query rows/bins; sum per-query counts to obtain cross-group shell totals', 'NONE'),
 ('PHYSICS_ISING_OBSERVABLES_I32_V1', 10, 'ising', 'Periodic square-lattice Ising bond energy and magnetization', 'Observables of the zero-field nearest-neighbor Ising model with J=1.',
  'e[x,y]=-s[x,y]*(s[(x+1)modW,y]+s[x,(y+1)modH]); m[x,y]=s[x,y]; E=sum(e),M=sum(m)',
  'spins[H,W] in {-1,+1}, 3<=H,W<=1024; one static configuration', 'H*W x [i32 local energy,i32 spin]; each undirected nearest-neighbor bond counted once', 'sites with periodic one-cell neighbor halo; integer sum of site outputs', 'NONE'),
 ('SIGNAL_FIR_ACCUMULATE_I16_V1', 11, 'fir', 'Full-precision fixed-point FIR accumulation', 'Digital filtering of integer/Q15 samples with no discarded accumulator bits.',
  'a[n]=sum_{k=0}^{K-1} h[k]*x[n-k], x[j<0]=0',
  'samples[N],coefficients[K] signed16;1<=K<=1024; coefficients in forward delay order; for Q15 input output unit=2^-30',
  'N x signed64 accumulator; no rescaling, saturation or hidden rounding', 'output intervals with K-1 input halo; zero padding only at global origin', 'STRONG_CANDIDATE'),
 ('ENGINEERING_CSR_MATVEC_I32_V1', 12, 'csr', 'Exact sparse CSR matrix-vector product', 'Sparse integer or explicitly scaled fixed-point systems used in solver/operator stages.',
  'y[r]=sum_{j=rowptr[r]}^{rowptr[r+1]-1} values[j]*x[col[j]]',
  'CSR rowptr nondecreasing from0 to nnz; col in vector bounds; values,x signed16; <=65536 entries per row',
  'rows x signed64 exact products summed; duplicate columns supported; empty rows zero; downstream iterative solver not included', 'CSR rows with shared vector', 'STRONG_CANDIDATE'),
 ('ENGINEERING_ORIENT2D_I32_V1', 13, 'orient', 'Exact two-dimensional triangle orientation', 'Robust sidedness predicate for mesh/CAD triangulation on bounded integer coordinates.',
  'det=(bx-ax)*(cy-ay)-(by-ay)*(cx-ax); orientation=sign(det)',
  'triangles[N,3,2] integer coordinates in +/-10000', 'N x [i32 determinant,i32 sign]; collinear => [0,0]', 'independent triangles', 'NONE'),
]

from .float_catalog import DEFINITIONS as FLOAT_DEFINITIONS, SOURCES as FLOAT_SOURCES, PRECISION
SOURCES.update(FLOAT_SOURCES)
DEFINITIONS.extend(FLOAT_DEFINITIONS)

from .legacy_catalog import DEFINITIONS as LEGACY_DEFINITIONS, SOURCES as LEGACY_SOURCES, ORIGINALS
SOURCES.update(LEGACY_SOURCES)
DEFINITIONS.extend(LEGACY_DEFINITIONS)

from .triangle_catalog import DEFINITIONS as TRIANGLE_DEFINITIONS, SOURCES as TRIANGLE_SOURCES, ORIGINALS as TRIANGLE_ORIGINALS
SOURCES.update(TRIANGLE_SOURCES)
DEFINITIONS.extend(TRIANGLE_DEFINITIONS)
ORIGINALS.update(TRIANGLE_ORIGINALS)

from .space_search_catalog import DEFINITIONS as SPACE_SEARCH_DEFINITIONS, SOURCES as SPACE_SEARCH_SOURCES
SOURCES.update(SPACE_SEARCH_SOURCES)
DEFINITIONS.extend(SPACE_SEARCH_DEFINITIONS)

from .space_statistics_catalog import DEFINITIONS as SPACE_STATISTICS_DEFINITIONS, SOURCES as SPACE_STATISTICS_SOURCES
SOURCES.update(SPACE_STATISTICS_SOURCES)
DEFINITIONS.extend(SPACE_STATISTICS_DEFINITIONS)

from .space_inference_catalog import DEFINITIONS as SPACE_INFERENCE_DEFINITIONS, SOURCES as SPACE_INFERENCE_SOURCES
SOURCES.update(SPACE_INFERENCE_SOURCES)
DEFINITIONS.extend(SPACE_INFERENCE_DEFINITIONS)

from .space_imaging_catalog import DEFINITIONS as SPACE_IMAGING_DEFINITIONS, SOURCES as SPACE_IMAGING_SOURCES
SOURCES.update(SPACE_IMAGING_SOURCES)
DEFINITIONS.extend(SPACE_IMAGING_DEFINITIONS)

from .space_dynamics_catalog import DEFINITIONS as SPACE_DYNAMICS_DEFINITIONS, SOURCES as SPACE_DYNAMICS_SOURCES
SOURCES.update(SPACE_DYNAMICS_SOURCES)
DEFINITIONS.extend(SPACE_DYNAMICS_DEFINITIONS)

from .space_period_catalog import DEFINITIONS as SPACE_PERIOD_DEFINITIONS, SOURCES as SPACE_PERIOD_SOURCES
SOURCES.update(SPACE_PERIOD_SOURCES)
DEFINITIONS.extend(SPACE_PERIOD_DEFINITIONS)

from .space_psf_catalog import DEFINITIONS as SPACE_PSF_DEFINITIONS, SOURCES as SPACE_PSF_SOURCES
SOURCES.update(SPACE_PSF_SOURCES)
DEFINITIONS.extend(SPACE_PSF_DEFINITIONS)

from .space_background_catalog import DEFINITIONS as SPACE_BACKGROUND_DEFINITIONS, SOURCES as SPACE_BACKGROUND_SOURCES
SOURCES.update(SPACE_BACKGROUND_SOURCES)
DEFINITIONS.extend(SPACE_BACKGROUND_DEFINITIONS)

from .space_biweight_catalog import DEFINITIONS as SPACE_BIWEIGHT_DEFINITIONS, SOURCES as SPACE_BIWEIGHT_SOURCES
SOURCES.update(SPACE_BIWEIGHT_SOURCES)
DEFINITIONS.extend(SPACE_BIWEIGHT_DEFINITIONS)

from .space_mode_catalog import DEFINITIONS as SPACE_MODE_DEFINITIONS, SOURCES as SPACE_MODE_SOURCES
SOURCES.update(SPACE_MODE_SOURCES)
DEFINITIONS.extend(SPACE_MODE_DEFINITIONS)

from .space_uncertainty_catalog import DEFINITIONS as SPACE_UNCERTAINTY_DEFINITIONS, SOURCES as SPACE_UNCERTAINTY_SOURCES
SOURCES.update(SPACE_UNCERTAINTY_SOURCES)
DEFINITIONS.extend(SPACE_UNCERTAINTY_DEFINITIONS)

from .space_gls_catalog import DEFINITIONS as SPACE_GLS_DEFINITIONS, SOURCES as SPACE_GLS_SOURCES
SOURCES.update(SPACE_GLS_SOURCES)
DEFINITIONS.extend(SPACE_GLS_DEFINITIONS)

from .space_joint_gls_catalog import DEFINITIONS as SPACE_JOINT_GLS_DEFINITIONS, SOURCES as SPACE_JOINT_GLS_SOURCES
SOURCES.update(SPACE_JOINT_GLS_SOURCES)
DEFINITIONS.extend(SPACE_JOINT_GLS_DEFINITIONS)

from .space_nbody_catalog import DEFINITIONS as SPACE_NBODY_DEFINITIONS, SOURCES as SPACE_NBODY_SOURCES
SOURCES.update(SPACE_NBODY_SOURCES)
DEFINITIONS.extend(SPACE_NBODY_DEFINITIONS)

from .space_encounter_catalog import DEFINITIONS as SPACE_ENCOUNTER_DEFINITIONS, SOURCES as SPACE_ENCOUNTER_SOURCES
SOURCES.update(SPACE_ENCOUNTER_SOURCES)
DEFINITIONS.extend(SPACE_ENCOUNTER_DEFINITIONS)

from .space_kalman_catalog import DEFINITIONS as SPACE_KALMAN_DEFINITIONS, SOURCES as SPACE_KALMAN_SOURCES
SOURCES.update(SPACE_KALMAN_SOURCES)
DEFINITIONS.extend(SPACE_KALMAN_DEFINITIONS)

from .space_rts_catalog import DEFINITIONS as SPACE_RTS_DEFINITIONS, SOURCES as SPACE_RTS_SOURCES
SOURCES.update(SPACE_RTS_SOURCES)
DEFINITIONS.extend(SPACE_RTS_DEFINITIONS)

from .space_precession_catalog import DEFINITIONS as SPACE_PRECESSION_DEFINITIONS, SOURCES as SPACE_PRECESSION_SOURCES
SOURCES.update(SPACE_PRECESSION_SOURCES)
DEFINITIONS.extend(SPACE_PRECESSION_DEFINITIONS)

from .space_kepler_catalog import DEFINITIONS as SPACE_KEPLER_DEFINITIONS, SOURCES as SPACE_KEPLER_SOURCES
SOURCES.update(SPACE_KEPLER_SOURCES)
DEFINITIONS.extend(SPACE_KEPLER_DEFINITIONS)

from .space_hyperbolic_catalog import DEFINITIONS as SPACE_HYPERBOLIC_DEFINITIONS, SOURCES as SPACE_HYPERBOLIC_SOURCES
SOURCES.update(SPACE_HYPERBOLIC_SOURCES)
DEFINITIONS.extend(SPACE_HYPERBOLIC_DEFINITIONS)

from .space_parabolic_catalog import DEFINITIONS as SPACE_PARABOLIC_DEFINITIONS, SOURCES as SPACE_PARABOLIC_SOURCES
SOURCES.update(SPACE_PARABOLIC_SOURCES)
DEFINITIONS.extend(SPACE_PARABOLIC_DEFINITIONS)

from .space_coherence_catalog import DEFINITIONS as SPACE_COHERENCE_DEFINITIONS, SOURCES as SPACE_COHERENCE_SOURCES
SOURCES.update(SPACE_COHERENCE_SOURCES)
DEFINITIONS.extend(SPACE_COHERENCE_DEFINITIONS)

from .space_gnomonic_catalog import DEFINITIONS as SPACE_GNOMONIC_DEFINITIONS, SOURCES as SPACE_GNOMONIC_SOURCES
SOURCES.update(SPACE_GNOMONIC_SOURCES)
DEFINITIONS.extend(SPACE_GNOMONIC_DEFINITIONS)

from .space_tangent_vector_catalog import DEFINITIONS as SPACE_TANGENT_VECTOR_DEFINITIONS, SOURCES as SPACE_TANGENT_VECTOR_SOURCES
SOURCES.update(SPACE_TANGENT_VECTOR_SOURCES)
DEFINITIONS.extend(SPACE_TANGENT_VECTOR_DEFINITIONS)

from .space_sip_catalog import DEFINITIONS as SPACE_SIP_DEFINITIONS, SOURCES as SPACE_SIP_SOURCES
SOURCES.update(SPACE_SIP_SOURCES)
DEFINITIONS.extend(SPACE_SIP_DEFINITIONS)

def specifications():
    result = []
    for wid, opcode, source, name, purpose, equations, inp, out, partition, ai in DEFINITIONS:
        title, url, license_note = SOURCES[source]
        rt = opcode in (5, 7, 9, 37, 38)
        result.append(dict(
            workload_id=wid, domain=wid.split('_')[0], scientific_domain=wid.split('_')[0],
            scientific_name=name, common_name=name, scientific_use=purpose, scientific_purpose=purpose,
            opcode=opcode, source_references=[dict(title=title,url=url,accessed='2026-10-03')],
            canonical_equations=equations, input_contract=inp, output_contract=out, result_contract=out,
            precision_requirements='Exact bounded integer arithmetic. 64-bit values are serialized as low/high uint32 words. Float inputs rejected; no implicit quantization.',
            tolerances=dict(allowed_differing_bits=0,absolute=0,relative=0),
            validation_method='Entire output byte stream vs independent Python arbitrary-precision CPU reference; edge vectors before search; each timing candidate checked before/after; held-out winner confirmation.',
            reference_implementation='science_library/reference.py', CPU_reference='science_library/reference.py',
            reference_test_vectors=f'science_library/vectors/{wid}.json',
            licensing_provenance=dict(implementation='Original ASTRO implementation of published equations; no external code copied.',reference_license=license_note),
            generic_GPU='runtime/native_science_library + science_library/shaders.py',
            RT_backend='AABB broadphase + exact64 integer narrowphase' if rt else 'NOT_APPLICABLE_NO_SPATIAL_PRUNING',
            RT_applicability='Bounded radius broadphase; expanded float boxes are conservative only; all accepted results use integer arithmetic.' if rt else 'Dense reductions, recurrences or all-pair output have no useful ray/BVH candidate pruning.',
            AI_relevance=ai, AI_backend='AI_BACKEND_UNAVAILABLE', partition_strategy=partition,
            status='IMPLEMENTATION_REQUIRES_LOCAL_BITEXACT_VALIDATION',
            MathSpec=f'science_library/specs/{wid}.json',
            scientific_scope='Stated primitive only. Generated test vectors validate algorithms, not researcher-authorized live jobs.',
        ))
    for spec in result:
        if spec['opcode'] >= 14 and spec['opcode'] not in (25,34):
            spec['precision_requirements']=PRECISION
            spec['reference_implementation']='science_library/float_reference.py + f32.py (Fraction oracle)'
            spec['CPU_reference']=spec['reference_implementation']
            spec['validation_method']='Full byte comparison against independent exact-rational RN32 CPU oracle; analytic, adversarial and held-out vectors; arithmetic tested separately.'
            spec['arithmetic_contract']='docs/BINARY32_CONTRACT.md'
            spec['source_references'].append(dict(title='Berkeley SoftFloat: software IEEE arithmetic methodology (no code copied)',url='https://www.jhauser.us/arithmetic/SoftFloat.html',accessed='2026-10-03'))
        if spec['opcode']>=25:
            spec['reference_implementation']='science_library/domain_reference.py + f32.py (integer/Fraction oracle)'
            spec['CPU_reference']=spec['reference_implementation']
        if 30<=spec['opcode']<=38:
            spec['reference_implementation']='science_library/legacy_reference.py + vector_f32.py (CPU hardware binary32, probed against Fraction oracle)'
            spec['CPU_reference']=spec['reference_implementation']
            spec['contract_revision']='ZERO_BIT_AMENDMENT_V2'
            spec['historical_contract']=ORIGINALS[spec['opcode']]
            spec['historical_contract_sha256']=__import__('hashlib').sha256((ROOT/spec['historical_contract']).read_bytes()).hexdigest()
            spec['legacy_compatibility']='Scientific operator and input representation retained; deterministic rounding/serialization strengthened. Not a claim of identical bytes to historical tolerant executors.'
            spec['validation_method']='Full raw GPU bytes against independent CPU binary32 reference; CPU operations cross-checked with exact Fraction oracle; historical double/scientific invariants reported separately, never substituted for zero-bit gate.'
            spec['partition_limits']=spec['input_contract']
        if spec['opcode'] in (35,36):
            spec['precision_requirements']+=' Hann/windowed FFT use deterministic double-single (two binary32 components), then RN32 complex output; see docs/SPACE_ZERO_BIT_AMENDMENTS.md for the exact operation graph. No native GPU float64 required.'
            spec['CPU_reference']+=' + spectral_precision.py (exact binary64 product residual)'
            spec['reference_implementation']=spec['CPU_reference']
            spec['source_references'].append(dict(title='Hida, Li, Bailey: Library for Double-Double and Quad-Double Arithmetic; Two-Sum methodology adapted to binary32',url='https://www.davidhbailey.com/dhbpapers/qd.pdf',accessed='2026-10-03'))
        if spec['opcode'] in (37,38):
            spec['precision_requirements']='Exact rational intersection on preserved binary32 inputs; canonical RN32 direction normalization and final distance. Dynamic RN32 frozen sine offset and addition. GPU signed 256-bit integer determinants; no float narrowphase, no quantization.'
            spec['CPU_reference']=spec['reference_implementation']='science_library/triangle_reference.py + f32.py (independent Fraction oracle)'
            spec['arithmetic_contract']='docs/TRIANGLE_ZERO_BIT_CONTRACT.md'
            spec['RT_backend']='Conservative AABB ray-query broadphase + exact 256-bit determinant narrowphase; dynamic has BLAS and TLAS update and rebuild paths'
            spec['RT_applicability']='BVH prunes ray/triangle candidates; hardware-computed triangle distance is never accepted as the answer'
            spec['validation_method']='Full CPU/GPU raw-byte equality for every ray and, for dynamic jobs, every mutated vertex at every requested frame, warmup and final; generic, RT update and rebuild independently checked'
            spec['scientific_scope']='Geometric primitive / local commissioning. No public science credit; original tolerant GPU-vs-GPU tests are not independent proofs.'
            spec['source_references'].append(dict(title='Khronos Vulkan ray traversal and acceleration-structure updates',url='https://docs.vulkan.org/spec/latest/chapters/raytraversal.html',accessed='2026-10-03'))
        if 39<=spec['opcode']<=44:
            spec['CPU_reference']=spec['reference_implementation']='science_library/space_search_reference.py + f32.py (Fraction oracle)'
            spec['arithmetic_contract']='docs/SPACE_SEARCH_CONTRACTS.md'
            spec['partition_limits']=spec['input_contract']
        if 45<=spec['opcode']<=47:
            spec['CPU_reference']=spec['reference_implementation']='science_library/space_statistics_reference.py + f32.py (Fraction oracle; independent flood fill for labels)'
            spec['arithmetic_contract']='docs/SPACE_STATISTICS_CONTRACTS.md'
            spec['partition_limits']=spec['input_contract']
            spec['RT_applicability']='Ordered statistical reductions and local pixel adjacency do not use ray/BVH candidate pruning.'
            if spec['opcode']==47:
                spec['precision_requirements']='Preserved finite binary32 comparisons; exact uint32 component labels. No arithmetic quantization or numeric label tolerance.'
        if 48<=spec['opcode']<=50:
            spec['CPU_reference']=spec['reference_implementation']='science_library/space_inference_reference.py + f32.py (Fraction oracle)'
            spec['arithmetic_contract']='docs/SPACE_INFERENCE_CONTRACTS.md'
            spec['partition_limits']=spec['input_contract']
            spec['RT_applicability']='Quantiles, statistical tails and dense band reductions have no ray/BVH candidate pruning.'
            if spec['opcode']==49:
                spec['precision_requirements']='Exact finite binary32 comparisons and uint32 counts/rational probability; no float division or tolerance window.'
        if 51<=spec['opcode']<=53:
            spec['CPU_reference']=spec['reference_implementation']='science_library/space_imaging_reference.py + f32.py (Fraction oracle; BFS graph closure)'
            spec['arithmetic_contract']='docs/SPACE_IMAGING_CONTRACTS.md'
            spec['partition_limits']=spec['input_contract']
            spec['RT_applicability']='Mesh gathers, graph equivalences and ordered pixel reductions have no conservative ray/BVH pruning.'
            if spec['opcode']==52:
                spec['precision_requirements']='Exact uint32 identifiers and checked uint32 component counts; no floating point.'
        if 54<=spec['opcode']<=56:
            spec['CPU_reference']=spec['reference_implementation']='science_library/space_dynamics_reference.py + f32.py (independent Fraction oracle)'
            spec['arithmetic_contract']='docs/SPACE_DYNAMICS_CONTRACTS.md'
            spec['partition_limits']=spec['input_contract']
            spec['RT_applicability']='Analytic central/J2 force and trajectory stages have no candidate geometry for BVH pruning.'
        if 57<=spec['opcode']<=58:
            spec['CPU_reference']=spec['reference_implementation']='science_library/space_period_reference.py + f32.py (independent Fraction oracle)'
            spec['arithmetic_contract']='docs/SPACE_PERIOD_CONTRACTS.md'
            spec['partition_limits']=spec['input_contract']
            spec['RT_applicability']='Fourier design matrices and phase-bin reductions do not admit ray/BVH pruning.'
        if 59<=spec['opcode']<=60:
            spec['CPU_reference']=spec['reference_implementation']='science_library/space_psf_reference.py + f32.py (independent Fraction oracle)'
            spec['arithmetic_contract']='docs/SPACE_PSF_MIXTURE_CONTRACTS.md'
            spec['partition_limits']=spec['input_contract']
            spec['RT_applicability']='Weighted image gathers and dense template solves have no conservative ray/BVH pruning.'
        if 61<=spec['opcode']<=62:
            spec['CPU_reference']=spec['reference_implementation']='science_library/space_background_reference.py + f32.py (independent integer/Fraction oracle)'
            spec['arithmetic_contract']='docs/SPACE_BACKGROUND_CONTRACTS.md'
            spec['partition_limits']=spec['input_contract']
            spec['RT_applicability']='Bounded integer neighbor scans and local median selection use no ray/BVH path.'
        if spec['opcode']==63:
            spec['CPU_reference']=spec['reference_implementation']='science_library/space_biweight_reference.py + f32.py (independent Fraction oracle)'
            spec['arithmetic_contract']='docs/SPACE_BIWEIGHT_CONTRACT.md'
            spec['partition_limits']=spec['input_contract']
            spec['RT_applicability']='Median selection and ordered robust reductions have no ray/BVH path.'
        if spec['opcode']==64:
            spec['CPU_reference']=spec['reference_implementation']='science_library/space_mode_reference.py + f32.py (independent recursive Fraction oracle)'
            spec['arithmetic_contract']='docs/SPACE_MODE_CONTRACT.md'
            spec['partition_limits']=spec['input_contract']
            spec['RT_applicability']='Shortest-half order statistics use no ray/BVH path.'
        if 65<=spec['opcode']<=66:
            spec['CPU_reference']=spec['reference_implementation']='science_library/space_uncertainty_reference.py + f32.py (independent Fraction oracle)'
            spec['arithmetic_contract']='docs/SPACE_UNCERTAINTY_CONTRACTS.md'
            spec['partition_limits']=spec['input_contract']
            spec['RT_applicability']='Pointwise noise and ordered covariance projection have no ray/BVH path.'
        if spec['opcode']==67:
            spec['CPU_reference']=spec['reference_implementation']='science_library/space_gls_reference.py + f32.py (independent Fraction oracle)'
            spec['arithmetic_contract']='docs/SPACE_GLS_CONTRACT.md'
            spec['partition_limits']=spec['input_contract']
            spec['RT_applicability']='Small factor solves and ordered covariance quadratics have no ray/BVH path.'
        if spec['opcode']==68:
            spec['CPU_reference']=spec['reference_implementation']='science_library/space_joint_gls_reference.py + f32.py (independent Fraction oracle)'
            spec['arithmetic_contract']='docs/SPACE_JOINT_GLS_CONTRACT.md'
            spec['partition_limits']=spec['input_contract']
            spec['RT_applicability']='Guarded joint matrix solves have no ray/BVH path.'
        if spec['opcode'] in (69,70):
            spec['CPU_reference']=spec['reference_implementation']='science_library/space_nbody_reference.py + f32.py (independent Fraction oracle)'
            spec['arithmetic_contract']='docs/SPACE_NBODY_CONTRACTS.md'
            spec['partition_limits']=spec['input_contract']
            spec['RT_applicability']='All gravitational pairs contribute; no conservative ray-pruning route is claimed.'
        spec['reference_sources']=spec['source_references']
        spec['provenance']=spec['licensing_provenance']
        if spec['opcode']<30:
            spec['partition_limits']='At most1,000,000 output records; spatial pair tests <=16,000,000 per job; RDF pair-bin tests <=16,000,000. Submit smaller tiles otherwise.'
        if spec['opcode']==71:
            spec['CPU_reference']=spec['reference_implementation']='science_library/space_encounter_reference.py + f32.py (independent Fraction oracle)'
            spec['arithmetic_contract']='docs/SPACE_ENCOUNTER_CONTRACT.md'
            spec['partition_limits']=spec['input_contract']
            spec['RT_applicability']='Explicit complete pair outputs; rounded contact is not conservative RT pruning.'
        if spec['opcode']==72:
            spec['CPU_reference']=spec['reference_implementation']='science_library/space_kalman_reference.py + f32.py (independent Fraction oracle)'
            spec['arithmetic_contract']='docs/SPACE_KALMAN_CONTRACT.md'
            spec['partition_limits']=spec['input_contract']
            spec['RT_applicability']='Small dense prediction and measurement update has no conservative ray/BVH pruning.'
        if spec['opcode']==73:
            spec['CPU_reference']=spec['reference_implementation']='science_library/space_rts_reference.py + f32.py (independent Fraction oracle)'
            spec['arithmetic_contract']='docs/SPACE_RTS_CONTRACT.md'
            spec['partition_limits']=spec['input_contract']
            spec['RT_applicability']='Dense backwards smoothing solve has no conservative ray/BVH pruning.'
        if spec['opcode']==74:
            spec['CPU_reference']=spec['reference_implementation']='science_library/space_precession_reference.py + f32.py (independent Fraction oracle)'
            spec['arithmetic_contract']='docs/SPACE_PRECESSION_CONTRACT.md'
            spec['partition_limits']=spec['input_contract']
            spec['RT_applicability']='Epoch polynomials and fixed-size rotations have no ray/BVH pruning.'
        if spec['opcode']==75:
            spec['CPU_reference']=spec['reference_implementation']='science_library/space_kepler_reference.py + f32.py (independent Fraction oracle)'
            spec['arithmetic_contract']='docs/SPACE_KEPLER_CONTRACT.md'
            spec['partition_limits']=spec['input_contract']
            spec['RT_applicability']='Implicit orbital equation and direct state conversion have no ray/BVH pruning.'
        if spec['opcode']==76:
            spec['CPU_reference']=spec['reference_implementation']='science_library/space_hyperbolic_reference.py + f32.py (independent Fraction oracle)'
            spec['arithmetic_contract']='docs/SPACE_HYPERBOLIC_CONTRACT.md'
            spec['partition_limits']=spec['input_contract']
            spec['RT_applicability']='Hyperbolic implicit root and direct state conversion have no ray/BVH pruning.'
        if spec['opcode']==77:
            spec['CPU_reference']=spec['reference_implementation']='science_library/space_parabolic_reference.py + f32.py (independent Fraction oracle)'
            spec['arithmetic_contract']='docs/SPACE_PARABOLIC_CONTRACT.md'
            spec['partition_limits']=spec['input_contract']
            spec['RT_applicability']='Cubic time-of-flight root and direct state conversion have no ray/BVH pruning.'
        if spec['opcode']==78:
            spec['CPU_reference']=spec['reference_implementation']='science_library/space_coherence_reference.py + f32.py (independent Fraction oracle)'
            spec['arithmetic_contract']='docs/SPACE_COHERENCE_CONTRACT.md'
            spec['partition_limits']=spec['input_contract']
            spec['RT_applicability']='Ordered complex-product reductions have no conservative ray/BVH pruning.'
            spec['source_references'].append(dict(title='SciPy magnitude-squared coherence definition',url='https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.coherence.html',accessed='2026-10-03'))
        if spec['opcode']==79:
            spec['CPU_reference']=spec['reference_implementation']='science_library/space_gnomonic_reference.py + f32.py (independent Fraction oracle)'
            spec['arithmetic_contract']='docs/SPACE_GNOMONIC_CONTRACT.md'
            spec['partition_limits']=spec['input_contract']
            spec['RT_applicability']='Dense spherical projection and perspective division have no conservative ray/BVH pruning.'
        if spec['opcode']==80:
            spec['CPU_reference']=spec['reference_implementation']='science_library/space_tangent_vector_reference.py + f32.py (independent Fraction oracle)'
            spec['arithmetic_contract']='docs/SPACE_TANGENT_VECTOR_CONTRACT.md'
            spec['partition_limits']=spec['input_contract']
            spec['RT_applicability']='Dense tangent-basis reconstruction and normalization have no conservative ray/BVH pruning.'
            spec['source_references'][0]['accessed']='2026-10-04'
        if spec['opcode']==81:
            spec['CPU_reference']=spec['reference_implementation']='science_library/space_sip_reference.py + f32.py (independent Fraction oracle)'
            spec['arithmetic_contract']='docs/SPACE_SIP_FORWARD_CONTRACT.md'
            spec['partition_limits']=spec['input_contract']
            spec['RT_applicability']='Independent pixel distortion polynomials have no conservative ray/BVH pruning.'
            spec['source_references'][0]['accessed']='2026-10-04'
    return result

SPECS = {r['workload_id']: r for r in sorted(specifications(), key=lambda r: (DOMAINS.index(r['domain']), r['opcode']))}

def write_specs():
    for spec in SPECS.values():
        (ROOT/spec['MathSpec']).write_text(json.dumps(spec, indent=2, ensure_ascii=False)+'\n')

if __name__ == '__main__':
    write_specs()
