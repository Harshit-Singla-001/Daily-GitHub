import os
import uuid

from flask import (
    Flask,
    jsonify,
    render_template,
    request
)

from assistant import run_assistant

from memory import (
    initialize_memory,
    get_memory,
    clear_memory
)

from observability import (
    initialize_observability,
    get_metrics,
    get_recent_requests
)

from document_processor import (
    SUPPORTED_EXTENSIONS,
    process_document
)

from vector_store import (
    add_chunks,
    get_documents
)

from config import (
    UPLOAD_FOLDER,
    MAX_INPUT_LENGTH
)


app = Flask(__name__)

app.config["MAX_CONTENT_LENGTH"] = (
    20 * 1024 * 1024
)

initialize_memory()
initialize_observability()


@app.route("/")
def index():
    return render_template(
        "index.html"
    )


@app.route(
    "/ask",
    methods=["POST"]
)
def ask():
    data = request.get_json(
        silent=True
    )

    if not isinstance(
        data,
        dict
    ):
        return jsonify({
            "success": False,
            "error": "Request body must be valid JSON."
        }), 400

    user_input = data.get(
        "input"
    )

    session_id = data.get(
        "session_id"
    )

    if not session_id:
        session_id = uuid.uuid4().hex

    if (
        isinstance(
            user_input,
            str
        )
        and len(user_input) > MAX_INPUT_LENGTH
    ):
        return jsonify({
            "success": False,
            "error": f"Input must be {MAX_INPUT_LENGTH} characters or less."
        }), 400

    result = run_assistant(
        user_input,
        session_id
    )

    result["session_id"] = session_id

    if result.get("success"):
        return jsonify(
            result
        ), 200

    error_type = result.get(
        "error_type",
        "APPLICATION_ERROR"
    )

    status_codes = {
        "INVALID_INPUT": 400,
        "PROMPT_INJECTION": 400,
        "RATE_LIMITED": 429,
        "SERVICE_UNAVAILABLE": 503,
        "TIMEOUT": 504
    }

    status_code = status_codes.get(
        error_type,
        500
    )

    return jsonify(
        result
    ), status_code


@app.route(
    "/memory",
    methods=["GET"]
)
def memory():
    session_id = request.args.get(
        "session_id"
    )

    if not session_id:
        return jsonify({
            "success": False,
            "error": "session_id is required."
        }), 400

    return jsonify({
        "success": True,
        "memory": get_memory(
            session_id,
            limit=50
        )
    })


@app.route(
    "/memory/clear",
    methods=["POST"]
)
def memory_clear():
    data = request.get_json(
        silent=True
    ) or {}

    session_id = data.get(
        "session_id"
    )

    if not session_id:
        return jsonify({
            "success": False,
            "error": "session_id is required."
        }), 400

    clear_memory(
        session_id
    )

    return jsonify({
        "success": True,
        "message": "Memory cleared."
    })


@app.route(
    "/documents",
    methods=["GET"]
)
def documents():
    return jsonify({
        "success": True,
        "documents": get_documents()
    })


@app.route(
    "/documents/upload",
    methods=["POST"]
)
def upload_document():
    uploaded_file = request.files.get(
        "document"
    )

    if uploaded_file is None:
        return jsonify({
            "success": False,
            "error": "No document was uploaded."
        }), 400

    filename = uploaded_file.filename or ""

    if not filename:
        return jsonify({
            "success": False,
            "error": "Filename is missing."
        }), 400

    extension = os.path.splitext(
        filename
    )[1].lower()

    if extension not in SUPPORTED_EXTENSIONS:
        return jsonify({
            "success": False,
            "error": (
                "Supported formats: "
                "TXT, PDF, DOCX and CSV."
            )
        }), 400

    safe_filename = (
        uuid.uuid4().hex
        + extension
    )

    file_path = os.path.join(
        UPLOAD_FOLDER,
        safe_filename
    )

    uploaded_file.save(
        file_path
    )

    try:
        chunks = process_document(
            file_path
        )

        added = add_chunks(
            chunks
        )

        return jsonify({
            "success": True,
            "message": "Document processed successfully.",
            "filename": filename,
            "chunks": len(chunks),
            "embeddings_added": added
        })

    except Exception as error:
        return jsonify({
            "success": False,
            "error": str(error)
        }), 500

    finally:
        if os.path.exists(
            file_path
        ):
            os.remove(
                file_path
            )


@app.route(
    "/metrics",
    methods=["GET"]
)
def metrics():
    return jsonify({
        "success": True,
        "metrics": get_metrics()
    })


@app.route(
    "/requests",
    methods=["GET"]
)
def requests_list():
    try:
        limit = int(
            request.args.get(
                "limit",
                20
            )
        )

    except (
        ValueError,
        TypeError
    ):
        limit = 20

    limit = max(
        1,
        min(limit, 100)
    )

    return jsonify({
        "success": True,
        "requests": get_recent_requests(
            limit
        )
    })


@app.errorhandler(413)
def request_too_large(error):
    return jsonify({
        "success": False,
        "error": "Uploaded request is too large."
    }), 413


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": "Resource not found."
    }), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        "success": False,
        "error": "An unexpected server error occurred."
    }), 500


if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )