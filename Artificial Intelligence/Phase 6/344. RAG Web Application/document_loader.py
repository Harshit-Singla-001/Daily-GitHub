from pathlib import Path

import pandas as pd
from docx import Document
from pypdf import PdfReader


def load_txt(path):
    return Path(path).read_text(
        encoding="utf-8",
        errors="ignore"
    )


def load_pdf(path):
    reader = PdfReader(path)
    pages = []

    for page in reader.pages:
        text = page.extract_text()

        if text:
            pages.append(text)

    return "\n".join(pages)


def load_docx(path):
    document = Document(path)
    paragraphs = []

    for paragraph in document.paragraphs:
        if paragraph.text.strip():
            paragraphs.append(
                paragraph.text.strip()
            )

    return "\n".join(paragraphs)


def load_csv(path):
    dataframe = pd.read_csv(path)

    return dataframe.to_string(
        index=False
    )


def load_document(path):
    path = Path(path)

    extension = path.suffix.lower()

    if extension == ".txt":
        return load_txt(path)

    if extension == ".pdf":
        return load_pdf(path)

    if extension == ".docx":
        return load_docx(path)

    if extension == ".csv":
        return load_csv(path)

    raise ValueError(
        f"Unsupported file type: {extension}"
    )