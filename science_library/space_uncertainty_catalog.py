"""Source Poisson variance and covariance-aware linear photometry."""
SOURCES={
    'source_noise':('Photutils total error: background variance plus source Poisson noise','https://photutils.readthedocs.io/en/stable/api/photutils.utils.calc_total_error.html','BSD documentation; original ASTRO implementation'),
    'linear_covariance':('NIST law of uncertainty propagation including covariance','https://physics.nist.gov/cuu/Uncertainty/combination.html','NIST reference equations; original ASTRO factorized implementation')}
DEFINITIONS=[
 ('SPACE_SOURCE_NOISE_MAP_F32_V1',65,'source_noise','Source Poisson plus background noise map',
  'Construct per-pixel total variance, error and diagonal photometry weights using explicit gain.',
  'Vs=RN(signal/gain) if both positive else0;V=RN(Vbackground+Vs);error=sqrt(V);weight=1/V. Negative signal and zero gain contribute no source Poisson variance.',
  'binary32-hex flat signal,background_variance,gain[N],valid[N] uint0/1;N1..65536;nonnegative background variance and gain;all finite with finite executed intermediates.',
  'N x [u32 status,f32 source_variance,total_variance,error,inverse_variance];status1 masked,status2 zero total variance, zero numerical output in both;status0 positive variance.',
  'whole independent image pixels with supplied calibration','POSSIBLE'),
 ('SPACE_LINEAR_FLUX_COVARIANCE_F32_V1',66,'linear_covariance','Covariance-aware fixed linear flux and uncertainty',
  'Propagate independent pixel variance and supplied low-rank correlated noise into a signed linear flux estimator.',
  'C=diag(D)+U^TU;F=sum(w*f);Vd=sum(w^2*D);Vc=sum_k(sum_i(w_i*U_ki))^2;V=Vd+Vc;error=sqrt(V);standardized_flux=F/error. Ordered per-operation RN32.',
  'binary32-hex flux,weights,diagonal_variance[B,N],factors[B,K,N];B1..128,N1..256,K0..16;B*N*(K+1)<=262144;D>=0;finite inputs/executed intermediates;zero weights omitted.',
  'B x [u32 status,active_count,f32 flux,diagonal_variance,correlated_variance,total_variance,error,standardized_flux];status1 no active coefficients all other0;status2 zero variance retains flux/count,others0.',
  'whole independent linear observation rows, never split ordered covariance reductions','POSSIBLE'),
]
