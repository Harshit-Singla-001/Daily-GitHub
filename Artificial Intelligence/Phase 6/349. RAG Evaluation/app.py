import os
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename

from config import UPLOAD_FOLDER
from document_processor import extract_text
from chunker import create_chunks
from embeddings import create_embedding
from vector_store import add_records, load_store, clear_store
from rag import generate_answer
from evaluator import evaluate_all

app = Flask(__name__)

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {
    ".txt",
    ".pdf",
    ".docx",
    ".csv"
}

def allowed_file(filename):
    extension = os.path.splitext(filename)[1].lower()
    return extension in ALLOWED_EXTENSIONS

@app.route("/")
def index():
    records = load_store()

    documents = sorted(
        set(
            record.get("document", "")
            for record in records
        )
    )

    return render_template(
        "index.html",
        documents=documents,
        chunk_count=len(records)
    )

@app.route("/upload", methods=["POST"])
def upload():
    files = request.files.getlist("files")

    if not files:
        return jsonify({
            "success": False,
            "message": "No files selected."
        }), 400

    total_chunks = 0
    uploaded_documents = []

    for file in files:
        if not file.filename:
            continue

        if not allowed_file(file.filename):
            continue

        filename = secure_filename(file.filename)
        path = os.path.join(UPLOAD_FOLDER, filename)

        file.save(path)

        text = extract_text(path)
        chunks = create_chunks(text, filename)

        records = []

        for chunk in chunks:
            embedding = create_embedding(chunk["text"])
            chunk["embedding"] = embedding
            records.append(chunk)

        add_records(records)

        total_chunks += len(records)
        uploaded_documents.append(filename)

    return jsonify({
        "success": True,
        "message": "Documents indexed successfully.",
        "documents": uploaded_documents,
        "chunks": total_chunks
    })

@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json(silent=True) or {}
    question = data.get("question", "").strip()

    if not question:
        return jsonify({
            "success": False,
            "message": "Question is required."
        }), 400

    result = generate_answer(question)

    sources = []

    for index, item in enumerate(result["results"], start=1):
        sources.append({
            "source_number": index,
            "document": item.get("document", ""),
            "page": item.get("page"),
            "section": item.get("section"),
            "chunk_id": item.get("chunk_id"),
            "score": item.get("score")
        })

    return jsonify({
        "success": True,
        "answer": result["answer"],
        "sources": sources
    })

@app.route("/evaluate", methods=["POST"])
def evaluate():
    try:
        evaluation = evaluate_all()

        return jsonify({
            "success": True,
            **evaluation
        })

    except Exception as error:
        return jsonify({
            "success": False,
            "message": str(error)
        }), 500

@app.route("/clear", methods=["POST"])
def clear():
    clear_store()

    return jsonify({
        "success": True,
        "message": "Vector store cleared."
    })

if __name__ == "__main__":
    app.run(debug=True)