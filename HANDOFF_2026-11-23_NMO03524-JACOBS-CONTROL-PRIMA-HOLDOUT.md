# Handoff — NMO_03524 Jacobs control PRIMA holdout

**Date:** 23 November 2026  
**Branch:** \`research/prima-jacobs-control-independent-holdout-2026-11-23\`  
**Base:** PR #13 head \`c3888f5655f70f473ffc5d0a27bb38c2ebc53849\`

## Goal

Add a second external human morphology for passive PRIMA shift/order validation, distinct from the NMO_162186 epilepsy specimen. This specimen is published as Control and is from the Jacobs archive.

## Current source checks

- NeuroMorpho ID: NMO_03524; cell 1-5-3.
- 23-year-old male; temporal? No: occipital neocortex, Brodmann area 18.
- Human pyramidal principal cell, control, in vitro, Golgi.
- Soma + dendrites + incomplete axon; dendrites rated moderate.
- Initial SWC inventory: 869 records, one root, no missing parents; type counts 1:3, 2:42, 3:816, 4:8.
- Seven unique PRIMA ports were not yet executed locally; CI preflight checks them after Import3D.

## Implementation

- Download original standardized SWC from the official NeuroMorpho direct file URL.
- Recompute SHA-256, bytes, topology and type counts in the CI preflight.
- Run NEURON 9.0.2 Import3D with 0.125 µm segment cap.
- Verify seven unique PRIMA ports and 1 kHz passive response.
- Run the existing nine-candidate seven-port shift/order matrix on identical passive scenarios/protocol.
- Verify 81 model rows, 729 frequency rows and 3,402 transient-port rows; commit results and upload artifact.

## Status

Numerical replay and exact source hash are pending the Actions workflow. No result is claimed until CI, full matrix coverage and artifact archival pass.

## Scientific boundary

Single control-condition morphology; moderate dendrites; incomplete axon. This is passive linear-RC validation only. No active-channel, nonlinear-synapse or population-level biological claim. Full Hines remains canonical.
