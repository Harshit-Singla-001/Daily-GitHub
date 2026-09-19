from embeddings import create_embedding
from vector_store import load_store, cosine_similarity
from config import TOP_K, SIMILARITY_THRESHOLD

def retrieve(question, top_k=TOP_K):
    records = load_store()

    if not records:
        return []

    question_embedding = create_embedding(question)
    results = []

    for record in records:
        score = cosine_similarity(
            question_embedding,
            record["embedding"]
        )

        result = record.copy()
        result["score"] = round(score, 4)
        results.append(result)

    results.sort(
        key=lambda item: item["score"],
        reverse=True
    )

    filtered = [
        item for item in results
        if item["score"] >= SIMILARITY_THRESHOLD
    ]

    return filtered[:top_k]