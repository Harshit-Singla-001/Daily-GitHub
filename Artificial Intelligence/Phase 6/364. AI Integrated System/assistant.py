import re
import time
import uuid
from datetime import datetime, timezone

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


# ============================================================
# MEMORY FORMATTER
# ============================================================

def format_memory(memory):
    if not memory:
        return ""

    parts = []

    for item in memory:
        role = str(
            item.get(
                "role",
                "unknown"
            )
        ).upper()

        message = str(
            item.get(
                "message",
                ""
            )
        )

        parts.append(
            f"{role}: {message}"
        )

    return "\n".join(parts)


# ============================================================
# CAPABILITY DETECTION
# ============================================================

def detect_capability(user_input):
    text = user_input.lower().strip()

    # --------------------------------------------------------
    # Calculator
    # --------------------------------------------------------

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
        "what is",
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

    # --------------------------------------------------------
    # Database
    # --------------------------------------------------------

    database_words = [
        "show all products",
        "show products",
        "list products",
        "show customers",
        "list customers",
        "show orders",
        "list orders",
        "show order items",
        "list order items"
    ]

    if any(
        phrase in text
        for phrase in database_words
    ):
        return "database"

    # --------------------------------------------------------
    # File Search
    # --------------------------------------------------------

    file_words = [
        "search my files",
        "find in my files",
        "search files",
        "find in files"
    ]

    if any(
        phrase in text
        for phrase in file_words
    ):
        return "file_search"

    # --------------------------------------------------------
    # RAG
    # --------------------------------------------------------

    rag_words = [
        "according to my documents",
        "according to my document",
        "from my documents",
        "from my document",
        "uploaded document",
        "uploaded documents",
        "knowledge base",
        "my pdf",
        "my files"
    ]

    if any(
        phrase in text
        for phrase in rag_words
    ):
        return "rag"

    # --------------------------------------------------------
    # Direct LLM
    # --------------------------------------------------------

    return "direct"


# ============================================================
# CALCULATION EXTRACTION
# ============================================================

def extract_calculation(user_input):
    expression = user_input

    expression = re.sub(
        r"(?i)calculate",
        "",
        expression
    )

    expression = re.sub(
        r"(?i)compute",
        "",
        expression
    )

    expression = re.sub(
        r"(?i)solve",
        "",
        expression
    )

    expression = re.sub(
        r"(?i)what is",
        "",
        expression
    )

    expression = re.sub(
        r"(?i)how much is",
        "",
        expression
    )

    expression = expression.strip()

    return expression


# ============================================================
# DATABASE TABLE DETECTION
# ============================================================

def choose_database_table(user_input):
    text = user_input.lower()

    if "customer" in text:
        return "customers"

    if "product" in text:
        return "products"

    if "order item" in text:
        return "order_items"

    if "order" in text:
        return "orders"

    return None


# ============================================================
# GET RESPONSE TEXT
# ============================================================

def extract_response_text(response):
    """
    Supports both versions of ai_service.py.

    Older version:
        {"text": "..."}

    Current integrated version:
        {"response": "..."}
    """

    if not isinstance(
        response,
        dict
    ):
        return None

    response_text = response.get(
        "response"
    )

    if response_text is None:
        response_text = response.get(
            "text"
        )

    if response_text is None:
        return None

    return str(
        response_text
    ).strip()


# ============================================================
# GET TOKEN VALUE
# ============================================================

def get_token_value(
    response,
    key
):
    if not isinstance(
        response,
        dict
    ):
        return 0

    try:
        return int(
            response.get(
                key,
                0
            ) or 0
        )
    except (
        TypeError,
        ValueError
    ):
        return 0


# ============================================================
# RUN ASSISTANT
# ============================================================

def run_assistant(
    user_input,
    session_id
):
    request_id = uuid.uuid4().hex[:12]

    timestamp = datetime.now(
        timezone.utc
    ).isoformat()

    start_time = time.perf_counter()

    tools_used = []

    sources = []

    memory_used = False

    rag_used = False

    capability = "unknown"

    validated_input = (
        str(user_input)
        if user_input is not None
        else ""
    )

    try:

        # ====================================================
        # INPUT VALIDATION
        # ====================================================

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
                "error_type": "INVALID_INPUT",
                "error": validated_input
            }

        # ====================================================
        # PROMPT INJECTION CHECK
        # ====================================================

        blocked, matches = check_prompt_injection(
            validated_input
        )

        if blocked:

            logger.warning(
                "Request %s blocked by prompt guard | matches=%s",
                request_id,
                matches
            )

            return {
                "success": False,
                "request_id": request_id,
                "error_type": "PROMPT_INJECTION",
                "error": (
                    "The request was blocked by "
                    "the security layer."
                )
            }

        # ====================================================
        # CONVERSATION MEMORY
        # ====================================================

        memory = get_memory(
            session_id
        )

        if memory:
            memory_used = True

        memory_context = format_memory(
            memory
        )

        # ====================================================
        # CAPABILITY DETECTION
        # ====================================================

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

        # ====================================================
        # CALCULATOR TOOL
        # ====================================================

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
                f"Calculator result: {result}"
            )

        # ====================================================
        # DATABASE TOOL
        # ====================================================

        elif capability == "database":

            table_name = choose_database_table(
                validated_input
            )

            if table_name is None:

                table_context = (
                    "Available tables: "
                    + ", ".join(
                        list_tables()
                    )
                )

            else:

                result = search_database(
                    table_name
                )

                table_context = str(
                    result
                )

            tools_used.append(
                "database"
            )

            tool_context = table_context

        # ====================================================
        # FILE SEARCH TOOL
        # ====================================================

        elif capability == "file_search":

            results = search_files(
                validated_input
            )

            tools_used.append(
                "file_search"
            )

            tool_context = str(
                results
            )

        # ====================================================
        # RAG
        # ====================================================

        elif capability == "rag":

            rag_result = search_knowledge_base(
                validated_input
            )

            if isinstance(
                rag_result,
                dict
            ):

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

        # ====================================================
        # GEMINI
        # ====================================================

        response = generate_response(
            validated_input,
            memory_context=memory_context,
            rag_context=rag_context,
            tool_context=tool_context
        )

        # ====================================================
        # EXTRACT RESPONSE
        # ====================================================

        response_text = extract_response_text(
            response
        )

        if not response_text:

            raise RuntimeError(
                "The AI service returned an empty response."
            )

        # ====================================================
        # OUTPUT VALIDATION
        # ====================================================

        valid_output, validated_output = validate_output(
            response_text
        )

        if not valid_output:

            raise RuntimeError(
                validated_output
            )

        # ====================================================
        # SAVE CONVERSATION
        # ====================================================

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

        # ====================================================
        # LATENCY
        # ====================================================

        latency_ms = (
            time.perf_counter()
            - start_time
        ) * 1000

        # ====================================================
        # TOKEN USAGE
        # ====================================================

        input_tokens = get_token_value(
            response,
            "input_tokens"
        )

        output_tokens = get_token_value(
            response,
            "output_tokens"
        )

        total_tokens = get_token_value(
            response,
            "total_tokens"
        )

        # ====================================================
        # OBSERVABILITY
        # ====================================================

        save_request(
            request_id=request_id,
            timestamp=timestamp,
            model=MODEL,
            input_text=validated_input,
            response_text=validated_output,
            status="SUCCESS",
            latency_ms=round(
                latency_ms,
                2
            ),
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=total_tokens,
            rag_used=rag_used,
            memory_used=memory_used,
            tools_used=",".join(
                tools_used
            )
        )

        logger.info(
            "Request %s completed | capability=%s | latency=%.2fms | input_tokens=%s | output_tokens=%s | total_tokens=%s",
            request_id,
            capability,
            latency_ms,
            input_tokens,
            output_tokens,
            total_tokens
        )

        # ====================================================
        # SUCCESS RESPONSE
        # ====================================================

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

            "input_tokens": input_tokens,

            "output_tokens": output_tokens,

            "total_tokens": total_tokens
        }

    except Exception as error:

        # ====================================================
        # ERROR HANDLING
        # ====================================================

        latency_ms = (
            time.perf_counter()
            - start_time
        ) * 1000

        error_type = type(
            error
        ).__name__

        error_message = str(
            error
        )

        logger.exception(
            "Request %s failed",
            request_id
        )

        # ----------------------------------------------------
        # IMPORTANT:
        # Observability failure should NOT hide the original
        # application error.
        # ----------------------------------------------------

        try:

            save_request(
                request_id=request_id,
                timestamp=timestamp,
                model=MODEL,
                input_text=validated_input[:3000],
                response_text="",
                status="ERROR",
                latency_ms=round(
                    latency_ms,
                    2
                ),
                input_tokens=0,
                output_tokens=0,
                total_tokens=0,
                rag_used=rag_used,
                memory_used=memory_used,
                tools_used=",".join(
                    tools_used
                ),
                error_type=error_type,
                error_message=error_message
            )

        except Exception as observability_error:

            logger.exception(
                "Request %s | failed to save observability record: %s",
                request_id,
                str(observability_error)
            )

        return {
            "success": False,

            "request_id": request_id,

            "error_type": error_type,

            "error": error_message,

            "capability": capability,

            "latency_ms": round(
                latency_ms,
                2
            )
        }