from __future__ import annotations

from pathlib import Path
import sys
import tempfile
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from entity_matching.evaluation import (
    RAW_PREDICTION_SCHEMA_VERSION,
    PredictionArtifactError,
    prediction_artifact_path,
    summarize_prediction_rows,
    validate_prediction_rows,
    write_prediction_csv,
)


class PredictionArtifactTests(unittest.TestCase):
    def test_prediction_artifact_path(self) -> None:
        path = prediction_artifact_path(
            "results", "experiment_a", "logistic_regression", 13, "validation"
        )

        self.assertEqual(
            str(path),
            str(
                Path(
                    "results/predictions/experiment_a/logistic_regression/seed_13/validation.csv"
                )
            ),
        )

    def test_validate_prediction_rows(self) -> None:
        rows = validate_prediction_rows([_toy_prediction_row()])

        self.assertEqual(rows[0]["schema_version"], RAW_PREDICTION_SCHEMA_VERSION)
        self.assertEqual(rows[0]["y_true"], 1)
        self.assertEqual(rows[0]["score"], 0.8)

    def test_reject_invalid_score(self) -> None:
        row = _toy_prediction_row()
        row["score"] = 1.5

        with self.assertRaises(PredictionArtifactError):
            validate_prediction_rows([row])

    def test_summarize_prediction_rows(self) -> None:
        summary = summarize_prediction_rows(
            [
                _toy_prediction_row(),
                {
                    **_toy_prediction_row(),
                    "pair_id": "p2",
                    "y_true": 0,
                    "score": 0.2,
                    "y_pred": 0,
                },
            ]
        )

        self.assertEqual(summary["row_count"], 2)
        self.assertEqual(summary["label_counts"], {"0": 1, "1": 1})
        self.assertEqual(summary["prediction_counts"], {"0": 1, "1": 1})

    def test_write_prediction_csv_to_temp_file(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output_path = Path(directory) / "toy_predictions.csv"
            row_count = write_prediction_csv([_toy_prediction_row()], output_path)

            self.assertEqual(row_count, 1)
            self.assertTrue(output_path.exists())


def _toy_prediction_row() -> dict[str, object]:
    return {
        "schema_version": RAW_PREDICTION_SCHEMA_VERSION,
        "experiment_id": "toy_experiment",
        "model_id": "toy_model",
        "seed": 13,
        "split_role": "validation",
        "split": "toy_validation",
        "pair_id": "p1",
        "y_true": 1,
        "score": 0.8,
        "threshold": 0.5,
        "y_pred": 1,
    }


if __name__ == "__main__":
    unittest.main()
