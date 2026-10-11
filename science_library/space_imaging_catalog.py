"""Spatial background, cross-tile components and source-catalog contracts."""
SOURCES = {
 'mesh_linear': ('SciPy regular-grid linear interpolation', 'https://docs.scipy.org/doc/scipy/reference/generated/scipy.interpolate.RegularGridInterpolator.html', 'BSD documentation; equations only, original implementation'),
 'component_graph': ('SciPy undirected graph connected components', 'https://docs.scipy.org/doc/scipy/reference/generated/scipy.sparse.csgraph.connected_components.html', 'BSD documentation; independent graph algorithms'),
 'segment_catalog': ('Photutils SourceCatalog photometry and morphology', 'https://photutils.readthedocs.io/en/stable/api/photutils.segmentation.SourceCatalog.html', 'BSD documentation; method only, no source copied'),
}
DEFINITIONS = [
 ('SPACE_BACKGROUND_BILINEAR_F32_V1',51,'mesh_linear','Bilinear background mesh evaluation',
  'Interpolate a supplied astronomical background mesh at image positions expressed in mesh-index coordinates.',
  'Clamp x,y to mesh domain; j=floor(x),k=floor(y); tx=RN32(x-j),ty=RN32(y-k); lerp(a,b,t)=RN32(RN32((1-t)*a)+RN32(t*b)), exact t=0 returns canonical a; x interpolation then y.',
  'encoding=binary32-hex; mesh[H,W],H/W2..64; points[Q,2],Q1..65536; all finite; explicit grid-coordinate queries, nearest-edge extension.',
  'Q x binary32 background; no mesh estimation, missing-cell filling or implicit world-coordinate conversion.',
  'query positions sharing the complete mesh; retain global mesh coordinates','NONE'),
 ('SPACE_COMPONENT_GRAPH_MERGE_U32_V1',52,'component_graph','Cross-tile component equivalence closure',
  'Merge local image components connected at tile boundaries, applying minimum source size only after global merging.',
  'For each undirected connected component output min(component_id),sum(pixel_count),min(component_id) if total>=npixels else0; output one row per input node.',
  'encoding=uint32; unique nonzero component_ids[N],pixel_counts[N]>0,N1..512; edges[M,2] node indices,M0..8192; sum counts<=2^32-1; npixels1..2^32-1; caller supplies disjoint pixel sets and complete seam adjacency.',
  'N x [u32 canonical_id,u32 global_pixel_count,u32 accepted_id]; duplicates/self edges harmless; isolated components retained; does not discover missing edges or deblend.',
  'whole component graph shared by output-node partitions; graph shards require explicit equivalence reconciliation','NONE'),
 ('SPACE_SEGMENT_CATALOG_F32_V1',53,'segment_catalog','Segmented-source flux, centroid and central moments',
  'Produce a photometric/morphological source table from a background map and globally labeled image.',
  'd=RN32(image-background); ordered flux=sum(d),variance=sum(input_variance); morphology weights=max(d,0); centroid=sum(w*x,y)/sum(w); second pass central moments=sum(w*dx^2,w*dx*dy,w*dy^2)/sum(w).',
  'encoding=binary32-hex; image/background/variance[H,W],H/W1..128; nonnegative variance; labels[H,W] uint32; valid[H,W]0/1; unique nonzero source_ids[Q],Q1..256; H*W*Q<=1048576; all inputs and RN32 intermediates finite.',
  'Q x [u32 status,u32 count,f32 signed_flux,f32 variance_sum,f32 positive_flux,f32 cx,cy,mu20,mu11,mu02]; status0 normal,1 no valid pixels,2 zero positive flux; absent centroid/moments zero. Coordinates are zero-based pixel centers. Independent pixel errors assumed; no PSF or deblending model.',
  'source IDs with complete shared image in row-major order; do not independently round and sum pixel shards','NONE'),
]
