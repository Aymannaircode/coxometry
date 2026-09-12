"""Detect residual identifying metadata. Does not claim clinical de-id."""

from __future__ import annotations

from .constants import SENSITIVE_TAGS, UID_TAGS


def _nonempty(value) -> bool:
    if value is None:
        return False
    text = str(value).strip()
    return bool(text) and text not in {None, ""}


def detect_sensitive_metadata(dataset) -> list[str]:
    found: list[str] = []
    for name in SENSITIVE_TAGS:
        if hasattr(dataset, name) and _nonempty(getattr(dataset, name, None)):
            found.append(name)
    for elem in dataset:
        if elem.tag.is_private and _nonempty(elem.value):
            found.append(f"PRIVATE_{elem.tag}")
    return found


def collect_uids(dataset) -> dict[str, str]:
    return {name: str(getattr(dataset, name, "") or "") for name in UID_TAGS}
