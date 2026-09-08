import os

import numpy as np


def normalize_vectors(vectors):
    norms = np.linalg.norm(
        vectors,
        axis=1,
        keepdims=True
    )

    norms = np.maximum(
        norms,
        1e-12
    )

    return vectors / norms


def create_store(
    chunks,
    embeddings
):
    embeddings = normalize_vectors(
        embeddings
    )

    return {
        "chunks": chunks,
        "embeddings": embeddings
    }


def save_store(store, path):
    os.makedirs(
        os.path.dirname(path),
        exist_ok=True
    )

    np.savez(
        path,
        chunks=np.array(
            store["chunks"],
            dtype=object
        ),
        embeddings=store["embeddings"]
    )


def load_store(path):
    data = np.load(
        path,
        allow_pickle=True
    )

    return {
        "chunks": data["chunks"].tolist(),
        "embeddings": data["embeddings"]
    }


def search(
    store,
    query_embedding,
    top_k=3
):
    query_embedding = (
        query_embedding
        / max(
            np.linalg.norm(
                query_embedding
            ),
            1e-12
        )
    )

    scores = (
        store["embeddings"]
        @ query_embedding
    )

    indexes = np.argsort(
        scores
    )[::-1][:top_k]

    results = []

    for index in indexes:
        results.append({
            "chunk": store["chunks"][index],
            "score": float(scores[index])
        })

    return results