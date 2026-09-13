import os
import uuid

from flask import (
    Flask,
    render_template,
    request,
    jsonify
)

from werkzeug.utils import secure_filename

from config import (
    UPLOAD_FOLDER,
    ALLOWED_EXTENSIONS,
    MAX_FILE_SIZE_MB
)

from document_processor import (
    extract_document
)

from chunker import create_chunks

from embeddings import (
    generate_embeddings
)

from vector_store import (
    create_index,
    save_vector_store,
    load_vector_store,
    delete_vector_store
)

from rag import generate_answer

app = Flask(__name__)

app.config["UPLOAD_FOLDER"] = (
    UPLOAD_FOLDER
)

app.config["MAX_CONTENT_LENGTH"] = (
    MAX_FILE_SIZE_MB
    * 1024
    * 1024
)

def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(
            ".",
            1
        )[1].lower()
        in ALLOWED_EXTENSIONS
    )

def process_file(
    file_path,
    original_name
):
    pages = extract_document(
        file_path
    )

    all_chunks = []

    for page_data in pages:
        chunks = create_chunks(
            page_data["text"],
            document_name=original_name,
            page=page_data.get("page"),
            section=page_data.get("section")
        )

        all_chunks.extend(
            chunks
        )

    return all_chunks

def rebuild_vector_store():
    all_chunks = []

    for filename in os.listdir(
        UPLOAD_FOLDER
    ):
        file_path = os.path.join(
            UPLOAD_FOLDER,
            filename
        )

        if not os.path.isfile(
            file_path
        ):
            continue

        if not allowed_file(
            filename
        ):
            continue

        try:
            chunks = process_file(
                file_path,
                filename
            )

            all_chunks.extend(
                chunks
            )

        except Exception as error:
            print(
                f"Skipping {filename}: {error}"
            )

    if not all_chunks:
        delete_vector_store()

        return 0

    texts = [
        chunk["text"]
        for chunk in all_chunks
    ]

    embeddings = generate_embeddings(
        texts
    )

    index = create_index(
        embeddings
    )

    save_vector_store(
        index,
        all_chunks
    )

    return len(all_chunks)

@app.route("/")
def home():
    index, metadata = load_vector_store()

    documents = sorted({
        item.get(
            "document",
            "Unknown"
        )
        for item in metadata
    })

    return render_template(
        "index.html",
        documents=documents,
        chunk_count=len(metadata)
    )

@app.route(
    "/upload",
    methods=["POST"]
)
def upload_files():
    files = request.files.getlist(
        "files"
    )

    if not files:
        return jsonify({
            "success": False,
            "message": "No files selected."
        }), 400

    uploaded = []

    for file in files:
        if not file.filename:
            continue

        if not allowed_file(
            file.filename
        ):
            continue

        safe_name = secure_filename(
            file.filename
        )

        unique_name = (
            f"{uuid.uuid4().hex[:8]}_"
            f"{safe_name}"
        )

        file_path = os.path.join(
            UPLOAD_FOLDER,
            unique_name
        )

        file.save(
            file_path
        )

        uploaded.append(
            unique_name
        )

    if not uploaded:
        return jsonify({
            "success": False,
            "message": (
                "No supported files were uploaded."
            )
        }), 400

    try:
        chunk_count = (
            rebuild_vector_store()
        )

        return jsonify({
            "success": True,
            "message": (
                f"{len(uploaded)} file(s) uploaded "
                f"and indexed successfully."
            ),
            "files": uploaded,
            "chunks": chunk_count
        })

    except Exception as error:
        return jsonify({
            "success": False,
            "message": str(error)
        }), 500

@app.route(
    "/ask",
    methods=["POST"]
)
def ask_question():
    data = request.get_json(
        silent=True
    ) or {}

    question = (
        data.get("question", "")
        .strip()
    )

    if not question:
        return jsonify({
            "success": False,
            "message": "Question is required."
        }), 400

    index, metadata = (
        load_vector_store()
    )

    if index is None or not metadata:
        return jsonify({
            "success": False,
            "message": (
                "Please upload and index "
                "a document first."
            )
        }), 400

    try:
        result = generate_answer(
            question,
            index,
            metadata
        )

        return jsonify({
            "success": True,
            **result
        })

    except Exception as error:
        return jsonify({
            "success": False,
            "message": str(error)
        }), 500

@app.route(
    "/clear",
    methods=["POST"]
)
def clear_documents():
    for filename in os.listdir(
        UPLOAD_FOLDER
    ):
        file_path = os.path.join(
            UPLOAD_FOLDER,
            filename
        )

        if os.path.isfile(
            file_path
        ):
            os.remove(
                file_path
            )

    delete_vector_store()

    return jsonify({
        "success": True,
        "message": "All documents cleared."
    })

if __name__ == "__main__":
    app.run(
        debug=True
    )