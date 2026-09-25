from classifier import classify_request

from processor import (
    process_calculation,
    process_question,
    process_general,
    get_database_data
)

from validator import validate_result

from response_generator import generate_response

def run_workflow(user_input):
    workflow = {
        "input": user_input,
        "steps": []
    }

    # STEP 1: CLASSIFY

    classification = classify_request(user_input)

    workflow["steps"].append({
        "step": "CLASSIFY",
        "status": "completed",
        "category": classification["category"],
        "reason": classification["reason"]
    })

    category = classification["category"]

    # STEP 2: PROCESS

    if category == "CALCULATION":
        processed_result = process_calculation(
            user_input
        )

    elif category == "DATABASE":
        processed_result = get_database_data(
            user_input
        )

    elif category == "QUESTION":
        processed_result = process_question(
            user_input
        )

    else:
        processed_result = process_general(
            user_input
        )

    workflow["steps"].append({
        "step": "PROCESS",
        "status": (
            "completed"
            if processed_result.get("success")
            else "failed"
        )
    })

    # STEP 3: VALIDATE

    validation = validate_result(
        category,
        processed_result
    )

    workflow["steps"].append({
        "step": "VALIDATE",
        "status": (
            "completed"
            if validation["valid"]
            else "failed"
        ),
        "reason": validation["reason"]
    })

    if not validation["valid"]:
        return {
            "success": False,
            "answer": validation["reason"],
            "category": category,
            "workflow": workflow
        }

    # STEP 4: GENERATE RESPONSE

    answer = generate_response(
        user_input,
        category,
        processed_result
    )

    workflow["steps"].append({
        "step": "GENERATE RESPONSE",
        "status": "completed"
    })

    return {
        "success": True,
        "answer": answer,
        "category": category,
        "processed_result": processed_result,
        "workflow": workflow
    }