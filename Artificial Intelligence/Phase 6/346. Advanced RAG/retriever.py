import numpy as np
from config import (
    TOP_K,
    SIMILARITY_THRESHOLD,
    MAX_CONTEXT_CHUNKS
)

def normalize_vector(vector):
    vector = np.array(
        vector,
        dtype=np.float32
    ).reshape(1, -1)

    norm = np.linalg.norm(
        vector
    )

    if norm == 0:
        return vector

    return vector / norm

def retrieve_chunks(
    query_embedding,
    index,
    metadata
):
    if index is None:
        return []

    query_vector = normalize_vector(
        query_embedding
    )

    scores, indices = index.search(
        query_vector,
        TOP_K
    )

    results = []

    for score, index_position in zip(
        scores[0],
        indices[0]
    ):
        if index_position < 0:
            continue

        if score < SIMILARITY_THRESHOLD:
            continue

        if index_position >= len(metadata):
            continue

        item = metadata[
            index_position
        ].copy()

        item["score"] = float(score)

        results.append(item)

    results.sort(
        key=lambda item: item["score"],
        reverse=True
    )

    return results[
        :MAX_CONTEXT_CHUNKS
    ]