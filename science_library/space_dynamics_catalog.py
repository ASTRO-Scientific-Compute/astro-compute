"""Source-backed axisymmetric gravity and adaptive-orbit contracts, before code."""
SOURCES={
 'j2_force':('poliastro J2 perturbation acceleration','https://docs.poliastro.space/en/stable/autoapi/poliastro/core/perturbations/index.html','Published equations only; original implementation, no code imported'),
 'adaptive_rk4':('GNU GSL classical RK4 with step-doubling error estimate','https://www.gnu.org/software/gsl/doc/html/ode-initval.html','GPL documentation/reference only; no GSL implementation copied'),
 'orbit_diagnostics':('UT Austin celestial mechanics conservation laws','https://farside.ph.utexas.edu/teaching/celestial/Celestial/node25.html','University equations only; original implementation'),
}
DEFINITIONS=[
 ('SPACE_J2_ACCELERATION_F32_V1',54,'j2_force','Central plus J2 gravitational acceleration','Evaluate the acceleration of test particles in a supplied static axisymmetric gravity model with symmetry axis z.',
  'a=-mu*rvec/r^3+(3/2)*J2*mu*R^2/r^5 * [x*(5*z^2/r^2-1),y*(5*z^2/r^2-1),z*(5*z^2/r^2-3)]; exact RN32 order in contract.',
  'encoding=binary32-hex; positions[N,3],N1..4096; mu>=0,reference_radius>=0,finite j2; coherent units supplied by caller; finite RN32 intermediates.',
  'N x [u32 status,f32 ax,ay,az]; status1 when rounded radius squared is zero with mu>0, then zero acceleration; mu=0 yields status0 zero force. No collision/body-surface or atmosphere model.',
  'independent positions with the same model parameters','NONE'),
 ('SPACE_ADAPTIVE_ORBIT_RK4_F32_V1',55,'adaptive_rk4','Adaptive RK4 step-doubling trajectories with J2','Propagate independent orbits with explicit local error estimates, rejected steps and bounded-work failure statuses.',
  'One RK4 step h vs two steps h/2; accept fine state when max(abs(fine-coarse)/15/(atol[k]+rtol*max(abs(old),abs(fine))))<=1; halve on rejection, double after acceptance if error<=1/32; clamp final step to remaining duration.',
  'encoding=binary32-hex; states[N,6],N1..64; shared mu>=0,reference_radius>=0,j2; duration>=0;0<dt_min<=dt_initial<=dt_max;atol[6]>0,rtol>=0;max_attempts1..128,N*max_attempts<=2048; finite RN32 intermediates.',
  'N x [u32 status,attempts,accepted,rejected,f32 elapsed,last_error,next_dt,x,y,z,vx,vy,vz]; status0 completed,1 attempt limit,2 step/time resolution limit,3 singular force; nonzero status retains last accepted state. Local error is a numerical estimate, not global error proof; CPU/GPU allowed differing bits remains0.',
  'whole independent trajectories; accepted/rejected history affects state and cannot be split as independent time shards','NONE'),
 ('SPACE_ORBIT_DIAGNOSTICS_F32_V1',56,'orbit_diagnostics','Specific orbital energy and angular momentum diagnostics','Measure radius, speed squared, model-specific energy and angular momentum for a central plus J2 trajectory.',
  'E=v^2/2-mu/r*(1-J2*(R^2/r^2)*(3*z^2/r^2-1)/2);h=rvec cross v; ordered RN32 arithmetic.',
  'encoding=binary32-hex; states[N,6],N1..4096;mu>=0,reference_radius>=0,finite j2; all RN32 intermediates finite.',
  'N x [u32 status,f32 radius,speed_squared,energy,hx,hy,hz]; status1 singular gravity gives all zeros; mu=0 permits origin. Energy and hz are invariants of the continuous axisymmetric J2 model; hx/hy generally are not. No orbital-element/WCS conversion.',
  'independent states; compare only matching force-model parameters and units','NONE'),
]
