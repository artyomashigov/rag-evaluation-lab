import json
import re
from collections import Counter
from pathlib import Path
from typing import Any, Mapping


def run_evaluation(
    benchmark: Mapping[str, Any],
    configuration: Mapping[str, int],
    output: Path,
) -> dict[str, Any]:
    """Evaluate a benchmark and save the result for the dashboard."""
    _validate_benchmark(benchmark)
    documents = benchmark["documents"]
    sections = [
        {
            **section,
            "document_id": document["document_id"],
            "document_title": document["title"],
        }
        for document in documents
        for section in document["sections"]
    ]
    questions = benchmark["questions"]
    top_k = configuration["top_k"]
    question_results = []

    for question in questions:
        # ponytail: lexical ranking keeps ticket 01 offline; ticket 03 replaces it with embeddings.
        evidence = sorted(
            sections,
            key=lambda section: _word_overlap(question["question"], section["text"]),
            reverse=True,
        )[:top_k]
        question_results.append(
            {
                **question,
                "retrieved_evidence": evidence,
                "retrieval_hit": question["expected_section"] is not None
                and question["expected_section"]
                in {section["section_id"] for section in evidence},
            }
        )

    result = {
        "configuration": dict(configuration),
        "benchmark_summary": {
            "document_count": len(documents),
            "section_count": len(sections),
            "question_count": len(questions),
            "answerable_count": sum(question["answerable"] for question in questions),
            "unanswerable_count": sum(
                not question["answerable"] for question in questions
            ),
            "category_counts": dict(
                sorted(Counter(question["category"] for question in questions).items())
            ),
        },
        "questions": question_results,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2) + "\n")
    return result


def _validate_benchmark(benchmark: Mapping[str, Any]) -> None:
    documents = benchmark.get("documents")
    questions = benchmark.get("questions")
    if not isinstance(documents, list) or not isinstance(questions, list):
        raise ValueError("Benchmark requires documents and questions lists")

    document_ids: set[str] = set()
    section_ids: set[str] = set()
    for index, document in enumerate(documents, start=1):
        missing = {"document_id", "title", "sections"} - document.keys()
        if missing:
            raise ValueError(f"Document {index} is missing: {', '.join(sorted(missing))}")
        document_id = document["document_id"]
        if document_id in document_ids:
            raise ValueError(f"Duplicate document_id: {document_id}")
        document_ids.add(document_id)

        for section_index, section in enumerate(document["sections"], start=1):
            missing = {"section_id", "text"} - section.keys()
            if missing:
                raise ValueError(
                    f"Section {section_index} in {document_id} is missing: "
                    f"{', '.join(sorted(missing))}"
                )
            section_id = section["section_id"]
            if section_id in section_ids:
                raise ValueError(f"Duplicate section_id: {section_id}")
            section_ids.add(section_id)

    required_question_fields = {
        "question_id",
        "question",
        "category",
        "answerable",
        "expected_section",
        "reference_answer",
        "expected_abstention",
        "reviewer_note",
    }
    question_ids: set[str] = set()
    for index, question in enumerate(questions, start=1):
        missing = required_question_fields - question.keys()
        label = question.get("question_id", str(index))
        if missing:
            raise ValueError(f"Question {label} is missing: {', '.join(sorted(missing))}")
        if label in question_ids:
            raise ValueError(f"Duplicate question_id: {label}")
        question_ids.add(label)

        expected_section = question["expected_section"]
        if question["answerable"] and expected_section not in section_ids:
            raise ValueError(
                f"Question {label} references unknown section_id: {expected_section}"
            )
        if not question["answerable"] and (
            expected_section is not None or not question["expected_abstention"]
        ):
            raise ValueError(
                f"Unanswerable question {label} must have no expected section and must abstain"
            )


def _word_overlap(left: str, right: str) -> int:
    words = lambda text: set(re.findall(r"[a-z0-9]+", text.lower()))
    return len(words(left) & words(right))
