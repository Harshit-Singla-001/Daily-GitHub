def create_chunks(
    text,
    chunk_size=800,
    overlap=150
):
    text = text.strip()

    if not text:
        return []

    if overlap >= chunk_size:
        raise ValueError(
            "Overlap must be smaller than chunk size."
        )

    chunks = []
    start = 0

    while start < len(text):
        end = min(
            start + chunk_size,
            len(text)
        )

        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        if end == len(text):
            break

        start = end - overlap

    return chunks