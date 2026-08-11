import json
import re
from pathlib import Path
from typing import Any, Mapping


def run_evaluation(
    benchmark: Mapping[str, list[dict[str, str]]],
    configuration: Mapping[str, int],
    output: Path,
) -> dict[str, Any]:
    """Evaluate a benchmark and save the result for the dashboard."""
    sections = benchmark["sections"]
    top_k = configuration["top_k"]
    question_results = []

    for question in benchmark["questions"]:
        # ponytail: lexical ranking keeps ticket 01 offline; ticket 03 replaces it with embeddings.
        evidence = sorted(
            sections,
            key=lambda section: _word_overlap(question["question"], section["text"]),
            reverse=True,
        )[:top_k]
        question_results.append(
            {
                "question": question["question"],
                "expected_section": question["expected_section"],
                "retrieved_evidence": evidence,
                "retrieval_hit": question["expected_section"]
                in {section["section_id"] for section in evidence},
            }
        )

    result = {
        "configuration": dict(configuration),
        "questions": question_results,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2) + "\n")
    return result


def _word_overlap(left: str, right: str) -> int:
    words = lambda text: set(re.findall(r"[a-z0-9]+", text.lower()))
    return len(words(left) & words(right))
