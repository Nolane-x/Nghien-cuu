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

### GitHub writes in this checkpoint
- `README.md` — initial commit `7e24a283e29169ef6c9702798ef1858caecf52d5`; subsequently updated to link the AI instructions and experiment template.
- `HANDOFF.md` — `63360012a1037628670e0e67d98103dd868b2c73`.
- `research/AMSN_RESEARCH_DOSSIER.md` — `3ebe7594ea1b46d5f21353ab701166a563863f83`.
- `research/AMSN_RECOVERY_STATUS_2026-11-20.md` — `449458cc1bba8363fc690d77194b07d5422d7da5`.
- `AGENTS.md` — `143b5de37d0056f35ff80ac7ee71468181d9fee9`.
- `research/EXPERIMENT_REPORT_TEMPLATE.md` — `b927a92e90926144c811ed97a1f5e324b34ab29f`.
- This log is being updated to include its own initial commit and final verification.

### Tests and verification performed
- GitHub repository metadata and default branch checked.
- Empty tree confirmed before first write.
- Local project paths, file sizes and directory contents inspected.
- All initial documentation files were read back from GitHub and their paths/blob SHAs confirmed.
- Latest Git tree was read back and contained all five research/handoff files plus `README.md` and `AGENTS.md`.
- No neuron simulation, package benchmark or pytest suite executed in this checkpoint.

### Next action
Reproduce the original Eyal et al. 2018 L2/3 neuron model in NEURON from its published source; save exact source version, environment, commands, output traces and validation metrics. Only after this baseline is reproducible should an alternative simulator or added biology be benchmarked.
