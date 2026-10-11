"""Bounded interacting N-body evolution and full-system invariants."""
SOURCES={
 'nbody_adaptive':('GSL classical RK4 step doubling and REBOUND softened gravity model','https://www.gnu.org/software/gsl/doc/html/ode-initval.html','Public algorithm descriptions; original ASTRO implementation; no GSL or REBOUND code copied'),
 'nbody_invariants':('REBOUND gravitational constant and softened force model','https://pyodide.hanno-rein.de/simulation/variables/','Public model description; original ASTRO implementation')}
DEFINITIONS=[
 ('SPACE_ADAPTIVE_NBODY_RK4_F32_V1',69,'nbody_adaptive','Adaptive interacting N-body RK4',
  'Evolve complete coupled gravitational systems with local step-doubling control, explicit work and singularity statuses.',
  'dr_i/dt=v_i;dv_i/dt=sum_j!=i G*m_j*(r_j-r_i)/(distance^2+eps2)^(3/2); classical RK4 at all coupled stages; max scaled |two_half-one_full|/15; accept two half steps; ordered RN32.',
  'binary32 states[B,N,6],masses[B,N],G>=0,eps2>=0,masses>=0;B1..16,N1..8;shared duration>=0,0<dt_min<=dt_initial<=dt_max,rtol>=0,atol[6]>0;max_attempts1..64;B*N*N*max_attempts<=16384;finite executed intermediates.',
  'B x [u32 status,attempts,accepted,rejected;f32 elapsed,last_error,next_dt,states[N,6]];status0 complete,1 attempt limit,2 step limit,3 singular force; failure preserves last accepted state.',
  'whole coupled systems only; never split bodies across independent records','POSSIBLE'),
 ('SPACE_NBODY_INVARIANTS_F32_V1',70,'nbody_invariants','Softened N-body system invariants',
  'Compute total mass, energy, linear/angular momentum, center of mass and minimum squared separation.',
  'M=sum m;T=sum(m*v^2/2);U=-sum_i<j G*m_i*m_j/sqrt(r_ij^2+eps2);E=T+U;P=sum m*v;L=sum m*r cross v;COM=sum m*r/M;ordered RN32.',
  'binary32 states[B,N,6],masses[B,N],G>=0,eps2>=0,masses>=0;B1..64,N1..64;B*N*N<=65536;finite executed intermediates.',
  'B x [u32 status;f32 total_mass,kinetic,potential,energy,Px,Py,Pz,Lx,Ly,Lz,COMx,COMy,COMz,min_distance_squared];status1 singular weighted pair,2 zero total mass; failure has only status.',
  'whole independent systems; pair reductions and centers remain within records','POSSIBLE')]
