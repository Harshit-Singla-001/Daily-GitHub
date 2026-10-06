import re

from config import MAX_OUTPUT_LENGTH


def validate_output(output):
    errors = []
    warnings = []

    if not isinstance(output, str):
        errors.append("Output must be a string.")
        return {
            "valid": False,
            "errors": errors,
            "warnings": warnings,
        }

    if not output.strip():
        errors.append("Output is empty.")

    if len(output) > MAX_OUTPUT_LENGTH:
        errors.append(
            f"Output exceeds {MAX_OUTPUT_LENGTH} characters."
        )

    secret_patterns = [
        r"\bsk-[A-Za-z0-9_-]{10,}\b",
        r"\bAIza[A-Za-z0-9_-]{20,}\b",
        r"(?i)\bpassword\s*[:=]\s*\S+",
        r"(?i)\bbearer\s+[A-Za-z0-9._-]+",
    ]

    for pattern in secret_patterns:
        if re.search(pattern, output):
            errors.append(
                "Potential secret or credential detected."
            )
            break

    suspicious_phrases = [
        "ignore previous instructions",
        "system prompt",
        "developer message",
        "jailbreak",
    ]

    lowered = output.lower()

    for phrase in suspicious_phrases:
        if phrase in lowered:
            warnings.append(
                f"Suspicious phrase detected: '{phrase}'."
            )

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
    }