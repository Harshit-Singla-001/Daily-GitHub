import re


def split_sentences(text):
    text = re.sub(
        r"\s+",
        " ",
        text
    ).strip()

    if not text:
        return []

    sentences = re.split(
        r"(?<=[.!?])\s+",
        text
    )

    return [
        sentence.strip()
        for sentence in sentences
        if sentence.strip()
    ]


def create_chunks(
    text,
    document_name,
    page=1,
    chunk_size=800,
    overlap=120
):
    paragraphs = re.split(
        r"\n\s*\n",
        text
    )

    chunks = []

    current_sentences = []
    current_length = 0
    position = 0

    for paragraph in paragraphs:
        sentences = split_sentences(
            paragraph
        )

        for sentence in sentences:
            sentence_length = len(sentence)

            if (
                current_sentences
                and current_length + sentence_length > chunk_size
            ):
                chunk_text = " ".join(
                    current_sentences
                ).strip()

                if chunk_text:
                    chunks.append(
                        {
                            "chunk_id": f"{document_name}_{position}",
                            "text": chunk_text,
                            "document": document_name,
                            "page": page,
                            "section": "",
                            "position": position
                        }
                    )

                    position += 1

                overlap_text = []

                overlap_length = 0

                for previous in reversed(
                    current_sentences
                ):
                    if (
                        overlap_length
                        + len(previous)
                        > overlap
                    ):
                        break

                    overlap_text.insert(
                        0,
                        previous
                    )

                    overlap_length += len(previous)

                current_sentences = overlap_text

                current_length = sum(
                    len(item)
                    for item in current_sentences
                )

            current_sentences.append(
                sentence
            )

            current_length += sentence_length

    if current_sentences:
        chunk_text = " ".join(
            current_sentences
        ).strip()

        if chunk_text:
            chunks.append(
                {
                    "chunk_id": f"{document_name}_{position}",
                    "text": chunk_text,
                    "document": document_name,
                    "page": page,
                    "section": "",
                    "position": position
                }
            )

    return chunks