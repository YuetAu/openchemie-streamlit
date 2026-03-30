from __future__ import annotations

import traceback

import streamlit as st

from openchemie_streamlit.executor import OpenChemIERunner
from openchemie_streamlit.methods import METHOD_SPECS
from openchemie_streamlit.pdf_utils import validate_pdf_bytes
from openchemie_streamlit.ui import render_export, render_result_panels, render_run_summary

st.set_page_config(page_title="OpenChemIE Streamlit Runner", layout="wide")

st.title("OpenChemIE PDF Method Runner")
st.write("Upload a PDF, select extraction methods, and inspect/export method-level results.")

with st.container(border=True):
    st.subheader("1) Upload PDF")
    uploaded = st.file_uploader("Choose a PDF", type=["pdf"])

pdf_bytes: bytes | None = None
pdf_is_valid = False
if uploaded is not None:
    pdf_bytes = uploaded.read()
    pdf_is_valid, validation_msg = validate_pdf_bytes(pdf_bytes)
    if pdf_is_valid:
        st.success(validation_msg)
    else:
        st.error(validation_msg)

with st.container(border=True):
    st.subheader("2) Choose Methods")
    all_method_ids = [method.method_id for method in METHOD_SPECS]
    id_to_spec = {method.method_id: method for method in METHOD_SPECS}

    default_selection = [
        "extract_figures_from_pdf",
        "extract_tables_from_pdf",
    ]

    selected_method_ids = st.multiselect(
        "Select one or more methods",
        options=all_method_ids,
        default=[method for method in default_selection if method in all_method_ids],
        format_func=lambda method_id: f"{id_to_spec[method_id].label} ({method_id})",
        disabled=not pdf_is_valid,
    )

    run_all = st.checkbox("Run all methods", value=False, disabled=not pdf_is_valid)
    if run_all:
        selected_method_ids = all_method_ids

    if selected_method_ids:
        st.caption("Selected methods:")
        for method_id in selected_method_ids:
            spec = id_to_spec[method_id]
            st.markdown(f"- `{spec.method_id}`: {spec.description}")

with st.container(border=True):
    st.subheader("3) Execute")
    skip_preload = st.checkbox(
        "Skip model preloading (recommended on Streamlit Cloud)",
        value=True,
        help="Loads models lazily during each method call to reduce startup spikes.",
        disabled=not pdf_is_valid,
    )
    if not skip_preload and len(selected_method_ids) > 3:
        st.warning(
            "Preloading many methods may take a long time and can exceed Cloud limits. "
            "Consider enabling skip preloading or running fewer methods."
        )
    run_clicked = st.button(
        "Run selected methods",
        type="primary",
        disabled=not pdf_is_valid or len(selected_method_ids) == 0,
        use_container_width=True,
    )

if run_clicked and pdf_bytes:
    st.subheader("4) Results")
    progress_text = st.empty()
    progress_bar = st.progress(0)

    try:
        runner = OpenChemIERunner()
    except RuntimeError as exc:
        st.error(str(exc))
        st.info(
            "Install OpenChemIE in your active environment, then restart Streamlit. "
            "Example:\n\n"
            "```bash\n"
            "pip install git+https://github.com/CrystalEye42/OpenChemIE.git\n"
            "```"
        )
        with st.expander("Show full error details", expanded=True):
            root = exc.__cause__ or exc
            st.exception(root)
            st.code(traceback.format_exc())
        st.stop()

    selected_method_ids = list(dict.fromkeys(selected_method_ids))

    if skip_preload:
        progress_text.info("Skipping preload. Models will download/load lazily per method.")
        progress_bar.progress(40)
    else:
        progress_text.info("Preparing required models and downloads...")

        def model_progress(done: int, total: int, message: str) -> None:
            if total <= 0:
                progress_bar.progress(20)
                progress_text.info(f"Model preparation: {message}")
                return
            pct = int((done / total) * 40)
            progress_bar.progress(min(max(pct, 0), 40))
            progress_text.info(f"Model preparation {done}/{total}: {message}")

        try:
            runner.prepare_models(selected_method_ids, progress_callback=model_progress)
        except Exception as exc:
            progress_bar.progress(100)
            progress_text.error("Model preparation failed.")
            st.error(f"Model loading error: {exc}")
            with st.expander("Show full error details", expanded=True):
                st.exception(exc)
                st.code(traceback.format_exc())
            st.stop()

    def run_progress(done: int, total: int, message: str) -> None:
        if total <= 0:
            progress_bar.progress(100)
            progress_text.info(message)
            return
        base = 40
        span = 60
        pct = base + int((done / total) * span)
        progress_bar.progress(min(max(pct, base), 100))
        progress_text.info(f"Execution {done}/{total}: {message}")

    try:
        results = runner.run_selected(selected_method_ids, pdf_bytes, progress_callback=run_progress)
    except Exception as exc:
        progress_bar.progress(100)
        progress_text.error("Execution failed.")
        st.error(f"Run error: {exc}")
        with st.expander("Show full error details", expanded=True):
            st.exception(exc)
            st.code(traceback.format_exc())
        st.stop()

    progress_bar.progress(100)
    progress_text.success("Execution complete.")

    render_run_summary(results)
    render_result_panels(results)
    render_export(results)
elif run_clicked:
    st.error("Upload a valid PDF before running methods.")
