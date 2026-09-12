#!/usr/bin/env python3
"""Initialise worklist.csv et JSON vides pour le lot bassin (26 cas retenus CSV)."""

from __future__ import annotations

import sys
from pathlib import Path

TOOL_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOL_DIR))

from prepare_manual_annotation_new_26 import ensure_worklist_and_json  # noqa: E402
from verification_radios import DICOM_DIR, selected_dicom_names  # noqa: E402


def main() -> None:
    selected = selected_dicom_names()
    if len(selected) != 26:
        raise SystemExit(
            f"Attendu 26 DICOM utilisable=oui dans verification_radios.csv, trouvé {len(selected)}"
        )
    missing = [name for name in selected if not (DICOM_DIR / name).is_file()]
    if missing:
        raise SystemExit(f"DICOM absent(s) dans {DICOM_DIR}: {', '.join(missing)}")

    rows = ensure_worklist_and_json(selected)
    print(f"Initialisé {len(rows)} cas depuis verification_radios.csv → {TOOL_DIR.parent / 'annotations' / 'new_26'}")


if __name__ == "__main__":
    main()
