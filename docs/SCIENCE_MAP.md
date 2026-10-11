# Science map and complete registry inventory

**IMPLEMENTED public reference corpus: 81 primitives, including 66 SPACE.** The development registry contains 94 distinct entries. This inventory preserves all entries without inventing a public executor for the remaining 13.

Natural performance units must be derived from each exact workload/contract. Similar names do not make historical and canonical amended workloads comparable. The [public GPU demo](GPU_DEMO.md) enables only FFT256, Convolution, XCORR and integer FIR; other GPU workloads are outside its permitted execution scope.

| Workload | Domain | Public canonical CPU reference |
|---|---|---|
| SPACE_IMAGE_MOMENTS_U16_V1 | SPACE | [Contract](../science_library/specs/SPACE_IMAGE_MOMENTS_U16_V1.json) |
| SPACE_APERTURE_SUM_I32_V1 | SPACE | [Contract](../science_library/specs/SPACE_APERTURE_SUM_I32_V1.json) |
| SPACE_TRANSIT_FOLD_STATS_I32_V1 | SPACE | [Contract](../science_library/specs/SPACE_TRANSIT_FOLD_STATS_I32_V1.json) |
| SPACE_WEIGHTED_LINEAR_STATS_I32_V1 | SPACE | [Contract](../science_library/specs/SPACE_WEIGHTED_LINEAR_STATS_I32_V1.json) |
| SPACE_CATALOG_CHORD_MATCH_I32_V1 | SPACE | [Contract](../science_library/specs/SPACE_CATALOG_CHORD_MATCH_I32_V1.json) |
| SPACE_CONVOLUTION_F32_V1 | SPACE | [Contract](../science_library/specs/SPACE_CONVOLUTION_F32_V1.json) |
| SPACE_CROSS_CORRELATION_F32_V1 | SPACE | [Contract](../science_library/specs/SPACE_CROSS_CORRELATION_F32_V1.json) |
| SPACE_NORMALIZED_CORRELATION_F32_V1 | SPACE | [Contract](../science_library/specs/SPACE_NORMALIZED_CORRELATION_F32_V1.json) |
| SPACE_FFT_COMPLEX_F32_V1 | SPACE | [Contract](../science_library/specs/SPACE_FFT_COMPLEX_F32_V1.json) |
| SPACE_WEIGHTED_LINEAR_FIT_F32_V1 | SPACE | [Contract](../science_library/specs/SPACE_WEIGHTED_LINEAR_FIT_F32_V1.json) |
| SPACE_CARTESIAN_TRANSFORM_F32_V1 | SPACE | [Contract](../science_library/specs/SPACE_CARTESIAN_TRANSFORM_F32_V1.json) |
| SPACE_TRAPEZOID_F32_V1 | SPACE | [Contract](../science_library/specs/SPACE_TRAPEZOID_F32_V1.json) |
| SPACE_NBODY_ACCELERATION_F32_V1 | SPACE | [Contract](../science_library/specs/SPACE_NBODY_ACCELERATION_F32_V1.json) |
| SPACE_LEAPFROG_DRIFT_F32_V1 | SPACE | [Contract](../science_library/specs/SPACE_LEAPFROG_DRIFT_F32_V1.json) |
| SPACE_CENTROID_F32_V1 | SPACE | [Contract](../science_library/specs/SPACE_CENTROID_F32_V1.json) |
| SPACE_PERIODOGRAM_F32_V1 | SPACE | [Contract](../science_library/specs/SPACE_PERIODOGRAM_F32_V1.json) |
| SPACE_GWOSC_FFT256_V1 | SPACE | [Contract](../science_library/specs/SPACE_GWOSC_FFT256_V1.json) |
| SPACE_GWOSC_CONVOLUTION_V1 | SPACE | [Contract](../science_library/specs/SPACE_GWOSC_CONVOLUTION_V1.json) |
| SPACE_GWOSC_XCORR_V1 | SPACE | [Contract](../science_library/specs/SPACE_GWOSC_XCORR_V1.json) |
| SPACE_GWOSC_NXCORR_V1 | SPACE | [Contract](../science_library/specs/SPACE_GWOSC_NXCORR_V1.json) |
| SPACE_EXOPLANET_EARTHSIZE_FILTER_V1 | SPACE | [Contract](../science_library/specs/SPACE_EXOPLANET_EARTHSIZE_FILTER_V1.json) |
| SPACE_GWOSC_WELCH_PSD_V1 | SPACE | [Contract](../science_library/specs/SPACE_GWOSC_WELCH_PSD_V1.json) |
| SPACE_GWOSC_WHITENING_V1 | SPACE | [Contract](../science_library/specs/SPACE_GWOSC_WHITENING_V1.json) |
| SPACE_LOMB_SCARGLE_F32_V1 | SPACE | [Contract](../science_library/specs/SPACE_LOMB_SCARGLE_F32_V1.json) |
| SPACE_BLS_BINNED_F32_V1 | SPACE | [Contract](../science_library/specs/SPACE_BLS_BINNED_F32_V1.json) |
| SPACE_IMAGE_PEAK_MASK_F32_V1 | SPACE | [Contract](../science_library/specs/SPACE_IMAGE_PEAK_MASK_F32_V1.json) |
| SPACE_SED_TEMPLATE_CHI2_F32_V1 | SPACE | [Contract](../science_library/specs/SPACE_SED_TEMPLATE_CHI2_F32_V1.json) |
| SPACE_SPHERICAL_CARTESIAN_F32_V1 | SPACE | [Contract](../science_library/specs/SPACE_SPHERICAL_CARTESIAN_F32_V1.json) |
| SPACE_KEPLER_RK4_F32_V1 | SPACE | [Contract](../science_library/specs/SPACE_KEPLER_RK4_F32_V1.json) |
| SPACE_BOOTSTRAP_MEAN_VARIANCE_F32_V1 | SPACE | [Contract](../science_library/specs/SPACE_BOOTSTRAP_MEAN_VARIANCE_F32_V1.json) |
| SPACE_SIGMA_CLIP_STATS_F32_V1 | SPACE | [Contract](../science_library/specs/SPACE_SIGMA_CLIP_STATS_F32_V1.json) |
| SPACE_IMAGE_SEGMENTATION_U32_V1 | SPACE | [Contract](../science_library/specs/SPACE_IMAGE_SEGMENTATION_U32_V1.json) |
| SPACE_BOOTSTRAP_PERCENTILE_CI_F32_V1 | SPACE | [Contract](../science_library/specs/SPACE_BOOTSTRAP_PERCENTILE_CI_F32_V1.json) |
| SPACE_MONTE_CARLO_TAIL_U32_V1 | SPACE | [Contract](../science_library/specs/SPACE_MONTE_CARLO_TAIL_U32_V1.json) |
| SPACE_SED_TWO_TEMPLATE_NNLS_F32_V1 | SPACE | [Contract](../science_library/specs/SPACE_SED_TWO_TEMPLATE_NNLS_F32_V1.json) |
| SPACE_BACKGROUND_BILINEAR_F32_V1 | SPACE | [Contract](../science_library/specs/SPACE_BACKGROUND_BILINEAR_F32_V1.json) |
| SPACE_COMPONENT_GRAPH_MERGE_U32_V1 | SPACE | [Contract](../science_library/specs/SPACE_COMPONENT_GRAPH_MERGE_U32_V1.json) |
| SPACE_SEGMENT_CATALOG_F32_V1 | SPACE | [Contract](../science_library/specs/SPACE_SEGMENT_CATALOG_F32_V1.json) |
| SPACE_J2_ACCELERATION_F32_V1 | SPACE | [Contract](../science_library/specs/SPACE_J2_ACCELERATION_F32_V1.json) |
| SPACE_ADAPTIVE_ORBIT_RK4_F32_V1 | SPACE | [Contract](../science_library/specs/SPACE_ADAPTIVE_ORBIT_RK4_F32_V1.json) |
| SPACE_ORBIT_DIAGNOSTICS_F32_V1 | SPACE | [Contract](../science_library/specs/SPACE_ORBIT_DIAGNOSTICS_F32_V1.json) |
| SPACE_MULTIHARMONIC_PERIODOGRAM_F32_V1 | SPACE | [Contract](../science_library/specs/SPACE_MULTIHARMONIC_PERIODOGRAM_F32_V1.json) |
| SPACE_PHASE_DISPERSION_F32_V1 | SPACE | [Contract](../science_library/specs/SPACE_PHASE_DISPERSION_F32_V1.json) |
| SPACE_PSF_WEIGHTED_SCAN_F32_V1 | SPACE | [Contract](../science_library/specs/SPACE_PSF_WEIGHTED_SCAN_F32_V1.json) |
| SPACE_TEMPLATE_NNLS_F32_V1 | SPACE | [Contract](../science_library/specs/SPACE_TEMPLATE_NNLS_F32_V1.json) |
| SPACE_IDW_INTERPOLATE_F32_V1 | SPACE | [Contract](../science_library/specs/SPACE_IDW_INTERPOLATE_F32_V1.json) |
| SPACE_MASKED_MEDIAN_MESH_F32_V1 | SPACE | [Contract](../science_library/specs/SPACE_MASKED_MEDIAN_MESH_F32_V1.json) |
| SPACE_BIWEIGHT_STATS_F32_V1 | SPACE | [Contract](../science_library/specs/SPACE_BIWEIGHT_STATS_F32_V1.json) |
| SPACE_HALF_SAMPLE_MODE_F32_V1 | SPACE | [Contract](../science_library/specs/SPACE_HALF_SAMPLE_MODE_F32_V1.json) |
| SPACE_SOURCE_NOISE_MAP_F32_V1 | SPACE | [Contract](../science_library/specs/SPACE_SOURCE_NOISE_MAP_F32_V1.json) |
| SPACE_LINEAR_FLUX_COVARIANCE_F32_V1 | SPACE | [Contract](../science_library/specs/SPACE_LINEAR_FLUX_COVARIANCE_F32_V1.json) |
| SPACE_CORRELATED_TEMPLATE_FIT_F32_V1 | SPACE | [Contract](../science_library/specs/SPACE_CORRELATED_TEMPLATE_FIT_F32_V1.json) |
| SPACE_JOINT_TEMPLATE_GLS_F32_V1 | SPACE | [Contract](../science_library/specs/SPACE_JOINT_TEMPLATE_GLS_F32_V1.json) |
| SPACE_ADAPTIVE_NBODY_RK4_F32_V1 | SPACE | [Contract](../science_library/specs/SPACE_ADAPTIVE_NBODY_RK4_F32_V1.json) |
| SPACE_NBODY_INVARIANTS_F32_V1 | SPACE | [Contract](../science_library/specs/SPACE_NBODY_INVARIANTS_F32_V1.json) |
| SPACE_SWEPT_SPHERE_ENCOUNTER_F32_V1 | SPACE | [Contract](../science_library/specs/SPACE_SWEPT_SPHERE_ENCOUNTER_F32_V1.json) |
| SPACE_LINEAR_KALMAN_STEP_F32_V1 | SPACE | [Contract](../science_library/specs/SPACE_LINEAR_KALMAN_STEP_F32_V1.json) |
| SPACE_RTS_SMOOTHER_STEP_F32_V1 | SPACE | [Contract](../science_library/specs/SPACE_RTS_SMOOTHER_STEP_F32_V1.json) |
| SPACE_IAU2006_BIAS_PRECESSION_F32_V1 | SPACE | [Contract](../science_library/specs/SPACE_IAU2006_BIAS_PRECESSION_F32_V1.json) |
| SPACE_ELLIPTIC_KEPLER_STATE_F32_V1 | SPACE | [Contract](../science_library/specs/SPACE_ELLIPTIC_KEPLER_STATE_F32_V1.json) |
| SPACE_HYPERBOLIC_KEPLER_STATE_F32_V1 | SPACE | [Contract](../science_library/specs/SPACE_HYPERBOLIC_KEPLER_STATE_F32_V1.json) |
| SPACE_PARABOLIC_BARKER_STATE_F32_V1 | SPACE | [Contract](../science_library/specs/SPACE_PARABOLIC_BARKER_STATE_F32_V1.json) |
| SPACE_CROSS_SPECTRAL_COHERENCE_F32_V1 | SPACE | [Contract](../science_library/specs/SPACE_CROSS_SPECTRAL_COHERENCE_F32_V1.json) |
| SPACE_GNOMONIC_PROJECT_F32_V1 | SPACE | [Contract](../science_library/specs/SPACE_GNOMONIC_PROJECT_F32_V1.json) |
| SPACE_TANGENT_TO_UNIT_VECTOR_F32_V1 | SPACE | [Contract](../science_library/specs/SPACE_TANGENT_TO_UNIT_VECTOR_F32_V1.json) |
| SPACE_SIP_FORWARD_F32_V1 | SPACE | [Contract](../science_library/specs/SPACE_SIP_FORWARD_F32_V1.json) |
| BIO_SMITH_WATERMAN_I32_V1 | BIO | [Contract](../science_library/specs/BIO_SMITH_WATERMAN_I32_V1.json) |
| BIO_CONTACT_COUNTS_I32_V1 | BIO | [Contract](../science_library/specs/BIO_CONTACT_COUNTS_I32_V1.json) |
| BIO_KMER_COUNTS_U32_V1 | BIO | [Contract](../science_library/specs/BIO_KMER_COUNTS_U32_V1.json) |
| CHEM_PAIR_DISTANCE_SQUARED_I64_V1 | CHEM | [Contract](../science_library/specs/CHEM_PAIR_DISTANCE_SQUARED_I64_V1.json) |
| CHEM_RADIAL_HISTOGRAM_I64_V1 | CHEM | [Contract](../science_library/specs/CHEM_RADIAL_HISTOGRAM_I64_V1.json) |
| CHEM_LENNARD_JONES_PAIR_F32_V1 | CHEM | [Contract](../science_library/specs/CHEM_LENNARD_JONES_PAIR_F32_V1.json) |
| PHYSICS_ISING_OBSERVABLES_I32_V1 | PHYSICS | [Contract](../science_library/specs/PHYSICS_ISING_OBSERVABLES_I32_V1.json) |
| PHYSICS_HEAT_STEP_F32_V1 | PHYSICS | [Contract](../science_library/specs/PHYSICS_HEAT_STEP_F32_V1.json) |
| SIGNAL_FIR_ACCUMULATE_I16_V1 | SIGNAL | [Contract](../science_library/specs/SIGNAL_FIR_ACCUMULATE_I16_V1.json) |
| SIGNAL_LINEAR_RESAMPLE_F32_V1 | SIGNAL | [Contract](../science_library/specs/SIGNAL_LINEAR_RESAMPLE_F32_V1.json) |
| ENGINEERING_CSR_MATVEC_I32_V1 | ENGINEERING | [Contract](../science_library/specs/ENGINEERING_CSR_MATVEC_I32_V1.json) |
| ENGINEERING_ORIENT2D_I32_V1 | ENGINEERING | [Contract](../science_library/specs/ENGINEERING_ORIENT2D_I32_V1.json) |
| ENGINEERING_DENSE_MATMUL_F32_V1 | ENGINEERING | [Contract](../science_library/specs/ENGINEERING_DENSE_MATMUL_F32_V1.json) |
| RT_STATIC_NEAREST_TRIANGLE_HIT_V1 | RT | [Contract](../science_library/specs/RT_STATIC_NEAREST_TRIANGLE_HIT_V1.json) |
| RT_DYNAMIC_NEAREST_TRIANGLE_HIT_V1 | RT | [Contract](../science_library/specs/RT_DYNAMIC_NEAREST_TRIANGLE_HIT_V1.json) |
| ASTRO_SPACE_GENERIC | SPACE | UNAVAILABLE — historical/runtime-only entry |
| ASTRO_SIGNAL_GENERIC | SIGNAL | UNAVAILABLE — historical/runtime-only entry |
| ASTRO_BIO_GENERIC | BIO | UNAVAILABLE — historical/runtime-only entry |
| ASTRO_PHYSICS_GENERIC | PHYSICS | UNAVAILABLE — historical/runtime-only entry |
| ASTRO_CHEM_GENERIC | CHEM | UNAVAILABLE — historical/runtime-only entry |
| SPACE_GAIA_NEIGHBORS_V1 | SPACE | UNAVAILABLE — historical/runtime-only entry |
| SPACE_EXOPLANET_PERIOD_HIST_V1 | SPACE | UNAVAILABLE — historical/runtime-only entry |
| SPATIAL_NEAREST_TRIANGLE_HIT | MULTI | UNAVAILABLE — historical/runtime-only entry |
| SPATIAL_ANY_HIT_OCCLUSION | MULTI | UNAVAILABLE — historical/runtime-only entry |
| SPATIAL_SEGMENT_VISIBILITY | MULTI | UNAVAILABLE — historical/runtime-only entry |
| SPATIAL_FIRST_SURFACE_DISTANCE | MULTI | UNAVAILABLE — historical/runtime-only entry |
| SPATIAL_RADIUS_WEIGHT_SUM | MULTI | UNAVAILABLE — historical/runtime-only entry |
| SPATIAL_BOUNDED_NEAREST_POINT | MULTI | UNAVAILABLE — historical/runtime-only entry |

## Planned composition families

Reductions, convolution, correlation, normalized correlation, FFT/transforms, sparse and dense matrices, histogram, pairwise distance, neighbor search, geometry, stencils, integration, iterative solvers, sorting/filtering/scans, gather/scatter, tensor operations and spatial/ray traversal. Presence in this roadmap does not assert that every family or scientific application is implemented.
