from flask import Flask, render_template, request, jsonify

from config import MAX_TEXT_LENGTH
from model_runner import run_prediction, get_model_status
from model_info import get_model_information

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json(silent=True) or {}

    text = str(data.get("text", "")).strip()

    if not text:
        return jsonify({
            "success": False,
            "error": "Please enter some text."
        }), 400

    if len(text) > MAX_TEXT_LENGTH:
        return jsonify({
            "success": False,
            "error": f"Text must be {MAX_TEXT_LENGTH} characters or less."
        }), 400

    result = run_prediction(text)

    if not result["success"]:
        return jsonify(result), 500

    return jsonify(result)


@app.route("/model-info")
def model_info():
    return jsonify({
        "success": True,
        "model": get_model_information()
    })


@app.route("/status")
def status():
    return jsonify({
        "success": True,
        "status": get_model_status()
    })


@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "success": False,
        "error": "Invalid request."
    }), 400


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