"""Text standardization primitives for normalized pair attributes."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import html
import re
import unicodedata
from typing import Any, Mapping


TEXT_STANDARDIZATION_VERSION = "text_standardization_v1"
MISSING_MARKERS = {"", "n/a", "na", "nan", "none", "null"}

_WHITESPACE_RE = re.compile(r"\s+")
_TOKEN_RE = re.compile(r"[a-z0-9]+")
_NUMERIC_RE = re.compile(r"\d+(?:[.,]\d+)?")


@dataclass(frozen=True)
class TextProfile:
    """Standardized text view for one side of a pair."""

    normalized_attributes: dict[str, str]
    combined_text: str
    tokens: list[str]
    numeric_tokens: list[str]


def normalize_text(value: Any) -> str:
    """Normalize a raw attribute value into a lowercase single-space string."""

    if value is None:
        return ""

    text = unicodedata.normalize("NFKC", html.unescape(str(value)))
    text = _WHITESPACE_RE.sub(" ", text).strip().lower()
    if text in MISSING_MARKERS:
        return ""
    return text


def tokenize_text(value: Any) -> list[str]:
    """Tokenize normalized text into lowercase alphanumeric tokens."""

    return _TOKEN_RE.findall(normalize_text(value))


def extract_numeric_tokens(value: Any) -> list[str]:
    """Extract numeric tokens from normalized text for structured comparisons."""

    return [token.replace(",", ".") for token in _NUMERIC_RE.findall(normalize_text(value))]


def normalize_attributes(attributes: Mapping[str, Any]) -> dict[str, str]:
    """Normalize every attribute value while preserving attribute names."""

    return {name: normalize_text(value) for name, value in attributes.items()}


def build_text_profile(attributes: Mapping[str, Any]) -> TextProfile:
    """Build a standardized text profile from one side's attributes."""

    normalized_attributes = normalize_attributes(attributes)
    combined_text = " ".join(
        value for _, value in sorted(normalized_attributes.items()) if value
    )
    return TextProfile(
        normalized_attributes=normalized_attributes,
        combined_text=combined_text,
        tokens=tokenize_text(combined_text),
        numeric_tokens=extract_numeric_tokens(combined_text),
    )


def standardize_pair_payload(pair_payload: Mapping[str, Any]) -> dict[str, Any]:
    """Add standardized text profiles to an interim pair-table payload."""

    payload = dict(pair_payload)
    payload["text_standardization_version"] = TEXT_STANDARDIZATION_VERSION
    payload["left_text_profile"] = asdict(
        build_text_profile(pair_payload.get("left_attributes", {}))
    )
    payload["right_text_profile"] = asdict(
        build_text_profile(pair_payload.get("right_attributes", {}))
    )
    return payload
