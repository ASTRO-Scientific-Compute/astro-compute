"""Bit-exact precision amendments for the two original RT commissioning tasks."""
DEFINITIONS=[
('RT_STATIC_NEAREST_TRIANGLE_HIT_V1',37,'triangle_exact','Static nearest opaque triangle distance','Independent geometric ray query; local commissioning, no research credit.',
 'Normalize supplied direction with separate RN32 operations; exact rational Moller-Trumbore determinants/barycentrics; abs(det)>=RN32(1e-8); RN32(t)>RN32(1e-4); min RN32 positive t, miss RN32(1e30); two-sided closed triangle edges',
 'encoding=binary32-hex; triangles[M,3,3], rays[N]={origin[3],direction[3]}; each input component zero or magnitude 2^-16..2^16; nonzero directions; 1<=M,N<=4096 and M*N<=1048576; no hidden quantization',
 'N binary32 nearest-hit distances, original ray order; miss=0x7149f2ca', 'independent rays sharing full scene', 'NONE'),
('RT_DYNAMIC_NEAREST_TRIANGLE_HIT_V1',38,'triangle_exact','Mutate geometry and query exact nearest opaque hit','Local GPU geometry mutation + BVH update/refit or full rebuild, with complete output and mutation audit.',
 'For each explicit frame f: z=RN32(base_z+offset[(17*triangle+13*f)&1023]); offset[k]=frozen RN32(0.0025*sin(2*pi*k/1024)); query same exact static operator; every frame derives from immutable base',
 'static inputs plus frames[1..8] uint32; M*N*F<=1048576; mutated coordinates magnitude<=2^16 and exactly representable on 2^-56 grid; input bits retained',
 'F*N binary32 distances, frame-major then ray order; separate full byte audit of all F*M*9 mutated coordinates', 'ray/frame output intervals; mutation and BVH maintenance always cover complete scene for every frame', 'NONE')]
SOURCES={'triangle_exact':('Moller and Trumbore: Fast, Minimum Storage Ray/Triangle Intersection (1997)','https://my.eng.utah.edu/~cs6965/papers/MT97.pdf','Paper reference only; original exact-rational / integer implementation, no source copied')}
ORIGINALS={37:'commissioning/contracts/rt_static_nearest_triangle_hit_v1.json',38:'commissioning/contracts/rt_dynamic_nearest_triangle_hit_v1.json'}
