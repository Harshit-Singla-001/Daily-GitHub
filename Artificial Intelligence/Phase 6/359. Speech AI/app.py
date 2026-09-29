import os
import uuid

from flask import (
    Flask,
    render_template,
    request,
    jsonify,
    send_from_directory
)

from config import (
    UPLOAD_FOLDER,
    AUDIO_FOLDER,
    MAX_AUDIO_SIZE
)

from speech_to_text import transcribe_audio
from llm import generate_response
from text_to_speech import generate_speech


app = Flask(__name__)

app.config["MAX_CONTENT_LENGTH"] = MAX_AUDIO_SIZE


ALLOWED_EXTENSIONS = {
    "webm",
    "wav",
    "mp3",
    "m4a",
    "ogg",
    "mp4",
    "aac"
}


def allowed_file(filename):
    if "." not in filename:
        return False

    extension = (
        filename.rsplit(".", 1)[1]
        .lower()
    )

    return extension in ALLOWED_EXTENSIONS


@app.route("/")
def index():
    return render_template(
        "index.html"
    )


@app.route(
    "/voice",
    methods=["POST"]
)
def voice():
    if "audio" not in request.files:
        return jsonify({
            "success": False,
            "error": "No audio file was uploaded."
        }), 400

    audio = request.files["audio"]

    if not audio.filename:
        return jsonify({
            "success": False,
            "error": "Audio filename is missing."
        }), 400

    if not allowed_file(
        audio.filename
    ):
        return jsonify({
            "success": False,
            "error": "Unsupported audio format."
        }), 400

    extension = (
        audio.filename
        .rsplit(".", 1)[1]
        .lower()
    )

    filename = (
        f"{uuid.uuid4().hex}.{extension}"
    )

    file_path = os.path.join(
        UPLOAD_FOLDER,
        filename
    )

    try:
        audio.save(file_path)

        # Step 1: Speech to Text
        transcription = transcribe_audio(
            file_path
        )

        if not transcription["success"]:
            return jsonify({
                "success": False,
                "stage": "speech_to_text",
                "error": transcription["error"]
            }), 500

        transcript = transcription["text"]

        # Step 2: LLM
        ai_response = generate_response(
            transcript
        )

        if not ai_response["success"]:
            return jsonify({
                "success": False,
                "stage": "llm",
                "transcript": transcript,
                "error": ai_response["error"]
            }), 500

        response_text = ai_response["text"]

        # Step 3: Text to Speech
        speech = generate_speech(
            response_text
        )

        if not speech["success"]:
            return jsonify({
                "success": False,
                "stage": "text_to_speech",
                "transcript": transcript,
                "response": response_text,
                "error": speech["error"]
            }), 500

        return jsonify({
            "success": True,
            "transcript": transcript,
            "response": response_text,
            "audio_url": (
                "/audio/"
                + speech["filename"]
            )
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
    "/audio/<filename>"
)
def audio(filename):
    return send_from_directory(
        AUDIO_FOLDER,
        filename
    )


@app.errorhandler(413)
def request_too_large(error):
    return jsonify({
        "success": False,
        "error": "Audio file is too large. Maximum size is 15 MB."
    }), 413


@app.errorhandler(500)
def server_error(error):
    return jsonify({
        "success": False,
        "error": "An unexpected server error occurred."
    }), 500


if __name__ == "__main__":
    app.run(
        debug=True
    )