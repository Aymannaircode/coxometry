"""Generate the official synthetic fixture and run the isolated intake gate."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from intake.generate_synthetic_dicom import write_synthetic_dicom  # noqa: E402
from intake.gate import run_intake_gate  # noqa: E402
from intake.hashing import sha256_file  # noqa: E402


def main() -> int:
    fixture = write_synthetic_dicom(ROOT / "fixtures" / "synthetic_r27_001.dcm")
    incoming = write_synthetic_dicom(ROOT / "input" / "synthetic_r27_001.dcm")
    result = run_intake_gate(
        incoming,
        output_path=ROOT / "output" / "SYNTHETIC_R27_001_deidentified.dcm",
        index_path=ROOT / "reports" / "synthetic_duplicate_index.json",
        manifest_path=ROOT / "reports" / "SYNTHETIC_R27_001_provenance.json",
        register_index=True,
    )
    summary = {
        "gate_status": result.get("status"),
        "case_id": result.get("case_id"),
        "fixture_path": str(fixture),
        "input_hash": sha256_file(incoming),
        "fixture_hash": sha256_file(fixture),
        "source_file_hash": result.get("source_file_hash"),
        "deidentified_file_hash": result.get("deidentified_file_hash"),
        "pixel_hash": result.get("pixel_hash"),
        "pixel_hash_before": result.get("pixel_hash_before"),
        "output_path": result.get("output_path"),
        "manifest_path": result.get("manifest_path"),
        "reason": result.get("reason"),
    }
    (ROOT / "reports" / "dry_run_summary.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, indent=2))
    return 0 if result.get("status") == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
