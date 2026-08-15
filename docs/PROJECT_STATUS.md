# Project Status

## Current Phase

Phase 1: Literature and Dataset Audit.

## Completed Work

- Initialized the local Git repository on branch `main`.
- Created the initial repository directory structure.
- Added initial repository documentation and ignore rules.
- Connected the local repository to the GitHub remote `https://github.com/cacacacc/robust-entity-matching.git`.
- Created the first commit: `c70cb51 Initialize research project structure`.
- Added Phase 0 concept explanation, research-question review, scope boundaries, and feasibility judgment.
- Checked Python, Git, repository status, and document structure.
- Started Phase 1 with an initial audit of two core papers and official dataset sources.
- Updated `docs/LITERATURE_NOTES.md` with source-grounded notes on class ratio and unseen-entity evaluation.
- Updated `docs/DATASET_AUDIT.md` with initial dataset suitability notes for WDC Products, CompERBench, and WDC LSPM.
- Updated `docs/EXPERIMENT_PROTOCOL.md` with audit-derived draft constraints.

## Verification Results

- Git is installed.
- Git version: `2.51.0.windows.2`.
- Python is installed as `python`.
- Python version: `3.11.9`.
- Windows `py` launcher is not available in the current shell.
- The workspace was initially empty.
- The workspace is now a local Git repository.
- The current branch tracks `origin/main`.
- Git reported a `dubious ownership` warning because the repository was initialized by the sandbox user while the normal Windows user is `Catherine`. This can be fixed by adding the workspace to Git's safe directory list.
- Git also reported a warning that `C:\Users\Catherine/.config/git/ignore` could not be accessed due to permission restrictions. Repository-local `.gitignore` is present and usable.

## Current Issues

- No Python environment has been created yet.
- No datasets, code, tests, or experiments have been added yet.
- Dataset selection is not locked yet.
- No data files have been downloaded yet.
- WDC Products appears strongly aligned with RQ2 and RQ3, but actual file schema still needs local inspection.
- CompERBench appears useful for RQ1 and baseline experiments, but entity ID support still needs local inspection.

## Next Milestone

Phase 1 next milestone: inspect small sample or benchmark files for WDC Products and one CompERBench task, then decide the first two MVP datasets.

## Key Commands

```powershell
git config --global --add safe.directory D:/code/robust-entity-matching
git status --short --branch
git remote -v
python --version
git --version
```

## Latest Phase 1 Sources Checked

- Foxcroft, Christen, and Antonie, `Class Ratio and Its Implications for Reproducibility and Performance in Record Linkage`: https://users.cecs.anu.edu.au/~Peter.Christen/publications/foxcroft2024ratio.pdf
- Foxcroft, Sartor, and Antonie, `Comparing Traditional and Deep Learning Approaches for Product Matching: Performance on Unseen Entities`: https://assets.pubpub.org/izpipo2h/189-51747605873107.pdf
- WDC Products benchmark official page: https://webdatacommons.org/largescaleproductcorpus/wdc-products/index.html
- CompERBench official page: https://data.dws.informatik.uni-mannheim.de/benchmarkmatchingtasks/
- WDC LSPM v2 official page: https://webdatacommons.org/largescaleproductcorpus/v2/

## Files Created So Far

- `README.md`: public-facing project overview.
- `AGENTS.md`: collaboration and research-integrity rules.
- `.gitignore`: prevents local data, outputs, caches, and environments from being committed.
- `requirements.txt`: placeholder for future locked dependencies.
- `docs/PROJECT_BRIEF.md`: project motivation, RQs, scope, and success criteria.
- `docs/PROJECT_STATUS.md`: truthful current state and next milestone.
- `docs/DECISIONS.md`: important decisions and rationale.
- `docs/EXPERIMENT_PROTOCOL.md`: draft experiment protocol.
- `docs/PHASE_0_FOUNDATION.md`: Phase 0 explanation, RQ review, scope, and feasibility.
- `docs/LITERATURE_NOTES.md`: future paper audit notes.
- `docs/DATASET_AUDIT.md`: future dataset audit notes.
- `docs/RESULTS_LOG.md`: future experiment run log.
- `docs/LEARNING_GUIDE.md`: future learning notes.
- `docs/CODE_WALKTHROUGH.md`: future code explanation.
- `docs/INTERVIEW_GUIDE.md`: future advisor interview preparation.
