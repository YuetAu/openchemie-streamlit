from io import BytesIO

from pypdf import PdfWriter

from openchemie_streamlit.pdf_utils import validate_pdf_bytes


def _build_pdf_bytes() -> bytes:
    writer = PdfWriter()
    writer.add_blank_page(width=300, height=300)
    output = BytesIO()
    writer.write(output)
    return output.getvalue()


def test_valid_pdf_is_accepted() -> None:
    ok, message = validate_pdf_bytes(_build_pdf_bytes())
    assert ok is True
    assert "valid" in message.lower()


def test_invalid_pdf_is_rejected() -> None:
    ok, message = validate_pdf_bytes(b"not-a-pdf")
    assert ok is False
    assert "valid pdf" in message.lower() or "missing" in message.lower()
