import re


def normalize_text(text):
    text = text.lower()
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def keyword_overlap(question, answer):
    question_words = set(
        normalize_text(question).split()
    )

    answer_words = set(
        normalize_text(answer).split()
    )

    question_words = {
        word
        for word in question_words
        if len(word) > 3
    }

    if not question_words:
        return 1.0

    overlap = question_words.intersection(answer_words)

    return len(overlap) / len(question_words)


def calculate_relevance(question, answer):
    score = keyword_overlap(question, answer)

    return round(score * 100, 2)


def evaluate_groundedness(context, answer):
    if not context.strip():
        return {
            "score": 0,
            "status": "NOT_EVALUATED",
            "reason": "No trusted context was provided.",
        }

    context_words = set(
        normalize_text(context).split()
    )

    answer_words = set(
        normalize_text(answer).split()
    )

    answer_words = {
        word
        for word in answer_words
        if len(word) > 3
    }

    if not answer_words:
        return {
            "score": 0,
            "status": "NOT_EVALUATED",
            "reason": "Answer contains no meaningful words.",
        }

    supported = answer_words.intersection(context_words)

    score = round(
        len(supported) / len(answer_words) * 100,
        2,
    )

    if score >= 70:
        status = "GROUNDED"
    elif score >= 40:
        status = "PARTIALLY_GROUNDED"
    else:
        status = "POTENTIAL_HALLUCINATION"

    return {
        "score": score,
        "status": status,
        "reason": (
            "The answer was compared with the "
            "provided trusted context."
        ),
    }


def evaluate_answer(question, context, answer):
    relevance = calculate_relevance(
        question,
        answer,
    )

    groundedness = evaluate_groundedness(
        context,
        answer,
    )

    evaluation_score = relevance

    if groundedness["status"] != "NOT_EVALUATED":
        evaluation_score = (
            relevance + groundedness["score"]
        ) / 2

    if evaluation_score >= 80:
        quality = "EXCELLENT"
    elif evaluation_score >= 60:
        quality = "GOOD"
    elif evaluation_score >= 40:
        quality = "NEEDS_REVIEW"
    else:
        quality = "POOR"

    return {
        "relevance_score": round(relevance, 2),
        "groundedness": groundedness,
        "overall_score": round(
            evaluation_score,
            2,
        ),
        "quality": quality,
    }