from retriever import retrieve_chunks


def build_context(
    query_embedding,
    chunks,
    embeddings
):
    results = retrieve_chunks(
        query_embedding,
        chunks,
        embeddings
    )

    if not results:
        return "", []

    context = []
    sources = []

    for result in results:
        chunk = result["chunk"]

        context.append(
            (
                f"[Document: "
                f"{chunk['document']}]\n"
                f"{chunk['text']}"
            )
        )

        sources.append({
            "document": chunk["document"],
            "page": chunk["page"],
            "section": chunk["section"],
            "chunk_id": chunk["chunk_id"],
            "score": round(
                result["score"],
                4
            )
        })

    return (
        "\n\n".join(context),
        sources
    )