"""Published scientific methods with an explicit reproducible binary32 contract.

All implementations are original; cited software documents equations/use, not
bit identity to that package. ASTRO fixes operation order separately.
"""
SOURCES = {
    'conv': ('SciPy linear convolution', 'https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.convolve.html', 'BSD-3-Clause; reference only'),
    'corr': ('SciPy cross-correlation and matched filtering', 'https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.correlate.html', 'BSD-3-Clause; reference only'),
    'fft': ('FFTW one-dimensional DFT definition', 'https://www.fftw.org/fftw3_doc/The-1d-Discrete-Fourier-Transform-_0028DFT_0029.html', 'GPL-2.0-or-later; documentation only, no code copied'),
    'fit': ('GSL linear least squares', 'https://www.gnu.org/software/gsl/doc/html/lls.html', 'GPL-3.0-or-later; equations only'),
    'transform': ('Astropy CartesianRepresentation.transform', 'https://docs.astropy.org/en/stable/api/astropy.coordinates.CartesianRepresentation.html', 'BSD-3-Clause; reference only'),
    'quad': ('SciPy composite trapezoidal integration', 'https://docs.scipy.org/doc/scipy/reference/generated/scipy.integrate.trapezoid.html', 'BSD-3-Clause; reference only'),
    'gravity': ('GPU Gems 3 chapter 31: softened N-body gravity and leapfrog integration', 'https://developer.nvidia.com/gpugems/gpugems3/part-v-physics-simulation/chapter-31-fast-n-body-simulation-cuda', 'NVIDIA/author publication; equations only, no source copied'),
    'centroid': ('Photutils center-of-mass centroid', 'https://photutils.readthedocs.io/en/stable/api/photutils.centroids.centroid_com.html', 'BSD-3-Clause; reference only'),
    'periodogram': ('SciPy periodogram spectrum/density conventions', 'https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.periodogram.html', 'BSD-3-Clause; reference only'),
}
# Tuple structure matches the integer catalog. These IDs do not silently replace
# historical contracts with different boundary conditions/reduction orders.
DEFINITIONS = [
 ('SPACE_CONVOLUTION_F32_V1',14,'conv','Full linear convolution','Finite impulse response and time-series processing.',
  'y[i]=sum_j x[j]*h[i-j], out-of-range h=0; increasing j, RN32 product then RN32 addition',
  'encoding=binary32-hex; x[1..4096], kernel[1..1024]; N*M<=1048576', 'N+M-1 binary32 samples, zero padding; no normalization', 'output intervals sharing input and halo', 'STRONG_CANDIDATE'),
 ('SPACE_CROSS_CORRELATION_F32_V1',15,'corr','Real linear cross-correlation','Matched filtering and lagged time-series similarity.',
  'R[k]=sum_j x[j]*y[j-k], k=-(M-1)..N-1; zero padding; increasing j RN32 reduction',
  'encoding=binary32-hex; x,y lengths1..4096; N*M<=1048576', 'N+M-1 binary32 correlations in increasing lag order', 'lag intervals', 'STRONG_CANDIDATE'),
 ('SPACE_NORMALIZED_CORRELATION_F32_V1',16,'corr','Overlap-energy normalized real cross-correlation','Scale-normalized lag similarity; not mean-subtracted Pearson correlation.',
  'R[k]/sqrt(Ex[k]*Ey[k]); R,Ex,Ey sum only overlapping pairs; increasing j RN32; zero energy => status1, value0',
  'encoding=binary32-hex; x,y lengths1..4096; N*M<=1048576', 'per lag [u32 status,binary32 value]; status0 valid,1 zero denominator', 'lag intervals', 'STRONG_CANDIDATE'),
 ('SPACE_FFT_COMPLEX_F32_V1',17,'fft','Forward complex radix-2 FFT','Astronomical time-series and Fourier-domain processing.',
  'X[k]=sum_j x[j]*exp(-2*pi*i*j*k/N); unnormalized forward DFT; canonical radix2 DIT, bit-reversed input, increasing stage and butterfly; separately rounded complex products',
  'encoding=binary32-hex; signals[B,N,2]; N power of two2..256, B1..64; frozen RN32 twiddles', 'B records of2*N binary32 real/imag words in natural frequency order', 'whole transforms; no sample sharding', 'STRONG_CANDIDATE'),
 ('SPACE_WEIGHTED_LINEAR_FIT_F32_V1',18,'fit','Weighted straight-line fit','Fitted intercept and slope from astronomical measurements.',
  'S,Sx,Sy,Sxx,Sxy increasing sample sums; D=S*Sxx-Sx*Sx; slope=(S*Sxy-Sx*Sy)/D; intercept=(Sy-slope*Sx)/S; each operation RN32',
  'encoding=binary32-hex; samples[B,N,3]=(x,y,w), w>=0, N1..1024,B1..64', 'B x [status,intercept,slope]; status1 and positive zeros if S=0 or D<=0; no covariance/conditioning guarantee', 'independent fits', 'STRONG_CANDIDATE'),
 ('SPACE_CARTESIAN_TRANSFORM_F32_V1',19,'transform','Cartesian matrix coordinate transform','Apply a supplied astronomical frame matrix to Cartesian vectors.',
  'out[i,r]=sum_{k=0..2} matrix[r,k]*vectors[i,k]; increasing k RN32 dot product',
  'encoding=binary32-hex; vectors[N,3], matrix[3,3]; caller supplies correct frame and units', 'N x3 binary32 coordinates; no implicit RA/Dec, precession or epoch calculation', 'vector rows', 'STRONG_CANDIDATE'),
 ('SPACE_TRAPEZOID_F32_V1',20,'quad','Composite trapezoidal integration','Integration of tabulated spectra, fluxes and trajectories.',
  'I=sum_j ((x[j+1]-x[j])*(y[j]+y[j+1]))*0.5; increasing j RN32 operations; input order retained',
  'encoding=binary32-hex; curves[B,N,2]=(x,y), N1..4096,B1..64', 'B binary32 signed integrals; repeated/reversed abscissas allowed', 'whole curves; partial integrals need canonical reduction to retain byte identity', 'POSSIBLE'),
 ('SPACE_NBODY_ACCELERATION_F32_V1',21,'gravity','Softened all-pairs gravitational acceleration','Astrophysical direct gravity primitive in caller-consistent units, G absorbed in source mass parameter.',
  'a_i=sum_{j!=i} mu_j*(r_j-r_i)/(sum_k((r_jk-r_ik)^2)+epsilon_squared)^(3/2); canonical increasing j,k RN32; denominator=s*sqrt(s)',
  'encoding=binary32-hex; bodies[N,4]=(x,y,z,mu), N1..256, mu>=0, epsilon_squared>0', 'N x3 binary32 accelerations; no approximation, cutoff, periodic wrapping or time evolution', 'target bodies share all sources; RT cutoff would change gravity and is not applicable', 'POSSIBLE'),
 ('SPACE_LEAPFROG_DRIFT_F32_V1',22,'gravity','Staggered leapfrog kick and drift','One orbit/particle integration substep with supplied current acceleration.',
  'v_half_next=v_half_previous+dt*a(t); r_next=r(t)+dt*v_half_next; each operation RN32',
  'encoding=binary32-hex; states[N,9]=(r_xyz,v_half_xyz,a_xyz), dt>0; caller owns staggering, acceleration refresh and units', 'N x6 binary32 [r_next,v_half_next]; no hidden initial half kick or complete adaptive orbit solver', 'independent bodies per integration step', 'POSSIBLE'),
 ('SPACE_CENTROID_F32_V1',23,'centroid','Center-of-mass image centroid','Subpixel center estimate from nonnegative detector image cutouts.',
  'S=sum I, X=sum x*I,Y=sum y*I row-major RN32; centroid=(X/S,Y/S); S=0 => status1',
  'encoding=binary32-hex; images[B,H,W], B1..64,H,W1..64,I>=0', 'B x[status,x,y]; status1 => positive zeros; no source segmentation', 'image cutouts', 'POSSIBLE'),
 ('SPACE_PERIODOGRAM_F32_V1',24,'periodogram','Two-sided rectangular-window periodogram density','Spectral density estimate of sampled astronomical time series.',
  'P[k]=(Re FFT(x)[k]^2+Im FFT(x)[k]^2)/(fs*N); no detrending, rectangular window, canonical FFT and RN32 operations',
  'encoding=binary32-hex; signals[B,N] real samples, N power of two2..256,B1..64; fs>0', 'B xN binary32 two-sided density bins, units input_unit^2/frequency_unit; not Welch averaging or Lomb-Scargle', 'whole transforms', 'STRONG_CANDIDATE'),
]

PRECISION = ('Finite IEEE binary32 values, explicitly supplied as eight hex digits (encoding=binary32-hex). '
             'Every +,-,*,/,sqrt rounds to nearest ties-to-even; gradual underflow; canonical positive zero after arithmetic. '
             'No FMA or reassociation. Nonfinite inputs, intermediate overflow, division by zero and invalid roots reject the job on CPU before dispatch. '
             'Bit identity is to this specified rounded algorithm, not exact real arithmetic or other library reduction orders.')

SOURCES.update({
    'kmer': ('Jellyfish DNA k-mer counting and strand conventions','https://github.com/gmarcais/Jellyfish/blob/master/doc/Readme.md','BSD-3-Clause/GPL-3.0 by component; documentation only'),
    'lj': ('LAMMPS Lennard-Jones pair potential','https://docs.lammps.org/pair_lj.html','GPL-2.0; equations only'),
    'heat': ('UC Berkeley CS267: explicit heat equation finite differences','https://people.eecs.berkeley.edu/~demmel/cs267_Spr16/Lectures/lecture05_sources2_jwd16_4pp.pdf','University teaching reference; no code copied'),
    'interp': ('NumPy one-dimensional linear interpolation','https://numpy.org/doc/stable/reference/generated/numpy.interp.html','BSD-3-Clause; reference only'),
    'gemm': ('Netlib BLAS SGEMM','https://netlib.org/lapack/explore-html/dd/d09/group__gemm_ga8cad871c590600454d22564eff4fed6b.html','BSD-style BLAS license; equations only'),
})
DEFINITIONS.extend([
 ('BIO_KMER_COUNTS_U32_V1',25,'kmer','Overlapping oriented DNA k-mer counts','Count a supplied DNA word panel in independent sequence windows.',
  'C[s,q]=sum_{j=0..len(s)-k} [s[j:j+k]==query[q]]; overlapping occurrences count; orientation retained',
  'sequences[B] ACGT length0..4096,B1..256; kmers[Q] ACGT all same length1..15,Q1..256; B*Q*maxlen<=4194304', 'B*Q u32 counts sequence-major/query-minor; no reverse-complement merging or full vocabulary allocation', 'sequence/query tiles; sequence shards need k-1 halo and unique start ownership', 'POSSIBLE'),
 ('CHEM_LENNARD_JONES_PAIR_F32_V1',26,'lj','Lennard-Jones pair energy and force','Nonbonded molecular pair contribution in caller-consistent units.',
  'd=r_i-r_j;s=dot(d,d);q=sigma^2/s;t=(q*q)*q; E=4*epsilon*(t*t-t); F_i=(24*epsilon*(2*t*t-t)/s)*d; RN32 in stated order',
  'encoding=binary32-hex; pairs[N,6]=(ri_xyz,rj_xyz),sigma>0,epsilon>=0; rounded distance squared>0', 'N x4 binary32 [energy,Fx,Fy,Fz]; F_j=-F_i; no cutoff/PBC, mixing, total system sum or self pairs', 'independent supplied pairs; pair enumeration is caller owned', 'POSSIBLE'),
 ('PHYSICS_HEAT_STEP_F32_V1',27,'heat','Explicit two-dimensional heat diffusion step','Uniform-grid isotropic diffusion with periodic boundaries.',
  'lap=((left+right)+up)+down-4*center; next=center+lambda*lap; lambda=alpha*dt/h^2 in[0,1/4]; each operation RN32',
  'encoding=binary32-hex; field[H,W],3<=H,W<=256; lambda precomputed in physical units', 'H*W binary32 next-step field row-major; periodic one-cell neighbors; no forcing or variable diffusivity', 'sites with one-cell periodic halo; output is separate from input', 'POSSIBLE'),
 ('SIGNAL_LINEAR_RESAMPLE_F32_V1',28,'interp','Piecewise-linear one-dimensional resampling','Resample ordered measurements at explicit query coordinates.',
  'for xp[j]<x<xp[j+1]: y=fp[j]+((x-xp[j])/(xp[j+1]-xp[j]))*(fp[j+1]-fp[j]); exact knots and endpoints copy fp with canonical zero',
  'encoding=binary32-hex; xp,fp equal length1..4096, strictly increasing xp; queries1..4096', 'one binary32 value per query; out-of-range queries clamp to first/last sample; no periodic interpolation', 'query intervals sharing knot data', 'POSSIBLE'),
 ('ENGINEERING_DENSE_MATMUL_F32_V1',29,'gemm','Dense matrix multiplication','Dense operator and matrix stages of numerical solvers; BLAS alpha1,beta0,no transpose case.',
  'C[i,j]=sum_{k=0..K-1} A[i,k]*B[k,j]; increasing k separately rounded product and addition',
  'encoding=binary32-hex; left[M,K],right[K,N], dimensions1..128; M*N*K<=1048576', 'M*N binary32 row-major matrix; no FMA, reassociation or mixed precision', 'output row/column tiles; retain full canonical inner reduction', 'STRONG_CANDIDATE'),
])
