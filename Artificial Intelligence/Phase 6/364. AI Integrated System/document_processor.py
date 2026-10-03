import csv
import os

import pymupdf
from docx import Document

from chunker import create_chunks


SUPPORTED_EXTENSIONS = {
    ".txt",
    ".pdf",
    ".docx",
    ".csv"
}


def extract_txt(file_path):
    with open(
        file_path,
        "r",
        encoding="utf-8",
        errors="ignore"
    ) as file:
        return file.read()


def extract_pdf(file_path):
    document = pymupdf.open(
        file_path
    )

    pages = []

    try:
        for page_number, page in enumerate(
            document,
            start=1
        ):
            text = page.get_text(
                "text"
            )

            pages.append(
                {
                    "page": page_number,
                    "text": text
                }
            )
    finally:
        document.close()

    return pages


def extract_docx(file_path):
    document = Document(
        file_path
    )

    text = "\n".join(
        paragraph.text
        for paragraph in document.paragraphs
        if paragraph.text.strip()
    )

    return text


def extract_csv(file_path):
    rows = []

    with open(
        file_path,
        "r",
        encoding="utf-8",
        errors="ignore",
        newline=""
    ) as file:
        reader = csv.reader(file)

        for row in reader:
            rows.append(
                " | ".join(row)
            )

    return "\n".join(rows)


def process_document(file_path):
    extension = os.path.splitext(
        file_path
    )[1].lower()

    document_name = os.path.basename(
        file_path
    )

    if extension not in SUPPORTED_EXTENSIONS:
        raise ValueError(
            f"Unsupported file type: {extension}"
        )

    chunks = []

    if extension == ".pdf":
        pages = extract_pdf(
            file_path
        )

        for page_data in pages:
            page_chunks = create_chunks(
                page_data["text"],
                document_name,
                page=page_data["page"]
            )

            chunks.extend(
                page_chunks
            )

    elif extension == ".txt":
        text = extract_txt(
            file_path
        )

        chunks = create_chunks(
            text,
            document_name
        )

    elif extension == ".docx":
        text = extract_docx(
            file_path
        )

        chunks = create_chunks(
            text,
            document_name
        )

    elif extension == ".csv":
        text = extract_csv(
            file_path
        )

        chunks = create_chunks(
            text,
            document_name
        )

    return chunks