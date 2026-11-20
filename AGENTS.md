# Instructions for AI agents working in this repository

## Start here
1. Read `HANDOFF.md` completely.
2. Read `research/AMSN_RESEARCH_DOSSIER.md`.
3. Read the latest dated entries in `research/RESEARCH_LOG.md` and the latest recovery/checkpoint note.
4. Inspect the current Git branch, latest commit and working tree before changing anything.

## Preservation rules
- This is the durable research record. Do not leave useful findings only in chat.
- Prefer adding dated/versioned files. Do not delete, force-push, reset history, or overwrite research logs.
- Never replace an existing file without first fetching and reviewing its current contents and blob SHA.
- Do not run destructive Git operations. Never commit credentials, access tokens, private keys, passwords or identifiable human/patient data.
- Record every commit SHA and verify every new or updated path with a read-back.

## Scientific integrity
- Label each statement as one of: literature/source observation, locally reproduced result, validated result, hypothesis, design proposal, or unverified historical claim.
- A README or handoff assertion is not proof that code ran.
- Do not claim tests passed unless the tests were actually executed; include the command, environment and output summary.
- Record data provenance, licenses, software versions, parameters, units, random seeds, run commands, raw outputs and limitations.
- Do not infer intelligence, consciousness or general cognition from a neuron-level metric such as FCI.
- Treat human cell parameters as cell-/region-/condition-specific, not universal constants.
- Keep negative results and failed experiments.

## Session closeout
Before ending a research session, create a dated log entry with:
- question and hypothesis;
- sources examined;
- exact work completed;
- files/code/data created;
- tests and commands actually run;
- results, uncertainty and limitations;
- commit SHA;
- next concrete experiment.

Then create a new dated handoff/checkpoint when the research direction or implementation status materially changes.