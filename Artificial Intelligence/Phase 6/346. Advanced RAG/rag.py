from google import genai

from config import (
    GEMINI_API_KEY,
    GEMINI_MODEL
)

from embeddings import generate_embedding
from retriever import retrieve_chunks

client = genai.Client(
    api_key=GEMINI_API_KEY
)

def build_context(results):
    if not results:
        return ""

    context_parts = []

    for number, result in enumerate(
        results,
        start=1
    ):
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

        source_info = (
            f"Document: {document}"
        )

        if page:
            source_info += (
                f" | Page: {page}"
            )

        if section:
            source_info += (
                f" | Section: {section}"
            )

        context_parts.append(
            f"[Context {number}]\n"
            f"{source_info}\n"
            f"{result['text']}"
        )

    return "\n\n".join(
        context_parts
    )

def build_sources(results):
    sources = []

    seen = set()

    for result in results:
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

        key = (
            document,
            page,
            section
        )

        if key in seen:
            continue

        seen.add(key)

        sources.append({
            "document": document,
            "page": page,
            "section": section,
            "score": round(
                result.get(
                    "score",
                    0
                ),
                4
            )
        })

    return sources

def generate_answer(
    question,
    index,
    metadata
):
    query_embedding = generate_embedding(
        question
    )

    results = retrieve_chunks(
        query_embedding,
        index,
        metadata
    )

    if not results:
        return {
            "answer": (
                "The information is not available "
                "in the uploaded documents."
            ),
            "sources": [],
            "retrieved_chunks": []
        }

    context = build_context(
        results
    )

    prompt = f"""
You are a document question-answering assistant.

Answer the user's question using ONLY the provided context.

Rules:
1. Do not use outside knowledge.
2. Do not invent facts.
3. If the answer cannot be found in the context, say:
   "The information is not available in the uploaded documents."
4. Give a clear and concise answer.
5. Use the context carefully because multiple documents may be present.

CONTEXT:
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