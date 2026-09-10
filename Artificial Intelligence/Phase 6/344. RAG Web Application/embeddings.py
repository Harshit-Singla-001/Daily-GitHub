import numpy as np

from google import genai

from config import (
    GEMINI_API_KEY,
    EMBEDDING_MODEL
)


client = genai.Client(
    api_key=GEMINI_API_KEY
)


def generate_embedding(text):
    response = client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=text
    )

    return np.array(
        response.embeddings[0].values,
        dtype=np.float32
    )


def generate_embeddings(texts):
    if not texts:
        return np.array(
            [],
            dtype=np.float32
        )

    embeddings = []

    for index, text in enumerate(
        texts,
        start=1
    ):
        print(
            f"Embedding {index}/{len(texts)}..."
        )

        embeddings.append(
            generate_embedding(text)
        )

    return np.array(
        embeddings,
        dtype=np.float32
    )