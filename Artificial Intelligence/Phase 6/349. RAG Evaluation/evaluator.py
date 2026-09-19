import json
import re
from pathlib import Path
from google import genai
from config import API_KEY, MODEL, EVALUATION_FILE
from rag import generate_answer

client = genai.Client(api_key=API_KEY)

def load_questions():
    path = Path(EVALUATION_FILE)

    if not path.exists():
        raise FileNotFoundError(
            f"Evaluation file not found: {EVALUATION_FILE}"
        )

    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)

def normalize(value):
    return re.sub(
        r"[^a-z0-9\s]",
        "",
        value.lower()
    )

def calculate_keyword_score(answer, expected_keywords):
    if not expected_keywords:
        return 1.0

    normalized_answer = normalize(answer)

    matched = 0

    for keyword in expected_keywords:
        if normalize(keyword) in normalized_answer:
            matched += 1

    return matched / len(expected_keywords)

def evaluate_retrieval(results, expected_documents):
    if not expected_documents:
        return {
            "hit": 1 if not results else 0,
            "mrr": 1.0 if not results else 0.0,
            "precision": 1.0 if not results else 0.0
        }

    retrieved_documents = [
        result.get("document", "")
        for result in results
    ]

    hit = 0
    reciprocal_rank = 0.0

    for index, document in enumerate(retrieved_documents, start=1):
        if document in expected_documents:
            hit = 1
            reciprocal_rank = 1 / index
            break

    relevant_count = sum(
        1 for document in retrieved_documents
        if document in expected_documents
    )

    precision = relevant_count / len(retrieved_documents) if retrieved_documents else 0

    return {
        "hit": hit,
        "mrr": round(reciprocal_rank, 4),
        "precision": round(precision, 4)
    }

def judge_answer(question, answer, context):
    prompt = f"""
Evaluate the following RAG answer.

Question:
{question}

Answer:
{answer}

Retrieved Context:
{context}

Return ONLY valid JSON in this exact structure:

{{
  "relevance": 0,
  "groundedness": 0,
  "hallucination": 0,
  "reason": ""
}}

Rules:

relevance:
1 = answer directly addresses the question
0 = answer does not address the question

groundedness:
1 = answer is fully supported by the retrieved context
0 = answer contains unsupported claims

hallucination:
1 = hallucination is present
0 = no hallucination is present

Give a short reason.
"""

    response = client.models.generate_content(
        model=MODEL,
        contents=prompt
    )

    text = response.text.strip()

    text = re.sub(
        r"^```json\s*|\s*```$",
        "",
        text
    ).strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {
            "relevance": 0,
            "groundedness": 0,
            "hallucination": 1,
            "reason": "Evaluation model returned invalid JSON."
        }

def calculate_overall(result):
    retrieval = (
        result["retrieval"]["hit"] +
        result["retrieval"]["mrr"] +
        result["retrieval"]["precision"]
    ) / 3

    answer_quality = (
        result["relevance"] +
        result["groundedness"] +
        result["keyword_score"]
    ) / 3

    hallucination_score = 1 - result["hallucination"]

    overall = (
        retrieval * 0.4 +
        answer_quality * 0.4 +
        hallucination_score * 0.2
    )

    return round(overall * 100, 2)

def evaluate_all():
    questions = load_questions()
    results = []

    for test in questions:
        question = test["question"]

        rag_result = generate_answer(question)

        answer = rag_result["answer"]
        retrieved = rag_result["results"]
        context = rag_result["context"]

        retrieval = evaluate_retrieval(
            retrieved,
            test.get("expected_documents", [])
        )

        keyword_score = calculate_keyword_score(
            answer,
            test.get("expected_keywords", [])
        )

        judge = judge_answer(
            question,
            answer,
            context
        )

        result = {
            "id": test["id"],
            "question": question,
            "answer": answer,
            "retrieval": retrieval,
            "keyword_score": round(keyword_score, 4),
            "relevance": judge.get("relevance", 0),
            "groundedness": judge.get("groundedness", 0),
            "hallucination": judge.get("hallucination", 1),
            "reason": judge.get("reason", "")
        }

        result["overall_score"] = calculate_overall(result)

        results.append(result)

    return build_summary(results)

def build_summary(results):
    if not results:
        return {
            "results": [],
            "summary": {}
        }

    retrieval_hit_rate = sum(
        item["retrieval"]["hit"]
        for item in results
    ) / len(results)

    mrr = sum(
        item["retrieval"]["mrr"]
        for item in results
    ) / len(results)

    precision = sum(
        item["retrieval"]["precision"]
        for item in results
    ) / len(results)

    relevance = sum(
        item["relevance"]
        for item in results
    ) / len(results)

    groundedness = sum(
        item["groundedness"]
        for item in results
    ) / len(results)

    hallucination_rate = sum(
        item["hallucination"]
        for item in results
    ) / len(results)

    keyword_score = sum(
        item["keyword_score"]
        for item in results
    ) / len(results)

    overall_score = sum(
        item["overall_score"]
        for item in results
    ) / len(results)

    return {
        "results": results,
        "summary": {
            "total_questions": len(results),
            "retrieval_hit_rate": round(retrieval_hit_rate * 100, 2),
            "mrr": round(mrr * 100, 2),
            "precision": round(precision * 100, 2),
            "answer_relevance": round(relevance * 100, 2),
            "groundedness": round(groundedness * 100, 2),
            "hallucination_rate": round(hallucination_rate * 100, 2),
            "keyword_score": round(keyword_score * 100, 2),
            "overall_score": round(overall_score, 2)
        }
    }