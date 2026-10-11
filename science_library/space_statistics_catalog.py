"""Published SPACE methods and frozen contracts, specified before kernels."""

SOURCES = {
    'bootstrap': ('Astropy case bootstrap and statistics of resampled data',
                  'https://docs.astropy.org/en/stable/api/astropy.stats.bootstrap.html',
                  'BSD-3-Clause documentation; independent implementation, no source copied'),
    'sigma_clip': ('Astropy sigma_clip, mean center and population standard deviation',
                   'https://docs.astropy.org/en/stable/api/astropy.stats.sigma_clipping.sigma_clip.html',
                   'BSD-3-Clause documentation; independent implementation, no source copied'),
    'segmentation': ('Photutils detect_sources, threshold and 4/8-connected components',
                     'https://photutils.readthedocs.io/en/2.3.0/api/photutils.segmentation.detect_sources.html',
                     'BSD-3-Clause documentation; independent implementation, no source copied'),
}

DEFINITIONS = [
    ('SPACE_BOOTSTRAP_MEAN_VARIANCE_F32_V1', 45, 'bootstrap',
     'Case-bootstrap replicate mean and sample variance',
     'Resampling statistics for uncertainty estimation on astronomical measurements.',
     'For each supplied index row I: mu=ordered_sum(x[I[j]])/K; s2=ordered_sum((x[I[j]]-mu)^2)/(K-1); each operation RN32.',
     'encoding=binary32-hex; values[N],N1..4096; indices[B,K] uint indices0..N-1; B1..1024,K2..512,B*K<=262144; all RN32 intermediates finite.',
     'B x [binary32 mean,binary32 sample variance]; indices supplied with replacement; no internal RNG, confidence interval or independence claim.',
     'whole replicate rows, retaining ordered indices and shared original measurements', 'POSSIBLE'),
    ('SPACE_SIGMA_CLIP_STATS_F32_V1', 46, 'sigma_clip',
     'Iterative mean-centered sigma clipping with complete retained mask',
     'Reject outliers and estimate background statistics for astronomical image patches or time-series windows.',
     'For retained set: mu=ordered_sum(x)/n; v=ordered_sum((x-mu)^2)/n; bounds=mu-sigma_lower*sqrt(v),mu+sigma_upper*sqrt(v); reject strictly outside simultaneously; repeat until stable or maxiters; recompute final statistics; all operations RN32.',
     'encoding=binary32-hex; samples[B,N],valid[B,N] uint0/1; B1..128,N1..512; sigma_lower/upper finite>=0; maxiters1..16; B*N*maxiters<=1048576; all RN32 intermediates finite.',
     'B x [status,u32 retained_count,binary32 mean,binary32 population_variance,N uint retained_flags]; status0 stable,1 empty,2 last allowed iteration removed values; empty mean/variance/mask are positive zero.',
     'whole independent patches/windows; never split a statistical reduction', 'POSSIBLE'),
    ('SPACE_IMAGE_SEGMENTATION_U32_V1', 47, 'segmentation',
     'Thresholded connected source segmentation',
     'Label astronomical source islands before photometry; remove components below a supplied pixel count.',
     'Foreground=valid and value>threshold; 4/8-connected components inside each complete image; label=1+minimum row-major pixel index in component if size>=npixels, otherwise0.',
     'encoding=binary32-hex; images[B,H,W],valid[B,H,W] uint0/1; B1..128,H/W1..32; B*H*W<=65536; scalar finite threshold; connectivity4 or8; npixels1..H*W.',
     'B x (H*W) uint32 labels;0 background; labels canonical but not necessarily consecutive; no deblending or cross-image component merging.',
     'whole independent images/cutouts only; arbitrarily tiling a larger image changes connectivity', 'NONE'),
]
