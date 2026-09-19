from google import genai
from config import API_KEY, MODEL
from retriever import retrieve

client = genai.Client(api_key=API_KEY)

def build_context(results):
    context_parts = []

    for index, result in enumerate(results, start=1):
        context_parts.append(
            f"[Source {index}]\n"
            f"Document: {result.get('document', '')}\n"
            f"Page: {result.get('page', '')}\n"
            f"Section: {result.get('section', '')}\n"
            f"Content:\n{result.get('text', '')}"
        )

    return "\n\n".join(context_parts)

def generate_answer(question):
    results = retrieve(question)

    if not results:
        return {
            "answer": "I could not find relevant information in the uploaded documents.",
            "results": [],
            "context": ""
        }

    context = build_context(results)

    prompt = f"""
You are a document-based RAG assistant.

Answer the user's question ONLY using the provided context.

Rules:
1. Do not invent facts.
2. If the answer is not present in the context, say that the information is not available.
3. Keep the answer directly related to the question.
4. Add [Source N] after claims whenever possible.

Context:
{context}

Question:
{question}
"""

    response = client.models.generate_content(
        model=MODEL,
        contents=prompt
    )

    return {
        "answer": response.text.strip(),
        "results": results,
        "context": context
    }