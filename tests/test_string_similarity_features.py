from __future__ import annotations

from pathlib import Path
import sys
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from entity_matching.features import (
    STRING_FEATURE_VERSION,
    build_string_similarity_features,
    edit_similarity_ratio,
    exact_match_score,
    jaccard_similarity,
    levenshtein_distance,
    numeric_token_overlap,
)
from entity_matching.preprocessing import standardize_pair_payload


class StringSimilarityFeatureTests(unittest.TestCase):
    def test_exact_match_score_requires_non_empty_equal_text(self) -> None:
        self.assertEqual(exact_match_score(" Sony Camera ", "sony camera"), 1.0)
        self.assertEqual(exact_match_score("", ""), 0.0)
        self.assertEqual(exact_match_score("N/A", "NULL"), 0.0)
        self.assertEqual(exact_match_score("sony", "canon"), 0.0)

    def test_jaccard_similarity_handles_empty_and_overlap(self) -> None:
        self.assertEqual(jaccard_similarity([], []), 0.0)
        self.assertAlmostEqual(
            jaccard_similarity(["sony", "camera"], ["sony", "camcorder"]),
            1 / 3,
        )

    def test_numeric_token_overlap_is_containment_style(self) -> None:
        self.assertEqual(numeric_token_overlap([], ["10"]), 0.0)
        self.assertEqual(numeric_token_overlap(["10", "20"], ["10", "20", "30"]), 1.0)
        self.assertEqual(numeric_token_overlap(["10", "20"], ["10", "30"]), 0.5)

    def test_levenshtein_distance_uses_normalized_text(self) -> None:
        self.assertEqual(levenshtein_distance(" Sony ", "sony"), 0)
        self.assertEqual(levenshtein_distance("kitten", "sitting"), 3)

    def test_edit_similarity_ratio_is_normalized(self) -> None:
        self.assertEqual(edit_similarity_ratio("", ""), 0.0)
        self.assertEqual(edit_similarity_ratio("sony", "sony"), 1.0)
        self.assertAlmostEqual(edit_similarity_ratio("kitten", "sitting"), 4 / 7)

    def test_edit_similarity_ratio_is_bounded_for_long_text(self) -> None:
        left = "a" * 80 + "x"
        right = "a" * 80 + "y"
        self.assertEqual(edit_similarity_ratio(left, right), 1.0)

    def test_build_string_similarity_features_from_standardized_payload(self) -> None:
        payload = standardize_pair_payload(
            {
                "left_attributes": {
                    "title_left": "Sony Camera 10X",
                    "price_left": "549.00",
                },
                "right_attributes": {
                    "title_right": "Sony Camcorder 10X",
                    "price_right": "549.00",
                },
            }
        )

        features = build_string_similarity_features(payload)

        self.assertEqual(features["feature_version"], STRING_FEATURE_VERSION)
        self.assertIn("combined_token_jaccard", features)
        self.assertEqual(features["attr_price_exact_match"], 1.0)
        self.assertEqual(features["attr_price_numeric_overlap"], 1.0)
        self.assertLess(features["attr_title_exact_match"], 1.0)
        self.assertGreater(features["attr_title_token_jaccard"], 0.0)

    def test_build_string_similarity_features_uses_snake_case_feature_names(self) -> None:
        payload = standardize_pair_payload(
            {
                "left_attributes": {"priceCurrency_left": "EUR"},
                "right_attributes": {"priceCurrency_right": "EUR"},
            }
        )

        features = build_string_similarity_features(payload)

        self.assertEqual(features["attr_price_currency_exact_match"], 1.0)


if __name__ == "__main__":
    unittest.main()
