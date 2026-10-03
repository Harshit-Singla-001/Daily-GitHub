from config import (
    TOP_K,
    SIMILARITY_THRESHOLD
)

from embeddings import create_query_embedding

from vector_store import (
    load_vectors,
    cosine_similarity
)


def retrieve(
    query,
    top_k=None,
    threshold=None
):
    if top_k is None:
        top_k = TOP_K

    if threshold is None:
        threshold = SIMILARITY_THRESHOLD

    query_embedding = create_query_embedding(
        query
    )

    vectors = load_vectors()

    scored = []

    for item in vectors:
        score = cosine_similarity(
            query_embedding,
            item["embedding"]
        )

        if score >= threshold:
            result = {
                "chunk_id": item["chunk_id"],
                "text": item["text"],
                "document": item["document"],
                "page": item.get("page", 1),
                "section": item.get("section", ""),
                "position": item.get("position", 0),
                "score": round(
                    float(score),
                    4
                )
            }

            scored.append(
                result
            )

    scored.sort(
        key=lambda item: item["score"],
        reverse=True
    )

    return scored[:top_k]