# OpenChemIE Streamlit Frontend

This repository provides a Streamlit frontend to run OpenChemIE extraction methods against an uploaded PDF and inspect results per method.

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Install OpenChemIE in the same environment (for example from source or package) so the frontend can call its extraction methods.

## System Dependencies

Some PDF methods require Poppler (used by `pdf2image`).

- Local (macOS): `brew install poppler`
- Local (Ubuntu/Debian): `sudo apt-get install -y poppler-utils`
- Streamlit Cloud: include `packages.txt` with:
  - `poppler-utils`

## Run the app

```bash
streamlit run streamlit_app.py
```

## Supported methods

- `extract_molecules_from_figures_in_pdf`
- `extract_molecules_from_text_in_pdf`
- `extract_reactions_from_figures_in_pdf`
- `extract_reactions_from_text_in_pdf`
- `extract_reactions_from_pdf`
- `extract_reactions_from_text_in_pdf_combined`
- `extract_reactions_from_figures_and_tables_in_pdf`
- `extract_molecule_corefs_from_figures_in_pdf`
- `extract_molecules_from_figures`
- `extract_reactions_from_figures`
- `extract_molecule_bboxes_from_figures`
- `extract_molecule_corefs_from_figures`
- `extract_figures_from_pdf`
- `extract_tables_from_pdf`

## Troubleshooting

- `Could not import openchemie`: install OpenChemIE in this environment.
- Validation errors: ensure the input is a valid, readable PDF under 50 MB.
- Slow runs: run fewer methods first, then scale up to all methods.
- Dependency compatibility for OpenChemIE 0.1.0:
  - `torch==1.13.1`
  - `torchvision==0.14.1`
  - `transformers==4.30.2`
  - `numpy<2`

## Manual Verification Notes

Manual end-to-end verification should include:

1. Upload a known-good sample PDF and run 2-3 methods.
2. Confirm per-method statuses and durations appear.
3. Confirm one intentionally failing method does not stop others.
4. Download JSON results and verify status/payload fields.

Known limitations:

- Method signatures may differ between OpenChemIE versions; this frontend first tries a file path call, then bytes as a fallback.
- Some complex outputs may be shown as JSON-like normalized objects rather than rich visual overlays.
