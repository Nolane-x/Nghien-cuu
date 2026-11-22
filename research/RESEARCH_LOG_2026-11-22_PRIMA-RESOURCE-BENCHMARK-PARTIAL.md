# Research log — partial runtime/RSS resource benchmark

**Date:** 2026-11-22  
**Workflow:** https://github.com/Nolane-x/Nghien-cuu/actions/runs/45012282723  
**Head:** 5180f0bc72dbfad0a460b0870ca80fec772db0e3

The workflow matrix defines 36 resource jobs: 3 morphologies × 2 NEURON mesh caps × orders84/112/168 × 2 replicates, plus a dedicated 16-test validator preflight.

Twelve artifacts are currently available for NMO_68174 cell1125: two mesh caps × three orders × two replicates. All 12 ZIP SHA-256 digests match GitHub metadata; each archive's raw sweep CSV contains 210 rows (30 frequency, 162 per-port transient, 18 all-port transient), and each run/time record reports exit status 0. Every result contains the order-56 control plus the requested higher order with rank achieved. These 12 artifacts contribute 2,520 raw sweep rows.

Median wall/CPU/peak-RSS metrics are recorded in the partial report. The early pattern: peak RSS is more sensitive to NEURON reference mesh cap than PRIMA order in this one morphology; user CPU rises as PRIMA order increases. Wall time is not monotonic across candidate orders in two replicates on heterogeneous cloud CPU models.

This is a partial one-morphology result, not a completed matrix and not a universal resource ranking. The remaining two morphologies and resource jobs must be completed and artifact hashes inspected before choosing a production configuration. No defaults change; full Hines remains canonical.
