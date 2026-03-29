from __future__ import annotations

from io import BytesIO

from pypdf import PdfWriter

from openchemie_streamlit.executor import OpenChemIERunner


class ProgressBackend:
    def __init__(self) -> None:
        self.loaded: list[str] = []
        self.calls: list[str] = []

    @property
    def pdfparser(self) -> str:
        self.loaded.append("pdfparser")
        return "pdfparser"

    @property
    def rxnscribe(self) -> str:
        self.loaded.append("rxnscribe")
        return "rxnscribe"

    def extract_figures_from_pdf(self, _pdf_path: str) -> dict[str, object]:
        self.calls.append("extract_figures_from_pdf")
        return {"figures": [{"id": 1}]}

    def extract_reactions_from_figures(self, _pdf_path: str) -> dict[str, object]:
        self.calls.append("extract_reactions_from_figures")
        return {"reactions": [{"id": 2}]}


def _sample_pdf() -> bytes:
    writer = PdfWriter()
    writer.add_blank_page(width=300, height=300)
    output = BytesIO()
    writer.write(output)
    return output.getvalue()


def test_prepare_models_emits_progress_and_loads_required_components() -> None:
    backend = ProgressBackend()
    runner = OpenChemIERunner(backend=backend)
    progress_events: list[tuple[int, int, str]] = []

    runner.prepare_models(
        ["extract_figures_from_pdf", "extract_reactions_from_figures"],
        progress_callback=lambda done, total, msg: progress_events.append((done, total, msg)),
    )

    assert backend.loaded == ["pdfparser", "rxnscribe"]
    assert progress_events[0][0] == 0
    assert progress_events[-1][0] == 2
    assert progress_events[-1][1] == 2


def test_run_selected_emits_execution_progress() -> None:
    backend = ProgressBackend()
    runner = OpenChemIERunner(backend=backend)
    progress_events: list[tuple[int, int, str]] = []

    results = runner.run_selected(
        ["extract_figures_from_pdf", "extract_reactions_from_figures"],
        _sample_pdf(),
        progress_callback=lambda done, total, msg: progress_events.append((done, total, msg)),
    )

    assert len(results) == 2
    assert progress_events[0][0] == 0
    assert progress_events[-1][0] == 2
    assert progress_events[-1][1] == 2
    assert backend.calls == ["extract_figures_from_pdf", "extract_reactions_from_figures"]
