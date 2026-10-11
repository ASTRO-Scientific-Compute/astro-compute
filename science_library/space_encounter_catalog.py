SOURCES={'swept_encounter':('REBOUND straight-line collision detection and its curved-path limitation','https://rebound.hanno-rein.de/collisions/','Algorithm description only; original ASTRO projection implementation; no external code copied')}
DEFINITIONS=[('SPACE_SWEPT_SPHERE_ENCOUNTER_F32_V1',71,'swept_encounter','Closest approach and sphere contact along pair chords',
 'Detect contact during supplied straight-line motion, including complete pass-through with separated endpoints.',
 'p=b0-a0;q=b1-a1;d=q-p;t=clamp(-dot(p,d)/dot(d,d),0,1);zero rounded motion selects0;min_d2=|p+t*d|^2;contact=min_d2<=(ra+rb)^2;ordered RN32;exact endpoint reuse at t0/1.',
 'binary32 pairs[N,14]=[a0.xyz,a1.xyz,b0.xyz,b1.xyz,ra,rb];N1..4096;radii>=0;finite executed intermediates; simultaneous endpoints in one frame and consistent units.',
 'N x [u32 contact;f32 closest_fraction,min_d2,start_d2,end_d2,radius_sum_d2;u32 rounded_stationary];inclusive rounded contact;not first-contact time or a conservative geometric proof.',
 'complete independent pair chords; no implicit all-pair enumeration','POSSIBLE')]
