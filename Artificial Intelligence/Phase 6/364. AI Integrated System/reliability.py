import re

from config import (
    MAX_INPUT_LENGTH,
    MAX_OUTPUT_LENGTH
)


INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?previous\s+instructions",
    r"ignore\s+(all\s+)?prior\s+instructions",
    r"disregard\s+(all\s+)?previous\s+instructions",
    r"forget\s+(all\s+)?previous\s+instructions",
    r"override\s+(the\s+)?system",
    r"reveal\s+(the\s+)?system\s+prompt",
    r"show\s+(the\s+)?system\s+prompt",
    r"print\s+(the\s+)?system\s+prompt",
    r"reveal\s+(your\s+)?instructions",
    r"show\s+(your\s+)?instructions",
    r"jailbreak",
    r"bypass\s+safety",
    r"ignore\s+safety",
    r"reveal\s+(the\s+)?api\s*key",
    r"show\s+(the\s+)?api\s*key"
]


def validate_input(user_input):
    if user_input is None:
        return False, "Input is required."

    if not isinstance(
        user_input,
        str
    ):
        return False, "Input must be text."

    user_input = user_input.strip()

    if not user_input:
        return False, "Please enter a question."

    if len(user_input) > MAX_INPUT_LENGTH:
        return (
            False,
            f"Input must be {MAX_INPUT_LENGTH} characters or less."
        )

    return True, user_input


def check_prompt_injection(
    user_input
):
    text = user_input.lower()

    matches = []

    for pattern in INJECTION_PATTERNS:
        if re.search(
            pattern,
            text
        ):
            matches.append(
                pattern
            )

    return len(matches) > 0, matches


def validate_output(
    output
):
    if output is None:
        return False, "Empty AI response."

    if not isinstance(
        output,
        str
    ):
        return False, "AI response must be text."

    output = output.strip()

    if not output:
        return False, "AI returned an empty response."

    if len(output) > MAX_OUTPUT_LENGTH:
        return (
            False,
            f"AI response exceeded {MAX_OUTPUT_LENGTH} characters."
        )

    secret_patterns = [
        r"gemini_api_key\s*=",
        r"google_api_key\s*=",
        r"api_key\s*=",
        r"password\s*=",
        r"secret_key\s*="
    ]

    for pattern in secret_patterns:
        if re.search(
            pattern,
            output,
            re.IGNORECASE
        ):
            return (
                False,
                "The AI response appears to contain sensitive configuration."
            )

    return True, output