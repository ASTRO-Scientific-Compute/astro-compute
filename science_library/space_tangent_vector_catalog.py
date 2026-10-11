SOURCES={'tangent_vector':('ERFA inverse celestial tangent-plane equations and conventions','https://github.com/liberfa/erfa/blob/master/src/tpsts.c','ERFA BSD mathematical reference only; original bounded ordered RN32 basis/normalization, no external code copied')}
DEFINITIONS=[('SPACE_TANGENT_TO_UNIT_VECTOR_F32_V1',80,'tangent_vector','Tangent plane to normalized celestial unit vector',
 'Reconstruct celestial Cartesian sky directions from bounded east/north gnomonic plane coordinates and an explicit tangent point.',
 'center=(cosd*cosa,cosd*sina,sind);east=(-sina,cosa,0);north=(-sind*cosa,-sind*sina,cosd);u=center+xi*east+eta*north;r=sqrt(dot(u,u));v=u/r;ordered RN32 graph and frozen turn trig.',
 'N1..4096 plane coordinates(xi,eta) in[-16,16],one tangent point ra[0,1),dec[-1/4,1/4] turns;finite binary32-hex,explicit GNOMONIC_TAN/EAST_NORTH/common frame;exact payload fields.',
 'N x4 binary32[vx,vy,vz,r];r is canonical unnormalized-vector norm;dimensionless sky direction and norm,complete zero-bit validation;no output RA/Dec or pixel WCS.',
 'complete independent plane-coordinate rows with shared tangent point','POSSIBLE')]
