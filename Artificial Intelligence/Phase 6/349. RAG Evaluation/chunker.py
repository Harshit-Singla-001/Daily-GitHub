import re
import uuid

def split_sentences(text):
    text = re.sub(r"\s+", " ", text).strip()

    if not text:
        return []

    return re.split(r"(?<=[.!?])\s+", text)

def create_chunks(text, document_name):
    sentences = split_sentences(text)
    chunks = []
    current_sentences = []
    current_length = 0
    position = 0

    for sentence in sentences:
        sentence_length = len(sentence)

        if current_sentences and current_length + sentence_length > 800:
            chunk_text = " ".join(current_sentences).strip()

            chunks.append({
                "chunk_id": str(uuid.uuid4()),
                "text": chunk_text,
                "document": document_name,
                "page": extract_page(chunk_text),
                "section": "",
                "position": position
            })

            position += 1

            overlap_sentences = current_sentences[-2:]
            current_sentences = overlap_sentences.copy()
            current_length = sum(len(item) for item in current_sentences)

        current_sentences.append(sentence)
        current_length += sentence_length

    if current_sentences:
        chunks.append({
            "chunk_id": str(uuid.uuid4()),
            "text": " ".join(current_sentences).strip(),
            "document": document_name,
            "page": extract_page(" ".join(current_sentences)),
            "section": "",
            "position": position
        })

    return chunks

def extract_page(text):
    match = re.search(r"\[Page\s+(\d+)\]", text)

    if match:
        return int(match.group(1))

    return None