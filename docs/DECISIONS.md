# Decisions

## 2026-08-14: Initialize a public-ready research repository structure

Decision: Use a conventional Python research project layout with separate folders for configuration, source code, tests, documentation, local data, generated results, figures, and reports.

Alternatives considered:

- Put scripts and notebooks at the repository root.
- Delay documentation until experiments are complete.
- Track raw data and generated results directly in Git.

Reasoning: The selected layout keeps code, data, generated artifacts, and research documentation separate. This supports reproducibility and reduces the risk of committing large data or derived results accidentally.

Impact: Future experiments should be run through scripts or modules, with configurations and outputs stored in predictable locations.

Evidence available at decision time: Project requirements require reproducible commands, saved configurations, raw results, documentation, and scientific integrity checks.

