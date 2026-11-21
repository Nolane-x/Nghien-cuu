# Research log — Segev AC probe-coordinate mesh convergence — 2026-11-21

## Question

Do the site-dependent effects of complex-linear probe interpolation persist, shrink or change non-monotonically as the NEURON mesh is refined from 0.25 to 0.0625 µm?

## Motivation: verified 0.125 µm experiment

Workflow 44901688035 passed 2/2 morphology jobs on NEURON 9.0.2 (120 rows each), and Core CI 44901673896 passed.

At 0.125 µm:
- Exact-SWC vs nearest segment-centre Impedance.transfer() was identical at exported precision in all rows.
- Maximum complex interpolation shift: NMO_68174 apical q90 0.057785%; NMO_68175 apical q50 0.095872%.
- Cross-simulator rejoin:
  - NMO_68174 exact-SWC median/p95/max 0.001555/0.049634/0.130599%; interpolated 0.000670/0.046984/0.132786%. 26 improved, 70 worsened, 24 unchanged.
  - NMO_68175 exact-SWC 0.002297/0.073495/0.169222%; interpolated 0.001105/0.059094/0.125637%. 64 improved, 32 worsened, 24 unchanged.
- NMO_68175 basal q75 → apical q50 at 3 kHz improved from 0.169222% to 0.077077%, while some basal paths worsened.

These are not enough to adopt interpolation. They motivate mesh convergence.

## Method

Run human_segev_ac_probe_coordinate_audit.py unchanged except for mesh-cap configuration on both morphologies at 0.25, 0.125 and 0.0625 µm. Output CSVs include neuron_max_segment_um so mesh identity is self-contained.

## Expected outputs

Six jobs, 120 rows per job, 720 rows total. Raw artifacts contain CSVs and logs. The exact-SWC source coordinates, five probes, eight frequencies and passive parameters remain fixed.

## Verification

Pending GitHub Actions. Do not state mesh trends until all six jobs pass and raw data are inspected.

## Interpretation limits

Linear interpolation is an alternative readout, not a proven exact continuous-space solution. The effect may be morphology-, probe-, source-, frequency- and mesh-dependent. Keep all rows, including worsened and unchanged comparisons. Do not retune passive parameters.


## Verified results — six-mesh matrix complete

Workflow [44902130621](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44902130621) passed 6/6 jobs. Every job ran 81 tests, used NEURON 9.0.2, emitted 120 rows and uploaded raw CSV/log. Core CI [44902130609](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44902130609) passed 4/4 jobs. The six artifacts are 14706705700 (68174/0.25), 14706511545 (68174/0.125), 14706785100 (68174/0.0625), 14705604235 (68175/0.25), 14705544460 (68175/0.125) and 14706168324 (68175/0.0625).

Exact-SWC vs nearest-centre impedance was identical at exported precision for all 720 rows. The maximum interpolation-to-exact shift fell strongly between 0.25 and 0.0625 µm in both cells (68174: 0.213915%→0.041671%; 68175: 0.209515%→0.042864%), but its cross-simulator benefit was not monotone or universal.

At 0.0625 µm, NMO_68174 interpolated median/p95/max error improved from 0.001221/0.053004/0.133955% to 0.000253/0.033139/0.132166%. NMO_68175 worsened from 0.003012/0.059626/0.099512% to 0.003131/0.066941/0.104835%. Thus interpolation is diagnostic-only; exact-SWC remains canonical.

Full report: [HUMAN_SEGEV_AC_PROBE_MESH_SWEEP_2026-11-21.md](../research/HUMAN_SEGEV_AC_PROBE_MESH_SWEEP_2026-11-21.md). Summary table: [CSV](../results/human_segev_ac_probe_mesh_sweep_summary_2026-11-21.csv).
