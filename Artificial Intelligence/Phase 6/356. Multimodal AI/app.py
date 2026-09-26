import os
import uuid

from flask import (
    Flask,
    render_template,
    request,
    jsonify
)

from config import UPLOAD_FOLDER

from image_utils import (
    validate_image,
    get_image_info
)

from multimodal import analyze_image


app = Flask(__name__)

app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024


@app.route("/")
def index():
    return render_template(
        "index.html"
    )


@app.route(
    "/analyze",
    methods=["POST"]
)
def analyze():
    if "image" not in request.files:
        return jsonify({
            "success": False,
            "error": "Please upload an image."
        }), 400

    image = request.files["image"]

    prompt = request.form.get(
        "prompt",
        "Describe this image in detail."
    ).strip()

    if not prompt:
        prompt = "Describe this image in detail."

    valid, message = validate_image(
        image
    )

    if not valid:
        return jsonify({
            "success": False,
            "error": message
        }), 400

    original_name = image.filename

    extension = original_name.rsplit(
        ".",
        1
    )[1].lower()

    unique_name = (
        f"{uuid.uuid4().hex}.{extension}"
    )

    image_path = os.path.join(
        UPLOAD_FOLDER,
        unique_name
    )

    try:
        image.save(image_path)

        image_info = get_image_info(
            image_path
        )

        result = analyze_image(
            image_path,
            prompt
        )

        if not result["success"]:
            return jsonify({
                "success": False,
                "error": result["error"]
            }), 500

        return jsonify({
            "success": True,
            "filename": original_name,
            "image_info": image_info,
            "prompt": prompt,
            "analysis": result["analysis"]
        })

    finally:
        if os.path.exists(image_path):
            os.remove(image_path)


@app.errorhandler(413)
def file_too_large(error):
    return jsonify({
        "success": False,
        "error": "Image is too large. Maximum size is 5 MB."
    }), 413


if __name__ == "__main__":
    app.run(
        debug=True
    )