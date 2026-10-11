# Correlated single-template amplitude fit — v1.17.26

Primary references read 2026-10-03: [SciPy curve_fit, full covariance and absolute_sigma](https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.curve_fit.html), [statsmodels GLS](https://www.statsmodels.org/stable/generated/statsmodels.regression.linear_model.GLS.html). Original ASTRO implementation of generalized least squares; no external implementation copied. No SciPy/statsmodels runtime dependency is introduced.

## Model and input

`SPACE_CORRELATED_TEMPLATE_FIT_F32_V1`, opcode67. Fit one signed amplitude a in y=a*t+noise with fixed supplied covariance C=diag(D)+U^TU. The background is already subtracted. D is strictly positive; factors U are fixed, standardized independent latent-mode loadings. No intercept, position, shape, covariance or gain is fitted. Absolute covariance is used; parameter variance is not rescaled by residual chi-square.

`encoding=binary32-hex`, finite `flux[B,N]`, `template[B,N]`, `diagonal_variance[B,N]`, `factors[B,K,N]`; B1..64,N1..128,K0..8 and B*N*(K+1)^2<=131072. K0 uses an empty list per row. All rows have the same dimensions. Every executed intermediate must be finite; otherwise CPU preparation rejects before dispatch. Partition only by whole fits.

Over real arithmetic, information=t^T C^-1 t, a=(t^T C^-1 y)/information, variance(a)=1/information, residual quadratic=r^T C^-1 r. The returned chi_squared is this quadratic; no chi-square distribution, significance or coverage is asserted without separately validated noise assumptions.

## Explicit finite arithmetic

RN means round-to-nearest ties-to-even binary32 after each add/subtract/multiply/divide/sqrt, gradual underflow and canonical +0; no reassociation/FMA. All sums are increasing-index ordered RN additions initialized to +0. CPU arithmetic uses exact Fraction rounding, independent of the GPU software-binary32 implementation.

Let d_i=RN(1/D_i). Build a symmetric KxK matrix G by evaluating only its lower triangle and copying it: G_ab=RN(delta_ab + sum_i RN(RN(U_ai*d_i)*U_bi)). Form b_t,a=sum_i RN(RN(U_ai*d_i)*t_i), and similarly b_y. Obtain G=L L^T using ordinary lower-triangular Cholesky with sequential subtractive dot products. For a diagonal element p=RN(G_aa-sum_j RN(L_aj^2)), reject if p<=RN(G_aa*2^-16); otherwise L_aa=RN(sqrt(p)). Off-diagonal L_ab is RN((G_ab-sum_j RN(L_aj*L_bj))/L_bb). Subtractions occur one at a time in increasing j, not as one separately accumulated sum. The relative pivot guard is part of this bounded numerical contract.

Use forward and backward triangular substitution, each with increasing index order in its dot product and a single RN division after sequential subtractions, to solve G z_t=b_t and G z_y=b_y. Compute q_t,i=RN(t_i-sum_k RN(U_ki*z_t,k)), q_y similarly. Here each sum is accumulated first, then subtracted once.

Use the positive augmented representation of the covariance quadratic:

- information = sum_i RN(RN(q_t,i*d_i)*q_t,i), followed by additions of RN(z_t,k*z_t,k).
- numerator = sum_i RN(RN(q_t,i*d_i)*q_y,i), followed by additions of RN(z_t,k*z_y,k).
- amplitude=RN(numerator/information); variance=RN(1/information).
- z_r,k=RN(z_y,k-RN(amplitude*z_t,k)); r_i=RN(y_i-RN(amplitude*t_i)); q_r,i=RN(r_i-sum_k RN(U_ki*z_r,k)).
- chi_squared=sum_i RN(RN(q_r,i*d_i)*q_r,i), followed by additions of RN(z_r,k*z_r,k).

This augmented form equals v^T C^-1 v in real arithmetic: z solves (I+U D^-1 U^T)z=U D^-1 v, q=v-U^T z, and q^T D^-1 q+z^T z equals the covariance quadratic. It avoids subtracting two large nonnegative quadratics. In finite arithmetic this specified graph, rather than an arbitrary matrix-inverse implementation, defines the exact bytes. For K0 all factor operations disappear.

## Output and failure

Six words per fit: `[u32 status,f32 amplitude,amplitude_variance,chi_squared,information,u32 factor_count]`. Status0 succeeds. Status1 means rounded template information is zero (zero/tiny template); status2 means the factor Cholesky pivot guard rejected the solve. Failure records contain only the status and five zero words. No pseudoinverse, hidden diagonal regularization, nonnegative amplitude clamp or silent convergence fallback is used.

Analytic example: D=[1,1,1],U=[[1,1,1]],t=[1,1,1],y=[2,3,4]. G=4,L=2,z_t=0.75,z_y=2.25,information0.75,amplitude3,variance RN(4/3)=0x3faaaaab,chi_squared2,factor_count1. Doubling y gives amplitude6,chi_squared8 with unchanged information and variance. These golden words are fixed before GPU measurements.

## Validation and use

Every output word must match the independent CPU oracle exactly. Separately, float64 diagnostics construct the full covariance C and use NumPy linear solves, rather than reusing the augmented implementation, to check amplitude, variance, residual quadratic and information. Diagnostics do not relax the 0-bit gate. Edge cases include K0, zero template, collinear/redundant factors, pivot rejection, negative amplitude, subnormal input, signed zero and maximum dimensions/work.

An adapter consumes verified GPU noise maps from v1.17.25 and explicitly supplied unique pixel coordinates, templates and factors. All selected pixels must have usable positive variance. No masked-pixel padding or inferred covariance is permitted. The integration test uses real GPU variance outputs and demonstrates different diagonal-only versus correlated fit amplitudes on the same controlled data. Differences illustrate the specified noise model, not a universal accuracy or performance improvement.

The covariance and template are conditional inputs. Observed-signal-derived Poisson variance can make weights data-dependent; statistical optimality, unbiasedness and significance then require separate analysis. General multi-template GLS, automatic PSF estimation, position fitting and covariance calibration remain open. COLD-ZERO, full QUICK<=60s per MathSpec and INFORMATIONAL-only quick performance remain mandatory.
