#!/usr/bin/env python3
"""Serveur local pour l'annotation manuelle (pilote JPEG ou lot bassin DICOM)."""

from __future__ import annotations

import argparse
import csv
import json
import math
import mimetypes
import os
import tempfile
from dataclasses import dataclass
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, unquote, urlparse

from anatomical_checks import run_anatomical_checks
from dicom_render import ensure_display_png
from verification_radios import verification_by_dicom
from yolo_suggestions import load_yolo_suggestions, predictions_available_for


TOOL_DIR = Path(__file__).resolve().parent
PILOT_DIR = TOOL_DIR.parent
PROJECT_ROOT = PILOT_DIR.parent
YOLO_OVERLAY_DIR = PROJECT_ROOT / "datasets" / "yolo_pose_new_26" / "visual_check" / "overlays"

LANDMARKS = [
    ("LM-01", "TD_R", "right"),
    ("LM-02", "TD_L", "left"),
    ("LM-03", "FHC_R", "right"),
    ("LM-04", "FHC_L", "left"),
    ("LM-05", "ASL_R", "right"),
    ("LM-06", "ASL_L", "left"),
    ("LM-07", "ASM_R", "right"),
    ("LM-08", "ASM_L", "left"),
    ("LM-09", "FNM_R", "right"),
    ("LM-10", "FNM_L", "left"),
    ("LM-11", "FSP_R", "right"),
    ("LM-12", "FSP_L", "left"),
    ("LM-13", "FSD_R", "right"),
    ("LM-14", "FSD_L", "left"),
]


@dataclass(frozen=True)
class DatasetConfig:
    name: str
    label: str
    images_dir: Path | None
    dicom_dir: Path | None
    annotations_dir: Path
    worklist_path: Path
    cache_dir: Path | None
    expected_case_count: int
    annotator_id: str
    cases: tuple[dict[str, Any], ...]
    cases_by_annotation: dict[str, dict[str, Any]]
    cases_by_image: dict[str, dict[str, Any]]
    correction_mode: bool = False
    correction_case_ids: tuple[str, ...] = ()


def is_number(value: object) -> bool:
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(float(value))
    )


def expected_source_file(case: dict[str, Any]) -> str:
    dicom_name = case.get("dicom_name")
    if dicom_name:
        return str(dicom_name)
    image_name = str(case["image_name"])
    return image_name.split("_", 1)[1]


def load_pilot_cases(
    annotations_dir: Path,
    images_dir: Path,
    worklist_path: Path,
) -> tuple[dict[str, Any], ...]:
    with worklist_path.open("r", encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))

    if len(rows) != 16:
        raise RuntimeError(f"worklist.csv doit contenir 16 cas, trouvé : {len(rows)}")

    cases: list[dict[str, Any]] = []
    for row in rows:
        annotation_name = Path(row["annotation_file"]).name
        image_name = Path(row["image_file"]).name
        if annotation_name != row["annotation_file"]:
            raise RuntimeError(f"Chemin d'annotation non autorisé : {row['annotation_file']}")
        if not (annotations_dir / annotation_name).is_file():
            raise RuntimeError(f"JSON absent : {annotation_name}")
        if not (images_dir / image_name).is_file():
            raise RuntimeError(f"Image absente : {image_name}")
        cases.append(
            {
                "order": int(row["order"]),
                "pilot_id": row["pilot_id"],
                "image_name": image_name,
                "annotation_name": annotation_name,
            }
        )
    return tuple(sorted(cases, key=lambda case: int(case["order"])))


def enrich_case_metadata(case: dict[str, Any]) -> dict[str, Any]:
    enriched = dict(case)
    dicom_name = str(case.get("dicom_name", ""))
    meta = verification_by_dicom().get(dicom_name, {})
    enriched["verification_remarque"] = meta.get("remarque", "")
    enriched["verification_qualite"] = meta.get("qualite", "")
    enriched["verification_utilisable"] = meta.get("utilisable_annotation", "")
    pilot_id = str(case.get("pilot_id", ""))
    overlay_path = YOLO_OVERLAY_DIR / f"{pilot_id}_overlay.png"
    enriched["yolo_overlay_reference"] = (
        f"/reference/yolo-overlay/{pilot_id}" if overlay_path.is_file() else None
    )
    enriched["yolo_suggestions_available"] = predictions_available_for(pilot_id)
    return enriched


def load_new_26_cases(
    annotations_dir: Path,
    dicom_dir: Path,
    worklist_path: Path,
) -> tuple[dict[str, Any], ...]:
    with worklist_path.open("r", encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))

    if len(rows) != 26:
        raise RuntimeError(f"worklist.csv doit contenir 26 cas, trouvé : {len(rows)}")

    cases: list[dict[str, Any]] = []
    for row in rows:
        annotation_name = Path(row["annotation_file"]).name
        image_name = Path(row["image_file"]).name
        dicom_name = row["dicom_file"].strip()
        if annotation_name != row["annotation_file"]:
            raise RuntimeError(f"Chemin d'annotation non autorisé : {row['annotation_file']}")
        if not (annotations_dir / annotation_name).is_file():
            raise RuntimeError(f"JSON absent : {annotation_name}")
        if not (dicom_dir / dicom_name).is_file():
            raise RuntimeError(f"DICOM absent : {dicom_name}")
        cases.append(
            enrich_case_metadata(
                {
                    "order": int(row["order"]),
                    "pilot_id": row["pilot_id"],
                    "image_name": image_name,
                    "annotation_name": annotation_name,
                    "dicom_name": dicom_name,
                }
            )
        )
    return tuple(sorted(cases, key=lambda case: int(case["order"])))


def filter_cases(
    cases: tuple[dict[str, Any], ...], only_case_ids: tuple[str, ...] | None
) -> tuple[dict[str, Any], ...]:
    if not only_case_ids:
        return cases
    allowed = set(only_case_ids)
    filtered = tuple(case for case in cases if case["pilot_id"] in allowed)
    missing = sorted(allowed - {case["pilot_id"] for case in filtered})
    if missing:
        raise RuntimeError(f"Cas introuvable(s) dans la worklist : {', '.join(missing)}")
    return tuple(sorted(filtered, key=lambda case: int(case["order"])))


def build_dataset_config(
    dataset_name: str, only_case_ids: tuple[str, ...] | None = None
) -> DatasetConfig:
    if dataset_name == "pilot":
        annotations_dir = PILOT_DIR / "annotations" / "annotator_A"
        images_dir = PILOT_DIR / "images"
        worklist_path = annotations_dir / "worklist.csv"
        cases = filter_cases(load_pilot_cases(annotations_dir, images_dir, worklist_path), only_case_ids)
        return DatasetConfig(
            name="pilot",
            label="Pilote MVP · Annotateur A (16 JPEG)",
            images_dir=images_dir,
            dicom_dir=None,
            annotations_dir=annotations_dir,
            worklist_path=worklist_path,
            cache_dir=None,
            expected_case_count=16,
            annotator_id="annotator_A",
            cases=cases,
            cases_by_annotation={str(case["annotation_name"]): case for case in cases},
            cases_by_image={str(case["image_name"]): case for case in cases},
            correction_mode=bool(only_case_ids),
            correction_case_ids=only_case_ids or (),
        )

    if dataset_name == "new_26":
        annotations_dir = PILOT_DIR / "annotations" / "new_26"
        dicom_dir = PROJECT_ROOT / "bassin" / "a_annoter"
        worklist_path = annotations_dir / "worklist.csv"
        cache_dir = TOOL_DIR / "cache" / "new_26"
        cases = filter_cases(
            load_new_26_cases(annotations_dir, dicom_dir, worklist_path), only_case_ids
        )
        return DatasetConfig(
            name="new_26",
            label="Bassin adulte · 26 DICOM (a_annoter)",
            images_dir=None,
            dicom_dir=dicom_dir,
            annotations_dir=annotations_dir,
            worklist_path=worklist_path,
            cache_dir=cache_dir,
            expected_case_count=26,
            annotator_id="annotator_A",
            cases=cases,
            cases_by_annotation={str(case["annotation_name"]): case for case in cases},
            cases_by_image={str(case["image_name"]): case for case in cases},
            correction_mode=bool(only_case_ids),
            correction_case_ids=only_case_ids or (),
        )

    raise RuntimeError(f"Dataset inconnu : {dataset_name}. Valeurs : pilot, new_26.")


def validate_annotation(
    data: object, case: dict[str, Any], config: DatasetConfig, finalize: bool
) -> list[str]:
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["Le contenu de l'annotation doit être un objet JSON."]

    if data.get("schema_version") != "mvp-pilot-1.0":
        errors.append("schema_version doit être mvp-pilot-1.0.")
    if data.get("image_id") != case["pilot_id"]:
        errors.append("image_id ne correspond pas au cas chargé.")
    if data.get("source_file") != expected_source_file(case):
        errors.append("source_file ne correspond pas à l'image.")
    if data.get("annotator_id") != config.annotator_id:
        errors.append(f"annotator_id doit rester {config.annotator_id}.")

    width = data.get("image_width")
    height = data.get("image_height")
    dimensions_valid = (
        is_number(width)
        and is_number(height)
        and float(width) > 0
        and float(height) > 0
    )
    if (width is None) != (height is None):
        errors.append("image_width et image_height doivent être tous deux définis ou null.")
    elif width is not None and not dimensions_valid:
        errors.append("Les dimensions de l'image doivent être des nombres positifs.")

    landmarks = data.get("landmarks")
    if not isinstance(landmarks, list) or len(landmarks) != len(LANDMARKS):
        return errors + ["Le tableau landmarks doit contenir exactement 14 éléments."]

    for index, (landmark, expected) in enumerate(zip(landmarks, LANDMARKS)):
        landmark_id, name, side = expected
        prefix = f"{landmark_id}"
        if not isinstance(landmark, dict):
            errors.append(f"{prefix} doit être un objet.")
            continue
        if (
            landmark.get("id"),
            landmark.get("name"),
            landmark.get("side"),
        ) != expected:
            errors.append(f"{prefix} : id, name ou side a été modifié.")

        x, y, visibility = landmark.get("x"), landmark.get("y"), landmark.get("v")
        if visibility is None:
            if x is not None or y is not None:
                errors.append(f"{prefix} : v=null exige x=null et y=null.")
            if finalize:
                errors.append(f"{prefix} n'est pas renseigné.")
        elif visibility == 0:
            if x is not None or y is not None:
                errors.append(f"{prefix} : v=0 exige x=null et y=null.")
        elif visibility == 2:
            if not is_number(x) or not is_number(y):
                errors.append(f"{prefix} : v=2 exige deux coordonnées numériques.")
            elif not dimensions_valid:
                errors.append(f"{prefix} : dimensions d'image absentes ou invalides.")
            elif not (0 <= float(x) < float(width) and 0 <= float(y) < float(height)):
                errors.append(f"{prefix} : coordonnées hors de l'image.")
        else:
            errors.append(f"{prefix} : v doit être null, 0 ou 2 (v=1 non autorisé).")

        if landmark.get("id") != landmark_id:
            errors.append(f"Landmark à l'index {index} incorrect.")

    if not isinstance(data.get("ambiguity_flags"), list):
        errors.append("ambiguity_flags doit rester une liste.")
    if not isinstance(data.get("image_level"), dict):
        errors.append("image_level doit rester un objet.")
    return errors


def resolve_image_path(config: DatasetConfig, case: dict[str, Any]) -> Path:
    if config.dicom_dir is None:
        assert config.images_dir is not None
        return config.images_dir / str(case["image_name"])

    assert config.cache_dir is not None
    dicom_path = config.dicom_dir / str(case["dicom_name"])
    png_path = config.cache_dir / str(case["image_name"])
    return ensure_display_png(dicom_path, png_path)


class AnnotationHandler(BaseHTTPRequestHandler):
    server_version = "PilotAnnotationTool/2.0"
    config: DatasetConfig

    def log_message(self, format_string: str, *args: object) -> None:
        print(f"[{self.log_date_time_string()}] {format_string % args}")

    def send_json(self, payload: object, status: int = HTTPStatus.OK) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def send_file(self, path: Path) -> None:
        if not path.is_file():
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        body = path.read_bytes()
        content_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        config = self.config
        parsed = urlparse(self.path)
        if parsed.path == "/":
            self.send_file(TOOL_DIR / "index.html")
            return
        if parsed.path in {"/app.js", "/styles.css"}:
            self.send_file(TOOL_DIR / parsed.path.lstrip("/"))
            return
        if parsed.path == "/api/cases":
            self.send_json(
                {
                    "dataset": config.name,
                    "label": config.label,
                    "cases": list(config.cases),
                    "correction_mode": config.correction_mode,
                    "correction_case_ids": list(config.correction_case_ids),
                }
            )
            return
        if parsed.path == "/api/annotation":
            name = parse_qs(parsed.query).get("file", [""])[0]
            if name not in config.cases_by_annotation:
                self.send_json({"error": "Fichier d'annotation non autorisé."}, HTTPStatus.NOT_FOUND)
                return
            path = config.annotations_dir / name
            try:
                data = json.loads(path.read_text(encoding="utf-8-sig"))
            except (OSError, json.JSONDecodeError) as exc:
                self.send_json({"error": f"JSON illisible : {exc}"}, HTTPStatus.INTERNAL_SERVER_ERROR)
                return
            self.send_json(
                {
                    "annotation": data,
                    "last_modified_ns": str(path.stat().st_mtime_ns),
                }
            )
            return
        if parsed.path.startswith("/images/"):
            name = unquote(parsed.path.removeprefix("/images/"))
            case = config.cases_by_image.get(name)
            if case is None:
                self.send_error(HTTPStatus.NOT_FOUND)
                return
            try:
                image_path = resolve_image_path(config, case)
            except (OSError, RuntimeError) as exc:
                self.send_json({"error": str(exc)}, HTTPStatus.INTERNAL_SERVER_ERROR)
                return
            self.send_file(image_path)
            return
        if parsed.path.startswith("/reference/yolo-overlay/"):
            if config.name != "new_26":
                self.send_error(HTTPStatus.NOT_FOUND)
                return
            pilot_id = unquote(parsed.path.removeprefix("/reference/yolo-overlay/"))
            allowed = {str(case["pilot_id"]) for case in config.cases}
            if pilot_id not in allowed:
                self.send_error(HTTPStatus.NOT_FOUND)
                return
            overlay_path = YOLO_OVERLAY_DIR / f"{pilot_id}_overlay.png"
            self.send_file(overlay_path)
            return
        if parsed.path == "/api/yolo-suggestions":
            if config.name != "new_26":
                self.send_json({"error": "Suggestions YOLO disponibles uniquement en new_26."}, HTTPStatus.NOT_FOUND)
                return
            query = parse_qs(parsed.query)
            pilot_id = query.get("pilot_id", [""])[0]
            allowed = {str(case["pilot_id"]) for case in config.cases}
            if pilot_id not in allowed:
                self.send_json({"error": "Cas non autorisé."}, HTTPStatus.NOT_FOUND)
                return
            try:
                width = float(query.get("width", ["0"])[0])
                height = float(query.get("height", ["0"])[0])
            except ValueError:
                self.send_json({"error": "Dimensions image invalides."}, HTTPStatus.BAD_REQUEST)
                return
            try:
                suggestions = load_yolo_suggestions(pilot_id, width, height)
            except ValueError as exc:
                self.send_json({"error": str(exc)}, HTTPStatus.UNPROCESSABLE_ENTITY)
                return
            if suggestions is None:
                self.send_json({"available": False, "suggestions": None})
                return
            self.send_json({"available": True, **suggestions})
            return
        self.send_error(HTTPStatus.NOT_FOUND)

    def do_POST(self) -> None:
        config = self.config
        parsed = urlparse(self.path)
        if parsed.path != "/api/anatomical-checks":
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        try:
            content_length = int(self.headers.get("Content-Length", "0"))
            if content_length <= 0 or content_length > 1_000_000:
                raise ValueError("Taille de requête invalide.")
            payload = json.loads(self.rfile.read(content_length))
        except (ValueError, json.JSONDecodeError) as exc:
            self.send_json({"error": f"Requête JSON invalide : {exc}"}, HTTPStatus.BAD_REQUEST)
            return

        landmarks = payload.get("landmarks")
        width = payload.get("image_width")
        height = payload.get("image_height")
        if not isinstance(landmarks, list):
            self.send_json({"error": "landmarks requis."}, HTTPStatus.BAD_REQUEST)
            return
        if not is_number(width) or not is_number(height):
            self.send_json({"error": "image_width et image_height requis."}, HTTPStatus.BAD_REQUEST)
            return

        warnings = run_anatomical_checks(landmarks, float(width), float(height))
        self.send_json({"warnings": warnings})

    def do_PUT(self) -> None:
        config = self.config
        parsed = urlparse(self.path)
        if parsed.path != "/api/annotation":
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        name = parse_qs(parsed.query).get("file", [""])[0]
        case = config.cases_by_annotation.get(name)
        if case is None:
            self.send_json({"error": "Fichier d'annotation non autorisé."}, HTTPStatus.NOT_FOUND)
            return

        try:
            content_length = int(self.headers.get("Content-Length", "0"))
            if content_length <= 0 or content_length > 1_000_000:
                raise ValueError("Taille de requête invalide.")
            payload = json.loads(self.rfile.read(content_length))
        except (ValueError, json.JSONDecodeError) as exc:
            self.send_json({"error": f"Requête JSON invalide : {exc}"}, HTTPStatus.BAD_REQUEST)
            return

        annotation = payload.get("annotation")
        finalize = payload.get("finalize") is True
        errors = validate_annotation(annotation, case, config, finalize)
        if errors:
            self.send_json({"error": "Validation refusée.", "details": errors}, HTTPStatus.UNPROCESSABLE_ENTITY)
            return

        path = config.annotations_dir / name
        expected_mtime = payload.get("last_modified_ns")
        if expected_mtime != str(path.stat().st_mtime_ns):
            self.send_json(
                {"error": "Le fichier a changé sur disque. Rechargez-le avant de sauvegarder."},
                HTTPStatus.CONFLICT,
            )
            return

        serialized = json.dumps(annotation, ensure_ascii=False, indent=2) + "\n"
        temporary_name: str | None = None
        try:
            with tempfile.NamedTemporaryFile(
                "w",
                encoding="utf-8",
                newline="\n",
                dir=config.annotations_dir,
                prefix=f".{name}.",
                suffix=".tmp",
                delete=False,
            ) as temporary:
                temporary.write(serialized)
                temporary.flush()
                os.fsync(temporary.fileno())
                temporary_name = temporary.name
            os.replace(temporary_name, path)
        finally:
            if temporary_name and Path(temporary_name).exists():
                Path(temporary_name).unlink()

        self.send_json(
            {
                "saved": True,
                "finalized": finalize,
                "last_modified_ns": str(path.stat().st_mtime_ns),
            }
        )


def main() -> None:
    parser = argparse.ArgumentParser(description="Outil local d'annotation manuelle.")
    parser.add_argument("--port", type=int, default=8765, help="Port local (défaut : 8765)")
    parser.add_argument(
        "--dataset",
        choices=("pilot", "new_26"),
        default="pilot",
        help="Jeu de données : pilot (16 JPEG) ou new_26 (26 DICOM bassin)",
    )
    parser.add_argument(
        "--cases",
        nargs="+",
        metavar="PILOT_ID",
        help="Limiter la session à certains cas (ex. --cases B26_25 B26_26). Mode correction.",
    )
    args = parser.parse_args()
    if not 1024 <= args.port <= 65535:
        parser.error("Le port doit être compris entre 1024 et 65535.")

    only_case_ids = tuple(args.cases) if args.cases else None
    config = build_dataset_config(args.dataset, only_case_ids)
    AnnotationHandler.config = config

    server = ThreadingHTTPServer(("127.0.0.1", args.port), AnnotationHandler)
    print(f"Dataset : {config.label}")
    if config.correction_mode:
        print(f"Mode correction — cas autorisés : {', '.join(config.correction_case_ids)}")
    print(f"Outil prêt : http://127.0.0.1:{args.port}")
    if config.dicom_dir is not None:
        print("Affichage DICOM : PNG mises en cache localement (originaux intacts).")
    print("Arrêt : Ctrl+C")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nArrêt du serveur.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
