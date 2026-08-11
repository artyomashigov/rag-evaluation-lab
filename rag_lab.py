import json
from collections import Counter
from functools import lru_cache
from pathlib import Path
from time import perf_counter
from typing import Any, Callable, Mapping


Embedder = Callable[[list[str]], list[list[float]]]
Tokenizer = Callable[[str], list[tuple[int, int]]]


def run_evaluation(
    benchmark: Mapping[str, Any],
    configuration: Mapping[str, Any],
    output: Path,
    *,
    embedder: Embedder | None = None,
    tokenizer: Tokenizer | None = None,
) -> dict[str, Any]:
    """Evaluate a benchmark and save the result for the dashboard."""
    _validate_benchmark(benchmark)
    documents = benchmark["documents"]
    questions = benchmark["questions"]
    effective_configuration = {
        "chunk_size": configuration.get("chunk_size", 700),
        "chunk_overlap": configuration.get("chunk_overlap", 0),
        "top_k": configuration["top_k"],
        "reranking": configuration.get("reranking", False),
        "embedding_model": configuration.get(
            "embedding_model", "Alibaba-NLP/gte-modernbert-base"
        ),
    }
    model_name = effective_configuration["embedding_model"]
    tokenize = tokenizer or (lambda text: _local_token_offsets(text, model_name))
    chunks = _chunk_documents(
        documents,
        effective_configuration["chunk_size"],
        effective_configuration["chunk_overlap"],
        tokenize,
    )
    embed = embedder or (lambda texts: _local_embeddings(texts, model_name))
    chunk_embeddings = embed([chunk["text"] for chunk in chunks])
    question_results = []

    for question in questions:
        started = perf_counter()
        query_embedding = embed([question["question"]])[0]
        ranked = sorted(
            (
                (_dot_product(query_embedding, vector), chunk)
                for chunk, vector in zip(chunks, chunk_embeddings)
            ),
            reverse=True,
            key=lambda item: item[0],
        )[: effective_configuration["top_k"]]
        evidence = [
            {
                **chunk,
                "similarity_score": round(score, 6),
            }
            for score, chunk in ranked
        ]
        latency_ms = round((perf_counter() - started) * 1000, 3)
        question_results.append(
            {
                **question,
                "retrieved_evidence": evidence,
                "retrieval_hit": question["expected_section"] is not None
                and question["expected_section"]
                in {chunk["section_id"] for chunk in evidence},
                "retrieval_latency_ms": latency_ms,
            }
        )

    answerable_results = [result for result in question_results if result["answerable"]]
    result = {
        "configuration": effective_configuration,
        "benchmark_summary": {
            "document_count": len(documents),
            "section_count": sum(len(document["sections"]) for document in documents),
            "chunk_count": len(chunks),
            "question_count": len(questions),
            "answerable_count": sum(question["answerable"] for question in questions),
            "unanswerable_count": sum(
                not question["answerable"] for question in questions
            ),
            "category_counts": dict(
                sorted(Counter(question["category"] for question in questions).items())
            ),
        },
        "metrics": {
            "retrieval_hit_rate": round(
                sum(item["retrieval_hit"] for item in answerable_results)
                / len(answerable_results),
                4,
            ),
            "average_retrieval_latency_ms": round(
                sum(item["retrieval_latency_ms"] for item in question_results)
                / len(question_results),
                3,
            ),
        },
        "questions": question_results,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2) + "\n")
    return result


def _chunk_documents(
    documents: list[dict[str, Any]],
    chunk_size: int,
    overlap: int,
    tokenize: Tokenizer,
) -> list[dict[str, Any]]:
    if chunk_size < 1 or overlap < 0 or overlap >= chunk_size:
        raise ValueError("Chunk size must be positive and overlap must be smaller")

    chunks = []
    step = chunk_size - overlap
    for document in documents:
        for section in document["sections"]:
            tokens = tokenize(section["text"])
            for token_start in range(0, len(tokens), step):
                selected = tokens[token_start : token_start + chunk_size]
                if not selected:
                    break
                start_char = selected[0][0]
                end_char = selected[-1][1]
                chunks.append(
                    {
                        "chunk_id": f"{section['section_id']}:{start_char}-{end_char}",
                        "document_id": document["document_id"],
                        "document_title": document["title"],
                        "section_id": section["section_id"],
                        "start_char": start_char,
                        "end_char": end_char,
                        "text": section["text"][start_char:end_char],
                    }
                )
                if token_start + chunk_size >= len(tokens):
                    break
    return chunks


def _dot_product(left: list[float], right: list[float]) -> float:
    return sum(a * b for a, b in zip(left, right))


@lru_cache(maxsize=1)
def _embedding_model(model_name: str) -> Any:
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer(model_name)


def _local_embeddings(texts: list[str], model_name: str) -> list[list[float]]:
    embeddings = _embedding_model(model_name).encode(
        texts, normalize_embeddings=True, show_progress_bar=False
    )
    return embeddings.tolist()


def _local_token_offsets(text: str, model_name: str) -> list[tuple[int, int]]:
    encoded = _embedding_model(model_name).tokenizer(
        text,
        add_special_tokens=False,
        return_offsets_mapping=True,
        truncation=False,
    )
    return [
        (int(start), int(end))
        for start, end in encoded["offset_mapping"]
        if end > start
    ]


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

        empty = [
            field
            for field in ("question_id", "question", "category", "reviewer_note")
            if not isinstance(question[field], str) or not question[field].strip()
        ]
        if empty:
            raise ValueError(f"Question {label} has empty: {', '.join(empty)}")

        expected_section = question["expected_section"]
        if question["answerable"] and expected_section not in section_ids:
            raise ValueError(
                f"Question {label} references unknown section_id: {expected_section}"
            )
        if question["answerable"] and (
            not isinstance(question["reference_answer"], str)
            or not question["reference_answer"].strip()
            or question["expected_abstention"] is not False
        ):
            raise ValueError(
                f"Answerable question {label} requires a reference answer and cannot abstain"
            )
        if not question["answerable"] and (
            expected_section is not None
            or question["reference_answer"] is not None
            or question["expected_abstention"] is not True
        ):
            raise ValueError(
                f"Unanswerable question {label} must have no expected section or answer and must abstain"
            )
