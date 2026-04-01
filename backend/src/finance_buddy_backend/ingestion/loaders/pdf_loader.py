from pathlib import Path

from pypdf import PdfReader


def extract_text_from_pdf(pdf_path: Path) -> str:
    if not pdf_path.exists():
        raise FileNotFoundError(f"File not found: {pdf_path}")

    reader = PdfReader(str(pdf_path))
    pages: list[str] = []

    for page in reader.pages:
        text = page.extract_text() or ""
        if text.strip():
            pages.append(text.strip())

    extracted_text = "\n\n".join(pages)

    if not extracted_text:
        raise ValueError(f"No text could be extracted from: {pdf_path}")

    return extracted_text