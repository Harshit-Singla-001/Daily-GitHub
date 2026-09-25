def validate_result(category, result):
    if not result:
        return {
            "valid": False,
            "reason": "No result was produced."
        }

    if not isinstance(result, dict):
        return {
            "valid": False,
            "reason": "Invalid processing result."
        }

    if not result.get("success"):
        return {
            "valid": False,
            "reason": result.get(
                "error",
                "Processing failed."
            )
        }

    if category == "CALCULATION":
        if "result" not in result:
            return {
                "valid": False,
                "reason": "Calculation result is missing."
            }

    if category == "DATABASE":
        if "rows" not in result:
            return {
                "valid": False,
                "reason": "Database rows are missing."
            }

    if category in {"QUESTION", "GENERAL"}:
        if not result.get("result"):
            return {
                "valid": False,
                "reason": "AI response is empty."
            }

    return {
        "valid": True,
        "reason": "Validation successful."
    }