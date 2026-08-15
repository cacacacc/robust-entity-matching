"""String-similarity feature primitives for standardized pair payloads."""

from __future__ import annotations

import re
from typing import Any, Iterable, Mapping

from entity_matching.preprocessing import extract_numeric_tokens, normalize_text, tokenize_text


STRING_FEATURE_VERSION = "string_similarity_v1"
MAX_EDIT_SIMILARITY_CHARS = 64


def exact_match_score(left: Any, right: Any) -> float:
    """Return 1.0 for equal non-empty normalized strings, otherwise 0.0."""

    left_text = normalize_text(left)
    right_text = normalize_text(right)
    if not left_text or not right_text:
        return 0.0
    return 1.0 if left_text == right_text else 0.0


def jaccard_similarity(left_tokens: Iterable[str], right_tokens: Iterable[str]) -> float:
    """Compute set Jaccard similarity for two token collections."""

    left_set = set(left_tokens)
    right_set = set(right_tokens)
    union = left_set | right_set
    if not union:
        return 0.0
    return len(left_set & right_set) / len(union)


def numeric_token_overlap(
    left_numeric_tokens: Iterable[str], right_numeric_tokens: Iterable[str]
) -> float:
    """Compute containment-style overlap for numeric-token sets."""

    left_set = set(left_numeric_tokens)
    right_set = set(right_numeric_tokens)
    if not left_set or not right_set:
        return 0.0
    return len(left_set & right_set) / min(len(left_set), len(right_set))


def levenshtein_distance(left: Any, right: Any) -> int:
    """Compute Levenshtein edit distance between normalized strings."""

    left_text = normalize_text(left)
    right_text = normalize_text(right)
    if left_text == right_text:
        return 0
    if not left_text:
        return len(right_text)
    if not right_text:
        return len(left_text)

    previous = list(range(len(right_text) + 1))
    for left_index, left_char in enumerate(left_text, start=1):
        current = [left_index]
        for right_index, right_char in enumerate(right_text, start=1):
            insertion = current[right_index - 1] + 1
            deletion = previous[right_index] + 1
            substitution = previous[right_index - 1] + (left_char != right_char)
            current.append(min(insertion, deletion, substitution))
        previous = current
    return previous[-1]


def edit_similarity_ratio(
    left: Any, right: Any, max_chars: int = MAX_EDIT_SIMILARITY_CHARS
) -> float:
    """Return bounded normalized edit similarity in [0.0, 1.0]."""

    left_text = normalize_text(left)[:max_chars]
    right_text = normalize_text(right)[:max_chars]
    if not left_text or not right_text:
        return 0.0
    distance = levenshtein_distance(left_text, right_text)
    return 1.0 - (distance / max(len(left_text), len(right_text)))


def build_string_similarity_features(
    standardized_pair_payload: Mapping[str, Any],
) -> dict[str, float | str]:
    """Build initial string-similarity features from standardized text profiles."""

    left_profile = standardized_pair_payload["left_text_profile"]
    right_profile = standardized_pair_payload["right_text_profile"]
    left_text = left_profile["combined_text"]
    right_text = right_profile["combined_text"]

    features: dict[str, float | str] = {
        "feature_version": STRING_FEATURE_VERSION,
        "combined_exact_match": exact_match_score(left_text, right_text),
        "combined_edit_similarity": edit_similarity_ratio(left_text, right_text),
        "combined_token_jaccard": jaccard_similarity(
            left_profile["tokens"], right_profile["tokens"]
        ),
        "combined_numeric_overlap": numeric_token_overlap(
            left_profile["numeric_tokens"], right_profile["numeric_tokens"]
        ),
    }

    left_attributes = left_profile["normalized_attributes"]
    right_attributes = right_profile["normalized_attributes"]
    for base_name in _shared_attribute_base_names(left_attributes, right_attributes):
        left_value = _get_attribute_by_base_name(left_attributes, base_name)
        right_value = _get_attribute_by_base_name(right_attributes, base_name)
        prefix = f"attr_{_feature_safe_name(base_name)}"
        features[f"{prefix}_exact_match"] = exact_match_score(left_value, right_value)
        features[f"{prefix}_edit_similarity"] = edit_similarity_ratio(left_value, right_value)
        features[f"{prefix}_token_jaccard"] = jaccard_similarity(
            tokenize_text(left_value), tokenize_text(right_value)
        )
        features[f"{prefix}_numeric_overlap"] = numeric_token_overlap(
            extract_numeric_tokens(left_value),
            extract_numeric_tokens(right_value),
        )

    return features


def _shared_attribute_base_names(
    left_attributes: Mapping[str, str], right_attributes: Mapping[str, str]
) -> list[str]:
    left_names = {_base_attribute_name(name) for name in left_attributes}
    right_names = {_base_attribute_name(name) for name in right_attributes}
    return sorted(left_names & right_names)


def _base_attribute_name(attribute_name: str) -> str:
    for suffix in ("_left", "_right"):
        if attribute_name.endswith(suffix):
            return attribute_name[: -len(suffix)]
    return attribute_name


def _feature_safe_name(name: str) -> str:
    separated = re.sub(r"(?<!^)(?=[A-Z])", "_", name)
    safe_name = re.sub(r"[^a-zA-Z0-9]+", "_", separated).strip("_").lower()
    return safe_name


def _get_attribute_by_base_name(attributes: Mapping[str, str], base_name: str) -> str:
    for name, value in attributes.items():
        if _base_attribute_name(name) == base_name:
            return value
    return ""
