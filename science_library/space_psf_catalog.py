"""Frozen weighted PSF and bounded mixture contracts, before GPU code."""
SOURCES = {
    'psf_scan': ('Photutils PSF photometry and simultaneous source fitting', 'https://photutils.readthedocs.io/en/stable/api/photutils.psf.PSFPhotometry.html', 'BSD documentation; independent implementation'),
    'template_nnls': ('SciPy NNLS objective and Lawson-Hanson active-set family', 'https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.nnls.html', 'Published method; original bounded subset implementation'),
}
DEFINITIONS = [
    ('SPACE_PSF_WEIGHTED_SCAN_F32_V1', 59, 'psf_scan', 'Weighted spatial PSF amplitude scan',
     'Estimate supplied-PSF amplitude, known-noise variance and fit residuals at integer image centers.',
     'A=sum(w*P*(image-background))/sum(w*P*P); var=1/sum(w*P*P); snr=A/sqrt(var); chi2=sum(w*(image-background-A*P)^2), ordered RN32.',
     'encoding=binary32-hex; image,background,weights[H,W], H,W1..64; weights>=0; nonnegative PSF odd shape1..9, positive sum; all finite intermediates; full support only.',
     'H*W x [u32 status,f32 amplitude,variance,snr,chi2,u32 positive_weight_pixels]; status1 zero information,2 partial support; remaining fields0 on failure; no PSF normalization or significance inference.',
     'output centers retaining the entire input image and PSF; halo required for image tiles', 'STRONG_CANDIDATE'),
    ('SPACE_TEMPLATE_NNLS_F32_V1', 60, 'template_nnls', 'Bounded weighted nonnegative template mixture',
     'Fit three to five fixed nonnegative templates jointly for SED mixtures or fixed-position PSF groups.',
     'min sum(w*(y-sum_k(a_k*T_k))^2), a_k>=0; exhaustive ordered active-subset Cholesky solves with RN32 residual ranking and explicit pivot gate.',
     'encoding=binary32-hex; templates[M,N]>=0,M3..5,N M..128; flux,weights[R,N],R1..64,weights>=0; R*2^M*(N*M+M^3)<=2097152; finite RN32 intermediates.',
     'R x [u32 status,positive_coefficient_mask,f32 chi2,coefficients[M]]; status1 zero information,2 any principal Cholesky pivot<=RN(maxdiag*2^-18); remaining fields0 on failure; no covariance or arbitrary-group guarantee.',
     'independent observation rows with shared complete template matrix', 'STRONG_CANDIDATE'),
]
