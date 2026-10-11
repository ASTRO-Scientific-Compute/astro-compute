SOURCES={'stabilized_rts':('Chin/JPL 2023: RTS gain/mean and stabilized covariance, equations (11–12),(20)','https://ipnpr.jpl.nasa.gov/progress_report/42-233/42-233A-orig.pdf','Equations only; original ASTRO implementation; no external source code copied')}
DEFINITIONS=[('SPACE_RTS_SMOOTHER_STEP_F32_V1',73,'stabilized_rts','Stabilized RTS backward smoothing step',
 'Use later observations through a supplied next smoothed state to revise an earlier filtered linear state.',
 'xp=F*x+u;Pp=F*P*F^T+Q;G=P*F^T*Pp^-1;xs=x+G*(xs_next-xp);Ps=G*(Ps_next+Q)*G^T+(I-GF)*P*(I-GF)^T;guarded Cholesky and ordered RN32.',
 'binary32-hex B1..64,n1..6;shared transition F and process covariance Q;per-record filtered x,P,control u,next smoothed xs_next,Ps_next;P,Q,Ps_next exact symmetric PSD;finite executed graph.',
 'B x [u32 status;xp[n],Pp[n*n],xs[n],Ps[n*n],G[n*n]];status1 guarded prediction solve with all numeric output zero;no automatic model or posterior calibration.',
 'whole independent state/covariance records; backward dependency requires verified successor output','POSSIBLE')]
