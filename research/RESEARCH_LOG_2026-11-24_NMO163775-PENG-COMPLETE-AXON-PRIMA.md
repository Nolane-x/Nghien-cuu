# Research log — third PRIMA morphology holdout: NMO_163775

**Date:** 24 November 2026  
**PR:** #16  
**Source:** NeuroMorpho.Org NMO_163775, Peng archive

A third independent morphology was selected to extend the matched port-count × morphology test beyond two individual human morphologies. NMO_163775 is a mouse somatosensory neocortical layer 2–3 pyramidal IT projection cell, Control condition, 56 days, Cux2-CreERT2;Ai166. NeuroMorpho metadata marks dendrites and axon complete, but lists Morphological Attributes as No Diameter.

The standardized source was extracted into the repository with numeric node records unchanged and an attribution/provenance header. Repository file SHA-256: 94eb448c2d70b6dfa78322df8a18013d0899e0908cd203b79c4a7a9a954dd00f. It has 4,209 records: soma 3, axon 3,602, basal 306 and apical 298; one root; all nodes reachable; no duplicates or missing parents.

The AMSN/Import3D preflight passed with 4,200 electrical compartments, 251 sections, 82,587 NEURON segments and maximum segment length 0.4999943591 µm under a 0.5 µm cap. The actual AMSN mapper reports seven shared SWC IDs {1,40,144,3926,3948,4104,4180}. The q25 identities are computed and pinned in preflight; replay must reproduce them exactly. A prior manual path-distance calculation yielded different seven-port IDs, and was discarded in favor of the project's actual Import3D mapper.

The matched seven/nine-port order112/order168 replay is configured for six extended10kHz shifts, nine deterministic passive parameter scenarios, nine AC frequencies, three source locations and two pulse widths. Expected coverage: 36 models, 324 AC rows, 1,728 transient rows, 756 shared pairs, 216 q25 observations and 378 common-Hines checks. Same 0.5 µm mesh for seven/nine layouts. This mesh differs from the two earlier human holdouts' 0.125 µm cap, so absolute metrics are not directly comparable across morphologies.

Critical interpretation guard: because NeuroMorpho marks No Diameter, the SWC radii cannot be called measured biological diameters. This is a passive topology/port-selection test under the repository's standardized geometry representation, not diameter-grounded biological validation.

Validated run 45311916600: 173/173 full-suite tests passed; 19/19 Peng-specific tests passed; checksum and Import3D preflight passed; all 36 model builds and matched replay passed; 378 shared Hines traces were exactly identical; result archive and artifact upload passed. Artifact #14883752560; ZIP SHA-256 9060b04e6e769a1e9b40700197361bf67a59b164965441849e8cd3effb716a58.

At order112, nine-port was worse on all 378 shared pairs, with median 9/7 error ratio 78.051×; maximum absolute nine-port shared NRMSE was 0.0001933%. At order168, nine-port was worse on 347/378 and better on 31, with median ratio 14.501×; maximum absolute nine-port shared NRMSE was 6.0657e−7%. These large ratios reflect a very small seven-port baseline; they must be interpreted alongside absolute errors.

The q25-only nodes were basal 224 and apical 4096. q25 maximum NRMSE was 2.1588e−4% at order112 and 4.2824e−7% at order168. Coverage: 36 models, 324 AC rows, 1,728 transient rows, 756 shared pairs, 216 q25 observations and 378 exact shared-Hines checks.

Across the three morphology holdouts, the relative cost of q25 ports differs substantially. The evidence does not support a universal port-count/order rule. The Peng mesh cap is 0.5 µm (earlier human holdouts used 0.125 µm); NeuroMorpho marks No Diameter, so this is not diameter-grounded biological validation. No production defaults or canonical Hines behavior changed.
