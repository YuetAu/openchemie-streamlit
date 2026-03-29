from openchemie_streamlit.methods import METHOD_IDS


def test_registry_contains_all_required_methods() -> None:
    expected = {
        "extract_molecules_from_figures_in_pdf",
        "extract_molecules_from_text_in_pdf",
        "extract_reactions_from_figures_in_pdf",
        "extract_reactions_from_text_in_pdf",
        "extract_reactions_from_pdf",
        "extract_reactions_from_text_in_pdf_combined",
        "extract_reactions_from_figures_and_tables_in_pdf",
        "extract_molecule_corefs_from_figures_in_pdf",
        "extract_molecules_from_figures",
        "extract_reactions_from_figures",
        "extract_molecule_bboxes_from_figures",
        "extract_molecule_corefs_from_figures",
        "extract_figures_from_pdf",
        "extract_tables_from_pdf",
    }
    assert set(METHOD_IDS) == expected


def test_registry_order_is_deterministic() -> None:
    assert METHOD_IDS == tuple(METHOD_IDS)
