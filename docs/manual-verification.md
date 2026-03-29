# Manual End-to-End Verification

Date: 2026-03-30

## Scope

Verify the Streamlit frontend flow for upload, method selection, execution sequencing, failure isolation, and JSON export.

## Procedure Performed

1. Created a sample 1-page PDF in memory.
2. Validated the PDF with `validate_pdf_bytes`.
3. Ran deterministic sequential execution with a demo backend for:
   - `extract_figures_from_pdf`
   - `extract_tables_from_pdf`
   - `extract_reactions_from_pdf` (intentional failure)
4. Confirmed one failure did not block remaining methods and that normalized envelopes were returned.

## Results

- PDF validation: `VALID True` with message `PDF is valid.`
- `extract_figures_from_pdf`: `success`
- `extract_tables_from_pdf`: `success`
- `extract_reactions_from_pdf`: `failed` with captured error

## Known Limitations

- This verification used a demo backend because OpenChemIE may not be installed in every local environment.
- Full production behavior depends on installed OpenChemIE version and model/runtime availability.
- Very large PDFs can still be expensive even with front-end validation and sequential execution.
