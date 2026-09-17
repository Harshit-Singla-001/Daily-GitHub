from google import genai

from config import (
    GEMINI_API_KEY,
    GEMINI_MODEL
)

from embeddings import (
    generate_embedding
)

from retriever import (
    retrieve_chunks
)

client = genai.Client(
    api_key=GEMINI_API_KEY
)

def build_context(results):
    if not results:
        return ""

    context_parts = []

    for result in results:
        source_number = (
            result["source_number"]
        )

        document = result.get(
            "document",
            "Unknown"
        )

        page = result.get(
            "page"
        )

        section = result.get(
            "section"
        )

        source_header = (
            f"[Source {source_number}] "
            f"Document: {document}"
        )

        if page:
            source_header += (
                f" | Page: {page}"
            )

        if section:
            source_header += (
                f" | Section: {section}"
            )

        context_parts.append(
            f"{source_header}\n"
            f"{result['text']}"
        )

    return "\n\n".join(
        context_parts
    )

def build_sources(results):
    sources = []

    for result in results:
        sources.append({
            "source_number": (
                result["source_number"]
            ),
            "source_id": (
                result.get(
                    "source_id"
                )
            ),
            "chunk_id": (
                result.get(
                    "chunk_id"
                )
            ),
            "document": (
                result.get(
                    "document",
                    "Unknown"
                )
            ),
            "page": (
                result.get(
                    "page"
                )
            ),
            "section": (
                result.get(
                    "section"
                )
            ),
            "position": (
                result.get(
                    "position"
                )
            ),
            "score": (
                result.get(
                    "score"
                )
            )
        })

    return sources

def generate_answer(
    question,
    index,
    metadata
):
    query_embedding = (
        generate_embedding(
            question
        )
    )

    results = retrieve_chunks(
        query_embedding,
        index,
        metadata
    )

    if not results:
        return {
            "answer": (
                "The information is not "
                "available in the uploaded "
                "documents."
            ),
            "sources": [],
            "retrieved_chunks": []
        }

    context = build_context(
        results
    )

    prompt = f"""
You are a document question-answering assistant.

Answer the user's question using ONLY the
provided document context.

SOURCE RULES:
1. Every factual claim must be supported by
   one or more provided sources.
2. Add source references directly after the
   relevant statement.
3. Use the exact format [Source 1],
   [Source 2], etc.
4. Never create a source that does not exist.
5. Do not use outside knowledge.
6. Do not invent facts.
7. If the answer is not present in the
   provided context, say:
   "The information is not available in the
   uploaded documents."
8. If multiple sources support the answer,
   reference all relevant sources.

DOCUMENT CONTEXT:

{context}

USER QUESTION:

{question}

ANSWER:
"""

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt
    )

    answer = (
        response.text.strip()
        if response.text
        else "No answer was generated."
    )

    return {
        "answer": answer,
        "sources": build_sources(
            results
        ),
        "retrieved_chunks": results
    }