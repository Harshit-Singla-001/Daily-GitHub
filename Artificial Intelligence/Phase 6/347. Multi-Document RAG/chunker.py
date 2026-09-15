import re

from config import (
    CHUNK_SIZE,
    CHUNK_OVERLAP
)


def clean_text(text):
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
    return [
        sentence.strip()
        for sentence in re.split(
            r"(?<=[.!?])\s+",
            text
        )
        if sentence.strip()
    ]


def create_chunks(
    text,
    document_name,
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
    current = []
    current_length = 0
    number = 1

    for sentence in sentences:
        length = len(sentence)

        if (
            current
            and current_length + length
            > CHUNK_SIZE
        ):
            chunk_text = " ".join(
                current
            )

            chunks.append({
                "chunk_id": (
                    f"{document_name}_"
                    f"{number}"
                ),
                "text": chunk_text,
                "document": document_name,
                "page": page,
                "section": section,
                "position": number
            })

            overlap = []
            overlap_length = 0

            for old in reversed(current):
                if (
                    overlap_length
                    + len(old)
                    > CHUNK_OVERLAP
                ):
                    break

                overlap.insert(
                    0,
                    old
                )

                overlap_length += len(old)

            current = overlap
            current_length = overlap_length
            number += 1

        current.append(sentence)
        current_length += length + 1

    if current:
        chunks.append({
            "chunk_id": (
                f"{document_name}_"
                f"{number}"
            ),
            "text": " ".join(current),
            "document": document_name,
            "page": page,
            "section": section,
            "position": number
        })

    return chunks