"""Tests YOLO suggestions et contrôles anatomiques."""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path


TOOL_DIR = Path(__file__).resolve().parent.parent
if str(TOOL_DIR) not in sys.path:
    sys.path.insert(0, str(TOOL_DIR))

import server  # noqa: E402
from anatomical_checks import run_anatomical_checks  # noqa: E402
from yolo_suggestions import (  # noqa: E402
    load_yolo_suggestions,
    parse_prediction_line,
    predictions_available_for,
)


PREDICTIONS_DIR = (
    TOOL_DIR.parent.parent / "datasets" / "yolo_pose_new_26" / "predictions" / "labels"
)


class YoloSuggestionsTests(unittest.TestCase):
    def test_predictions_available_for_all_new_26(self) -> None:
        config = server.build_dataset_config("new_26")
        for case in config.cases:
            pilot_id = str(case["pilot_id"])
            self.assertTrue(
                predictions_available_for(pilot_id),
                f"Prédiction absente pour {pilot_id}",
            )

    def test_load_b26_01_suggestions_in_pixels(self) -> None:
        line = (PREDICTIONS_DIR / "B26_01.txt").read_text(encoding="utf-8").strip()
        payload = parse_prediction_line(line, 2730, 2665)
        self.assertEqual(len(payload["suggestions"]), 14)
        first = payload["suggestions"][0]
        self.assertEqual(first["name"], "TD_R")
        self.assertIsNotNone(first["x"])
        self.assertIsNotNone(first["y"])
        self.assertGreater(first["confidence"], 0.25)

        loaded = load_yolo_suggestions("B26_01", 2730, 2665)
        assert loaded is not None
        self.assertEqual(loaded["source"], "yolo_prediction")
        self.assertEqual(loaded["pilot_id"], "B26_01")

    def test_suggestions_differ_from_ground_truth(self) -> None:
        gt_line = (
            TOOL_DIR.parent.parent
            / "datasets/yolo_pose_new_26/labels/train/B26_01.txt"
        ).read_text(encoding="utf-8").strip()
        pred_line = (PREDICTIONS_DIR / "B26_01.txt").read_text(encoding="utf-8").strip()
        self.assertNotEqual(gt_line.split()[5:8], pred_line.split()[5:8])

    def test_missing_prediction_returns_none(self) -> None:
        self.assertIsNone(load_yolo_suggestions("B26_99", 100, 100))


class AnatomicalChecksTests(unittest.TestCase):
    def _landmark(self, name: str, x: float, y: float) -> dict:
        return {"name": name, "x": x, "y": y, "v": 2}

    def test_side_rl_warning_for_inverted_right_point(self) -> None:
        landmarks = [self._landmark("TD_R", 900, 100)]
        warnings = run_anatomical_checks(landmarks, 1000, 800)
        categories = {item["category"] for item in warnings}
        self.assertIn("side_rl", categories)

    def test_out_of_bounds_warning(self) -> None:
        landmarks = [self._landmark("TD_R", -5, 10)]
        warnings = run_anatomical_checks(landmarks, 1000, 800)
        self.assertTrue(any(item["category"] == "out_of_bounds" for item in warnings))

    def test_femoral_chain_warning(self) -> None:
        landmarks = [
            self._landmark("FHC_R", 100, 100),
            self._landmark("FNM_R", 100, 200),
            self._landmark("FSP_R", 100, 150),
        ]
        warnings = run_anatomical_checks(landmarks, 1000, 800)
        self.assertTrue(any(item["category"] == "femoral_chain" for item in warnings))

    def test_yolo_suggestions_not_used_in_validation(self) -> None:
        annotation = json.loads(
            (
                TOOL_DIR.parent / "annotations/new_26/B26_01.json"
            ).read_text(encoding="utf-8-sig")
        )
        for landmark in annotation["landmarks"]:
            landmark["v"] = None
            landmark["x"] = None
            landmark["y"] = None
        config = server.build_dataset_config("new_26")
        case = config.cases[0]
        errors = server.validate_annotation(annotation, case, config, finalize=True)
        self.assertTrue(any("n'est pas renseigné" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
