"""Rendering helpers for Streamlit output sections."""

from __future__ import annotations

from collections import Counter

import streamlit as st

from .executor import MethodResult
from .serialization import infer_output_category, to_json_string


def render_run_summary(results: list[MethodResult]) -> None:
    total = len(results)
    counts = Counter(result.status for result in results)
    total_duration = sum(result.duration_ms for result in results)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Selected", total)
    col2.metric("Succeeded", counts.get("success", 0))
    col3.metric("Failed", counts.get("failed", 0))
    col4.metric("Total duration (ms)", total_duration)


def render_result_panels(results: list[MethodResult]) -> None:
    for result in results:
        header = f"{result.method} - {result.status.upper()} ({result.duration_ms} ms)"
        with st.expander(header, expanded=(result.status == "failed")):
            if result.error:
                st.error(result.error)
            if result.data is not None:
                category = infer_output_category(result.data)
                st.caption(f"Detected output type: {category}")
                st.json(result.data)
            else:
                st.info("No result payload returned.")


def render_export(results: list[MethodResult]) -> None:
    payload = [result.as_dict() for result in results]
    st.download_button(
        "Download run results (JSON)",
        data=to_json_string(payload),
        file_name="openchemie_run_results.json",
        mime="application/json",
        use_container_width=True,
    )
