from google import genai
from config import GEMINI_API_KEY, EMBEDDING_MODEL

client = genai.Client(
    api_key=GEMINI_API_KEY
)

def generate_embedding(text):
    if not text or not text.strip():
        return None

    response = client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=text
    )

    return response.embeddings[0].values

def generate_embeddings(texts):
    if not texts:
        return []

    response = client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=texts
    )

    return [
        embedding.values
        for embedding in response.embeddings
    ]