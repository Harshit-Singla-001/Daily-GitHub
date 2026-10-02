import re
from config import MAX_INPUT_LENGTH


def validate_input(user_input):
    if user_input is None:
        return {
            "valid": False,
            "error": "Input is required."
        }

    if not isinstance(user_input, str):
        return {
            "valid": False,
            "error": "Input must be text."
        }

    cleaned_input = user_input.strip()

    if not cleaned_input:
        return {
            "valid": False,
            "error": "Input cannot be empty."
        }

    if len(cleaned_input) > MAX_INPUT_LENGTH:
        return {
            "valid": False,
            "error": (
                f"Input is too long. Maximum allowed length is "
                f"{MAX_INPUT_LENGTH} characters."
            )
        }

    if not re.search(r"[A-Za-z0-9]", cleaned_input):
        return {
            "valid": False,
            "error": "Input must contain meaningful text."
        }

    return {
        "valid": True,
        "text": cleaned_input
    }