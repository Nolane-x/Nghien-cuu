# Wilbers 2023 Dataverse v3 and NMODL source audit

**Date:** 2026-11-22 (Asia/Bangkok)  
**Dataset:** [DataverseNL DOI 10.34894/L5J0SD](https://doi.org/10.34894/L5J0SD), released version 3.0  
**Branch:** `research/wilbers-human-active-channel-baseline-2026-11-22`  
**Status:** selected source bytes inspected and hashed; no mechanism execution or biological reproduction claimed.

## Dataset identity and access

The official DataverseNL API resolves DOI 10.34894/L5J0SD to dataset ID 317867, released version 3.0 (internal version ID 24561), published 2022-11-10 and last updated 2022-12-13. The dataset declares CC0-1.0 and contains 65 files.

The inventory includes raw Figure 1–4 workbooks, AP-clamp traces and amplitudes, channel-fitting code, two distinct MOD folders, current-clamp code and conductance-density grids, and frequency-tracking data. A curated inventory with file paths, IDs, MIME types, byte sizes, official SHA-1 checksums and independently computed SHA-256 values is stored in `references/wilbers2023_dataverse_source_manifest_2026-11-22.json`.

Selected Na/K mechanism files and fitting/helper scripts were read from the Dataverse public object-store endpoints in an isolated research session and SHA-256 hashed. Their byte counts and SHA-1 values were cross-checked against the Dataverse file metadata API. The source bytes were not committed into AMSN. Numeric workbooks and the 15.1 MB AP-clamp `H_wide.csv` remain undownloaded; this manifest is a curated subset, not a 65-file mirror.

## Sodium mechanism — Figures5_6/MOD/na_human.mod

Dataverse file ID 318629; 3,602 bytes; SHA-1 `b199d70c3d0e7a2e991fd8d26c54b1318e3c0970`; observed SHA-256 `e23ed354aa683639bfd2ffdeae4b2544adf8c5cce6f8a4adbada42549310f2fd`.

The source comments describe an HH-style sodium channel based on Mainen (1994), edited by Kole (2006), then modified/fitted by René Wilbers at VU in 2020. It uses two gates `m,h`:

[
g_{Na}=tadj\,\bar g_{Na}m^3h,\qquad I_{Na}=10^{-4}g_{Na}(V-E_{Na}).
]

Steady-state activation/inactivation are separated from activation/inactivation time constants. Reference temperature is 25 °C, (Q_{10}=2.3), and the MOD file has an active 199-point `TABLE` over -120 to +100 mV. The fitting driver uses a 10 µm single-compartment section (`Ra=200`, `cm=1`) and sequentially fits inactivation/recovery, activation kinetics, and activation steady-state Vhalf/slope. The script's final parameter dictionary matches the distributed Na MOD values. Its voltage-clamp analysis runs steps from -80 to +10 mV in 5 mV increments at 25 °C.

## Potassium mechanism — Figures5_6/MOD/k_human.mod

Dataverse file ID 318647; 4,220 bytes; SHA-1 `d299b3430ecda7a94f6d1c37ac76b2878052c7d5`; observed SHA-256 `899aa0dfa697b7f735258e10b002c8876c108902afc0c13b82fc619decb66063`.

This is a mixed population of fast-, slow- and non-inactivating potassium channels. It uses `m,h1,h2`; default mixture values are `prop_inact=0.85`, `prop_h2=0.4`, `h2tau_inact=450 ms`, and `h2tau_inact_rec=2789.7929 ms`. Reference temperature is 34 °C and (Q_{10}=2.3). Unlike the sodium file, the `TABLE` directive in the distributed potassium MOD is commented out.

The fitting driver uses test steps from -110 to +50 mV in 10 mV increments and a long recovery protocol. **A parameter-provenance discrepancy remains unresolved:** its intermediate inactivation-fit dictionary matches the distributed MOD, but a later dictionary labelled “final best fit” reports different values for `thi1, thi2, qi1, qi2, Rd, Rg`. The driver also sets `h12factor=10.5`, while the distributed MOD comments out the `h1tau*h12factor` expression and uses fixed slow-inactivation/recovery time constants. No K kinetic snapshot is selected as definitive.

## Separate current-clamp variants

The dataset also contains `na_human.mod` and `k_human.mod` under `Figures5_6/Current_clamp/mod`. These are different Dataverse file records with different hashes; they add global conductance scaling and human-fraction variables `na_human_ratio` and `k_human_ratio`. They must not be silently substituted for the `Figures5_6/MOD` variants used for the channel comparison.

The current-clamp helper initializes a 10 µm compartment at 34 °C, inserts both human and mouse mechanisms and adjusts reversal potentials/voltage offsets for liquid-junction potentials. Its Powell gbar fit uses a target constructed as a **50:50 average of human and mouse median AP amplitude, upstroke and downstroke**. The resulting conductance densities are therefore not a human-only fit. The K voltage-clamp helper's recovery target is also explicitly the mean of human and mouse values.

## High-priority source-level warning — trap0

Both canonical human MOD files contain a `trap0` implementation where:

- the branch condition tests `fabs((v+th)/q)`;
- the main quotient uses `a*(v-th)/(1-exp(-(v-th)/q))`;
- the commented intended limit is `a*q`;
- the active fallback is `q*(1--(v-th)/q/2)`, omitting multiplier `a`.

At (v=th), the main expression has a removable (0/0) limit, but for nonzero `th` the current branch condition does not select that limit. The active fallback also does not equal the standard (a q) limit. This is a source-level numerical warning, **not yet a proven simulation failure**. The Na MOD uses tabulated rates while K calculates rates directly, so the runtime consequences may differ.

Before porting, compile the original mechanisms and probe values at (v=th-\epsilon), (v=th), and (v=th+\epsilon), comparing with a stable analytic reference and the published voltage-clamp protocols. Do not patch the source and claim equivalence without that comparison.

## Verification state and next gates

Verified: dataset DOI/version/license/file count, selected file metadata, source bytes, and selected SHA-256 digests. Inspected: original Na/K MODs, current-clamp variants, Na/K fitting drivers, channel tools and current-clamp helpers.

Not yet completed: NEURON compilation/execution of the original MOD files, reproduction of channel voltage-clamp/AP-clamp traces, downloading the raw numerical workbooks/AP-clamp matrix, or integrating a mechanism into AMSN.

1. Download and SHA-256 verify the numerical workbooks and AP-clamp trace file.
2. Compile the unchanged original Na/K MOD files with the pinned NEURON version.
3. Test the `trap0` singular points against a stable analytic reference.
4. Reproduce Na/K activation, inactivation, recovery and AP-clamp protocols at the published temperatures.
5. Resolve the K parameter-snapshot mismatch and mixed-species fitting objectives.
6. Only then implement an opt-in human somatic channel mechanism. Do not infer AIS, axonal or dendritic densities from soma measurements.

A dedicated GitHub Actions source audit was added to re-download the exact canonical MOD files, verify SHA-256, compile with NEURON 9.0.2 and probe near source-declared characteristic voltages. The first workflow result is pending. No human mechanism was added to AMSN runtime and no production defaults were changed.


## First compiled NEURON result — 22/11/2026

GitHub Actions run [45039313143](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45039313143) completed successfully on Python 3.12 / NEURON 9.0.2. All 11 provenance-registry tests passed. Both original Dataverse MOD files were downloaded again, their SHA-256 values matched the pinned manifest, and both compiled and loaded into NEURON.

The initial point probe found:

- NaV source: all 9 tested exact/near-positive-singularity observations were finite. This is not proof of correctness; the Na mechanism uses a 199-point TABLE.
- KV source: non-finite time constants were observed exactly at `tha=-29.9618 mV` (`mtau`), `thi1=40.5659 mV` (`h1tau`) and `thi2=-75.9382 mV` (`h1tau`). At the immediately adjacent ±0.00001 mV values, the same observables were finite.

The source workflow therefore proves successful compilation but exposes a real pointwise runtime singularity in the unmodified potassium mechanism. It does not yet prove how often the singularity is encountered in physiological voltage trajectories or how much it distorts the published protocols. An extended comparison now compiles a temporary corrected `trap0` clone for diagnostic reference only, probes both +th and -th as well as the published command-voltage grids, and requires the diagnostic clone to maintain finite positive time constants. The original Dataverse source remains unchanged; the corrected clone is not accepted for production.

The first workflow artifact is [`wilbers-original-nmodl-source-audit`](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45039313143/artifacts/14764015969). The run's artifact ZIP SHA-256 is `31a5883d6cb46670b3b8795afc7fa656ba0632ef544db2b328e922921ce82658`.


## Extended original-vs-stable `trap0` comparison — 23/11/2026

Workflow [45115543259](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45115543259) passed after the registry assertions were synchronized with the already verified NEURON compilation. It compiled both the unmodified source and a separate diagnostic-only clone whose `trap0` branch uses `v-th` and whose limiting expansion is (a q(1+(v-th)/(2q))). Original source files remain unchanged.

The extended audit tested both signs of each characteristic voltage, adjacent points at ±0.00001 mV, and the discrete command-voltage grids listed in the original fitting helpers:

- Na: 41 points, 19 command test voltages. Original and diagnostic rates were identical at exported precision at every probe; all original and diagnostic time constants were finite and positive.
- K: 38 points, 17 command test voltages. The original mechanism has three non-finite time-constant points at the positive source singularities: `mtau` at -29.9618 mV; `h1tau` at +40.5659 mV and -75.9382 mV.
- The mirror-branch defect also creates negative K `h1tau`: -0.072506 ms around -40.56590 mV, and -0.013253 ms at +75.9382 mV. At +29.9618 mV, original K `mtau` is 0.075868 ms versus 0.903835 ms for the stable diagnostic clone (91.61% relative difference).
- On the *discrete static test-voltage samples* in the archived fitting scripts, K source and diagnostic outputs agree at the exported precision and all original time constants are positive. This does not prove full time-domain clamp equivalence: dynamic membrane voltage passes through values between those test steps, and raw trace replay has not yet been performed.

The stable clone is only a mathematical diagnostic comparator. It is not the published source, not a validated fix, and not eligible for AMSN runtime. See the complete point-level JSON artifact [14790704932](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45115543259/artifacts/14790704932) (artifact ZIP SHA-256 `c53df1ef02993fddc2ee466203c700e949e36cc71a0e2cfb74ab25ac07fec7d3`).
