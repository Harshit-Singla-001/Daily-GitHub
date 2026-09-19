from google import genai
from config import API_KEY, EMBEDDING_MODEL

client = genai.Client(api_key=API_KEY)

def create_embedding(text):
    result = client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=text
    )

    return result.embeddings[0].values