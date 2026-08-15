"""Split manifests and leakage guards for model-ready feature tables."""

from entity_matching.splitting.guards import (
    SplitGuardError,
    assert_no_leakage,
    build_split_guard_report,
    compare_pair_sets,
    compare_record_and_entity_sets,
)
from entity_matching.splitting.manifest import (
    FeatureTableSplit,
    SplitManifest,
    load_feature_table_rows,
    load_feature_table_summary,
    validate_feature_table_file,
    build_split_manifest,
)

__all__ = [
    "FeatureTableSplit",
    "SplitGuardError",
    "SplitManifest",
    "assert_no_leakage",
    "build_split_guard_report",
    "build_split_manifest",
    "compare_pair_sets",
    "compare_record_and_entity_sets",
    "load_feature_table_rows",
    "load_feature_table_summary",
    "validate_feature_table_file",
]
