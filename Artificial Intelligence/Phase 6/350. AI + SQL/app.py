from flask import Flask, render_template, request, jsonify

from database import initialize_database
from assistant import process_question

app = Flask(__name__)

initialize_database()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json(silent=True) or {}

    question = data.get("question", "").strip()

    result = process_question(question)

    status_code = 200 if result.get("success") else 400

    return jsonify(result), status_code

if __name__ == "__main__":
    app.run(debug=True)