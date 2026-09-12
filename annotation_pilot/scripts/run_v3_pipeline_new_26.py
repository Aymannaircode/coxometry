#!/usr/bin/env python3
"""Pipeline V3 complet : train → inference → géométrie → comparaison V2."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
PYTHON = SCRIPTS.parent.parent / ".venv" / "Scripts" / "python.exe"
STEPS = [
    "train_yolo_pose_v3_new_26.py",
    "run_yolo_pose_inference_v3_new_26.py",
    "test_v3_geometry_new_26.py",
    "compare_v2_v3_landmarks_new_26.py",
]


def run_step(name: str) -> None:
    script = SCRIPTS / name
    print(f"\n=== {name} ===")
    result = subprocess.run([str(PYTHON), str(script)], check=False)
    if result.returncode != 0:
        raise SystemExit(f"Échec : {name} (code {result.returncode})")


def main() -> int:
    for step in STEPS:
        run_step(step)
    print("\nV3 PIPELINE COMPLETE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
