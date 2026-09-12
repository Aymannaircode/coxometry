"""Lecture des radiographies retenues depuis bassin/verification_radios.csv."""

from __future__ import annotations

import csv
from pathlib import Path

TOOL_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = TOOL_DIR.parent.parent
VERIFICATION_CSV = PROJECT_ROOT / "bassin" / "verification_radios.csv"
DICOM_DIR = PROJECT_ROOT / "bassin" / "a_annoter"


def load_verification_rows() -> list[dict[str, str]]:
    if not VERIFICATION_CSV.is_file():
        raise FileNotFoundError(f"CSV introuvable : {VERIFICATION_CSV}")
    with VERIFICATION_CSV.open("r", encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def selected_dicom_names(*, require_usable: str = "oui") -> list[str]:
    """Retourne les noms DICOM retenus (utilisable_annotation == oui), tri stables."""
    rows = load_verification_rows()
    selected = [
        row["nom_fichier"].strip().strip('"')
        for row in rows
        if row.get("utilisable_annotation", "").strip().lower() == require_usable.lower()
    ]
    return sorted(selected)


def verification_by_dicom() -> dict[str, dict[str, str]]:
    return {
        row["nom_fichier"].strip().strip('"'): row
        for row in load_verification_rows()
    }
