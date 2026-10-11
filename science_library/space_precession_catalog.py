SOURCES={'iau2006_precession':('IERS Conventions2010 chapter5: TT epoch, Fukushima–Williams rotation and IAU2006 coefficients','https://iers-conventions.obspm.fr/content/chapter5/icc5.pdf','Published mathematical coefficients/equations only; original ASTRO stable binary32 realization, not SOFA/ERFA code')}
DEFINITIONS=[('SPACE_IAU2006_BIAS_PRECESSION_F32_V1',74,'iau2006_precession','IAU2006 bias/precession of GCRS Cartesian vectors',
 'Generate the epoch-dependent bias/precession matrix and rotate GCRS vectors to mean equator/equinox of date.',
 'T=(JD_TT-2451545)/36525;IERS(5.40) Fukushima–Williams polynomials;R=X(-epsilon)*Z(-psi)*X(phi)*Z(gamma), evaluated as stable conjugation M*X(phi-epsilon)*Z(gamma);output R*v;ordered RN32.',
 'N1..4096;binary32-hex tt_centuries in[-1,1],vectors[N,3];explicit TT/GCRS/MEAN_EQUATOR_EQUINOX_OF_DATE_IAU2006 tags;finite executed intermediates.',
 'N x16 binary32[gamma,phi-epsilon,psi,epsilon,R row-major9,transformed_xyz];mean-of-date only,no nutation/apparent-place corrections or microarcsecond accuracy guarantee.',
 'complete independent epoch/vector records','POSSIBLE')]
