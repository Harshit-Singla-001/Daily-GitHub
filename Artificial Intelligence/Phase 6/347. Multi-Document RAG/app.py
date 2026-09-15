import os
import uuid

from flask import (
    Flask,
    render_template,
    request
)
from werkzeug.utils import secure_filename

from config import (
    UPLOAD_FOLDER,
    ALLOWED_EXTENSIONS,
    MAX_DOCUMENTS,
    MAX_FILE_SIZE,
    GEMINI_API_KEY,
    GEMINI_MODEL
)

from document_processor import (
    process_document
)

from chunker import create_chunks

from embeddings import (
    generate_embeddings,
    generate_embedding
)

from rag import build_context

from google import genai


app = Flask(__name__)

app.config["UPLOAD_FOLDER"] = (
    UPLOAD_FOLDER
)

app.config["MAX_CONTENT_LENGTH"] = (
    MAX_DOCUMENTS * MAX_FILE_SIZE
)

os.makedirs(
    UPLOAD_FOLDER,
    exist_ok=True
)


client = genai.Client(
    api_key=GEMINI_API_KEY
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


def build_document_chunks(
    files
):
    all_chunks = []

    saved_files = []

    for file in files:

        if not file.filename:
            continue

        if not allowed_file(
            file.filename
        ):
            continue

        original_name = secure_filename(
            file.filename
        )

        unique_name = (
            f"{uuid.uuid4().hex}_"
            f"{original_name}"
        )

        path = os.path.join(
            UPLOAD_FOLDER,
            unique_name
        )

        file.save(path)

        saved_files.append(
            original_name
        )

        extracted = process_document(
            path
        )

        if isinstance(
            extracted,
            list
        ):
            for page in extracted:

                chunks = create_chunks(
                    page["text"],
                    original_name,
                    page=page["page"]
                )

                all_chunks.extend(
                    chunks
                )

        else:
            chunks = create_chunks(
                extracted,
                original_name
            )

            all_chunks.extend(
                chunks
            )

    return (
        all_chunks,
        saved_files
    )


def generate_answer(
    question,
    context
):
    prompt = f"""
You are a document question-answering assistant.

Answer the user's question using ONLY the
provided document context.

The context may contain information from
multiple documents.

If the answer cannot be found in the
provided context, say:

"The information is not available
in the uploaded documents."

Do not invent facts.

Keep the answer clear and concise.

DOCUMENT CONTEXT:
{context}

USER QUESTION:
{question}
"""

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt
    )

    return response.text


@app.route("/")
def home():
    return render_template(
        "index.html"
    )


@app.route(
    "/ask",
    methods=["POST"]
)
def ask():

    files = request.files.getlist(
        "documents"
    )

    question = request.form.get(
        "question",
        ""
    ).strip()

    if not files:
        return render_template(
            "index.html",
            error="Please upload at least one document."
        )

    if len(files) > MAX_DOCUMENTS:
        return render_template(
            "index.html",
            error=(
                f"Maximum "
                f"{MAX_DOCUMENTS} documents "
                f"are allowed."
            )
        )

    if not question:
        return render_template(
            "index.html",
            error="Please enter a question."
        )

    try:

        chunks, documents = (
            build_document_chunks(files)
        )

        if not chunks:
            return render_template(
                "index.html",
                error="No readable text was found."
            )

        embeddings = generate_embeddings(
            chunks
        )

        query_embedding = (
            generate_embedding(question)
        )

        context, sources = (
            build_context(
                query_embedding,
                chunks,
                embeddings
            )
        )

        if not context:
            return render_template(
                "index.html",
                documents=documents,
                question=question,
                error=(
                    "No sufficiently relevant "
                    "information was found "
                    "in the uploaded documents."
                )
            )

        answer = generate_answer(
            question,
            context
        )

        return render_template(
            "index.html",
            answer=answer,
            sources=sources,
            documents=documents,
            question=question
        )

    except Exception as error:

        print(
            f"Application error: {error}"
        )

        return render_template(
            "index.html",
            error=(
                "An error occurred while "
                "processing the documents."
            )
        )


if __name__ == "__main__":
    app.run(
        debug=True
    )