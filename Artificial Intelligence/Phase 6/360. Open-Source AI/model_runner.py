from transformers import pipeline
from config import MODEL_ID, MODEL_TASK

_model = None
_model_error = None


def load_model():
    global _model
    global _model_error

    if _model is not None:
        return _model

    if _model_error is not None:
        raise RuntimeError(_model_error)

    try:
        print(f"Loading Hugging Face model: {MODEL_ID}")
        print("The first run may take some time because the model must be downloaded.")

        _model = pipeline(
            task=MODEL_TASK,
            model=MODEL_ID
        )

        print("Hugging Face model loaded successfully.")
        return _model

    except Exception as error:
        _model_error = str(error)
        raise RuntimeError(
            f"Failed to load Hugging Face model: {_model_error}"
        )


def run_prediction(text):
    if not text or not text.strip():
        return {
            "success": False,
            "error": "Please enter some text."
        }

    text = text.strip()

    try:
        model = load_model()

        predictions = model(
            text,
            truncation=True
        )

        if not predictions:
            return {
                "success": False,
                "error": "The model returned no prediction."
            }

        prediction = predictions[0]

        label = str(prediction.get("label", "UNKNOWN"))
        score = float(prediction.get("score", 0.0))

        return {
            "success": True,
            "label": label,
            "confidence": round(score * 100, 2),
            "raw_score": score,
            "model": MODEL_ID,
            "task": MODEL_TASK,
            "inference_mode": "Local"
        }

    except Exception as error:
        return {
            "success": False,
            "error": str(error)
        }


def get_model_status():
    return {
        "loaded": _model is not None,
        "model": MODEL_ID,
        "task": MODEL_TASK,
        "inference_mode": "Local"
    }