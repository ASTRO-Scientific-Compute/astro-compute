SOURCES={'parabolic_barker':('NASA/JPL parabolic time-of-flight Barker equation','https://naif.jpl.nasa.gov/pub/naif/toolkit_docs/FORTRAN/spicelib/partof.html','Published equations only; original bounded RN32 Barker root/state, no external implementation copied')}
DEFINITIONS=[('SPACE_PARABOLIC_BARKER_STATE_F32_V1',77,'parabolic_barker','Bounded parabolic Barker state',
 'Solve Barker time-of-flight cubic for exactly parabolic e=1 and obtain zero-energy unperturbed perifocal position and velocity.',
 'D+D^3/3=M;32 fixed sign-symmetric RN32 bisections;den=1+D^2;r=q*den;position=(q*(1-D^2),2*q*D,0);velocity=sqrt(2*mu/q)/den*(-D,1,0). q is periapsis distance;M=(t-T)*sqrt(mu/(2*q^3)).',
 'N1..1024 elements(q,M);q,shared mu in[2^-32,2^32],M in[-16,16] Barker dimensionless parameter;binary32-hex,PARABOLIC_E1,PERIFOCAL,distance/time labels;exact payload fields.',
 'N x8 binary32[D,r,x,y,z,vx,vy,vz];canonical fixed cubic solve/state graph,complete zero-bit validation;bounded exactly parabolic two-body states.',
 'complete independent parabolic element records','POSSIBLE')]
