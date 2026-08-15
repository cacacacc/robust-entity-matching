from __future__ import annotations

from pathlib import Path
import sys
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from entity_matching.preprocessing import (
    TEXT_STANDARDIZATION_VERSION,
    build_text_profile,
    extract_numeric_tokens,
    normalize_attributes,
    normalize_text,
    standardize_pair_payload,
    tokenize_text,
)


class TextStandardizationTests(unittest.TestCase):
    def test_normalize_text_handles_case_html_and_whitespace(self) -> None:
        text = "  Sony&nbsp;HDV\n\tCamcorder  "
        self.assertEqual(normalize_text(text), "sony hdv camcorder")

    def test_normalize_text_handles_missing_values(self) -> None:
        self.assertEqual(normalize_text(None), "")
        self.assertEqual(normalize_text(""), "")
        self.assertEqual(normalize_text(" N/A "), "")
        self.assertEqual(normalize_text("NULL"), "")

    def test_tokenize_text_returns_alphanumeric_tokens(self) -> None:
        text = "HDR-HC9 / 10X Optical Zoom"
        self.assertEqual(tokenize_text(text), ["hdr", "hc9", "10x", "optical", "zoom"])

    def test_extract_numeric_tokens_finds_product_numbers_and_prices(self) -> None:
        text = "10X optical, 2.7 inch display, price 549.00"
        self.assertEqual(extract_numeric_tokens(text), ["10", "2.7", "549.00"])

    def test_normalize_attributes_preserves_attribute_names(self) -> None:
        attributes = {"name": " Sony Camera ", "price": "", "manufacturer": None}
        self.assertEqual(
            normalize_attributes(attributes),
            {"name": "sony camera", "price": "", "manufacturer": ""},
        )

    def test_build_text_profile_combines_sorted_attributes(self) -> None:
        profile = build_text_profile({"name": "Sony Camera", "price": "549.00"})
        self.assertEqual(profile.combined_text, "sony camera 549.00")
        self.assertEqual(profile.tokens, ["sony", "camera", "549", "00"])
        self.assertEqual(profile.numeric_tokens, ["549.00"])

    def test_standardize_pair_payload_adds_profiles_without_removing_raw_attributes(self) -> None:
        payload = {
            "dataset_id": "example",
            "left_attributes": {"name": "Sony Camera", "price": ""},
            "right_attributes": {"name": " SONY camera ", "price": "549.00"},
        }

        standardized = standardize_pair_payload(payload)

        self.assertEqual(
            standardized["text_standardization_version"], TEXT_STANDARDIZATION_VERSION
        )
        self.assertEqual(standardized["left_attributes"], payload["left_attributes"])
        self.assertEqual(
            standardized["right_text_profile"]["normalized_attributes"]["name"],
            "sony camera",
        )
        self.assertEqual(standardized["right_text_profile"]["numeric_tokens"], ["549.00"])


if __name__ == "__main__":
    unittest.main()
