# Research log — 2026-11-20 — human morphology CI verification

The human L2-3 morphology integration was committed in `869e4faa80c6cf4145cd0a176c1000aad5ed0964`. GitHub Actions initially found one outdated synthetic test expecting the soma/root to count as a neurite bifurcation. Changed that expected count from 2 to 1 in commit `6b99618f8b6d76d6bb0f8c943500db8c6804d2d9`.

Final CI run 44737462769 succeeded:
- Python 3.12.16: 33 passed in 0.98 s.
- Python 3.13.18: 33 passed in 1.54 s.
- Both jobs passed installation, pytest, compileall and all examples.
- Human SWC example parsed all 8,903 nodes and printed 12,610.981 µm neurite path, 58 bifurcations and 8 stems.

The initial fail and correction are retained in Actions history. No rollback was needed.

This is verification of morphology parsing/comparison and code integration only. It is not a human electrophysiology reproduction. Next: multiple stimulation/recording locations in a passive cable built from the real SWC, then cross-simulator validation.
