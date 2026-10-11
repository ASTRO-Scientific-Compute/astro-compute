# SPACE search contracts, v1.17.14

Six new published scientific operators extend SPACE from 23 to 29 contracts. The catalog contains source URLs, equations, provenance, exact dimensions, partition limits and output schemas. They are independent original implementations. No external code or trained model is embedded.

## Numerical boundary

All six accept explicit `binary32-hex` values (BLS timestamps and periods remain exact integer ticks; image validity is an integer mask). Every scalar arithmetic operation uses the existing rational CPU oracle and independent integer GPU RN32 implementation, with gradual underflow, canonical positive zero and no FMA/reassociation. Nonfinite inputs, overflowing intermediates, invalid roots and divisions by zero reject the job before dispatch. Output acceptance allows **zero differing bits** at warmup and final execution, including status fields and every trajectory state.

Scientific accuracy and byte reproducibility are distinct checks. The scientific tests use separate NumPy binary64 least-squares, direct exhaustive masks, analytic orbit solutions and refined integration. Their approximation budgets never replace or relax the zero-bit output gate. Correct binary32 execution is not a claim of exact real arithmetic, correctly rounded transcendental functions or universal physical-model accuracy.

## Reproducible sine/cosine

Used by Lomb–Scargle and spherical coordinates. Angles are in turns. For input u, retain its sign and extract p=abs(u) mod 1 exactly from the binary32 value. Set q=floor(4p) and d=p-q/4. Form x=RN32(d*0x40c90fdb), z=RN32(x*x). Evaluate, in descending Horner order with separate RN32 multiply/add:

- sin(x)=RN32(x * sum(k=0..6, RN32((-1)^k/(2k+1)!)*z^k)).
- cos(x)=sum(k=0..7, RN32((-1)^k/(2k)!)*z^k).

Apply the exact quadrant swaps/signs, then the original sine sign. Cardinal quarter turns are exact. Constants are frozen rational coefficients; CPU reduces turns with Fraction, GPU with bit-extracted integer/fraction parts. This polynomial is explicitly part of the numerical contract, not native device `sin`/`cos`. A 2,049-angle GPU sweep is independently compared with binary64 trigonometry. Multiplying frequency by relative time in Lomb–Scargle rounds before phase reduction; callers must supply a suitable relative epoch and obey |RN32(f*t)|<=256.

## Weighted floating-mean Lomb–Scargle

For each frequency, compute sine/cosine bases on every supplied relative timestamp. In input order, sum weights and weighted y/cos/sin to obtain their weighted means. Revisit samples in the same order to form centered CC, SS, CS, YC, YS and YY. Each term is `(w*first)*second` with separately rounded operations. Set D=CC*SS-CS*CS.

Zero summed weight or zero YY yields status 1. D<=RN32(CC*SS*2^-18) yields status 2 for a singular/poorly conditioned basis. These return five zero numerical words. This conditioning boundary is not a CPU/GPU tolerance.

Otherwise a=(YC*SS-YS*CS)/D, b=(YS*CC-YC*CS)/D, offset=(mean_y-a*mean_cos)-b*mean_sin. Recompute chi2 by summing `w*(y-((offset+a*cos)+b*sin))^2` in input order. Return status, `(YY-chi2)/YY`, offset, a, b, chi2. Rounded power is not silently clipped. This is a full one-harmonic, weighted, floating-mean evaluation of the supplied grid, with no automatic frequency selection, significance calculation or multi-harmonic extension.

## Binned box least squares

Integer tick times fold exactly as floor((t mod P)*K/P). Within each bin, sum binary32 flux in original observation order and count observations exactly. Sum bin flux in increasing bin order for the total. Scan starts 0..K-1; for each start append bins cyclically for widths 1..max_width. Evaluate eligible widths >=min_width if both groups contain observations. Empty bins remain zero.

Compute outside mean=(total-inside_sum)/outside_count, inside mean=inside_sum/inside_count, depth=outside-inside. Positive depth candidates receive `(((depth*depth)*inside_count)*outside_count)/N`, with RN32 at every operation. Retain only strictly greater scores, so equal bit scores select earliest start then shortest width. If no strictly positive representable score exists, status 1 and five zero words are returned. Output is status, start bin, width bins, depth, outside mean, score. All phase/duration combinations on the declared grid are searched; continuous transit fitting and unequal uncertainties are outside this contract.

## Image peak mask

Input image and validity mask have identical shape. A valid pixel qualifies when it is strictly above the scalar threshold and no unmasked neighbor in the declared square is brighter. Values outside the image are zero; masked interior pixels are ignored. Equal-height plateaus retain all qualifying pixels. Output has one exact uint32 flag per pixel. Source segmentation, deblending, noise estimation and centroid fitting remain separate work.

## SED template chi-square

For every object/template pair, reduce bands in order: num=sum((w*T)*y), den=sum((w*T)*T). A zero rounded denominator produces status 1, amplitude 0, chi2 0. Otherwise amplitude=max(0,num/den); chi2=sum(w*(y-amplitude*T)^2). Zero-weight bands are supported; negative observations are accepted. Output preserves object-major, template-minor order, including duplicate templates. The caller supplies bandpass-integrated templates, redshift grid and template labels. This is the single-template amplitude-fitting/scoring primitive, not a complete photo-z posterior, template mixture fitter or trained classifier.

## Spherical coordinates

Rows contain radius, latitude turns, longitude turns. Radius is nonnegative; latitude is in [-1/4,1/4], longitude in [-65536,65536]. Compute rc=RN32(r*cos(lat)), then (rc*cos(lon), rc*sin(lon), r*sin(lat)) with separate rounding. No frame/epoch transform or implicit angle-unit conversion is performed.

## RK4 point-mass trajectories

Each record contains an independent six-component (position,velocity) state. The derivative is (v,-mu*r/(r²*sqrt(r²))) with increasing x,y,z reduction. For mu=0, acceleration is exactly zero even at the origin. For positive mu, every RK stage must have a positive representable denominator. dt>0 and steps 1..64. Initial state and every subsequent step are returned and checked, so transient errors cannot hide behind a correct endpoint.

Compute half_dt=RN32(dt*1/2), sixth_dt=RN32(dt/6). Evaluate k1=F(y), k2=F(y+half_dt*k1), k3=F(y+half_dt*k2), k4=F(y+dt*k3). For each component, sum `((k1+2*k2)+2*k3)+k4`; update y+sixth_dt*sum. All operations are RN32. This is a fixed-step Newtonian point-mass model, not an adaptive high-order ephemeris propagator. Step-size adequacy remains a scientific modeling choice.

## Search and execution

All six are generic compute workloads with 12 finite local/pack configurations each. None benefits from the current RT spatial candidate interface without changing its declared operator: fitting and filtering need all selected samples, and each orbit is independent central-force integration. AI relevance is metadata; AI_BACKEND_UNAVAILABLE remains explicit. Every tuning session begins with fresh Max Out mapping and no historical winners or rates. The common worker still verifies full current outputs even when using a tuned profile.
