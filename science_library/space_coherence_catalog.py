SOURCES={'cross_coherence':('SciPy coherence and conjugate-X cross spectrum equations','https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.csd.html','Published equations only; original bounded RN32 mean complex cross-products and coherence, no external implementation copied')}
DEFINITIONS=[('SPACE_CROSS_SPECTRAL_COHERENCE_F32_V1',78,'cross_coherence','Paired complex cross-spectrum and magnitude-squared coherence',
 'Measure shared spectral content of matched complex segment spectra from two astronomical measurement channels; no significance inference.',
 'Pxx=mean(abs(X)^2);Pyy=mean(abs(Y)^2);Pxy=mean(conj(X)*Y);Cxy=abs(Pxy)^2/(Pxx*Pyy);ordered separate RN32 operations;explicit undefined status for zero channel power;no clamping.',
 'B1..256 bins, uniform R2..64 ordered matched replicates of [xr,xi,yr,yi];finite binary32-hex components either zero or magnitude2^-28..2^16;explicit conjugation,mean-product,replicate,unit and grid labels;exact payload fields.',
 'B x6 uint32 words [status,bits(Pxx),bits(Pyy),bits(RePxy),bits(ImPxy),bits(Cxy)];status bit0 zero X power,bit1 zero Y;undefined coherence has explicit status and zero sentinel. Complete zero-bit gate.',
 'independent bins;all replicates of each bin remain ordered and complete','POSSIBLE')]
