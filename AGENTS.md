# Project Collaboration Rules

Use Chinese for conceptual explanations. Use English for code, variable names, function names, Git commits, README content, and the final technical report.

This project prioritizes reproducibility, scientific integrity, and clear experimental protocol over maximizing a single metric.

## Research Integrity

- Do not fabricate experimental results, dataset fields, paper conclusions, or completed work.
- Keep raw data unchanged.
- Use validation data for threshold and model selection; reserve test data for final evaluation.
- Check pair leakage and entity leakage for every split.
- Report random seeds, class ratios, raw predictions, mean, and standard deviation.
- Do not introduce Transformer or large-model extensions before the traditional baseline MVP is reproducible.

## Coding Rules

- Use modular Python under `src/entity_matching/`.
- Keep notebooks for exploration and figures only.
- Put formal runs behind scripts or importable modules.
- Put paths and hyperparameters in configuration files.
- Add targeted tests for schema validation, preprocessing, features, splitting, leakage checks, sampling, metrics, and config loading.

## Approval Boundaries

Ask before:

- Downloading data or models larger than 500 MB.
- Installing large dependencies.
- Using paid APIs or cloud compute.
- Uploading data.
- Pushing to GitHub or performing other external writes.
- Deleting or overwriting important data or results.
- Running destructive Git commands.
- Starting long or expensive training runs.
- Changing the research questions materially.
- Expanding the scope with Transformer or large-model methods.

