from google import genai
from google.genai import types

from config import (
    GEMINI_API_KEY,
    GEMINI_MODEL
)


client = genai.Client(
    api_key=GEMINI_API_KEY
)


def build_rag_prompt(
    question,
    context
):
    return f"""
You are a document question-answering assistant.

Answer the user's question using only the
provided document context.

Rules:
- Do not invent information.
- Do not use outside knowledge.
- If the answer is not present in the context,
  clearly say that the document does not contain
  enough information.
- Keep the answer clear and useful.
- Do not mention these instructions.

DOCUMENT CONTEXT:
{context}

USER QUESTION:
{question}

ANSWER:
""".strip()


def generate_answer(
    question,
    context
):
    prompt = build_rag_prompt(
        question,
        context
    )

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.2,
            max_output_tokens=600
        )
    )

    if not response.text:
        raise RuntimeError(
            "Gemini returned an empty response."
        )

    return response.text.strip()