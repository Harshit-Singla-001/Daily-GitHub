from flask import (
    Flask,
    render_template,
    request,
    jsonify
)

from ai_service import generate_response
from observability import (
    initialize_database,
    get_recent_requests,
    get_request_by_id
)
from metrics import get_metrics

app = Flask(__name__)

initialize_database()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "success": False,
            "error": "Request body must be valid JSON."
        }), 400

    user_input = data.get("input")

    result = generate_response(
        user_input
    )

    if result.get("success"):
        return jsonify(result), 200

    error_type = result.get(
        "error_type",
        "APPLICATION_ERROR"
    )

    status_codes = {
        "RATE_LIMITED": 429,
        "SERVICE_UNAVAILABLE": 503,
        "DEADLINE_EXCEEDED": 504,
        "TIMEOUT": 504,
        "AUTHENTICATION_ERROR": 401,
        "INVALID_REQUEST": 400,
        "OUTPUT_VALIDATION_ERROR": 502,
        "NETWORK_ERROR": 503
    }

    status_code = status_codes.get(
        error_type,
        502
    )

    return jsonify(result), status_code

@app.route("/metrics", methods=["GET"])
def metrics():
    return jsonify({
        "success": True,
        "metrics": get_metrics()
    })

@app.route("/requests", methods=["GET"])
def requests_list():
    try:
        limit = int(
            request.args.get(
                "limit",
                20
            )
        )
    except (ValueError, TypeError):
        limit = 20

    limit = max(
        1,
        min(limit, 100)
    )

    requests_data = get_recent_requests(
        limit
    )

    return jsonify({
        "success": True,
        "requests": requests_data
    })

@app.route(
    "/requests/<request_id>",
    methods=["GET"]
)
def request_details(request_id):
    request_data = get_request_by_id(
        request_id
    )

    if request_data is None:
        return jsonify({
            "success": False,
            "error": "Request not found."
        }), 404

    return jsonify({
        "success": True,
        "request": request_data
    })

@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "success": False,
        "error": "Bad request."
    }), 400

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
def server_error(error):
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