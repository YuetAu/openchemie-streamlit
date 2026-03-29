"""Serialization helpers for OpenChemIE outputs."""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence


def normalize_for_json(value: object) -> object:
    """Best-effort JSON normalization for heterogeneous outputs."""
    if value is None or isinstance(value, (str, int, float, bool)):
        return value

    if isinstance(value, Mapping):
        return {str(k): normalize_for_json(v) for k, v in value.items()}

    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return [normalize_for_json(v) for v in value]

    if hasattr(value, "model_dump"):
        return normalize_for_json(value.model_dump())

    if hasattr(value, "dict"):
        return normalize_for_json(value.dict())

    if hasattr(value, "__dict__"):
        raw_vars = vars(value)
        if raw_vars:
            return normalize_for_json(raw_vars)
        return repr(value)

    return repr(value)


def to_json_string(payload: object, indent: int = 2) -> str:
    """Serialize payload to deterministic JSON string."""
    normalized = normalize_for_json(payload)
    return json.dumps(normalized, indent=indent, ensure_ascii=False, sort_keys=True)


def infer_output_category(payload: object) -> str:
    """Infer a broad output category for UI-friendly rendering."""
    text = json.dumps(normalize_for_json(payload), ensure_ascii=False).lower()

    if "reaction" in text:
        return "reactions"
    if "molecule" in text:
        return "molecules"
    if "table" in text:
        return "tables"
    if "figure" in text:
        return "figures"
    if "bbox" in text or "bounding" in text:
        return "bboxes"
    if "coref" in text:
        return "coreferences"
    return "generic"
