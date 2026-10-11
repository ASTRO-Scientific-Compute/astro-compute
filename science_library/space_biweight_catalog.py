"""One shared-pass robust location/dispersion MathSpec."""
SOURCES = {'biweight': ('Astropy biweight location and midvariance estimators', 'https://docs.astropy.org/en/stable/api/astropy.stats.biweight_midvariance.html', 'BSD documentation; independently implemented finite operation graph')}
DEFINITIONS = [
    ('SPACE_BIWEIGHT_STATS_F32_V1',63,'biweight','Robust biweight location, midvariance and scale',
     'Estimate robust center and dispersion of masked astronomical samples or background boxes.',
     'Median M and MAD; u=(x-M)/(c*MAD), abs(u)<1. location=M+sum((x-M)*(1-u^2)^2)/sum((1-u^2)^2); midvariance=n*sum((x-M)^2*(1-u^2)^4)/sum((1-u^2)*(1-5*u^2))^2; scale=sqrt(midvariance), ordered RN32.',
     'encoding=binary32-hex;samples,valid[B,N],B1..128,N1..256,valid uint0/1;B*N*N<=2097152;c_location,c_variance finite f32 in[1,16];finite RN32 intermediates.',
     'B x [u32 status,valid_count,f32 median,MAD,location,midvariance,scale,u32 location_inliers,variance_inliers]; status1 empty,2 MAD0,3 degenerate denominator; failed records retain only status/count. n counts all valid observations; no universal variance calibration.',
     'whole independent observation rows/boxes, never split an ordered statistical reduction','POSSIBLE'),
]
