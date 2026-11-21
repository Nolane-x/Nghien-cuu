# Human AMPA axial-resistance matched-support audit

**Date:** 2026-11-21 (UTC+7)  
**Code commit:** [56a731c156db32f6beb35b813e177039d739a850](https://github.com/Nolane-x/Nghien-cuu/commit/56a731c156db32f6beb35b813e177039d739a850)  
**Workflow:** [44870476391 — successful](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44870476391)  
**Raw data:** [human_ampa_axial_resistance_2026-11-21.csv](../results/human_ampa_axial_resistance_2026-11-21.csv)  
**Workflow artifact:** [14693647848](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44870476391/artifacts/14693647848)

## 1. Research question and falsifiable hypothesis

The previous AMPA comparison left a small cross-engine voltage residual after timestep convergence, probe-location interpolation checks and matched-support membrane-area checks. This audit asks whether a mismatch in the axial geometry integral on the same electrical control-volume support could explain that residual.

**Hypothesis:** if AMSN and NEURON represent the same SWC cable geometry and the same half-edge support consistently, their axial geometry factors should closely agree. A material difference would identify a candidate geometry/discretization source that must be investigated before changing solver parameters.

This is a numerical geometry audit. It does not fit biological parameters or compare EPSP waveforms.

## 2. Provenance and reference implementation

- Morphology: NeuroMorpho.Org NMO_290988, `1094_Mohan_etal_2015.CNG.swc`. Repository provenance metadata records its source and CC BY 4.0 attribution. The available reconstruction is partial (soma and dendrites, no axon; moderate dendritic completeness; source metadata describes mesiotemporal sclerosis). Do not generalize it to all human pyramidal neurons.
- Reference simulator: NEURON 9.0.2, installed as an exact version pin in GitHub Actions.
- NEURON implementation inspected: [NEURON 9.0.2 `src/nrnoc/treeset.cpp`](https://github.com/neuronsimulator/nrn/blob/9.0.2/src/nrnoc/treeset.cpp). In this version, `ri()` returns the resistance between the centre of a segment and the centre of its parent segment; the pt3d geometry path integrates resistance over the left/right half-segment spans before combining them.
- This experiment uses the repository's existing `neuron_cross_validation.py` Import3D path and the same underlying human SWC data as AMSN.

## 3. Model and method

For a circular cable with linearly varying diameter from (d_0) to (d_1), the axial geometry factor is

[
G = \int \frac{ds}{\pi r(s)^2}
  = \frac{4L}{\pi d_0d_1}.
]

The factor is reported in m⁻¹ when dimensions are converted to SI. The corresponding axial resistance is (R_i G), where (R_i=0.7\;\Omega\,m). The audit computes the taper integral on each underlying SWC piece, so a support spanning multiple SWC edges is integrated piece by piece.

For each preserved electrical site:
1. Identify the incoming and outgoing AMSN electrical edges.
2. Define the local control-volume support as half the incoming edge plus half the outgoing edge.
3. Integrate the two AMSN half-supports separately on the original SWC taper geometry.
4. Map the same arc-length support to the corresponding NEURON Import3D section.
5. Independently integrate NEURON's pt3d diameter profile over that support.
6. Reconstruct the NEURON network resistance by summing actual `segment.ri()` values between adjacent segment centres inside the support and integrating only the two partial endpoint caps directly.
7. Check that NEURON's segment-level `ri()` values reproduce the pt3d integral and that the network-plus-cap result reproduces the direct support integral.

The audit rejects a site if its parent, site and child do not map to one ordered NEURON section. It therefore does not silently approximate branch points or section joins.

## 4. Environment and parameters

| Item | Value |
|---|---|
| GitHub runner | Ubuntu 26.04.1 |
| Python | CPython 3.12.16 |
| NEURON | 9.0.2 |
| NumPy | 2.5.5 |
| Axial resistivity | 0.7 Ω·m |
| NEURON maximum segment length | 0.5 µm |
| NEURON reference segments | 25,233 |
| AMSN reference frequencies | 2,000 / 4,000 / 6,000 Hz |
| AMSN compartment counts | 2,540 / 3,525 / 4,287 |

Run commands from `amsn-core/`:

```bash
python -m pip install -e ".[test]"
python -m pip install --only-binary=neuron "neuron==9.0.2"
python examples/human_ampa_axial_resistance_audit.py
```

The workflow itself ran the script successfully and preserved its stdout as an artifact. The exact raw 15-row CSV is also committed alongside this report.

## 5. Measurement sites

| Label | SWC node | NEURON section |
|---|---:|---|
| Basal q75 source (existing point) | 3784 | dend[54] |
| Basal q90 (existing point) | 3814 | dend[54] |
| Other basal branch q75 | 2986 | dend[42] |
| Apical q75 | 5078 | apic[20] |
| Apical q90 | 4665 | apic[17] |

New basal/apical quantiles are selected deterministically from internal unbranched points for which parent, site and child map to one ordered NEURON section. The two established basal sites are retained to connect the new audit to the previous AMPA work.

## 6. Results

### Relative difference in axial geometry factor

Values below are ((G_{AMSN}-G_{NEURON})/G_{NEURON}\times100\%). Positive values mean AMSN's factor is larger; negative values mean it is smaller.

| AMSN reference frequency | Compartments | Basal q75 (3784) | Basal q90 (3814) | Other basal (2986) | Apical q75 (5078) | Apical q90 (4665) |
|---:|---:|---:|---:|---:|---:|---:|
| 2,000 Hz | 2,540 | +0.0000115922% | +0.0000036281% | +0.0000025775% | +0.0000008515% | -0.0002396760% |
| 4,000 Hz | 3,525 | +0.0000090496% | +0.0000036281% | +0.0000025775% | +0.0000008515% | -0.0001628496% |
| 6,000 Hz | 4,287 | +0.0000073090% | +0.0000036281% | +0.0000025775% | +0.0000008515% | -0.0001288341% |

### Internal consistency checks

| Check | Observed maximum across 15 rows | Audit gate | Outcome |
|---|---:|---:|---|
| Actual NEURON `segment.ri()` vs its pt3d-derived centre-to-centre integral | 5.7433 × 10⁻¹²% | 1 × 10⁻⁷% | Pass |
| NEURON network reconstruction vs direct support integral | 6.0730 × 10⁻¹³% | 1 × 10⁻⁷% | Pass |
| Mapped support-length mismatch | 4.6431 × 10⁻¹³% | 1 × 10⁻⁵% | Pass |
| Number of measurement rows | 15 | 15 expected | Pass |

The largest absolute AMSN/NEURON factor difference is 0.0002396760% at apical q90 on the 2,000-Hz mesh. At the 6,000-Hz mesh it is 0.0001288341%. The other four sites remain within approximately 0.0000116%.

## 7. Interpretation

**Locally reproduced result:** in this exact morphology, support definition, Import3D mapping and NEURON 9.0.2 configuration, the matched-support axial geometry integrals agree to a maximum relative difference below 0.00024%. The independent use of NEURON's actual `segment.ri()` values also agrees with the pt3d-derived integral at near machine precision.

**Interpretation, limited to this experiment:** a large error in the axial taper integral at these five tested unbranched sites is unlikely to explain the remaining AMPA voltage residual by itself. The result narrows the search; it does not eliminate errors at branch junctions, section connections, soma representations, terminals, or in the full time-dependent cable matrix.

The larger relative difference at apical q90 is still very small and falls as the AMSN reference frequency increases. The experiment does not separately identify the cause of that tiny residual. Do not attribute it to floating-point rounding or mapping without a dedicated isolation test.

The thresholds above are implementation sanity gates for this audit, not scientifically established biological acceptance tolerances.

## 8. Limitations and what was not tested

- One partial morphology and one simulator version.
- Five unbranched control sites; no branchpoint, soma-junction or terminal-support audit.
- No membrane voltage, synaptic current or experimental EPSP trace was evaluated here.
- No biological parameter fitting or biological validation was performed.
- The result is not evidence that one mesh frequency is globally optimal.
- The NEURON pt3d path and SWC-derived AMSN path are two representations of one imported reconstruction; importer or coordinate effects have not been isolated as a separate cause.
- The audit validates a local support geometry calculation, not all entries of the global cable conductance matrix.

## 9. Next experiments

1. Audit the full AMSN/NEURON axial edge and junction conductance matrix, including branchpoints, parent-child section connections, soma attachment and terminal edges. Report every mapping/support exception instead of dropping it.
2. Repeat the critical basal/apical AMPA waveform comparison after the full edge audit, retaining the same timing and spatial baselines.
3. Then prioritize a reproducible reproduction of the published Eyal et al. 2018 human L2/3 NEURON/ModelDB 238347 baseline with its own matched morphology and mechanisms. Keep this distinct from the NMO_290988 engineering fixture.
4. Only after the matched published baseline is stable should the project expand into calibrated NMDA voltage-dependent Mg²⁺ block, calcium microdomains and plasticity.

## 10. Reproducibility record

- Script: `amsn-core/examples/human_ampa_axial_resistance_audit.py`.
- Workflow: `.github/workflows/amsn-ampa-axial-resistance-audit.yml`.
- Workflow run: [44870476391](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44870476391), successful.
- Artifact: [14693647848](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44870476391/artifacts/14693647848).
- Code commit: `56a731c156db32f6beb35b813e177039d739a850`.
- Raw data: `amsn-core/results/human_ampa_axial_resistance_2026-11-21.csv`.


## Comprehensive AMSN Core CI — final verification

Workflow [44870476392](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44870476392) completed with conclusion **success** on the same code commit `56a731c156db32f6beb35b813e177039d739a850`.

All four jobs completed successfully:
- Unit/numerical test matrix: Python 3.12 — 65 passed; Python 3.13 — 65 passed.
- NEURON cross-validation: Python 3.12 — all steps successful.
- NEURON cross-validation: Python 3.13 — all steps successful.

The two test jobs also compiled all Python modules and ran the configured examples. Both NEURON jobs completed passive cross-simulator, temporal/spatial convergence, transient pulse/step, AMPA-like conductance, Exp2Syn timing and matched single-compartment voltage/current checks. The dedicated axial audit remains independently green in workflow [44870476391](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44870476391).

