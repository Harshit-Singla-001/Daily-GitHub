from config import MODEL_ID, MODEL_TASK
from model_runner import get_model_status


def get_model_information():
    status = get_model_status()

    return {
        "model": MODEL_ID,
        "task": MODEL_TASK,
        "framework": "Hugging Face Transformers + PyTorch",
        "inference_mode": "Local",
        "model_source": "Hugging Face Hub",
        "loaded": status["loaded"],
        "description": (
            "A pretrained DistilBERT model fine-tuned for "
            "binary sentiment classification."
        )
    }