SOURCES={'elliptic_kepler':('JPL SSD Kepler equation and perifocal position from eccentric anomaly','https://ssd.jpl.nasa.gov/planets/approx_pos.html','Published equations only; original ASTRO bounded binary32 solve and differentiated velocity, no external code copied')}
DEFINITIONS=[('SPACE_ELLIPTIC_KEPLER_STATE_F32_V1',75,'elliptic_kepler','Direct bounded elliptic Kepler state',
 'Solve the elliptic Kepler equation and obtain the unperturbed perifocal position and velocity at a supplied mean anomaly.',
 '2*pi*(E-M)-e*sin(2*pi*E)=0;32 fixed reflected bisections in RN32;d=1-e*cos(2*pi*E);r=a*d;position=(a*(cos(2*pi*E)-e),a*sqrt(1-e^2)*sin(2*pi*E),0);v=sqrt(mu/a)/d*(-sin(2*pi*E),sqrt(1-e^2)*cos(2*pi*E),0).',
 'N1..1024 elements(a,e,M);a,shared mu in[2^-32,2^32],e in[0,15/16],M in[0,1) turns;explicit binary32-hex/turn/PERIFOCAL tags and distance/time units.',
 'N x8 binary32[E_turns,r,x,y,z,vx,vy,vz];canonical graph and complete zero-bit validation;bounded two-body states,not a perturbed ephemeris.',
 'complete independent orbital-element records','POSSIBLE')]
