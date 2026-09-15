import csv
import os

from docx import Document
from pypdf import PdfReader


def extract_txt(path):
    with open(
        path,
        "r",
        encoding="utf-8"
    ) as file:
        return file.read()


def extract_pdf(path):
    reader = PdfReader(path)

    pages = []

    for page_number, page in enumerate(
        reader.pages,
        start=1
    ):
        text = page.extract_text() or ""

        if text.strip():
            pages.append({
                "text": text,
                "page": page_number
            })

    return pages


def extract_docx(path):
    document = Document(path)

    text = []

    for paragraph in document.paragraphs:
        if paragraph.text.strip():
            text.append(
                paragraph.text
            )

    return "\n\n".join(text)


def extract_csv(path):
    rows = []

    with open(
        path,
        "r",
        encoding="utf-8-sig",
        newline=""
    ) as file:

        reader = csv.reader(file)

        for row in reader:
            rows.append(
                " | ".join(row)
            )

    return "\n".join(rows)


def process_document(path):
    extension = os.path.splitext(
        path
    )[1].lower()

    if extension == ".txt":
        return extract_txt(path)

    if extension == ".pdf":
        return extract_pdf(path)

    if extension == ".docx":
        return extract_docx(path)

    if extension == ".csv":
        return extract_csv(path)

    raise ValueError(
        f"Unsupported file type: {extension}"
    )