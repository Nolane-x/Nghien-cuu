# Research log — initial checkpoint

## 2026-11-20 — Repository initialized and AMSN handoff committed

### Goal
Preserve the neuronal simulation research so a future AI session can continue without relying on chat history.

### Repository state before writes
- Repository: https://github.com/Nolane-x/Nghien-cuu
- Default branch: `main`
- GitHub reported `size: 0` and the Git tree endpoint returned 409 “Git Repository is empty”.
- Permissions reported admin/push access.
- No prior file was overwritten or deleted.

### Local artifacts inspected
- `/mnt/data/AMSN_research_dossier_v1.md` — 32,586 bytes, 340 lines.
- `/mnt/data/amsn_alpha/README.md` — 9,341 bytes, describing Alpha 0.2.0a2.
- `amsn/`, `tests/`, `scripts/`, `docs/`, `results/`, `data/` under `/mnt/data/amsn_alpha/` were empty at inspection.
- Three PNG plots were found in a temporary mounted directory, outside the normal project results folder; no reproducible source data was present alongside them.

### Research content carried forward
- Human cortical layer 2/3 pyramidal neuron as pilot cell type.
- FCI source reconnaissance: valuable morphology/synaptic integration baseline, not a complete multiphysics neuron.
- BRAINCELL source reconnaissance: relevant NEURON-based neuron/astrocyte/synapse/extracellular framework; audit incomplete.
- MOOSE, NEURON-RxD, STEPS, MCell, Jaxley, Arbor, COPASI and standards mapped to likely roles.
- AMSN architecture, known gaps, validation gates V0–V10, and experiments A–E documented in dossier.

### Important correction
The Alpha README claims “69 passing tests” and describes multiple executable modules. Those claims could not be verified because the corresponding source/test directories were empty. Do not repeat them as current results. The next session should recreate or retrieve code, run tests and record actual output.

### GitHub writes
- `README.md` created — commit `7e24a283e29169ef6c9702798ef1858caecf52d5`.
- `HANDOFF.md` created — commit `63360012a1037628670e0e67d98103dd868b2c73`.
- This research dossier and recovery note are being added in this checkpoint.

### Tests performed
- GitHub repository metadata inspection.
- Local filesystem/path and file-size inspection.
- No neuron simulation, package benchmark or pytest suite executed in this checkpoint.

### Next action
Reproduce the original Eyal et al. 2018 L2/3 neuron model in NEURON from its published source; save exact source version, environment, commands, output traces and validation metrics. Only after this baseline is reproducible should an alternative simulator or added biology be benchmarked.
