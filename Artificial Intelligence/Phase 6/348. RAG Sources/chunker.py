import re
import hashlib

from config import (
    CHUNK_SIZE,
    CHUNK_OVERLAP
)

def clean_text(text):
    if not text:
        return ""

    text = text.replace(
        "\x00",
        ""
    )

    text = re.sub(
        r"[ \t]+",
        " ",
        text
    )

    text = re.sub(
        r"\n{3,}",
        "\n\n",
        text
    )

    return text.strip()

def split_sentences(text):
    text = clean_text(text)

    if not text:
        return []

    paragraphs = re.split(
        r"\n\s*\n",
        text
    )

    sentences = []

    for paragraph in paragraphs:
        paragraph = paragraph.strip()

        if not paragraph:
            continue

        paragraph_sentences = re.split(
            r"(?<=[.!?])\s+",
            paragraph
        )

        for sentence in paragraph_sentences:
            sentence = sentence.strip()

            if sentence:
                sentences.append(
                    sentence
                )

    return sentences

def create_source_id(
    document_name,
    page,
    position
):
    raw_source = (
        f"{document_name}|"
        f"{page}|"
        f"{position}"
    )

    return hashlib.sha256(
        raw_source.encode(
            "utf-8"
        )
    ).hexdigest()[:12]

def create_chunks(
    text,
    document_name="Unknown",
    page=None,
    section=None
):
    text = clean_text(text)

    if not text:
        return []

    sentences = split_sentences(
        text
    )

    chunks = []
    current_sentences = []
    current_length = 0
    chunk_number = 1

    for sentence in sentences:
        sentence_length = len(
            sentence
        )

        if (
            current_sentences
            and
            current_length
            + sentence_length
            > CHUNK_SIZE
        ):
            chunk_text = (
                " ".join(
                    current_sentences
                ).strip()
            )

            source_id = create_source_id(
                document_name,
                page,
                chunk_number
            )

            chunks.append({
                "chunk_id": (
                    f"{document_name}_"
                    f"chunk_{chunk_number}"
                ),
                "source_id": source_id,
                "text": chunk_text,
                "document": document_name,
                "page": page,
                "section": section,
                "position": chunk_number
            })

            overlap_sentences = []
            overlap_length = 0

            for old_sentence in reversed(
                current_sentences
            ):
                if (
                    overlap_length
                    + len(old_sentence)
                    > CHUNK_OVERLAP
                ):
                    break

                overlap_sentences.insert(
                    0,
                    old_sentence
                )

                overlap_length += (
                    len(old_sentence)
                    + 1
                )

            current_sentences = (
                overlap_sentences
            )

            current_length = sum(
                len(sentence) + 1
                for sentence
                in current_sentences
            )

            chunk_number += 1

        current_sentences.append(
            sentence
        )

        current_length += (
            sentence_length + 1
        )

    if current_sentences:
        chunk_text = (
            " ".join(
                current_sentences
            ).strip()
        )

        source_id = create_source_id(
            document_name,
            page,
            chunk_number
        )

        chunks.append({
            "chunk_id": (
                f"{document_name}_"
                f"chunk_{chunk_number}"
            ),
            "source_id": source_id,
            "text": chunk_text,
            "document": document_name,
            "page": page,
            "section": section,
            "position": chunk_number
        })

    return chunks