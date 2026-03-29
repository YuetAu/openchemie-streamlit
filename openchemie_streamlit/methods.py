"""Canonical OpenChemIE method registry used by the Streamlit UI."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class MethodSpec:
    method_id: str
    label: str
    description: str


METHOD_SPECS: tuple[MethodSpec, ...] = (
    MethodSpec(
        method_id="extract_figures_from_pdf",
        label="Extract figures from PDF",
        description="Get figure regions and metadata from the uploaded PDF.",
    ),
    MethodSpec(
        method_id="extract_tables_from_pdf",
        label="Extract tables from PDF",
        description="Extract table structures and metadata from the uploaded PDF.",
    ),
    MethodSpec(
        method_id="extract_molecules_from_text_in_pdf",
        label="Extract molecules from text in PDF",
        description="Identify molecule mentions from document text.",
    ),
    MethodSpec(
        method_id="extract_molecules_from_figures_in_pdf",
        label="Extract molecules from figures in PDF",
        description="Detect molecules directly from PDF figures.",
    ),
    MethodSpec(
        method_id="extract_reactions_from_text_in_pdf",
        label="Extract reactions from text in PDF",
        description="Identify reaction information from document text.",
    ),
    MethodSpec(
        method_id="extract_reactions_from_figures_in_pdf",
        label="Extract reactions from figures in PDF",
        description="Detect reactions from figures found in the PDF.",
    ),
    MethodSpec(
        method_id="extract_reactions_from_pdf",
        label="Extract reactions from PDF",
        description="Run full reaction extraction pipeline over the PDF.",
    ),
    MethodSpec(
        method_id="extract_reactions_from_text_in_pdf_combined",
        label="Extract reactions from text in PDF (combined)",
        description="Run combined text-based reaction extraction pipeline.",
    ),
    MethodSpec(
        method_id="extract_reactions_from_figures_and_tables_in_pdf",
        label="Extract reactions from figures and tables in PDF",
        description="Extract reactions from both figure and table sources.",
    ),
    MethodSpec(
        method_id="extract_molecule_corefs_from_figures_in_pdf",
        label="Extract molecule coreferences from figures in PDF",
        description="Resolve molecule coreferences from PDF figure content.",
    ),
    MethodSpec(
        method_id="extract_molecules_from_figures",
        label="Extract molecules from figures",
        description="Run molecule extraction on figure objects.",
    ),
    MethodSpec(
        method_id="extract_reactions_from_figures",
        label="Extract reactions from figures",
        description="Run reaction extraction on figure objects.",
    ),
    MethodSpec(
        method_id="extract_molecule_bboxes_from_figures",
        label="Extract molecule bounding boxes from figures",
        description="Extract molecule bounding boxes from figure objects.",
    ),
    MethodSpec(
        method_id="extract_molecule_corefs_from_figures",
        label="Extract molecule coreferences from figures",
        description="Resolve molecule coreferences from figure objects.",
    ),
)

METHOD_IDS: tuple[str, ...] = tuple(spec.method_id for spec in METHOD_SPECS)


def get_method_specs() -> list[MethodSpec]:
    """Return method specs in canonical deterministic order."""
    return list(METHOD_SPECS)
