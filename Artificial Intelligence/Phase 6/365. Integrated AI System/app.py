import os

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
    get_recent_requests,
    get_request_by_id
)

from document_manager import (
    process_uploaded_document,
    get_document_list,
    remove_document
)

from config import (
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
            "error": (
                "Request body must "
                "be valid JSON."
            )
        }), 400

    user_input = data.get(
        "input"
    )

    session_id = data.get(
        "session_id"
    )

    if not session_id:
        return jsonify({
            "success": False,
            "error": "session_id is required."
        }), 400

    if (
        isinstance(
            user_input,
            str
        )
        and len(user_input)
        > MAX_INPUT_LENGTH
    ):
        return jsonify({
            "success": False,
            "error": (
                f"Input must be "
                f"{MAX_INPUT_LENGTH} "
                "characters or less."
            )
        }), 400

    result = run_assistant(
        user_input,
        session_id
    )

    result["session_id"] = session_id

    if result.get(
        "success"
    ):
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
        "TIMEOUT": 504,
        "NETWORK_ERROR": 503
    }

    status_code = status_codes.get(
        error_type,
        500
    )

    return jsonify(
        result
    ), status_code


@app.route(
    "/documents",
    methods=["GET"]
)
def documents():
    try:
        return jsonify({
            "success": True,
            "documents": get_document_list()
        })

    except Exception as error:
        return jsonify({
            "success": False,
            "error": str(error)
        }), 500


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

    result = process_uploaded_document(
        uploaded_file
    )

    if not result.get(
        "success"
    ):
        return jsonify(
            result
        ), 400

    return jsonify(
        result
    ), 200


@app.route(
    "/documents/delete",
    methods=["POST"]
)
def delete_document():
    data = request.get_json(
        silent=True
    ) or {}

    document_name = data.get(
        "document"
    )

    result = remove_document(
        document_name
    )

    if not result.get(
        "success"
    ):
        return jsonify(
            result
        ), 404

    return jsonify(
        result
    ), 200


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
            "error": (
                "session_id is required."
            )
        }), 400

    return jsonify({
        "success": True,
        "memory": get_memory(
            session_id,
            limit=100
        )
    })


@app.route(
    "/history",
    methods=["GET"]
)
def history():
    session_id = request.args.get(
        "session_id"
    )

    if not session_id:
        return jsonify({
            "success": False,
            "error": (
                "session_id is required."
            )
        }), 400

    messages = get_memory(
        session_id,
        limit=100
    )

    return jsonify({
        "success": True,
        "history": messages
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
            "error": (
                "session_id is required."
            )
        }), 400

    clear_memory(
        session_id
    )

    return jsonify({
        "success": True,
        "message": "Conversation history cleared."
    })


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
        min(
            limit,
            100
        )
    )

    return jsonify({
        "success": True,
        "requests": get_recent_requests(
            limit
        )
    })


@app.route(
    "/requests/<request_id>",
    methods=["GET"]
)
def request_details(
    request_id
):
    result = get_request_by_id(
        request_id
    )

    if result is None:
        return jsonify({
            "success": False,
            "error": "Request not found."
        }), 404

    return jsonify({
        "success": True,
        "request": result
    })


@app.errorhandler(413)
def request_too_large(error):
    return jsonify({
        "success": False,
        "error": (
            "Uploaded file or request "
            "is too large. Maximum size is 20 MB."
        )
    }), 413


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": "Resource not found."
    }), 404


@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        "success": False,
        "error": "HTTP method is not allowed."
    }), 405


@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        "success": False,
        "error": (
            "An unexpected server error occurred."
        )
    }), 500


if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )