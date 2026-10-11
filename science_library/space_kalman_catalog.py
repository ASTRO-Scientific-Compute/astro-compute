SOURCES={'linear_kalman':('Chin/JPL 2023: linear Kalman and Joseph covariance equations (1–2),(5–10),(14)', 'https://ipnpr.jpl.nasa.gov/progress_report/42-233/42-233A-orig.pdf', 'Published equations only; original ASTRO implementation; no external code copied')}
DEFINITIONS=[('SPACE_LINEAR_KALMAN_STEP_F32_V1',72,'linear_kalman','Linear Kalman prediction and measurement update',
 'Batched linear state estimation with explicit transition, controls, process covariance and measurement noise.',
 'xp=F*x+u;Pp=F*P*F^T+Q;S=H*Pp*H^T+R;K=Pp*H^T*S^-1;xpost=xp+K*(y-H*xp);Ppost=(I-KH)*Pp*(I-KH)^T+K*R*K^T;guarded Cholesky solves;ordered RN32, mirrored lower triangles.',
 'binary32-hex B1..64,n1..6,m1..3;shared F,Q,H,diagonal R>0;per-record x,P,u,y;P,Q exactly symmetric PSD;finite executed intermediates;explicit linear/noise model.',
 'B x [u32 status;xp[n],Pp[n*n],xpost[n],Ppost[n*n],innovation[m],chi2];status1 guarded innovation solve rejects with all numeric words zero;status0 success;no covariance calibration guarantee.',
 'complete independent state/covariance records; sequential updates require verified full output','POSSIBLE')]
