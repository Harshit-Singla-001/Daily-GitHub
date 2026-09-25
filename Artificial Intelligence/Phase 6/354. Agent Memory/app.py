from flask import Flask, render_template, request, jsonify

from agent import run_agent

from memory import (
    initialize_memory_database,
    get_short_term_memory,
    get_conversation_history,
    get_user_memories,
    clear_short_term_memory,
    clear_user_history,
    save_user_memory
)

app = Flask(__name__)

initialize_memory_database()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json() or {}

    user_id = str(data.get("user_id", "default")).strip()
    message = str(data.get("message", "")).strip()

    if not message:
        return jsonify({
            "success": False,
            "error": "Message is required."
        }), 400

    if not user_id:
        user_id = "default"

    result = run_agent(
        user_id,
        message
    )

    return jsonify(result)


@app.route("/memory", methods=["GET"])
def memory():
    user_id = request.args.get("user_id", "default")

    return jsonify({
        "success": True,
        "short_term": get_short_term_memory(user_id),
        "conversation_history": get_conversation_history(user_id),
        "persistent_memory": get_user_memories(user_id)
    })


@app.route("/memory/save", methods=["POST"])
def save_memory():
    data = request.get_json() or {}

    user_id = str(data.get("user_id", "default")).strip()
    key = str(data.get("key", "")).strip()
    value = str(data.get("value", "")).strip()

    if not key or not value:
        return jsonify({
            "success": False,
            "error": "Key and value are required."
        }), 400

    save_user_memory(
        user_id,
        key,
        value
    )

    return jsonify({
        "success": True,
        "message": "Persistent memory saved."
    })


@app.route("/memory/clear-short-term", methods=["POST"])
def clear_short_term():
    data = request.get_json() or {}
    user_id = str(data.get("user_id", "default"))

    clear_short_term_memory(user_id)

    return jsonify({
        "success": True,
        "message": "Short-term memory cleared."
    })


@app.route("/memory/clear-all", methods=["POST"])
def clear_all_memory():
    data = request.get_json() or {}
    user_id = str(data.get("user_id", "default"))

    clear_user_history(user_id)

    return jsonify({
        "success": True,
        "message": "All memory cleared."
    })


if __name__ == "__main__":
    app.run(debug=True)