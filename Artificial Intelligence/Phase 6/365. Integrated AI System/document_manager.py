import os
import uuid

from document_processor import (
    SUPPORTED_EXTENSIONS,
    process_document
)

from vector_store import (
    add_chunks,
    delete_document,
    get_documents,
    load_vectors
)

from config import UPLOAD_FOLDER


MAX_DOCUMENT_SIZE = 20 * 1024 * 1024


def get_document_extension(filename):
    return os.path.splitext(
        filename
    )[1].lower()


def validate_document(filename, file_size=None):
    if not filename:
        return False, "Filename is missing."

    extension = get_document_extension(
        filename
    )

    if extension not in SUPPORTED_EXTENSIONS:
        supported = ", ".join(
            sorted(
                extension.replace(".", "").upper()
                for extension in SUPPORTED_EXTENSIONS
            )
        )

        return (
            False,
            f"Unsupported file type. Supported formats: {supported}."
        )

    if file_size is not None:
        if file_size > MAX_DOCUMENT_SIZE:
            return (
                False,
                "Document size must be 20 MB or less."
            )

    return True, ""


def save_uploaded_file(uploaded_file):
    filename = uploaded_file.filename or ""

    valid, error = validate_document(
        filename
    )

    if not valid:
        return {
            "success": False,
            "error": error
        }

    extension = get_document_extension(
        filename
    )

    safe_filename = (
        uuid.uuid4().hex
        + extension
    )

    os.makedirs(
        UPLOAD_FOLDER,
        exist_ok=True
    )

    file_path = os.path.join(
        UPLOAD_FOLDER,
        safe_filename
    )

    uploaded_file.save(
        file_path
    )

    return {
        "success": True,
        "original_filename": filename,
        "path": file_path
    }


def process_uploaded_document(
    uploaded_file
):
    saved = save_uploaded_file(
        uploaded_file
    )

    if not saved["success"]:
        return saved

    file_path = saved["path"]
    original_filename = saved["original_filename"]

    try:
        chunks = process_document(
            file_path
        )

        if not chunks:
            return {
                "success": False,
                "error": (
                    "The document was processed "
                    "but no readable text was found."
                )
            }

        added = add_chunks(
            chunks
        )

        return {
            "success": True,
            "filename": original_filename,
            "chunks": len(chunks),
            "embeddings_added": added,
            "message": (
                "Document uploaded and added "
                "to the knowledge base."
            )
        }

    except Exception as error:
        return {
            "success": False,
            "error": str(error)
        }

    finally:
        if os.path.exists(
            file_path
        ):
            try:
                os.remove(
                    file_path
                )
            except OSError:
                pass


def get_document_details():
    vectors = load_vectors()

    documents = {}

    for item in vectors:
        document_name = item.get(
            "document",
            "Unknown"
        )

        if document_name not in documents:
            documents[document_name] = {
                "name": document_name,
                "chunks": 0,
                "pages": set()
            }

        documents[document_name]["chunks"] += 1

        page = item.get(
            "page"
        )

        if page is not None:
            documents[document_name]["pages"].add(
                page
            )

    result = []

    for document in documents.values():
        pages = sorted(
            document["pages"]
        )

        result.append({
            "name": document["name"],
            "chunks": document["chunks"],
            "pages": pages,
            "page_count": len(pages)
        })

    result.sort(
        key=lambda item: item["name"].lower()
    )

    return result


def remove_document(
    document_name
):
    if not document_name:
        return {
            "success": False,
            "error": "Document name is required."
        }

    removed_chunks = delete_document(
        document_name
    )

    if removed_chunks == 0:
        return {
            "success": False,
            "error": "Document was not found."
        }

    return {
        "success": True,
        "message": "Document removed from the knowledge base.",
        "document": document_name,
        "chunks_removed": removed_chunks
    }


def get_document_list():
    return get_document_details()