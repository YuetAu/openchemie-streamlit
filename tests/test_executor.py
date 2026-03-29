from __future__ import annotations

from io import BytesIO

from pypdf import PdfWriter

from openchemie_streamlit.executor import OpenChemIERunner


class FakeBackend:
    def __init__(self) -> None:
        self.calls: list[str] = []

    def extract_figures_from_pdf(self, _pdf_path: str) -> dict[str, object]:
        self.calls.append("extract_figures_from_pdf")
        return {"figures": [{"id": 1}]}

    def extract_tables_from_pdf(self, _pdf_path: str) -> dict[str, object]:
        self.calls.append("extract_tables_from_pdf")
        raise RuntimeError("table parser failed")

    def extract_molecules_from_text_in_pdf(self, _pdf_path: str) -> dict[str, object]:
        self.calls.append("extract_molecules_from_text_in_pdf")
        return {"molecules": ["H2O"]}


def _sample_pdf() -> bytes:
    writer = PdfWriter()
    writer.add_blank_page(width=300, height=300)
    output = BytesIO()
    writer.write(output)
    return output.getvalue()


def test_runner_executes_in_order_and_isolates_failures() -> None:
    backend = FakeBackend()
    runner = OpenChemIERunner(backend=backend)

    method_ids = [
        "extract_figures_from_pdf",
        "extract_tables_from_pdf",
        "extract_molecules_from_text_in_pdf",
    ]
    results = runner.run_selected(method_ids, _sample_pdf())

    assert [result.method for result in results] == method_ids
    assert backend.calls == method_ids

    assert results[0].status == "success"
    assert results[0].data == {"figures": [{"id": 1}]}

    assert results[1].status == "failed"
    assert "table parser failed" in (results[1].error or "")

    assert results[2].status == "success"
    assert results[2].data == {"molecules": ["H2O"]}
