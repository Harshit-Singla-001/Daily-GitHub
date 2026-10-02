from config import MAX_OUTPUT_LENGTH


def validate_output(output):
    if output is None:
        return {
            "valid": False,
            "error": "The AI returned no response."
        }

    if not isinstance(output, str):
        return {
            "valid": False,
            "error": "The AI returned an invalid response type."
        }

    cleaned_output = output.strip()

    if not cleaned_output:
        return {
            "valid": False,
            "error": "The AI returned an empty response."
        }

    if len(cleaned_output) > MAX_OUTPUT_LENGTH:
        return {
            "valid": False,
            "error": "The AI response exceeded the allowed output length."
        }

    dangerous_markers = [
        "api_key=",
        "gemini_api_key=",
        "password=",
        "secret_key="
    ]

    lower_output = cleaned_output.lower()

    for marker in dangerous_markers:
        if marker in lower_output:
            return {
                "valid": False,
                "error": "The AI response appears to contain sensitive data."
            }

    return {
        "valid": True,
        "text": cleaned_output
    }