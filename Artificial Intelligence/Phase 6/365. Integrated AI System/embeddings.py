from google import genai

from config import API_KEY, EMBEDDING_MODEL


client = genai.Client(
    api_key=API_KEY
)


def create_embedding(
    text,
    task_type="RETRIEVAL_DOCUMENT"
):
    if not text or not text.strip():
        raise ValueError(
            "Text cannot be empty."
        )

    response = client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=text,
        config={
            "task_type": task_type
        }
    )

    embedding = getattr(
        response,
        "embeddings",
        None
    )

    if not embedding:
        raise RuntimeError(
            "Embedding API returned no embedding."
        )

    first_embedding = embedding[0]

    values = getattr(
        first_embedding,
        "values",
        None
    )

    if values is None:
        raise RuntimeError(
            "Embedding response contains no values."
        )

    return list(values)


def create_document_embedding(text):
    return create_embedding(
        text,
        "RETRIEVAL_DOCUMENT"
    )


def create_query_embedding(text):
    return create_embedding(
        text,
        "RETRIEVAL_QUERY"
    )