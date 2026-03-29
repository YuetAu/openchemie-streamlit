"""PDF validation utilities."""

from __future__ import annotations

from io import BytesIO

from pypdf import PdfReader


MAX_UPLOAD_MB = 50


def validate_pdf_bytes(raw_pdf: bytes) -> tuple[bool, str]:
    """Validate uploaded PDF bytes.

    Returns:
        (is_valid, message)
    """
    if not raw_pdf:
        return False, "Uploaded file is empty."

    size_mb = len(raw_pdf) / (1024 * 1024)
    if size_mb > MAX_UPLOAD_MB:
        return False, f"PDF is too large ({size_mb:.1f} MB). Maximum size is {MAX_UPLOAD_MB} MB."

    if not raw_pdf.startswith(b"%PDF"):
        return False, "File does not appear to be a valid PDF (missing %PDF header)."

    try:
        reader = PdfReader(BytesIO(raw_pdf))
        if len(reader.pages) == 0:
            return False, "PDF contains no pages."
    except Exception as exc:  # pragma: no cover - specific parser exceptions vary
        return False, f"Unable to read PDF: {exc}"

    return True, "PDF is valid."
