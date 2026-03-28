import fitz
import docx


def extract_text(file_path: str) -> str:
    """
    Extracts raw text from a PDF or DOCX file.
    Preserves newlines so section headers can be detected downstream.
    """
    ext = file_path.lower()

    if ext.endswith(".pdf"):
        return _extract_pdf(file_path)
    elif ext.endswith(".docx"):
        return _extract_docx(file_path)
    else:
        raise ValueError(f"Unsupported file format: {file_path}. Only PDF and DOCX are supported.")


def _extract_pdf(file_path: str) -> str:
    """
    Extracts text from PDF using PyMuPDF.
    Preserves newlines between pages for section detection.
    """
    with fitz.open(file_path) as doc:
        pages = [page.get_text() for page in doc]
    return "\n".join(pages)


def _extract_docx(file_path: str) -> str:
    """
    Extracts text from DOCX using python-docx.
    Preserves paragraph breaks for section detection.
    Empty paragraphs are kept as blank lines (act as separators).
    """
    doc = docx.Document(file_path)
    return "\n".join(para.text for para in doc.paragraphs)