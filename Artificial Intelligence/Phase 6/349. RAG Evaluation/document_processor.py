from pathlib import Path

def extract_text(file_path):
    path = Path(file_path)
    extension = path.suffix.lower()

    if extension == ".txt":
        return path.read_text(encoding="utf-8", errors="ignore")

    if extension == ".pdf":
        return extract_pdf(file_path)

    if extension == ".docx":
        return extract_docx(file_path)

    if extension == ".csv":
        return extract_csv(file_path)

    raise ValueError(f"Unsupported file type: {extension}")

def extract_pdf(file_path):
    from pypdf import PdfReader

    reader = PdfReader(file_path)
    pages = []

    for page_number, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        if text.strip():
            pages.append(f"[Page {page_number}]\n{text}")

    return "\n\n".join(pages)

def extract_docx(file_path):
    from docx import Document

    document = Document(file_path)
    paragraphs = []

    for paragraph in document.paragraphs:
        text = paragraph.text.strip()
        if text:
            paragraphs.append(text)

    return "\n".join(paragraphs)

def extract_csv(file_path):
    import pandas as pd

    dataframe = pd.read_csv(file_path)
    return dataframe.to_string(index=False)