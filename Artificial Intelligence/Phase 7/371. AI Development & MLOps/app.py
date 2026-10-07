import logging
import time

from flask import (
    Flask,
    jsonify,
    render_template,
    request,
)

from config import Config
from metrics import metrics
from model import SentimentModel


def create_logger():
    logger = logging.getLogger(
        Config.APP_NAME
    )

    logger.setLevel(
        getattr(
            logging,
            Config.LOG_LEVEL,
            logging.INFO,
        )
    )

    if not logger.handlers:

        console_handler = (
            logging.StreamHandler()
        )

        formatter = logging.Formatter(
            "%(asctime)s | "
            "%(levelname)s | "
            "%(name)s | "
            "%(message)s"
        )

        console_handler.setFormatter(
            formatter
        )

        logger.addHandler(
            console_handler
        )

    return logger


logger = create_logger()

app = Flask(__name__)

model = SentimentModel(
    name=Config.MODEL_NAME,
    version=Config.MODEL_VERSION,
)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/health", methods=["GET"])
def health():

    return jsonify({
        "status": "healthy",
        "service": Config.APP_NAME,
        "environment":
            Config.ENVIRONMENT,
    })


@app.route("/info", methods=["GET"])
def info():

    return jsonify({
        "application":
            Config.APP_NAME,

        "environment":
            Config.ENVIRONMENT,

        "model": {
            "name":
                model.name,

            "version":
                model.version,
        },
    })


@app.route("/metrics", methods=["GET"])
def get_metrics():

    return jsonify(
        metrics.get_metrics()
    )


@app.route("/predict", methods=["POST"])
def predict():

    start_time = time.perf_counter()

    success = False

    try:

        data = request.get_json(
            silent=True
        )

        if not isinstance(data, dict):

            return jsonify({
                "error":
                    "Request body must be JSON."
            }), 400

        text = str(
            data.get("text", "")
        ).strip()

        if not text:

            return jsonify({
                "error":
                    "Text is required."
            }), 400

        if len(text) > Config.MAX_TEXT_LENGTH:

            return jsonify({
                "error":
                    "Input text is too long."
            }), 400

        logger.info(
            "Prediction request received."
        )

        result = model.predict(text)

        success = True

        total_latency = (
            time.perf_counter()
            - start_time
        )

        result["request_latency_ms"] = round(
            total_latency * 1000,
            3,
        )

        logger.info(
            "Prediction completed | "
            "model=%s | version=%s | "
            "latency_ms=%.3f",
            model.name,
            model.version,
            total_latency * 1000,
        )

        return jsonify({
            "success": True,
            "result": result,
        })

    except Exception as error:

        logger.exception(
            "Prediction failed."
        )

        return jsonify({
            "success": False,
            "error":
                "Internal prediction error.",
        }), 500

    finally:

        total_latency = (
            time.perf_counter()
            - start_time
        )

        metrics.record_request(
            latency=total_latency,
            success=success,
        )


if __name__ == "__main__":

    logger.info(
        "Starting %s",
        Config.APP_NAME,
    )

    logger.info(
        "Environment: %s",
        Config.ENVIRONMENT,
    )

    logger.info(
        "Model: %s",
        Config.MODEL_NAME,
    )

    logger.info(
        "Model version: %s",
        Config.MODEL_VERSION,
    )

    app.run(
        host="0.0.0.0",
        port=Config.PORT,
        debug=Config.DEBUG,
    )