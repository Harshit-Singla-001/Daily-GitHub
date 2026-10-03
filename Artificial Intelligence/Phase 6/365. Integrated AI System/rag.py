from retriever import retrieve


def build_context(
    retrieved_chunks
):
    if not retrieved_chunks:
        return ""

    context_parts = []

    for index, chunk in enumerate(
        retrieved_chunks,
        start=1
    ):
        context_parts.append(
            f"""
[Source {index}]
Document: {chunk["document"]}
Page: {chunk["page"]}
Section: {chunk["section"]}
Similarity: {chunk["score"]}

Content:
{chunk["text"]}
"""
        )

    return "\n".join(
        context_parts
    )


def search_knowledge_base(
    query
):
    chunks = retrieve(
        query
    )

    context = build_context(
        chunks
    )

    sources = []

    for index, chunk in enumerate(
        chunks,
        start=1
    ):
        sources.append(
            {
                "source_number": index,
                "document": chunk["document"],
                "page": chunk["page"],
                "section": chunk["section"],
                "score": chunk["score"],
                "chunk_id": chunk["chunk_id"]
            }
        )

    return {
        "context": context,
        "sources": sources,
        "chunks": chunks
    }