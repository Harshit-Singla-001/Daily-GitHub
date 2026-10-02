import traceback

from logger_config import logger


def handle_failure(stage, error, user_message=None):
    logger.error(
        "Failure at stage=%s | error=%s",
        stage,
        str(error)
    )

    logger.debug(
        "Traceback:\n%s",
        traceback.format_exc()
    )

    return {
        "success": False,
        "stage": stage,
        "error": user_message or (
            "The AI service could not complete the request."
        )
    }