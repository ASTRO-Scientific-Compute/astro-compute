SOURCES={'gnomonic':('ERFA celestial tangent-plane projection conventions and equations','https://raw.githubusercontent.com/liberfa/erfa/master/src/tpxes.c','ERFA BSD reference only; original bounded RN32 graph of published equations, no external implementation copied')}
DEFINITIONS=[('SPACE_GNOMONIC_PROJECT_F32_V1',79,'gnomonic','Bounded celestial gnomonic tangent-plane projection',
 'Project sky directions onto an east/north tangent plane for astronomical image/catalog geometry; not a complete pixel WCS.',
 'd=sin(dec)*sin(dec0)+cos(dec)*cos(dec0)*cos(ra-ra0);xi=cos(dec)*sin(ra-ra0)/d;eta=(sin(dec)*cos(dec0)-cos(dec)*sin(dec0)*cos(ra-ra0))/d;ordered RN32, fixed turn trig;invalid status and zero xy when rounded d<1/16.',
 'N1..4096 direction(ra,dec) rows and one shared tangent point;finite binary32-hex;ra[0,1),dec[-1/4,1/4] turns;explicit GNOMONIC_TAN/EAST_NORTH/frame tags;exact payload fields.',
 'N x4 uint32 [status,bits(xi),bits(eta),bits(d)];status0 accepted,status1 outside guarded projection;invalid xi/eta+0,denominator retained;dimensionless plane coordinates,complete zero-bit gate.',
 'complete independent direction rows with shared tangent point','POSSIBLE')]
