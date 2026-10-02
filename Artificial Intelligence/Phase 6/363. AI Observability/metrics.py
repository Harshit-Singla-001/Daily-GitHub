from observability import get_connection

def get_total_requests():
    connection = get_connection()

    try:
        result = connection.execute(
            """
            SELECT COUNT(*) AS count
            FROM ai_requests
            """
        ).fetchone()

        return int(result["count"])

    finally:
        connection.close()

def get_successful_requests():
    connection = get_connection()

    try:
        result = connection.execute(
            """
            SELECT COUNT(*) AS count
            FROM ai_requests
            WHERE status = 'SUCCESS'
            """
        ).fetchone()

        return int(result["count"])

    finally:
        connection.close()

def get_failed_requests():
    connection = get_connection()

    try:
        result = connection.execute(
            """
            SELECT COUNT(*) AS count
            FROM ai_requests
            WHERE status = 'ERROR'
            """
        ).fetchone()

        return int(result["count"])

    finally:
        connection.close()

def get_success_rate():
    total = get_total_requests()
    successful = get_successful_requests()

    if total == 0:
        return 0.0

    return round(
        (successful / total) * 100,
        2
    )

def get_error_rate():
    total = get_total_requests()
    failed = get_failed_requests()

    if total == 0:
        return 0.0

    return round(
        (failed / total) * 100,
        2
    )

def get_average_latency():
    connection = get_connection()

    try:
        result = connection.execute(
            """
            SELECT AVG(latency_ms) AS average_latency
            FROM ai_requests
            """
        ).fetchone()

        if result["average_latency"] is None:
            return 0.0

        return round(
            float(result["average_latency"]),
            2
        )

    finally:
        connection.close()

def get_min_latency():
    connection = get_connection()

    try:
        result = connection.execute(
            """
            SELECT MIN(latency_ms) AS minimum_latency
            FROM ai_requests
            """
        ).fetchone()

        if result["minimum_latency"] is None:
            return 0.0

        return round(
            float(result["minimum_latency"]),
            2
        )

    finally:
        connection.close()

def get_max_latency():
    connection = get_connection()

    try:
        result = connection.execute(
            """
            SELECT MAX(latency_ms) AS maximum_latency
            FROM ai_requests
            """
        ).fetchone()

        if result["maximum_latency"] is None:
            return 0.0

        return round(
            float(result["maximum_latency"]),
            2
        )

    finally:
        connection.close()

def get_total_tokens():
    connection = get_connection()

    try:
        result = connection.execute(
            """
            SELECT COALESCE(SUM(total_tokens), 0) AS total_tokens
            FROM ai_requests
            """
        ).fetchone()

        return int(result["total_tokens"])

    finally:
        connection.close()

def get_average_tokens():
    connection = get_connection()

    try:
        result = connection.execute(
            """
            SELECT AVG(total_tokens) AS average_tokens
            FROM ai_requests
            WHERE status = 'SUCCESS'
            """
        ).fetchone()

        if result["average_tokens"] is None:
            return 0.0

        return round(
            float(result["average_tokens"]),
            2
        )

    finally:
        connection.close()

def get_metrics():
    return {
        "total_requests": get_total_requests(),
        "successful_requests": get_successful_requests(),
        "failed_requests": get_failed_requests(),
        "success_rate": get_success_rate(),
        "error_rate": get_error_rate(),
        "average_latency_ms": get_average_latency(),
        "minimum_latency_ms": get_min_latency(),
        "maximum_latency_ms": get_max_latency(),
        "total_tokens": get_total_tokens(),
        "average_tokens": get_average_tokens()
    }