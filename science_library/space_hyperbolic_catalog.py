SOURCES={'hyperbolic_kepler':('NASA/JPL hyperbolic Kepler time-of-flight equation','https://naif.jpl.nasa.gov/pub/naif/toolkit_docs/FORTRAN/spicelib/hyptof.html','Published equations only; original bounded RN32 root/state implementation, no external code copied')}
DEFINITIONS=[('SPACE_HYPERBOLIC_KEPLER_STATE_F32_V1',76,'hyperbolic_kepler','Bounded hyperbolic Kepler state',
 'Solve the nonperiodic hyperbolic Kepler equation and return positive-energy unperturbed perifocal position and velocity.',
 'e*sinh(H)-H=M;32 sign-symmetric RN32 bisections;d=e*cosh(H)-1;r=a*d;position=(a*(e-cosh(H)),a*sqrt(e^2-1)*sinh(H),0);velocity=sqrt(mu/a)/d*(-sinh(H),sqrt(e^2-1)*cosh(H),0). a is the positive magnitude of the conventional negative semimajor axis.',
 'N1..1024 elements(a,e,M);a,shared mu in[2^-32,2^32],e in[5/4,4],M in[-16,16] hyperbolic radians;explicit binary32-hex,positive-magnitude a,PERIFOCAL and distance/time unit tags.',
 'N x8 binary32[H,r,x,y,z,vx,vy,vz];sinh degree21/cosh degree22 Horner RN32 and fixed root graph;complete zero-bit output validation;unperturbed bounded escape states.',
 'complete independent hyperbolic element records','POSSIBLE')]
