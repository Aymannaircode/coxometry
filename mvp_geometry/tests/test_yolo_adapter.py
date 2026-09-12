"""Tests unitaires de l'adaptateur YOLO Pose → landmarks MVP."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from mvp_geometry.landmarks import MVP_LANDMARK_NAMES
from mvp_geometry.yolo_adapter import landmarks_from_yolo_label, parse_yolo_pose_line

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
V2_LABEL = PROJECT_ROOT / "datasets/yolo_pose_new_26/predictions_v2/labels/B26_01.txt"
V2_WIDTH = 2730.0
V2_HEIGHT = 2665.0


def _synthetic_line(keypoint_triplets: list[tuple[float, float, float]], *, with_detection_conf: bool = True) -> str:
    header = ["0", "0.5", "0.5", "0.9", "0.9"]
    flat: list[str] = []
    for x_norm, y_norm, conf in keypoint_triplets:
        flat.extend(f"{value:.6f}" for value in (x_norm, y_norm, conf))
    parts = header + flat
    if with_detection_conf:
        parts.append("0.900000")
    return " ".join(parts)


def _all_visible_line() -> str:
    return _synthetic_line([(0.1 * (index + 1), 0.2 * (index + 1), 0.99) for index in range(14)])


class TestParseYoloPoseLine(unittest.TestCase):
    def test_normalized_to_pixels(self) -> None:
        line = _synthetic_line([(0.5, 0.25, 0.99)] + [(0.1, 0.2, 0.99)] * 13)
        landmarks = parse_yolo_pose_line(line, 1000.0, 800.0)
        td_r = landmarks["TD_R"]
        self.assertEqual(td_r.v, 2)
        self.assertAlmostEqual(td_r.x, 500.0)
        self.assertAlmostEqual(td_r.y, 200.0)

    def test_confidence_above_threshold_usable(self) -> None:
        line = _synthetic_line([(0.4, 0.6, 0.25)] + [(0.3, 0.7, 0.99)] * 13)
        landmarks = parse_yolo_pose_line(line, 200.0, 100.0, keypoint_conf_threshold=0.25)
        self.assertTrue(landmarks["TD_R"].usable)
        self.assertIsNotNone(landmarks["TD_R"].x)
        self.assertIsNotNone(landmarks["TD_R"].y)

    def test_confidence_below_threshold_not_usable(self) -> None:
        line = _synthetic_line([(0.4, 0.6, 0.249)] + [(0.3, 0.7, 0.99)] * 13)
        landmarks = parse_yolo_pose_line(line, 200.0, 100.0, keypoint_conf_threshold=0.25)
        self.assertFalse(landmarks["TD_R"].usable)
        self.assertEqual(landmarks["TD_R"].v, 0)
        self.assertIsNone(landmarks["TD_R"].x)
        self.assertIsNone(landmarks["TD_R"].y)

    def test_wrong_keypoint_count(self) -> None:
        # 13 keypoints (39 valeurs) + en-tête bbox (5) = 44 colonnes ≠ 47/48.
        line = "0 0.5 0.5 0.9 0.9 " + " ".join(["0.1", "0.2", "0.9"] * 13)
        with self.assertRaisesRegex(ValueError, "Format YOLO inattendu"):
            parse_yolo_pose_line(line, 100.0, 100.0)

    def test_wrong_keypoint_count_with_detection_conf(self) -> None:
        # 15 keypoints (45 valeurs) + bbox (5) + conf détection (1) = 51 colonnes.
        line = _synthetic_line([(0.1, 0.2, 0.9)] * 15)
        with self.assertRaisesRegex(ValueError, "Format YOLO inattendu"):
            parse_yolo_pose_line(line, 100.0, 100.0)

    def test_wrong_column_count(self) -> None:
        with self.assertRaisesRegex(ValueError, "Format YOLO inattendu"):
            parse_yolo_pose_line("0 0.5 0.5 0.9", 100.0, 100.0)

    def test_empty_line(self) -> None:
        with self.assertRaisesRegex(ValueError, "Label YOLO vide"):
            parse_yolo_pose_line("   ", 100.0, 100.0)

    def test_invalid_numeric_value(self) -> None:
        line = _all_visible_line().replace("0.500000", "not_a_number", 1)
        with self.assertRaisesRegex(ValueError, "valeur numérique invalide"):
            parse_yolo_pose_line(line, 100.0, 100.0)

    def test_returns_all_fourteen_landmarks(self) -> None:
        landmarks = parse_yolo_pose_line(_all_visible_line(), 640.0, 480.0)
        self.assertEqual(set(landmarks.keys()), set(MVP_LANDMARK_NAMES))


class TestLandmarksFromYoloLabel(unittest.TestCase):
    def test_missing_file(self) -> None:
        with self.assertRaises(FileNotFoundError):
            landmarks_from_yolo_label("/does/not/exist.txt", 100.0, 100.0)

    def test_empty_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "empty.txt"
            path.write_text("\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "Label YOLO vide"):
                landmarks_from_yolo_label(path, 100.0, 100.0)

    def test_invalid_file_wrapped_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bad.txt"
            path.write_text("0 0.5 0.5", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "bad.txt"):
                landmarks_from_yolo_label(path, 100.0, 100.0)

    @unittest.skipUnless(V2_LABEL.is_file(), "Label V2 B26_01 absent")
    def test_real_v2_label_b26_01(self) -> None:
        landmarks = landmarks_from_yolo_label(V2_LABEL, V2_WIDTH, V2_HEIGHT)
        self.assertEqual(len(landmarks), 14)
        self.assertEqual(sum(item.usable for item in landmarks.values()), 14)
        td_r = landmarks["TD_R"]
        self.assertAlmostEqual(td_r.x, 0.357475 * V2_WIDTH, places=1)
        self.assertAlmostEqual(td_r.y, 0.752299 * V2_HEIGHT, places=1)


if __name__ == "__main__":
    unittest.main()
