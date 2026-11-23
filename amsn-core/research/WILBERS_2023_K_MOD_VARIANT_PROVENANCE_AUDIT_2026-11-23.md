# Wilbers 2023 original K MOD variant provenance audit

**Date:** 2026-11-23  
**Dataset:** DataverseNL DOI 10.34894/L5J0SD, released version 3.0, CC0-1.0  
**Workflow:** [45144507180](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45144507180) — successful  
**Artifact:** [14803831434](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45144507180/artifacts/14803831434), SHA-256 `7e6e4855a390610313d2769ac87f90bf60b418f5e5e3126aacd92f33acc24e43`

## Scope and result

The audit fetched 9 immutable original K MOD files from Dataverse (canonical human plus eight variants), verified official file ID, SHA-1 and exact byte size, independently calculated SHA-256, parsed PARAMETER/RANGE declarations, compared the variants with canonical `k_human.mod`, and compiled all nine with NEURON 9.0.2.

<badge color="success">9/9 compiled</badge>

| Mechanism | Dataverse ID | Gates | Source role / structure |
|---|---:|---|---|
| `k_human` | 318647 | m,h1,h2 | Canonical human reference |
| `k_mouse` | 318649 | m,h1,h2 | Mouse species comparator |
| `k_human_h1` | 318627 | m,h | Reduced two-gate human variant |
| `k_human_hm12inf` | 318604 | m,m1,m2,h1,h2 | Alternate multi-gate human variant |
| `k_hybrid1` | 318628 | m,h1,h2 | Human G/Gmax activation + inactivation |
| `k_hybrid2` | 318622 | m,h1,h2 | Human G/Gmax activation |
| `k_hybrid3` | 318609 | m,h1,h2 | Human G/Gmax inactivation |
| `k_hybrid4` | 318619 | m,h1,h2 | Human activation time constant |
| `k_hybrid5` | 318605 | m,h1,h2 | Human G/Gmax activation + activation time constant |

The five hybrid source roles are taken from the original `channel_kinetics.py` helper, not inferred from model performance.

## Fitting provenance: an important boundary

The archived human K CMA driver groups fitted kinetic parameters as:

1. `thi1, thi2, qi1, qi2, Rd, Rg` — inactivation time-course kinetics.
2. `tha, qa, Ra` — activation time-course kinetics.
3. `th_act_inf, q_act_inf` — activation steady-state curve.

The published model's mixture/slow-inactivation parameters `prop_inact`, `prop_h2`, `h2tau_inact`, `h2tau_inact_rec` and `inact_rate_factor` are **not in the original fit vectors**. They are fixed mechanism parameters in the archived model, not parameters optimized by the CMA groups above.

This means the 200-AP sensitivity grid that varied `prop_inact` and `h2tau_inact` is useful to diagnose which state-mixture knobs influence use-dependent adaptation, but its best point is not a reproduction of the original authors' fitting process. In particular, the best tested point lies at the boundary of the local grid and still has an AP200 model value above the experimental mean. It must not be described as an identified biological parameter set.

## What this audit does not prove

- Successful NMODL compilation does not prove voltage-clamp kinetics or AP-clamp waveform agreement.
- The eight variants have not yet been replayed against the checksum-verified 200-AP H_wide command.
- No variant is promoted to AMSN runtime.
- Canonical human K source, human-fit defaults, Hines reference and production settings remain unchanged.

## Next gate

Replay each structurally compatible released K source variant under the exact same AP-clamp command, temperature, timestep, peak detector and normalization; report AP1–5 and AP1–200 against the 14 human and 11 mouse recording distributions. Variants with different state dimensions must be treated as distinct model structures, not parameter perturbations of the canonical m,h1,h2 mechanism. Then validate promising candidates against the original steady-state and kinetic voltage-clamp protocols before any candidate can be considered biologically defensible.
