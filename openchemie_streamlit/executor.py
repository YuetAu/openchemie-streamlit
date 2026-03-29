"""OpenChemIE method execution orchestration."""

from __future__ import annotations

import importlib
import time
from collections.abc import Callable
from dataclasses import asdict, dataclass
from pathlib import Path
from tempfile import NamedTemporaryFile

from .methods import METHOD_IDS
from .serialization import normalize_for_json


@dataclass
class MethodResult:
    method: str
    status: str
    duration_ms: int
    data: object | None
    error: str | None

    def as_dict(self) -> dict[str, object | None]:
        return asdict(self)


class OpenChemIERunner:
    """Runs selected OpenChemIE methods in deterministic sequence."""

    _COMPONENT_TO_ATTR: dict[str, str] = {
        "pdfparser": "pdfparser",
        "moldet": "moldet",
        "molscribe": "molscribe",
        "rxnscribe": "rxnscribe",
        "coref": "coref",
        "chemrxnextractor": "chemrxnextractor",
        "chemner": "chemner",
    }

    _COMPONENT_LABELS: dict[str, str] = {
        "pdfparser": "PDF layout parser",
        "moldet": "Molecule detector",
        "molscribe": "MolScribe",
        "rxnscribe": "RxnScribe",
        "coref": "Coreference model",
        "chemrxnextractor": "ChemRxnExtractor",
        "chemner": "ChemNER",
    }

    _METHOD_COMPONENTS: dict[str, tuple[str, ...]] = {
        "extract_molecules_from_figures_in_pdf": ("pdfparser", "moldet", "molscribe"),
        "extract_molecules_from_text_in_pdf": ("chemrxnextractor", "chemner"),
        "extract_reactions_from_figures_in_pdf": ("pdfparser", "rxnscribe"),
        "extract_reactions_from_text_in_pdf": ("chemrxnextractor",),
        "extract_reactions_from_pdf": ("pdfparser", "rxnscribe", "molscribe", "chemrxnextractor", "coref"),
        "extract_reactions_from_text_in_pdf_combined": ("chemrxnextractor", "pdfparser", "coref"),
        "extract_reactions_from_figures_and_tables_in_pdf": ("pdfparser", "rxnscribe", "molscribe", "coref"),
        "extract_molecule_corefs_from_figures_in_pdf": ("pdfparser", "coref"),
        "extract_molecules_from_figures": ("moldet", "molscribe"),
        "extract_reactions_from_figures": ("rxnscribe",),
        "extract_molecule_bboxes_from_figures": ("moldet",),
        "extract_molecule_corefs_from_figures": ("coref",),
        "extract_figures_from_pdf": ("pdfparser",),
        "extract_tables_from_pdf": ("pdfparser",),
    }

    def __init__(self, backend: object | None = None) -> None:
        self.backend = backend or self._load_backend()

    def _load_backend(self) -> object:
        try:
            module = importlib.import_module("openchemie")
        except Exception as exc:  # pragma: no cover - import availability is env-specific
            raise RuntimeError(
                "Could not import openchemie. Install OpenChemIE in this environment "
                "to run extraction methods. Try: "
                "`pip install git+https://github.com/CrystalEye42/OpenChemIE.git`."
            ) from exc

        if hasattr(module, "OpenChemIE"):
            return module.OpenChemIE()
        return module

    def prepare_models(
        self,
        method_ids: list[str],
        progress_callback: Callable[[int, int, str], None] | None = None,
    ) -> None:
        """Warm up model components needed by selected methods.

        The callback receives (completed, total, message).
        """
        components = self._required_components(method_ids)
        total = len(components)
        if progress_callback:
            progress_callback(0, total, "Planning model warmup")

        for idx, component in enumerate(components, start=1):
            label = self._COMPONENT_LABELS.get(component, component)
            self._load_component(component)
            if progress_callback:
                progress_callback(idx, total, f"Ready: {label}")

    def run_selected(
        self,
        method_ids: list[str],
        raw_pdf: bytes,
        progress_callback: Callable[[int, int, str], None] | None = None,
    ) -> list[MethodResult]:
        unknown = [method_id for method_id in method_ids if method_id not in METHOD_IDS]
        if unknown:
            raise ValueError(f"Unknown methods requested: {', '.join(unknown)}")

        results: list[MethodResult] = []
        total = len(method_ids)
        if progress_callback:
            progress_callback(0, total, "Starting method execution")

        with NamedTemporaryFile(suffix=".pdf", delete=True) as temp_pdf:
            temp_pdf.write(raw_pdf)
            temp_pdf.flush()
            pdf_path = Path(temp_pdf.name)

            for idx, method_id in enumerate(method_ids, start=1):
                if progress_callback:
                    progress_callback(idx - 1, total, f"Running {method_id}")
                start = time.perf_counter()
                try:
                    result = self._invoke_method(method_id, pdf_path)
                    status = "success"
                    error: str | None = None
                    payload = normalize_for_json(result)
                except Exception as exc:
                    status = "failed"
                    error = str(exc)
                    payload = None

                duration_ms = int((time.perf_counter() - start) * 1000)
                results.append(
                    MethodResult(
                        method=method_id,
                        status=status,
                        duration_ms=duration_ms,
                        data=payload,
                        error=error,
                    )
                )
                if progress_callback:
                    progress_callback(idx, total, f"Completed {method_id} ({status})")

        return results

    def _required_components(self, method_ids: list[str]) -> list[str]:
        ordered_components: list[str] = []
        seen: set[str] = set()
        for method_id in method_ids:
            components = self._METHOD_COMPONENTS.get(method_id, ())
            for component in components:
                if component not in seen:
                    seen.add(component)
                    ordered_components.append(component)
        return ordered_components

    def _load_component(self, component: str) -> None:
        attr_name = self._COMPONENT_TO_ATTR.get(component)
        if not attr_name:
            return
        try:
            getattr(self.backend, attr_name)
        except AttributeError:
            return

    def _invoke_method(self, method_id: str, pdf_path: Path) -> object:
        method = getattr(self.backend, method_id, None)
        if method is None:
            raise AttributeError(f"Backend does not expose method: {method_id}")

        try:
            return method(str(pdf_path))
        except TypeError:
            raw_pdf = pdf_path.read_bytes()
            return method(raw_pdf)
