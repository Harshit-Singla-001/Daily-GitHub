import os
import uuid

from flask import (
    Flask,
    render_template,
    request,
    jsonify
)

from config import (
    UPLOAD_FOLDER,
    MAX_FILE_SIZE,
    ALLOWED_EXTENSIONS
)

from document_processor import (
    process_document
)

from text_cleaner import (
    clean_text,
    get_text_statistics
)

from ai_analyzer import (
    analyze_text,
    generate_summary,
    extract_key_information
)


app = Flask(__name__)

app.config[
    "MAX_CONTENT_LENGTH"
] = MAX_FILE_SIZE


def allowed_file(filename):
    if not filename:
        return False

    if "." not in filename:
        return False

    extension = filename.rsplit(
        ".",
        1
    )[1].lower()

    return extension in ALLOWED_EXTENSIONS


@app.route("/")
def index():
    return render_template(
        "index.html"
    )


@app.route(
    "/extract",
    methods=["POST"]
)
def extract():
    if "file" not in request.files:
        return jsonify({
            "success": False,
            "error": "Please upload a file."
        }), 400

    uploaded_file = request.files["file"]

    if not uploaded_file.filename:
        return jsonify({
            "success": False,
            "error": "No file selected."
        }), 400

    if not allowed_file(
        uploaded_file.filename
    ):
        return jsonify({
            "success": False,
            "error": (
                "Unsupported file type. "
                "Use JPG, JPEG, PNG, WEBP, "
                "PDF, DOCX or TXT."
            )
        }), 400

    extension = uploaded_file.filename.rsplit(
        ".",
        1
    )[1].lower()

    unique_filename = (
        f"{uuid.uuid4().hex}.{extension}"
    )

    file_path = os.path.join(
        UPLOAD_FOLDER,
        unique_filename
    )

    try:
        uploaded_file.save(
            file_path
        )

        result = process_document(
            file_path
        )

        if not result["success"]:
            return jsonify({
                "success": False,
                "error": result["error"]
            }), 500

        raw_text = result.get(
            "text",
            ""
        )

        cleaned_text = clean_text(
            raw_text
        )

        statistics = get_text_statistics(
            cleaned_text
        )

        return jsonify({
            "success": True,
            "filename": uploaded_file.filename,
            "method": result.get(
                "method",
                "Unknown"
            ),
            "text": cleaned_text,
            "statistics": statistics
        })

    except Exception as error:
        return jsonify({
            "success": False,
            "error": str(error)
        }), 500

    finally:
        if os.path.exists(file_path):
            os.remove(file_path)


@app.route(
    "/analyze",
    methods=["POST"]
)
def analyze():
    data = request.get_json() or {}

    extracted_text = str(
        data.get(
            "text",
            ""
        )
    ).strip()

    prompt = str(
        data.get(
            "prompt",
            ""
        )
    ).strip()

    if not extracted_text:
        return jsonify({
            "success": False,
            "error": "No extracted text was provided."
        }), 400

    if not prompt:
        prompt = "Summarize this document."

    result = analyze_text(
        extracted_text,
        prompt
    )

    if not result["success"]:
        return jsonify({
            "success": False,
            "error": result["error"]
        }), 500

    return jsonify({
        "success": True,
        "analysis": result["analysis"]
    })


@app.route(
    "/summary",
    methods=["POST"]
)
def summary():
    data = request.get_json() or {}

    extracted_text = str(
        data.get(
            "text",
            ""
        )
    ).strip()

    if not extracted_text:
        return jsonify({
            "success": False,
            "error": "No extracted text was provided."
        }), 400

    result = generate_summary(
        extracted_text
    )

    if not result["success"]:
        return jsonify({
            "success": False,
            "error": result["error"]
        }), 500

    return jsonify({
        "success": True,
        "analysis": result["analysis"]
    })


@app.route(
    "/key-information",
    methods=["POST"]
)
def key_information():
    data = request.get_json() or {}

    extracted_text = str(
        data.get(
            "text",
            ""
        )
    ).strip()

    if not extracted_text:
        return jsonify({
            "success": False,
            "error": "No extracted text was provided."
        }), 400

    result = extract_key_information(
        extracted_text
    )

    if not result["success"]:
        return jsonify({
            "success": False,
            "error": result["error"]
        }), 500

    return jsonify({
        "success": True,
        "analysis": result["analysis"]
    })


@app.errorhandler(413)
def file_too_large(error):
    return jsonify({
        "success": False,
        "error": (
            "File is too large. "
            "Maximum size is 10 MB."
        )
    }), 413


if __name__ == "__main__":
    app.run(
        debug=True
    )