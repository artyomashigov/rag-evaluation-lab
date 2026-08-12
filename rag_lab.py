import json
from collections import Counter
from functools import lru_cache
from pathlib import Path
from time import perf_counter
from typing import Any, Callable, Mapping
from urllib.request import Request, urlopen


Embedder = Callable[[list[str]], list[list[float]]]
Tokenizer = Callable[[str], list[tuple[int, int]]]
Reranker = Callable[[str, list[str]], list[float]]
AnswerGenerator = Callable[[str, list[dict[str, Any]], str], dict[str, Any]]

ANSWER_FIELDS = (
    "answer",
    "citations",
    "abstained",
    "answer_model",
    "input_tokens",
    "output_tokens",
    "generation_latency_ms",
    "estimated_cost_usd",
)
ANSWER_INSTRUCTIONS = (
    "Answer only from the supplied evidence. Cite source section IDs. "
    "If the evidence is insufficient, abstain and return no citations. "
    "Use at most 30 words and copy each cited section_id exactly."
)


def run_evaluation(
    benchmark: Mapping[str, Any],
    configuration: Mapping[str, Any],
    output: Path,
    *,
    embedder: Embedder | None = None,
    tokenizer: Tokenizer | None = None,
    reranker: Reranker | None = None,
    answer_generator: AnswerGenerator | None = None,
    reviews: Mapping[str, Mapping[str, str]] | None = None,
    allow_paid_calls: bool = False,
) -> dict[str, Any]:
    """Evaluate a benchmark and save the result for the dashboard."""
    _validate_benchmark(benchmark)
    documents = benchmark["documents"]
    questions = benchmark["questions"]
    effective_configuration = {
        "chunk_size": configuration.get("chunk_size", 30),
        "chunk_overlap": configuration.get("chunk_overlap", 5),
        "top_k": configuration["top_k"],
        "reranking": configuration.get("reranking", False),
        "candidate_pool_size": configuration.get("candidate_pool_size", 10),
        "embedding_model": configuration.get(
            "embedding_model", "Alibaba-NLP/gte-modernbert-base"
        ),
        "reranker_model": configuration.get(
            "reranker_model", "cross-encoder/ms-marco-MiniLM-L6-v2"
        ),
    }
    generate_answers = bool(configuration.get("generate_answers", False))
    answer_provider = str(configuration.get("answer_provider", "openai"))
    answer_model = str(configuration.get("answer_model", "gpt-5.6-luna"))
    if generate_answers:
        effective_configuration.update(
            {
                "generate_answers": True,
                "answer_provider": answer_provider,
                "answer_model": answer_model,
            }
        )
    pricing = configuration.get(
        "price_snapshot",
        {
            "date": "2026-08-11",
            "currency": "USD",
            "input_usd_per_million_tokens": 0.2,
            "output_usd_per_million_tokens": 1.2,
        },
    )
    if answer_provider not in {"openai", "ollama"}:
        raise ValueError(f"Unknown answer provider: {answer_provider}")
    if generate_answers and answer_provider == "openai" and not allow_paid_calls:
        raise PermissionError("Answer generation requires allow_paid_calls=True")
    if effective_configuration["top_k"] < 1:
        raise ValueError("Top-k must be positive")
    if (
        effective_configuration["reranking"]
        and effective_configuration["candidate_pool_size"]
        < effective_configuration["top_k"]
    ):
        raise ValueError("Reranking candidate pool must be at least top-k")
    model_name = effective_configuration["embedding_model"]
    tokenize = tokenizer or (lambda text: _local_token_offsets(text, model_name))
    chunks = _chunk_documents(
        documents,
        effective_configuration["chunk_size"],
        effective_configuration["chunk_overlap"],
        tokenize,
    )
    embed = embedder or (lambda texts: _local_embeddings(texts, model_name))
    rerank = reranker or (
        lambda query, texts: _local_reranker_scores(
            query, texts, effective_configuration["reranker_model"]
        )
    )
    generate_answer = answer_generator or (
        _ollama_answer if answer_provider == "ollama" else _openai_answer
    )
    chunk_embeddings = embed([chunk["text"] for chunk in chunks])
    question_results = []
    completed_answers: dict[str, dict[str, Any]] = {}
    if generate_answers and output.exists():
        previous = json.loads(output.read_text())
        if (
            previous.get("configuration") == effective_configuration
            and previous.get("pricing") == pricing
        ):
            completed_answers = {
                item["question_id"]: item
                for item in previous.get("questions", [])
                if isinstance(item.get("answer"), str)
            }

    output.parent.mkdir(parents=True, exist_ok=True)

    for question in questions:
        started = perf_counter()
        query_embedding = embed([question["question"]])[0]
        initial_ranking = sorted(
            (
                (_dot_product(query_embedding, vector), chunk)
                for chunk, vector in zip(chunks, chunk_embeddings)
            ),
            reverse=True,
            key=lambda item: item[0],
        )
        candidate_count = (
            effective_configuration["candidate_pool_size"]
            if effective_configuration["reranking"]
            else effective_configuration["top_k"]
        )
        candidates: list[dict[str, Any]] = [
            {
                **chunk,
                "similarity_score": round(score, 6),
                "original_rank": rank,
            }
            for rank, (score, chunk) in enumerate(
                initial_ranking[:candidate_count], start=1
            )
        ]
        retrieval_latency_ms = round((perf_counter() - started) * 1000, 3)

        reranking_latency_ms = 0.0
        ranked: list[tuple[dict[str, Any], float | None]]
        if effective_configuration["reranking"]:
            started = perf_counter()
            reranker_scores = rerank(
                question["question"],
                [candidate["text"] for candidate in candidates],
            )
            ranked = [
                (candidate, float(score))
                for candidate, score in sorted(
                    zip(candidates, reranker_scores),
                    key=lambda item: item[1],
                    reverse=True,
                )[: effective_configuration["top_k"]]
            ]
            reranking_latency_ms = round((perf_counter() - started) * 1000, 3)
        else:
            ranked = [(candidate, None) for candidate in candidates]

        evidence = [
            {
                **candidate,
                "reranked_position": position
                if effective_configuration["reranking"]
                else None,
                "reranker_score": round(score, 6) if score is not None else None,
            }
            for position, (candidate, score) in enumerate(ranked, start=1)
        ]
        question_result = {
            **question,
            "retrieved_evidence": evidence,
            "retrieval_hit": question["expected_section"] is not None
            and question["expected_section"]
            in {chunk["section_id"] for chunk in evidence},
            "retrieval_latency_ms": retrieval_latency_ms,
            "reranking_latency_ms": reranking_latency_ms,
        }
        previous_answer = completed_answers.get(question["question_id"])
        if previous_answer:
            question_result.update(
                {field: previous_answer[field] for field in ANSWER_FIELDS}
            )
        elif generate_answers:
            started = perf_counter()
            generated = generate_answer(question["question"], evidence, answer_model)
            generation_latency_ms = round((perf_counter() - started) * 1000, 3)
            citations = generated["citations"]
            evidence_sections = {item["section_id"] for item in evidence}
            if (
                not isinstance(generated["answer"], str)
                or not generated["answer"].strip()
                or not isinstance(citations, list)
                or not isinstance(generated["abstained"], bool)
                or not all(
                    isinstance(citation, str) and citation in evidence_sections
                    for citation in citations
                )
                or (not generated["abstained"] and not citations)
                or (generated["abstained"] and citations)
            ):
                raise ValueError("Answer must cite retrieved sections or abstain")
            input_tokens = int(generated["input_tokens"])
            output_tokens = int(generated["output_tokens"])
            if input_tokens < 0 or output_tokens < 0:
                raise ValueError("Token counts cannot be negative")
            question_result.update(
                {
                    **generated,
                    "answer_model": answer_model,
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                    "generation_latency_ms": generation_latency_ms,
                    "estimated_cost_usd": _estimated_cost_usd(
                        input_tokens, output_tokens, pricing
                    ),
                }
            )
        question_results.append(question_result)
        if generate_answers:
            processed_ids = {item["question_id"] for item in question_results}
            _write_json(
                output,
                {
                    "status": "in_progress",
                    "configuration": effective_configuration,
                    "pricing": pricing,
                    "questions": question_results
                    + [
                        completed_answers[pending["question_id"]]
                        for pending in questions
                        if pending["question_id"] in completed_answers
                        and pending["question_id"] not in processed_ids
                    ],
                },
            )

    if reviews is not None:
        valid_labels = {"supported", "unsupported", "correct_abstention"}
        for question_result in question_results:
            review = reviews.get(question_result["question_id"])
            if review is None or review.get("label") not in valid_labels:
                raise ValueError("Every generated answer requires a valid review label")
            if (
                (review["label"] == "supported" and question_result["abstained"])
                or (
                    review["label"] == "correct_abstention"
                    and (
                        not question_result["abstained"]
                        or (
                            not question_result["expected_abstention"]
                            and question_result["retrieval_hit"]
                        )
                    )
                )
            ):
                raise ValueError("Review label contradicts the saved answer")
            question_result.update(
                {
                    "review_label": review["label"],
                    "answer_review_note": review.get("note", ""),
                }
            )

    answerable_results = [result for result in question_results if result["answerable"]]
    result: dict[str, Any] = {
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
            "average_reranking_latency_ms": round(
                sum(item["reranking_latency_ms"] for item in question_results)
                / len(question_results),
                3,
            ),
        },
        "questions": question_results,
    }
    if generate_answers:
        total_input_tokens = sum(item["input_tokens"] for item in question_results)
        total_output_tokens = sum(item["output_tokens"] for item in question_results)
        result.update({"status": "complete", "pricing": pricing})
        result["metrics"].update(
            {
                "average_generation_latency_ms": round(
                    sum(item["generation_latency_ms"] for item in question_results)
                    / len(question_results),
                    3,
                ),
                "input_tokens": total_input_tokens,
                "output_tokens": total_output_tokens,
                "estimated_cost_usd": _estimated_cost_usd(
                    total_input_tokens, total_output_tokens, pricing
                ),
            }
        )
        if reviews is not None:
            result["metrics"].update(
                {
                    "unsupported_answer_rate": round(
                        sum(
                            item["review_label"] == "unsupported"
                            for item in question_results
                        )
                        / len(question_results),
                        4,
                    ),
                    "correct_abstention_rate": round(
                        sum(
                            item["expected_abstention"]
                            and item["review_label"] == "correct_abstention"
                            for item in question_results
                        )
                        / sum(not item["answerable"] for item in question_results),
                        4,
                    ),
                    "average_total_latency_ms": round(
                        sum(
                            item["retrieval_latency_ms"]
                            + item["reranking_latency_ms"]
                            + item["generation_latency_ms"]
                            for item in question_results
                        )
                        / len(question_results),
                        3,
                    ),
                }
            )
    _write_json(output, result)
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


def _estimated_cost_usd(
    input_tokens: int, output_tokens: int, pricing: Mapping[str, Any]
) -> float:
    return round(
        (
            input_tokens * pricing["input_usd_per_million_tokens"]
            + output_tokens * pricing["output_usd_per_million_tokens"]
        )
        / 1_000_000,
        8,
    )


def _write_json(output: Path, value: Mapping[str, Any]) -> None:
    temporary = output.with_suffix(f"{output.suffix}.tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n")
    temporary.replace(output)


@lru_cache(maxsize=1)
def _embedding_model(model_name: str) -> Any:
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer(model_name)


def _local_embeddings(texts: list[str], model_name: str) -> list[list[float]]:
    embeddings = _embedding_model(model_name).encode(
        texts, normalize_embeddings=True, show_progress_bar=False
    )
    return embeddings.tolist()


@lru_cache(maxsize=1)
def _reranker_model(model_name: str) -> Any:
    from sentence_transformers import CrossEncoder

    return CrossEncoder(model_name)


def _local_reranker_scores(
    query: str, texts: list[str], model_name: str
) -> list[float]:
    scores = _reranker_model(model_name).predict(
        [(query, text) for text in texts], show_progress_bar=False
    )
    return scores.tolist()


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


def _openai_answer(
    question: str, evidence: list[dict[str, Any]], model_name: str
) -> dict[str, Any]:
    from openai import OpenAI

    response = OpenAI().responses.create(
        model=model_name,
        reasoning={"effort": "none"},
        store=False,
        input=[
            {
                "role": "system",
                "content": ANSWER_INSTRUCTIONS,
            },
            {
                "role": "user",
                "content": json.dumps(
                    {
                        "question": question,
                        "evidence": [
                            {
                                "section_id": item["section_id"],
                                "text": item["text"],
                            }
                            for item in evidence
                        ],
                    }
                ),
            },
        ],
        text={
            "format": {
                "type": "json_schema",
                "name": "grounded_answer",
                "strict": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "answer": {"type": "string"},
                        "citations": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                        "abstained": {"type": "boolean"},
                    },
                    "required": ["answer", "citations", "abstained"],
                    "additionalProperties": False,
                },
            }
        },
    )
    generated = json.loads(response.output_text)
    generated["input_tokens"] = response.usage.input_tokens
    generated["output_tokens"] = response.usage.output_tokens
    return generated


def _ollama_answer(
    question: str, evidence: list[dict[str, Any]], model_name: str
) -> dict[str, Any]:
    payload = {
        "model": model_name,
        "stream": False,
        "format": {
            "type": "object",
            "properties": {
                "answer": {"type": "string"},
                "citations": {"type": "array", "items": {"type": "string"}},
                "abstained": {"type": "boolean"},
            },
            "required": ["answer", "citations", "abstained"],
        },
        "options": {"temperature": 0, "num_predict": 128},
        "messages": [
            {
                "role": "system",
                "content": ANSWER_INSTRUCTIONS,
            },
            {
                "role": "user",
                "content": json.dumps(
                    {
                        "question": question,
                        "evidence": [
                            {"section_id": item["section_id"], "text": item["text"]}
                            for item in evidence
                        ],
                    }
                ),
            },
        ],
    }
    request = Request(
        "http://127.0.0.1:11434/api/chat",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
    )
    with urlopen(request, timeout=120) as response:
        result = json.load(response)
    generated = json.loads(result["message"]["content"])
    section_ids = {item["section_id"] for item in evidence}
    generated["citations"] = list(
        dict.fromkeys(
            section_id
            for citation in generated["citations"]
            for section_id in section_ids
            if section_id in citation
        )
    )
    if generated["abstained"] or not generated["citations"]:
        generated.update(
            {
                "answer": "The supplied documents do not contain enough information.",
                "citations": [],
                "abstained": True,
            }
        )
    generated["input_tokens"] = result["prompt_eval_count"]
    generated["output_tokens"] = result["eval_count"]
    return generated


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
