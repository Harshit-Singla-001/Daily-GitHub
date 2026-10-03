import re
import time
import uuid

from ai_service import generate_response

from calculator_tool import safe_calculate

from database_tool import (
    list_tables,
    search_database
)

from file_tool import search_files

from memory import (
    get_memory,
    save_message
)

from rag import search_knowledge_base

from reliability import (
    validate_input,
    check_prompt_injection,
    validate_output
)

from observability import save_request

from config import MODEL

from logger_config import logger


def format_memory(memory):
    if not memory:
        return ""

    parts = []

    for item in memory:
        role = str(
            item.get("role", "unknown")
        ).upper()

        message = item.get(
            "message",
            ""
        )

        parts.append(
            f"{role}: {message}"
        )

    return "\n".join(parts)


def detect_capability(user_input):
    text = user_input.lower().strip()

    calculation_pattern = re.compile(
        r"^[\d\s+\-*/%().^]+$"
    )

    if calculation_pattern.match(
        user_input.strip()
    ):
        return "calculator"

    calculator_words = [
        "calculate",
        "compute",
        "solve",
        "how much is"
    ]

    mathematical_symbols = [
        "+",
        "-",
        "*",
        "/",
        "%",
        "^"
    ]

    if (
        any(
            word in text
            for word in calculator_words
        )
        and any(
            symbol in user_input
            for symbol in mathematical_symbols
        )
    ):
        return "calculator"

    database_phrases = [
        "show all products",
        "show products",
        "list products",
        "show customers",
        "list customers",
        "show orders",
        "list orders",
        "show order items",
        "list order items",
        "show all customers",
        "show all orders"
    ]

    if any(
        phrase in text
        for phrase in database_phrases
    ):
        return "database"

    file_phrases = [
        "search my files",
        "find in my files",
        "search files",
        "find in files"
    ]

    if any(
        phrase in text
        for phrase in file_phrases
    ):
        return "file_search"

    rag_phrases = [
        "according to my documents",
        "according to my document",
        "from my documents",
        "from my document",
        "uploaded document",
        "uploaded documents",
        "knowledge base",
        "my pdf",
        "my document",
        "in the document"
    ]

    if any(
        phrase in text
        for phrase in rag_phrases
    ):
        return "rag"

    return "direct"


def extract_calculation(user_input):
    expression = user_input

    patterns = [
        r"(?i)calculate",
        r"(?i)compute",
        r"(?i)solve",
        r"(?i)how much is"
    ]

    for pattern in patterns:
        expression = re.sub(
            pattern,
            "",
            expression
        )

    expression = expression.strip()

    return expression


def choose_database_table(user_input):
    text = user_input.lower()

    if "order item" in text:
        return "order_items"

    if "customer" in text:
        return "customers"

    if "product" in text:
        return "products"

    if "order" in text:
        return "orders"

    return None


def extract_response_text(response):
    if not isinstance(
        response,
        dict
    ):
        raise RuntimeError(
            "AI service returned an invalid response."
        )

    text = response.get(
        "response"
    )

    if text is None:
        text = response.get(
            "text"
        )

    if not text:
        raise RuntimeError(
            "AI service returned an empty response."
        )

    return str(text)


def safe_observability_save(**kwargs):
    try:
        save_request(
            **kwargs
        )
    except Exception as error:
        logger.exception(
            "Observability save failed: %s",
            error
        )


def run_assistant(
    user_input,
    session_id
):
    request_id = uuid.uuid4().hex[:12]

    start_time = time.perf_counter()

    tools_used = []
    sources = []

    memory_used = False
    rag_used = False

    try:
        valid, validated_input = validate_input(
            user_input
        )

        if not valid:
            return {
                "success": False,
                "request_id": request_id,
                "error_type": "INVALID_INPUT",
                "error": validated_input
            }

        blocked, matches = check_prompt_injection(
            validated_input
        )

        if blocked:
            logger.warning(
                "Request %s blocked by prompt guard",
                request_id
            )

            return {
                "success": False,
                "request_id": request_id,
                "error_type": "PROMPT_INJECTION",
                "error": (
                    "The request was blocked "
                    "by the security layer."
                )
            }

        memory = get_memory(
            session_id
        )

        memory_used = bool(
            memory
        )

        memory_context = format_memory(
            memory
        )

        capability = detect_capability(
            validated_input
        )

        logger.info(
            "Request %s | capability=%s",
            request_id,
            capability
        )

        rag_context = ""
        tool_context = ""

        if capability == "calculator":
            expression = extract_calculation(
                validated_input
            )

            result = safe_calculate(
                expression
            )

            tools_used.append(
                "calculator"
            )

            tool_context = (
                "Calculator tool result:\n"
                f"{result}"
            )

        elif capability == "database":
            table_name = choose_database_table(
                validated_input
            )

            if table_name:
                result = search_database(
                    table_name
                )

                tool_context = (
                    "Database tool result:\n"
                    f"{result}"
                )

            else:
                tables = list_tables()

                tool_context = (
                    "Available database tables:\n"
                    f"{tables}"
                )

            tools_used.append(
                "database"
            )

        elif capability == "file_search":
            results = search_files(
                validated_input
            )

            tools_used.append(
                "file_search"
            )

            tool_context = (
                "File search tool result:\n"
                f"{results}"
            )

        elif capability == "rag":
            rag_result = search_knowledge_base(
                validated_input
            )

            rag_context = rag_result.get(
                "context",
                ""
            )

            sources = rag_result.get(
                "sources",
                []
            )

            rag_used = bool(
                sources
            )

            if rag_used:
                tools_used.append(
                    "knowledge_base"
                )

        response = generate_response(
            validated_input,
            memory_context=memory_context,
            rag_context=rag_context,
            tool_context=tool_context
        )

        response_text = extract_response_text(
            response
        )

        valid_output, validated_output = validate_output(
            response_text
        )

        if not valid_output:
            raise RuntimeError(
                validated_output
            )

        save_message(
            session_id,
            "user",
            validated_input
        )

        save_message(
            session_id,
            "assistant",
            validated_output
        )

        latency_ms = (
            time.perf_counter()
            - start_time
        ) * 1000

        safe_observability_save(
            request_id=request_id,
            model=MODEL,
            input_text=validated_input,
            response_text=validated_output,
            status="SUCCESS",
            latency_ms=round(
                latency_ms,
                2
            ),
            input_tokens=response.get(
                "input_tokens",
                0
            ),
            output_tokens=response.get(
                "output_tokens",
                0
            ),
            total_tokens=response.get(
                "total_tokens",
                0
            ),
            rag_used=rag_used,
            memory_used=memory_used,
            tools_used=",".join(
                tools_used
            )
        )

        logger.info(
            "Request %s completed | latency=%.2fms",
            request_id,
            latency_ms
        )

        return {
            "success": True,
            "request_id": request_id,
            "response": validated_output,
            "capability": capability,
            "sources": sources,
            "tools_used": tools_used,
            "memory_used": memory_used,
            "rag_used": rag_used,
            "latency_ms": round(
                latency_ms,
                2
            ),
            "input_tokens": response.get(
                "input_tokens",
                0
            ),
            "output_tokens": response.get(
                "output_tokens",
                0
            ),
            "total_tokens": response.get(
                "total_tokens",
                0
            )
        }

    except Exception as error:
        latency_ms = (
            time.perf_counter()
            - start_time
        ) * 1000

        logger.exception(
            "Request %s failed",
            request_id
        )

        safe_observability_save(
            request_id=request_id,
            model=MODEL,
            input_text=str(
                user_input
            )[:3000],
            response_text="",
            status="ERROR",
            latency_ms=round(
                latency_ms,
                2
            ),
            rag_used=rag_used,
            memory_used=memory_used,
            tools_used=",".join(
                tools_used
            ),
            error_type=type(
                error
            ).__name__,
            error_message=str(
                error
            )
        )

        return {
            "success": False,
            "request_id": request_id,
            "error_type": type(
                error
            ).__name__,
            "error": str(error),
            "latency_ms": round(
                latency_ms,
                2
            )
        }