"""Recall quiz grading — turns answers into learning events."""
from __future__ import annotations


def grade(quiz: list[dict], answers: list[int]) -> dict:
    """answers[i] is the chosen option index for quiz[i]. Returns score and per-question events."""
    results = []
    for i, q in enumerate(quiz):
        chosen = answers[i] if i < len(answers) else -1
        ok = chosen == q.get("answer")
        results.append({
            "article_id": q.get("article_id"),
            "type": "quiz_correct" if ok else "quiz_wrong",
            "correct": ok,
        })
    return {"score": sum(r["correct"] for r in results), "total": len(quiz), "events": results}
