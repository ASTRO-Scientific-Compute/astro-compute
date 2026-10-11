"""Single-template generalized least squares with supplied correlated noise."""
SOURCES={'correlated_template':('SciPy full covariance least squares and absolute parameter covariance','https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.curve_fit.html','BSD documentation; original independent ASTRO GLS implementation')}
DEFINITIONS=[('SPACE_CORRELATED_TEMPLATE_FIT_F32_V1',67,'correlated_template','Correlated single-template amplitude fit',
 'Fit a fixed PSF or signal template using positive diagonal plus low-rank covariance.',
 'C=diag(D)+U^TU; a=(t^T C^-1 y)/(t^T C^-1 t); variance=1/(t^T C^-1 t); chi2=r^T C^-1 r. Cholesky solves and positive augmented quadratic, ordered RN32.',
 'binary32-hex flux,template,diagonal_variance[B,N],factors[B,K,N];B1..64,N1..128,K0..8;B*N*(K+1)^2<=131072;D>0;finite inputs/intermediates;fixed absolute covariance.',
 'B x [u32 status,f32 amplitude,amplitude_variance,chi_squared,information,u32 factor_count];status1 zero information,status2 rejected factor pivot;failed records retain only status.',
 'whole independent template fits, no split matrix/reduction records','POSSIBLE')]
