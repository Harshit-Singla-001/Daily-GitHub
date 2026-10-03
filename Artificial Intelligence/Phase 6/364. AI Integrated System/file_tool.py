import os

from config import KNOWLEDGE_FOLDER


def search_files(
    query,
    max_results=5
):
    if not query or not query.strip():
        return []

    query_words = [
        word.lower()
        for word in query.split()
        if word.strip()
    ]

    results = []

    if not os.path.exists(
        KNOWLEDGE_FOLDER
    ):
        return results

    for filename in os.listdir(
        KNOWLEDGE_FOLDER
    ):
        if not filename.lower().endswith(
            ".txt"
        ):
            continue

        file_path = os.path.join(
            KNOWLEDGE_FOLDER,
            filename
        )

        try:
            with open(
                file_path,
                "r",
                encoding="utf-8",
                errors="ignore"
            ) as file:
                text = file.read()

        except OSError:
            continue

        text_lower = text.lower()

        matches = sum(
            1
            for word in query_words
            if word in text_lower
        )

        if matches > 0:
            results.append(
                {
                    "file": filename,
                    "matches": matches,
                    "preview": text[:1000]
                }
            )

    results.sort(
        key=lambda item: item["matches"],
        reverse=True
    )

    return results[:max_results]