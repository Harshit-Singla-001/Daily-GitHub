from flask import (
    Flask,
    jsonify,
    render_template,
    request,
)

from config import MAX_INPUT_LENGTH
from evaluator import evaluate_answer
from security import (
    create_security_report,
    save_audit_log,
)
from validators import validate_output


app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/evaluate", methods=["POST"])
def evaluate():
    try:
        data = request.get_json(silent=True)

        if not isinstance(data, dict):
            return jsonify({
                "success": False,
                "error": "Invalid JSON request.",
            }), 400

        question = str(
            data.get("question", "")
        ).strip()

        context = str(
            data.get("context", "")
        ).strip()

        answer = str(
            data.get("answer", "")
        ).strip()

        if not question:
            return jsonify({
                "success": False,
                "error": "Question is required.",
            }), 400

        if not answer:
            return jsonify({
                "success": False,
                "error": "AI answer is required.",
            }), 400

        if len(question) > MAX_INPUT_LENGTH:
            return jsonify({
                "success": False,
                "error": "Question is too long.",
            }), 400

        if len(context) > MAX_INPUT_LENGTH:
            return jsonify({
                "success": False,
                "error": "Context is too long.",
            }), 400

        security_report = create_security_report(
            question + "\n" + answer
        )

        output_validation = validate_output(
            answer
        )

        evaluation = evaluate_answer(
            question,
            context,
            answer,
        )

        final_risk = security_report["risk_score"]

        if not output_validation["valid"]:
            final_risk = min(
                100,
                final_risk + 30,
            )

        if (
            evaluation["groundedness"]["status"]
            == "POTENTIAL_HALLUCINATION"
        ):
            final_risk = min(
                100,
                final_risk + 20,
            )

        security_report["final_risk_score"] = (
            final_risk
        )

        save_audit_log({
            "question": question,
            "evaluation": evaluation,
            "security": security_report,
            "output_validation": output_validation,
        })

        return jsonify({
            "success": True,
            "evaluation": evaluation,
            "security": security_report,
            "output_validation": output_validation,
        })

    except Exception as error:
        return jsonify({
            "success": False,
            "error": str(error),
        }), 500


@app.route("/api/health")
def health():
    return jsonify({
        "status": "healthy",
        "service": "AI Evaluation & Security",
    })


if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True,
    )