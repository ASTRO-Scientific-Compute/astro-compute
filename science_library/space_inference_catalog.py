"""Source-backed inferential SPACE contracts, specified before implementation."""
SOURCES = {
    'percentile_ci': ('SciPy bootstrap percentile confidence intervals', 'https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.bootstrap.html', 'BSD-3-Clause documentation; equations only, original implementation'),
    'random_tail': ('SciPy randomized permutation p-value, inclusive upper tail and plus-one correction', 'https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.permutation_test.html', 'BSD-3-Clause documentation; no code copied'),
    'sed_pair': ('EAZY authors manual: analytic nonnegative two-template fits', 'https://github.com/gbrammer/eazy-photoz/blob/master/doc/eazy_manual.tex', 'Published method only; no EAZY source copied'),
}
DEFINITIONS = [
    ('SPACE_BOOTSTRAP_PERCENTILE_CI_F32_V1', 48, 'percentile_ci',
     'Two-sided percentile bootstrap confidence interval',
     'Convert supplied bootstrap-statistic replicates into uncertainty intervals for astronomical estimates.',
     'alpha=RN32((1-confidence)/2); return Q(alpha),Q(1-alpha); Q uses sorted values, h=RN32((N-1)*q),j=floor(h),g=RN32(h-j),RN32(RN32((1-g)*x[j])+RN32(g*x[min(j+1,N-1)])); exact rank returns x[j].',
     'encoding=binary32-hex; replicates[B,N], B1..128,N2..512; finite confidence in(0,1]; finite RN32 intermediates.',
     'B x[lower,upper] binary32; type7 linear percentile interval; caller supplies valid bootstrap replicates; no BCa correction or guaranteed finite-sample coverage.',
     'whole replicate-distribution rows; never split a quantile across independent shards', 'NONE'),
    ('SPACE_MONTE_CARLO_TAIL_U32_V1', 49, 'random_tail',
     'Exact inclusive Monte Carlo upper-tail counts',
     'Evaluate simulated-null significance of observed search statistics; suitable for periodogram maxima when simulations use the same observing/search setup.',
     'b=sum(null[j]>=observed[i]); output[b,N,b+1,N+1]; conservative randomized upper-tail estimate=(b+1)/(N+1).',
     'encoding=binary32-hex; observed[M]1..4096,null_statistics[N]1..65535; M*N<=4194304; null_model_id nonempty text<=256; search_grid_sha25664 lowercase hex chars; inputs finite.',
     'M x[u32 extreme_count,u32 simulations,u32 probability_numerator,u32 probability_denominator]; exact numeric comparisons, ties included; no RNG, null-model validation or posterior probability claim.',
     'observed thresholds with complete null distribution; to merge null shards sum b and N then apply plus-one exactly once', 'NONE'),
    ('SPACE_SED_TWO_TEMPLATE_NNLS_F32_V1', 50, 'sed_pair',
     'Two-template nonnegative weighted spectral fit',
     'Fit mixtures of two supplied bandpass-integrated SED templates for each source and template pair.',
     'Minimize sum(w*(y-a*t0-b*t1)^2), a,b>=0; ordered RN32 Gram/RHS; enumerate origin, each nonnegative axis optimum and nonnegative interior solution; select lowest RN32 residual chi2, fixed tie order.',
     'encoding=binary32-hex; flux[O,K],weights[O,K],template_pairs[P,2,K]; O/P1..128,K2..64; O*P*K<=1048576; weights/templates>=0; finite RN32 intermediates.',
     'O*P x[status,a,b,chi2]; status0 accepted,1 Gram determinant<=RN32(2^-18*g00*g11) then three zeros; no inferred redshift/prior, no general N-template solve.',
     'independent object/template-pair fits retaining the full ordered band set', 'STRONG_CANDIDATE'),
]
