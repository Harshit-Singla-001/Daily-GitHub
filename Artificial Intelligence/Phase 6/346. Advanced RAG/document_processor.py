import os
import pandas as pd
from pypdf import PdfReader
from docx import Document

def extract_txt(file_path):
    with open(
        file_path,
        "r",
        encoding="utf-8",
        errors="ignore"
    ) as file:
        return [{
            "text": file.read(),
            "page": None,
            "section": None
        }]

def extract_pdf(file_path):
    reader = PdfReader(file_path)
    pages = []

    for page_number, page in enumerate(
        reader.pages,
        start=1
    ):
        text = page.extract_text() or ""

        pages.append({
            "text": text,
            "page": page_number,
            "section": None
        })

    return pages

def extract_docx(file_path):
    document = Document(file_path)

    paragraphs = []

    for paragraph in document.paragraphs:
        text = paragraph.text.strip()

        if text:
            paragraphs.append(text)

    return [{
        "text": "\n\n".join(paragraphs),
        "page": None,
        "section": None
    }]

def extract_csv(file_path):
    dataframe = pd.read_csv(file_path)

    dataframe = dataframe.fillna("")

    text = dataframe.to_string(
        index=False
    )

    return [{
        "text": text,
        "page": None,
        "section": "CSV Data"
    }]

def extract_document(file_path):
    extension = os.path.splitext(
        file_path
    )[1].lower()

    if extension == ".txt":
        return extract_txt(file_path)

    if extension == ".pdf":
        return extract_pdf(file_path)

    if extension == ".docx":
        return extract_docx(file_path)

    if extension == ".csv":
        return extract_csv(file_path)

    raise ValueError(
        f"Unsupported file type: {extension}"
    )