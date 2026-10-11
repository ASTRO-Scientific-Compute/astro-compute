"""Joint signed template amplitudes with absolute correlated covariance."""
SOURCES={'joint_gls':('statsmodels GLS model and parameter covariance','https://www.statsmodels.org/stable/generated/statsmodels.regression.linear_model.GLS.html','BSD documentation; original independent ASTRO implementation')}
DEFINITIONS=[('SPACE_JOINT_TEMPLATE_GLS_F32_V1',68,'joint_gls','Joint correlated template fit',
 'Fit two to five fixed overlapping templates or supplied background columns jointly with correlated noise.',
 'C=diag(D)+U^TU;H=X^T C^-1 X;a=H^-1 X^T C^-1 y;Cov(a)=H^-1;chi2=r^T C^-1 r. Guarded Cholesky and ordered RN32 positive augmented products.',
 'binary32-hex flux,diagonal_variance[B,N],templates[B,M,N],factors[B,K,N];B1..32,M2..5,N=M..64,K0..4;B*N*(K+M+1)^2<=131072;D>0;finite inputs/intermediates;fixed absolute covariance.',
 'B x [u32 status,f32 amplitudes[M],covariance[M,M] row-major,chi_squared];status1 rejected model pivot,status2 rejected factor pivot;failure has only status and zero remaining words.',
 'whole independent multi-template fits, no split covariance/reduction records','POSSIBLE')]
