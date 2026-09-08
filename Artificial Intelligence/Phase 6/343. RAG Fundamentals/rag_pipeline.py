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
Use the provided context to answer the question.

Rules:
- Answer only from the provided context.
- If the answer is not present, say you don't know.
- Do not invent information.
- Keep the answer clear and concise.

Context:
{context}

Question:
{question}

Answer:
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
            max_output_tokens=500
        )
    )

    return response.text.strip()