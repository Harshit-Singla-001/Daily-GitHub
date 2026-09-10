import os
import uuid

from flask import (
    Flask,
    jsonify,
    render_template,
    request
)
from werkzeug.utils import secure_filename

from config import (
    ALLOWED_EXTENSIONS,
    MAX_FILE_SIZE,
    TOP_K,
    UPLOAD_FOLDER
)
from document_loader import load_document
from chunker import create_chunks
from embeddings import generate_embeddings
from vector_store import (
    create_store,
    search_store
)
from rag_pipeline import generate_answer


app = Flask(__name__)

app.config["MAX_CONTENT_LENGTH"] = MAX_FILE_SIZE


current_document = {
    "name": None,
    "chunks": [],
    "index": None
}


def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(
            ".",
            1
        )[1].lower()
        in ALLOWED_EXTENSIONS
    )


@app.route("/")
def home():
    return render_template(
        "index.html"
    )


@app.route(
    "/upload",
    methods=["POST"]
)
def upload_document():
    global current_document

    if "document" not in request.files:
        return jsonify({
            "success": False,
            "error": "No document selected."
        }), 400

    file = request.files["document"]

    if not file.filename:
        return jsonify({
            "success": False,
            "error": "Please select a document."
        }), 400

    if not allowed_file(file.filename):
        return jsonify({
            "success": False,
            "error": (
                "Only TXT, PDF, DOCX and CSV "
                "files are supported."
            )
        }), 400

    extension = os.path.splitext(
        file.filename
    )[1].lower()

    filename = (
        f"{uuid.uuid4().hex}"
        f"{extension}"
    )

    filename = secure_filename(
        filename
    )

    file_path = UPLOAD_FOLDER / filename

    try:
        file.save(file_path)

        text = load_document(
            file_path
        )

        if not text.strip():
            return jsonify({
                "success": False,
                "error": (
                    "The document contains "
                    "no readable text."
                )
            }), 400

        chunks = create_chunks(
            text
        )

        if not chunks:
            return jsonify({
                "success": False,
                "error": (
                    "Unable to create document chunks."
                )
            }), 400

        embeddings = generate_embeddings(
            chunks
        )

        index = create_store(
            embeddings
        )

        current_document = {
            "name": file.filename,
            "chunks": chunks,
            "index": index
        }

        return jsonify({
            "success": True,
            "filename": file.filename,
            "chunks": len(chunks),
            "message": (
                "Document processed successfully."
            )
        })

    except Exception as error:
        print(
            f"Upload error: {error}"
        )

        if file_path.exists():
            file_path.unlink()

        return jsonify({
            "success": False,
            "error": (
                "Failed to process the document."
            )
        }), 500


@app.route(
    "/ask",
    methods=["POST"]
)
def ask_question():
    if current_document["index"] is None:
        return jsonify({
            "success": False,
            "error": (
                "Please upload a document first."
            )
        }), 400

    data = request.get_json(
        silent=True
    )

    if not data:
        return jsonify({
            "success": False,
            "error": "Invalid request."
        }), 400

    question = data.get(
        "question",
        ""
    ).strip()

    if not question:
        return jsonify({
            "success": False,
            "error": (
                "Please enter a question."
            )
        }), 400

    try:
        question_embedding = (
            generate_embeddings(
                [question]
            )[0]
        )

        relevant_chunks = search_store(
            current_document["index"],
            question_embedding,
            current_document["chunks"],
            TOP_K
        )

        if not relevant_chunks:
            return jsonify({
                "success": False,
                "error": (
                    "No relevant information found."
                )
            }), 404

        context = "\n\n".join(
            relevant_chunks
        )

        answer = generate_answer(
            question,
            context
        )

        return jsonify({
            "success": True,
            "answer": answer
        })

    except Exception as error:
        print(
            f"Question error: {error}"
        )

        return jsonify({
            "success": False,
            "error": (
                "Failed to generate an answer."
            )
        }), 500


@app.route(
    "/status"
)
def status():
    return jsonify({
        "document_loaded": (
            current_document["index"]
            is not None
        ),
        "document_name": (
            current_document["name"]
        ),
        "chunks": len(
            current_document["chunks"]
        )
    })


@app.errorhandler(413)
def file_too_large(error):
    return jsonify({
        "success": False,
        "error": (
            "File size must be less than 10 MB."
        )
    }), 413


if __name__ == "__main__":
    print("=" * 60)
    print("RAG WEB APPLICATION")
    print("=" * 60)
    print("Open: http://127.0.0.1:5000")
    print()

    app.run(
        debug=True
    )