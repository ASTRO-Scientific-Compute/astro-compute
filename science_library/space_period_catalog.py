"""Explicit multi-harmonic and phase-dispersion scientific contracts."""
SOURCES={
 'multiharmonic':('Astropy multi-term Lomb-Scargle model and standard normalization','https://docs.astropy.org/en/stable/timeseries/lombscargle.html','BSD documentation; original implementation, no copied code'),
 'pdm':('Stellingwerf 1978 Phase Dispersion Minimization; PyAstronomy PDM documentation','https://pyastronomy.readthedocs.io/en/latest/pyTimingDoc/pyPDMDoc/classes.html','Published method only; independent fixed-bin implementation'),
}
DEFINITIONS=[
 ('SPACE_MULTIHARMONIC_PERIODOGRAM_F32_V1',57,'multiharmonic','Weighted multiple-harmonic periodogram and fit','Search irregular light curves with a floating mean plus two to four Fourier harmonics.',
  'Model=offset+sum_k(c_k*cos(2*pi*k*f*t)+s_k*sin(2*pi*k*f*t)); ordered RN32 weighted normal equations for centered y, Cholesky solve, P=(chi2_constant-chi2_fit)/chi2_constant. Exact operation graph and conditioning gate specified in contract.',
  'encoding=binary32-hex;samples[N,3]=(relative_time,value,inverse_variance);harmonics H2..4;N(2H+2)..256;frequencies[F]1..128>0;weights>=0;abs(RN32(RN32(t*f)*k))<=256;N*F*(2H+1)^2<=2097152;finite RN32 intermediates.',
  'F x [u32 status,f32 power,chi2,offset,c1,s1,...,cH,sH]; status1 zero weight/variance,2 Cholesky pivot<=RN32(weight_sum*2^-16), failed numeric fields0. No analytical false-alarm, multiband or covariance claim; RN32 powers are not clipped.',
  'independent trial frequencies retaining the complete ordered observation set','STRONG_CANDIDATE'),
 ('SPACE_PHASE_DISPERSION_F32_V1',58,'pdm','Fixed-bin phase-dispersion minimization','Search non-sinusoidal variability using phase-bin variance at supplied integer-tick trial periods.',
  'bin=floor((time mod period)*bins/period); theta=(within_bin_SSE/(N-occupied_bins))/(global_SSE/(N-1)); bin means and both residual sums follow original observation order.',
  'encoding=binary32-hex;times[N]integer ticks0..10000000,flux[N]finite binary32,N3..4096;periods[F]integer1..1000000,F1..128;bins2..64;N*F<=262144;equal observation weights.',
  'F x [u32 status,f32 theta,global_variance,within_variance,u32 occupied_bins,u32 residual_dof]; status1 zero rounded global variance,2 fewer than2 occupied bins or no residual degrees of freedom; failed fields0. Lower theta is better; no overlapping covers/bin merging/automatic significance.',
  'trial periods with full ordered light curve; observations cannot be independently sharded without a new reduction contract','NONE'),
]
