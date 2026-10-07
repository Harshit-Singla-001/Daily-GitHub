import os


class Config:
    APP_NAME = os.getenv(
        "APP_NAME",
        "AI MLOps Service",
    )

    MODEL_NAME = os.getenv(
        "MODEL_NAME",
        "sentiment-model",
    )

    MODEL_VERSION = os.getenv(
        "MODEL_VERSION",
        "1.0.0",
    )

    LOG_LEVEL = os.getenv(
        "LOG_LEVEL",
        "INFO",
    ).upper()

    PORT = int(
        os.getenv(
            "PORT",
            "5000",
        )
    )

    DEBUG = os.getenv(
        "DEBUG",
        "false",
    ).lower() == "true"

    ENVIRONMENT = os.getenv(
        "ENVIRONMENT",
        "development",
    )

    MAX_TEXT_LENGTH = int(
        os.getenv(
            "MAX_TEXT_LENGTH",
            "2000",
        )
    )