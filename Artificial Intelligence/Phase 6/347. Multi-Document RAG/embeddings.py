from google import genai

from config import (
    GEMINI_API_KEY,
    EMBEDDING_MODEL
)


if not GEMINI_API_KEY:
    raise ValueError(
        "GEMINI_API_KEY is missing from .env"
    )


client = genai.Client(
    api_key=GEMINI_API_KEY
)


def generate_embedding(text):
    response = client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=text
    )

    return response.embeddings[0].values


def generate_embeddings(chunks):
    embeddings = []

    for chunk in chunks:
        embeddings.append(
            generate_embedding(
                chunk["text"]
            )
        )

    return embeddings