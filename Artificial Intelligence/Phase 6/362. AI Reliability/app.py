import uuid

from flask import Flask, render_template, request, jsonify

from input_validator import validate_input
from prompt_guard import detect_prompt_injection, sanitize_for_prompt
from output_validator import validate_output
from ai_service import generate_response
from logger_config import logger
from failure_handler import handle_failure


app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/ask", methods=["POST"])
def ask():
    request_id = str(uuid.uuid4())[:8]

    logger.info(
        "Request received | request_id=%s",
        request_id
    )

    try:
        data = request.get_json(silent=True)

        if not data:
            logger.warning(
                "Invalid JSON | request_id=%s",
                request_id
            )

            return jsonify({
                "success": False,
                "error": "Invalid request data."
            }), 400

        user_input = data.get("message")

        # -------------------------------
        # 1. INPUT VALIDATION
        # -------------------------------
        input_result = validate_input(user_input)

        if not input_result["valid"]:
            logger.warning(
                "Input validation failed | request_id=%s | reason=%s",
                request_id,
                input_result["error"]
            )

            return jsonify({
                "success": False,
                "stage": "input_validation",
                "error": input_result["error"],
                "request_id": request_id
            }), 400

        clean_input = input_result["text"]

        # -------------------------------
        # 2. PROMPT-INJECTION CHECK
        # -------------------------------
        injection_result = detect_prompt_injection(clean_input)

        if injection_result["blocked"]:
            logger.warning(
                "Prompt injection detected | request_id=%s",
                request_id
            )

            return jsonify({
                "success": False,
                "stage": "prompt_guard",
                "error": (
                    "The request was blocked because it contains "
                    "a pattern that may attempt to manipulate "
                    "the AI's instructions."
                ),
                "request_id": request_id
            }), 400

        # -------------------------------
        # 3. SANITIZATION
        # -------------------------------
        safe_input = sanitize_for_prompt(clean_input)

        # -------------------------------
        # 4. AI GENERATION
        # -------------------------------
        ai_result = generate_response(safe_input)

        if not ai_result["success"]:
            return jsonify(
                handle_failure(
                    "llm_generation",
                    ai_result.get("error", "Unknown error"),
                    "The AI service is temporarily unavailable."
                ) | {
                    "request_id": request_id
                }
            ), 502

        # -------------------------------
        # 5. OUTPUT VALIDATION
        # -------------------------------
        output_result = validate_output(
            ai_result["text"]
        )

        if not output_result["valid"]:
            logger.warning(
                "Output validation failed | request_id=%s | reason=%s",
                request_id,
                output_result["error"]
            )

            return jsonify({
                "success": False,
                "stage": "output_validation",
                "error": (
                    "The AI generated a response that "
                    "did not pass validation."
                ),
                "request_id": request_id
            }), 502

        # -------------------------------
        # 6. SUCCESS
        # -------------------------------
        logger.info(
            "Request completed successfully | request_id=%s",
            request_id
        )

        return jsonify({
            "success": True,
            "response": output_result["text"],
            "request_id": request_id,
            "reliability_checks": {
                "input_validation": "passed",
                "prompt_injection_check": "passed",
                "output_validation": "passed"
            }
        })

    except Exception as error:
        logger.exception(
            "Unexpected application failure | request_id=%s",
            request_id
        )

        return jsonify({
            "success": False,
            "stage": "application",
            "error": (
                "An unexpected error occurred. "
                "Please try again."
            ),
            "request_id": request_id
        }), 500


@app.errorhandler(413)
def request_too_large(error):
    return jsonify({
        "success": False,
        "error": "Request is too large."
    }), 413


@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        "success": False,
        "error": "Internal server error."
    }), 500


if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )