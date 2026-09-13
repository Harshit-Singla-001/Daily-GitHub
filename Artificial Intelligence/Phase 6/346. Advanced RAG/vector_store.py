import json
import os
import numpy as np
import faiss

from config import (
    FAISS_INDEX_PATH,
    METADATA_PATH
)

def create_index(embeddings):
    if not embeddings:
        raise ValueError(
            "No embeddings available."
        )

    vectors = np.array(
        embeddings,
        dtype=np.float32
    )

    faiss.normalize_L2(vectors)

    dimension = vectors.shape[1]

    index = faiss.IndexFlatIP(
        dimension
    )

    index.add(vectors)

    return index

def save_vector_store(
    index,
    metadata
):
    os.makedirs(
        os.path.dirname(FAISS_INDEX_PATH),
        exist_ok=True
    )

    faiss.write_index(
        index,
        FAISS_INDEX_PATH
    )

    with open(
        METADATA_PATH,
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            metadata,
            file,
            ensure_ascii=False,
            indent=2
        )

def load_vector_store():
    if not os.path.exists(
        FAISS_INDEX_PATH
    ):
        return None, []

    if not os.path.exists(
        METADATA_PATH
    ):
        return None, []

    index = faiss.read_index(
        FAISS_INDEX_PATH
    )

    with open(
        METADATA_PATH,
        "r",
        encoding="utf-8"
    ) as file:
        metadata = json.load(file)

    return index, metadata

def delete_vector_store():
    if os.path.exists(
        FAISS_INDEX_PATH
    ):
        os.remove(
            FAISS_INDEX_PATH
        )

    if os.path.exists(
        METADATA_PATH
    ):
        os.remove(
            METADATA_PATH
        )