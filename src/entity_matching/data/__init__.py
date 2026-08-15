"""Data configuration loading and raw dataset validation helpers."""

from entity_matching.data.config import DatasetConfig, load_dataset_config
from entity_matching.data.interim import (
    INTERIM_SCHEMA_VERSION,
    export_dataset_interim,
    pair_to_dict,
    write_pair_table_jsonl,
)
from entity_matching.data.pairs import PairRecord, load_pair_table, summarize_pair_table
from entity_matching.data.quality import (
    report_dataset_quality,
    report_pair_table_quality,
    report_split_overlaps,
)
from entity_matching.data.validation import (
    DatasetValidationError,
    audit_dataset,
    validate_abt_buy,
    validate_wdc_products,
)

__all__ = [
    "DatasetConfig",
    "DatasetValidationError",
    "INTERIM_SCHEMA_VERSION",
    "PairRecord",
    "audit_dataset",
    "export_dataset_interim",
    "load_dataset_config",
    "load_pair_table",
    "pair_to_dict",
    "report_dataset_quality",
    "report_pair_table_quality",
    "report_split_overlaps",
    "summarize_pair_table",
    "validate_abt_buy",
    "validate_wdc_products",
    "write_pair_table_jsonl",
]
