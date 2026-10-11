# Joint correlated template amplitudes — v1.17.27

Primary references read 2026-10-03: [statsmodels GLS, design matrix and parameter covariance](https://www.statsmodels.org/stable/generated/statsmodels.regression.linear_model.GLS.html), [SciPy curve_fit, full covariance and absolute_sigma](https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.curve_fit.html). The model uses supplied absolute covariance and an explicit design matrix. No intercept is automatically added; a caller can supply a constant template. No residual variance rescaling is applied. The bounded finite arithmetic below is an original ASTRO implementation; no external implementation copied or runtime dependency added.

## Model and shape

`SPACE_JOINT_TEMPLATE_GLS_F32_V1`, opcode68. Fit signed amplitudes a in y=Xa+noise for M fixed templates (columns of X) and fixed C=diag(D)+U^TU. In real arithmetic H=X^T C^-1 X, a=H^-1 X^T C^-1 y, absolute conditional Cov(a)=H^-1 and chi_squared=(y-Xa)^T C^-1(y-Xa).

Binary32-hex flux and diagonal_variance[B,N], templates[B,M,N], factors[B,K,N]. B1..32, M2..5, M<=N<=64, K0..4; B*N*(K+M+1)^2<=131072. K0 uses an empty list per record. Dimensions are uniform. D strictly positive. All inputs and executed intermediates finite; preparation rejects overflow/nonfinite values before dispatch. Partition only by complete fit records.

Templates, positions, noise factors and D are conditional inputs. The signed fit permits negative amplitudes. It does not perform NNLS, automatic deblending, source detection, PSF/position estimation or physical calibration. Data-dependent estimated weights require separate inference analysis. A supplied constant column can represent an additive nuisance background; the program does not infer one.

## Exact finite arithmetic

RN is binary32 round-to-nearest ties-to-even after every add/subtract/multiply/divide/sqrt, gradual underflow and canonical +0. No FMA/reassociation. Sums begin at +0 and add increasing indices. CPU uses exact Fraction rounding independently of GPU software binary32.

Set d_i=RN(1/D_i). For lower-triangle indices a>=b, form G_ab=RN(delta_ab+sum_i RN(RN(U_ai*d_i)*U_bi)); mirror the lower triangle. A guarded Cholesky of any matrix A uses v=A_ab followed by sequential RN(v-RN(L_aj*L_bj)), j=0..b-1. Diagonal v must exceed RN(A_aa*2^-16); otherwise reject. Successful diagonals are RN(sqrt(v)); off-diagonals are RN(v/L_bb). This same relative pivot rule applies separately to the factor matrix G and model matrix H.

For each template v, then y, compute b_a=sum_i RN(RN(U_ai*d_i)*v_i). Solve Gz=b with forward substitution Lw=b and backward L^Tz=w. Each dot product is implemented as sequential subtractions followed by one RN division, with increasing j; backward row order decreases. Define q_i=RN(v_i-sum_a RN(U_ai*z_a)), accumulating the projection before its single subtraction.

Define augmented inner(a,b): start with sum_i RN(RN(q_ai*d_i)*q_bi), then add RN(z_aj*z_bj) in increasing j. Compute only H's lower triangle as inner(template_a,template_b), and mirror it. The right-hand side is inner(template_a,y). Cholesky H, then solve for a with the same substitutions.

The augmented representation is the bilinear extension of q^T D^-1 q+z^T z: in real arithmetic it equals v^T C^-1 w. This avoids subtracting large nonnegative covariance quadratics. It does not eliminate conditioning problems; the numerical pivot guards remain mandatory.

For covariance, obtain columns S_a of L_H^-1 by forward substitution on each unit vector. Compute Cov_ab=sum_j RN(S_aj*S_bj) for a>=b, then mirror it. This gives an exactly symmetric output; in real arithmetic it is H^-1. It is not separately rescaled by chi_squared or sample count.

Residual factors z_r,j=RN(z_y,j-sum_a RN(a_a*z_a,j)). At each sample form residual=RN(y_i-sum_a RN(a_a*X_ia)), then q_r,i=RN(residual-sum_j RN(U_ji*z_r,j)). Chi_squared starts with sum_i RN(RN(q_r,i*d_i)*q_r,i) and then adds RN(z_r,j*z_r,j).

## Output and failures

Per record 2+M+M*M words: `[u32 status,f32 amplitudes[M],covariance[M,M] row-major,chi_squared]`. Status0 succeeds, status1 rejects a model pivot (zero/rank-deficient/poorly conditioned information), status2 rejects a factor pivot. Failure outputs retain only the status and zero every other word. There is no pseudoinverse, implicit regularization, nonnegative clamp or silent fallback.

Analytic golden: D=[1,1,1,1], U=[[1,1,1,0]], templates [[1,1,0,0],[1,1,0,1]], y=[6,4,0,2]. G=4 and L_G=2. H=[[1,1],[1,2]], L_H=[[1,0],[1,1]], right-hand side=[5,7]. Amplitudes=[3,2], covariance=[[2,-1],[-1,1]], residual=[1,-1,0,0], chi_squared=2. Every arithmetic step in this example is exactly representable. The second golden record negates y and amplitudes while preserving covariance/chi_squared. Golden words were fixed before GPU execution.

## Validation and integration

Every output byte matches the independent Fraction CPU oracle, including failure records, off-diagonal covariance, and partition reassembly. Separate float64 diagnostics build the full N x N covariance and solve full matrix systems with NumPy. Their tolerances are scientific diagnostics, never byte tolerance. Tests cover degenerate and near-degenerate models, correlated and K0 noise, redundant factors, zero/negative/subnormal signals, signed zero, exact perfect fits and maximum bounds. Actual corrupted GPU output must fail the 0-bit gate.

The adapter takes the existing verified GPU noise-map output, explicit unique coordinates, template arrays and covariance factors. All selected pixels need usable positive variance. Upstream input/output, coordinates and job hashes are preserved. A three-stage integration test runs noise maps, existing single-template GLS and new joint GLS. On the same controlled data the one-template amplitude is5; the joint amplitudes are3 and2. This demonstrates how adding a supplied model column changes the fitted model, not a universal accuracy improvement or automatic source separation.

All templates and covariance values are supplied; multiple sources beyond five, covariance estimation, automatic deblending, position fitting and calibrated significance remain open. QUICK is informational and capped at60 seconds total per MathSpec. No release performance or energy claim follows without paired A/B evidence.
