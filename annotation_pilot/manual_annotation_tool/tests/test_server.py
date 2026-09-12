"""Tests pour le serveur d'annotation manuelle (pilote + new_26)."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


TOOL_DIR = Path(__file__).resolve().parent.parent
if str(TOOL_DIR) not in sys.path:
    sys.path.insert(0, str(TOOL_DIR))

import server  # noqa: E402
from dicom_render import ensure_display_png, read_dicom_dimensions  # noqa: E402


PILOT_ANNOTATIONS = TOOL_DIR.parent / "annotations" / "annotator_A"
NEW_26_ANNOTATIONS = TOOL_DIR.parent / "annotations" / "new_26"
DICOM_DIR = TOOL_DIR.parent.parent / "bassin" / "a_annoter"


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


PILOT_CHECKSUMS = {
    path.name: file_sha256(path)
    for path in sorted(PILOT_ANNOTATIONS.glob("P*.json"))
}


class PilotDatasetTests(unittest.TestCase):
    def test_pilot_loads_16_cases(self) -> None:
        config = server.build_dataset_config("pilot")
        self.assertEqual(config.expected_case_count, 16)
        self.assertEqual(len(config.cases), 16)

    def test_pilot_source_file_rule(self) -> None:
        case = server.build_dataset_config("pilot").cases[0]
        self.assertEqual(server.expected_source_file(case), "a308.jpg")


class New26DatasetTests(unittest.TestCase):
    def test_new_26_loads_26_cases(self) -> None:
        config = server.build_dataset_config("new_26")
        self.assertEqual(config.expected_case_count, 26)
        self.assertEqual(len(config.cases), 26)
        self.assertTrue(all("dicom_name" in case for case in config.cases))

    def test_all_dicoms_exist_on_disk(self) -> None:
        config = server.build_dataset_config("new_26")
        for case in config.cases:
            dicom_path = DICOM_DIR / str(case["dicom_name"])
            self.assertTrue(dicom_path.is_file(), dicom_path.name)

    def test_worklist_matches_verification_csv(self) -> None:
        from verification_radios import selected_dicom_names

        expected = selected_dicom_names()
        config = server.build_dataset_config("new_26")
        listed = [str(case["dicom_name"]) for case in config.cases]
        self.assertEqual(len(expected), 26)
        self.assertEqual(listed, expected)

    def test_cases_include_verification_metadata(self) -> None:
        config = server.build_dataset_config("new_26")
        case = config.cases[0]
        self.assertIn("verification_remarque", case)
        self.assertIn("yolo_overlay_reference", case)
        self.assertIn("yolo_suggestions_available", case)
        self.assertTrue(case["yolo_suggestions_available"])

    def test_dicom_render_produces_png_with_same_dimensions(self) -> None:
        config = server.build_dataset_config("new_26")
        case = config.cases[0]
        dicom_path = DICOM_DIR / str(case["dicom_name"])
        with tempfile.TemporaryDirectory() as temporary:
            png_path = Path(temporary) / "preview.png"
            expected_w, expected_h = read_dicom_dimensions(dicom_path)
            from dicom_render import render_dicom_png

            width, height = render_dicom_png(dicom_path, png_path)
            self.assertEqual((width, height), (expected_w, expected_h))
            self.assertTrue(png_path.is_file())
            self.assertGreater(png_path.stat().st_size, 0)

    def test_save_draft_to_temp_copy(self) -> None:
        config = server.build_dataset_config("new_26")
        case = config.cases[0]
        source_json = NEW_26_ANNOTATIONS / str(case["annotation_name"])
        annotation = json.loads(source_json.read_text(encoding="utf-8-sig"))
        annotation["annotator_id"] = "annotator_A"
        annotation["image_width"] = 100
        annotation["image_height"] = 100
        for index, landmark in enumerate(annotation["landmarks"]):
            if index == 0:
                landmark["v"] = 2
                landmark["x"] = 10.5
                landmark["y"] = 20.25
            else:
                landmark["v"] = None
                landmark["x"] = None
                landmark["y"] = None

        with tempfile.TemporaryDirectory() as temporary:
            temp_dir = Path(temporary)
            temp_json = temp_dir / str(case["annotation_name"])
            temp_json.write_text(json.dumps(annotation, indent=2), encoding="utf-8")
            temp_case = dict(case)
            temp_config = server.DatasetConfig(
                name=config.name,
                label=config.label,
                images_dir=config.images_dir,
                dicom_dir=config.dicom_dir,
                annotations_dir=temp_dir,
                worklist_path=config.worklist_path,
                cache_dir=temp_dir / "cache",
                expected_case_count=config.expected_case_count,
                annotator_id=config.annotator_id,
                cases=config.cases,
                cases_by_annotation=config.cases_by_annotation,
                cases_by_image=config.cases_by_image,
            )
            errors = server.validate_annotation(annotation, temp_case, temp_config, finalize=False)
            self.assertEqual(errors, [])


class IntegrityTests(unittest.TestCase):
    def test_pilot_annotations_unchanged(self) -> None:
        for name, checksum in PILOT_CHECKSUMS.items():
            current = file_sha256(PILOT_ANNOTATIONS / name)
            self.assertEqual(current, checksum, f"{name} a été modifié")


if __name__ == "__main__":
    unittest.main()
