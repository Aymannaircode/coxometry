"""Geometry / PixelData integrity. Unexpected change → INTEGRITY_FAIL."""

from __future__ import annotations

from .constants import GEOMETRY_TAGS
from .hashing import sha256_pixels


def _tag_value(dataset, name: str):
    if not hasattr(dataset, name):
        return None
    value = getattr(dataset, name)
    if value is None:
        return None
    if name == "PixelSpacing":
        return [float(v) for v in value]
    if name in {"Rows", "Columns", "BitsAllocated", "BitsStored", "HighBit", "PixelRepresentation", "SamplesPerPixel"}:
        return int(value)
    if name in {"RescaleSlope", "RescaleIntercept"}:
        return float(value)
    return str(value)


def read_integrity_snapshot(dataset) -> dict:
    snapshot = {name: _tag_value(dataset, name) for name in GEOMETRY_TAGS}
    if not hasattr(dataset, "PixelData") or not dataset.PixelData:
        snapshot["pixel_hash"] = None
        snapshot["pixel_data_present"] = False
        return snapshot
    snapshot["pixel_data_present"] = True
    snapshot["pixel_hash"] = sha256_pixels(dataset)
    return snapshot


def compare_integrity(before: dict, after: dict) -> dict:
    failures: list[str] = []
    required = (
        "Rows",
        "Columns",
        "PixelSpacing",
        "PhotometricInterpretation",
        "BitsAllocated",
        "BitsStored",
        "PixelRepresentation",
        "pixel_hash",
    )
    for name in required:
        if before.get(name) != after.get(name):
            failures.append(name)
    if not after.get("pixel_data_present"):
        failures.append("PixelData")
    for name in ("RescaleSlope", "RescaleIntercept", "PatientOrientation", "ImageOrientationPatient"):
        if before.get(name) is not None and before.get(name) != after.get(name):
            failures.append(name)
    status = "INTEGRITY_OK" if not failures else "INTEGRITY_FAIL"
    return {"status": status, "failures": failures, "before": before, "after": after}
