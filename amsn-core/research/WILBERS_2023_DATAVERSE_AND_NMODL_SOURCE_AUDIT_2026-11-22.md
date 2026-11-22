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

No human mechanism was added to AMSN runtime and no production defaults were changed.
