from __future__ import annotations

from dataclasses import dataclass

from openchemie_streamlit.serialization import infer_output_category, normalize_for_json


@dataclass
class CustomObj:
    name: str


class WeirdObject:
    pass


def test_normalize_handles_dataclasses_and_unserializable_objects() -> None:
    payload = {
        "nested": [CustomObj(name="mol")],
        "weird": WeirdObject(),
    }

    normalized = normalize_for_json(payload)

    assert normalized["nested"] == [{"name": "mol"}]
    assert isinstance(normalized["weird"], str)


def test_infer_output_category() -> None:
    assert infer_output_category({"reactions": [{"id": 1}]}) == "reactions"
    assert infer_output_category({"molecules": [{"name": "CO2"}]}) == "molecules"
    assert infer_output_category({"tables": [{"rows": 3}]}) == "tables"
