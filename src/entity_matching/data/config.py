"""Dataset configuration helpers."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class DatasetConfig:
    """Loaded dataset metadata from a JSON config file."""

    path: Path
    data: dict[str, Any]

    @property
    def dataset_id(self) -> str:
        return str(self.data["dataset_id"])

    @property
    def project_root(self) -> Path:
        return self.path.parents[2]

    def resolve_path(self, relative_path: str) -> Path:
        return self.project_root / relative_path


def load_dataset_config(path: str | Path) -> DatasetConfig:
    """Load and minimally validate a dataset config JSON file."""

    config_path = Path(path)
    with config_path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    required_top_level = {
        "dataset_id",
        "local_paths",
        "schema",
        "label_mapping",
        "audited_counts",
        "supported_research_questions",
    }
    missing = sorted(required_top_level - data.keys())
    if missing:
        raise ValueError(f"Dataset config {config_path} is missing keys: {missing}")

    return DatasetConfig(path=config_path, data=data)

