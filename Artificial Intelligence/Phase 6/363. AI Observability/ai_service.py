import time
import uuid
from datetime import datetime, timezone

from google import genai
from google.genai import types

from config import (
    API_KEY,
    MODEL,
    MAX_INPUT_LENGTH,
    MAX_OUTPUT_LENGTH
)
from observability import save_request
from logger_config import logger

client = genai.Client(
    api_key=API_KEY
)

SYSTEM_INSTRUCTION = """
You are a helpful AI assistant.

Answer the user's question clearly and accurately.

Do not reveal API keys, passwords, secrets,
system configuration or private credentials.

Do not claim that you performed an action
that you did not perform.

Keep responses reasonably concise unless
the user asks for more detail.
"""

GENERATION_CONFIG = types.GenerateContentConfig(
    system_instruction=SYSTEM_INSTRUCTION,
    automatic_function_calling=types.AutomaticFunctionCallingConfig(
        disable=True
    )
)

def extract_usage(response):
    input_tokens = 0
    output_tokens = 0
    thinking_tokens = 0
    total_tokens = 0

    usage = getattr(
        response,
        "usage_metadata",
        None
    )

    if usage is None:
        return {
            "input_tokens": 0,
            "output_tokens": 0,
            "thinking_tokens": 0,
            "total_tokens": 0
        }

    input_tokens = getattr(
        usage,
        "prompt_token_count",
        0
    ) or 0

    output_tokens = getattr(
        usage,
        "candidates_token_count",
        0
    ) or 0

    thinking_tokens = getattr(
        usage,
        "thoughts_token_count",
        0
    ) or 0

    total_tokens = getattr(
        usage,
        "total_token_count",
        0
    ) or 0

    return {
        "input_tokens": int(input_tokens),
        "output_tokens": int(output_tokens),
        "thinking_tokens": int(thinking_tokens),
        "total_tokens": int(total_tokens)
    }

def validate_input(user_input):
    if user_input is None:
        return False, "Input is required."

    if not isinstance(user_input, str):
        return False, "Input must be text."

    user_input = user_input.strip()

    if not user_input:
        return False, "Please enter a question."

    if len(user_input) > MAX_INPUT_LENGTH:
        return (
            False,
            f"Input must be {MAX_INPUT_LENGTH} "
            "characters or less."
        )

    return True, user_input

def validate_output(response_text):
    if response_text is None:
        return False, "The model returned no response."

    if not isinstance(response_text, str):
        return False, "The model returned an invalid response."

    response_text = response_text.strip()

    if not response_text:
        return False, "The model returned an empty response."

    if len(response_text) > MAX_OUTPUT_LENGTH:
        return (
            False,
            f"The model response exceeded the "
            f"{MAX_OUTPUT_LENGTH} character limit."
        )

    return True, response_text

def classify_api_error(error):
    error_type = type(error).__name__
    error_text = str(error)
    error_lower = error_text.lower()

    status_code = getattr(
        error,
        "status_code",
        None
    )

    if status_code is None:
        response = getattr(
            error,
            "response",
            None
        )

        status_code = getattr(
            response,
            "status_code",
            None
        )

    if status_code == 429 or "429" in error_text:
        return (
            "RATE_LIMITED",
            "The Gemini API rate limit was reached."
        )

    if status_code == 503 or "503" in error_text:
        return (
            "SERVICE_UNAVAILABLE",
            "The Gemini service is temporarily "
            "experiencing high demand. Please try again."
        )

    if status_code == 504 or "504" in error_text:
        return (
            "DEADLINE_EXCEEDED",
            "The Gemini request timed out. Please try again."
        )

    if status_code in (401, 403):
        return (
            "AUTHENTICATION_ERROR",
            "The Gemini API key or project access "
            "could not be verified."
        )

    if status_code == 400 or "400" in error_text:
        return (
            "INVALID_REQUEST",
            "The Gemini API rejected the request."
        )

    if (
        "timeout" in error_lower
        or "timed out" in error_lower
        or "deadline" in error_lower
    ):
        return (
            "TIMEOUT",
            "The AI request timed out. Please try again."
        )

    if (
        "connection" in error_lower
        or "network" in error_lower
    ):
        return (
            "NETWORK_ERROR",
            "A network error occurred while contacting Gemini."
        )

    return (
        error_type.upper(),
        "The AI service could not complete the request."
    )

def generate_response(user_input):
    request_id = uuid.uuid4().hex[:12]

    timestamp = datetime.now(
        timezone.utc
    ).isoformat()

    valid, validated_input = validate_input(
        user_input
    )

    if not valid:
        logger.warning(
            "Request %s rejected during input validation",
            request_id
        )

        return {
            "success": False,
            "request_id": request_id,
            "error": validated_input
        }

    logger.info(
        "Request %s started | model=%s",
        request_id,
        MODEL
    )

    start_time = time.perf_counter()

    try:
        prompt = f"""
USER INPUT:

{validated_input}

Answer the user's request.
"""

        response = client.models.generate_content(
            model=MODEL,
            contents=prompt,
            config=GENERATION_CONFIG
        )

        latency_ms = (
            time.perf_counter() - start_time
        ) * 1000

        response_text = getattr(
            response,
            "text",
            None
        )

        usage = extract_usage(response)

        valid_output, validated_output = validate_output(
            response_text
        )

        if not valid_output:
            save_request(
                request_id=request_id,
                timestamp=timestamp,
                model=MODEL,
                input_text=validated_input,
                response_text=response_text or "",
                status="ERROR",
                latency_ms=round(latency_ms, 2),
                input_tokens=usage["input_tokens"],
                output_tokens=usage["output_tokens"],
                total_tokens=usage["total_tokens"],
                error_type="OUTPUT_VALIDATION_ERROR",
                error_message=validated_output
            )

            logger.error(
                "Request %s failed output validation | "
                "latency=%.2fms",
                request_id,
                latency_ms
            )

            return {
                "success": False,
                "request_id": request_id,
                "error": validated_output
            }

        save_request(
            request_id=request_id,
            timestamp=timestamp,
            model=MODEL,
            input_text=validated_input,
            response_text=validated_output,
            status="SUCCESS",
            latency_ms=round(latency_ms, 2),
            input_tokens=usage["input_tokens"],
            output_tokens=usage["output_tokens"],
            total_tokens=usage["total_tokens"]
        )

        logger.info(
            "Request %s completed | "
            "latency=%.2fms | "
            "input_tokens=%s | "
            "output_tokens=%s | "
            "thinking_tokens=%s | "
            "total_tokens=%s",
            request_id,
            latency_ms,
            usage["input_tokens"],
            usage["output_tokens"],
            usage["thinking_tokens"],
            usage["total_tokens"]
        )

        return {
            "success": True,
            "request_id": request_id,
            "response": validated_output,
            "model": MODEL,
            "latency_ms": round(
                latency_ms,
                2
            ),
            "input_tokens": usage["input_tokens"],
            "output_tokens": usage["output_tokens"],
            "thinking_tokens": usage["thinking_tokens"],
            "total_tokens": usage["total_tokens"]
        }

    except Exception as error:
        latency_ms = (
            time.perf_counter() - start_time
        ) * 1000

        error_type, user_message = classify_api_error(
            error
        )

        raw_error_message = str(error)

        save_request(
            request_id=request_id,
            timestamp=timestamp,
            model=MODEL,
            input_text=validated_input,
            response_text="",
            status="ERROR",
            latency_ms=round(latency_ms, 2),
            input_tokens=0,
            output_tokens=0,
            total_tokens=0,
            error_type=error_type,
            error_message=raw_error_message
        )

        logger.error(
            "Request %s failed | "
            "type=%s | latency=%.2fms | error=%s",
            request_id,
            error_type,
            latency_ms,
            raw_error_message
        )

        return {
            "success": False,
            "request_id": request_id,
            "error_type": error_type,
            "error": user_message,
            "latency_ms": round(
                latency_ms,
                2
            )
        }