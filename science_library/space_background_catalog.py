"""Fixed interpolation and masked-median contracts, before kernels."""
SOURCES = {
    'idw_background': ('Photutils Shepard inverse-distance interpolation', 'https://photutils.readthedocs.io/en/stable/api/photutils.utils.ShepardIDWInterpolator.html', 'BSD documentation; independently implemented bounded integer-coordinate variant'),
    'median_mesh': ('Photutils Background2D mesh filtering and missing-cell handling', 'https://photutils.readthedocs.io/en/stable/api/photutils.background.Background2D.html', 'BSD documentation; original masked truncated-window median implementation'),
}
DEFINITIONS = [
    ('SPACE_IDW_INTERPOLATE_F32_V1', 61, 'idw_background', 'Nearest-neighbor inverse squared-distance interpolation',
     'Interpolate finite background samples and fill excluded mesh cells using explicit coordinate ticks.',
     'Exact integer d2; select up to K sources by (d2,index); exact coincidence returns source value; otherwise ordered RN32 sum(value/RN32(d2))/sum(1/RN32(d2)).',
     'encoding=binary32-hex; sources[M,2],queries[Q,2] uint ticks0..32767; unique sources,M1..256,Q1..4096; values[M] finite f32,valid[M]uint0/1; neighbors1..16; M*Q*K<=4194304; finite RN32 intermediates.',
     'Q x [u32 status,f32 value,u32 contributors,nearest_d2]; status1 no valid source with remaining fields0; status0 success; nearest distance exact; no variance or large-hole reconstruction guarantee.',
     'independent query rows with complete shared source set and tie order', 'NONE'),
    ('SPACE_MASKED_MEDIAN_MESH_F32_V1', 62, 'median_mesh', 'Masked truncated-window mesh median',
     'Suppress local mesh outliers while retaining sample counts and explicit insufficient-neighbor status.',
     'Gather valid in-bounds cells, sort numerically; odd median=middle; even median=RN32(RN32(lower*0.5)+RN32(upper*0.5)); no in-place propagation.',
     'encoding=binary32-hex; mesh,valid[H,W],H/W1..64,valid uint0/1; window odd1..7; minimum_valid1..window^2; finite f32 values.',
     'H*W x [u32 status,count,f32 median]; status1 count<minimum_valid and median0; status0 success; boundary window truncated, signed zero canonicalized; no uncertainty inference.',
     'independent output centers with complete original mesh; mesh tiling requires a half-window halo', 'NONE'),
]
