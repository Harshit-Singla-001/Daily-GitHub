import os

from flask import (
    Flask,
    render_template,
    request,
    jsonify,
    send_from_directory
)

from config import (
    GENERATED_FOLDER,
    MAX_PROMPT_LENGTH
)

from image_generator import (
    generate_image
)


app = Flask(__name__)

app.config[
    "MAX_CONTENT_LENGTH"
] = 1 * 1024 * 1024


@app.route("/")
def index():
    return render_template(
        "index.html"
    )


@app.route(
    "/generate",
    methods=["POST"]
)
def generate():

    data = request.get_json(
        silent=True
    ) or {}

    prompt = str(
        data.get(
            "prompt",
            ""
        )
    ).strip()

    if not prompt:
        return jsonify({
            "success": False,
            "error": (
                "Please enter an image prompt."
            )
        }), 400

    if len(prompt) > MAX_PROMPT_LENGTH:
        return jsonify({
            "success": False,
            "error": (
                f"Prompt must be "
                f"{MAX_PROMPT_LENGTH} "
                f"characters or less."
            )
        }), 400

    result = generate_image(
        prompt
    )

    if not result["success"]:
        return jsonify({
            "success": False,
            "error": result["error"]
        }), 500

    return jsonify({
        "success": True,
        "filename": result["filename"],
        "url": (
            "/generated/"
            + result["filename"]
        )
    })


@app.route(
    "/generated/<filename>"
)
def generated_image(filename):

    return send_from_directory(
        GENERATED_FOLDER,
        filename
    )


@app.errorhandler(413)
def file_too_large(error):

    return jsonify({
        "success": False,
        "error": "Request is too large."
    }), 413


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
        debug=True
    )