import faiss
import numpy as np


def create_store(embeddings):
    if len(embeddings) == 0:
        raise ValueError(
            "No embeddings available."
        )

    dimension = embeddings.shape[1]

    index = faiss.IndexFlatL2(
        dimension
    )

    index.add(
        embeddings.astype(
            np.float32
        )
    )

    return index


def search_store(
    index,
    query_embedding,
    chunks,
    top_k=4
):
    if index.ntotal == 0:
        return []

    top_k = min(
        top_k,
        index.ntotal
    )

    query = np.array(
        [query_embedding],
        dtype=np.float32
    )

    distances, indices = index.search(
        query,
        top_k
    )

    results = []

    for index in indices[0]:
        if index < len(chunks):
            results.append(
                chunks[index]
            )

    return results