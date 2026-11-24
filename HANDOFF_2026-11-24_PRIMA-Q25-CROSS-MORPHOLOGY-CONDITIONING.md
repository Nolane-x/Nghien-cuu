# Handoff — Cross-morphology PRIMA q25 basis conditioning audit

**Date:** 24 November 2026  
**Branch:** research/prima-cross-morphology-q25-conditioning-audit-2026-11-24  
**Parent:** Tamas q25 replication branch / PR #20

## Research question

The dual-q25 layout produced a 14.525× median shared-output error ratio at order 168 on the NMO_163775 Peng mouse morphology, but only 1.001× on the NMO_107159 Tamas human pyramidal morphology. This audit measures basis orthogonality, the condition number of the basis Gram matrix (V^T V), reduced G/C spectra, generalized passive RC decay-rate ranges and initial multi-shift seed allocation to check whether structural metrics track the morphology-by-order difference.

## Scope

Two separately held morphologies, four layouts (7, basal-only 8, apical-only 8, dual-q25 9), basis orders 112/168 and all nine passive parameter scenarios. The audit creates 144 reduced models, 1,152 per-port leverage rows and 864 initial shift-seed rows. It uses the existing validated source SHA-256 values and reruns both preflights. No transient matrix is replayed and no production solver default is changed.

## Validation contract

Expected exact counts: 144 model metric rows, 1,152 port leverage rows and 864 shift-seed rows. The workflow verifies both source hashes, reruns both Import3D preflights, executes dedicated tests, checks finite values and positive-definite projected matrices, and archives CSV/JSON outputs plus timing data. No numerical conclusion is claimed before CI success and read-back of the generated files.

## Scientific constraints

This is a numerical diagnostic of passive linear-RC reductions on two individual reconstructions, not a biological or population-level claim. Orthogonality and positive definiteness do not guarantee transient approximation quality; reduced-matrix condition numbers and seed allocation do not by themselves prove the cause of transient-error differences. Full Hines remains canonical.
