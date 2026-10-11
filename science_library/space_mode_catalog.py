"""Recursive half-sample modal location, distinct from median/biweight."""
SOURCES={'half_sample_mode':('Bickel and Fruehwirth: HalfSampleMode, Appendix pp.18–19','https://arxiv.org/abs/math/0505419','Published algorithm, original independent ASTRO implementation; no external code copied')}
DEFINITIONS=[('SPACE_HALF_SAMPLE_MODE_F32_V1',64,'half_sample_mode','Half-sample mode of masked observations',
    'Estimate a modal sky background from the recursively shortest half sample.',
    'Sort valid x. While n>=4 select first minimum RN32(x[j+ceil(n/2)-1]-x[j]); recurse. n1 canonical x; n2 correctly rounded exact mean; n3 closest-pair correctly rounded mean, equal gaps middle x.',
    'binary32-hex samples[B,N],valid[B,N] uint0/1;B1..128,N1..256,B*N*N<=2097152;finite values and executed intermediates.',
    'B x [u32 status,valid_count,f32 mode,low,high,width,u32 terminal_count,halving_rounds,sorted_start]; status1 empty with other fields0. No uncertainty is inferred from terminal width.',
    'whole independent observation rows/boxes, never split the order-statistic selection','POSSIBLE')]
