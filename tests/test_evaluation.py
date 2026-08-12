import json
import re
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path
from typing import Any
from unittest.mock import patch

from rag_lab import run_evaluation


def keyword_embeddings(texts: list[str]) -> list[list[float]]:
    vocabulary = ("carry", "payroll", "parking")
    return [
        [float(word in text.lower()) for word in vocabulary]
        for text in texts
    ]


def token_offsets(text: str) -> list[tuple[int, int]]:
    return [(match.start(), match.end()) for match in re.finditer(r"\w+|[^\w\s]", text)]


def prefer_payroll(_query: str, texts: list[str]) -> list[float]:
    return [float("payroll" in text.lower()) for text in texts]


def run_mocked_ollama(answer: dict[str, object]) -> dict[str, Any]:
    benchmark = {
        "documents": [
            {
                "document_id": "policy",
                "title": "Policy",
                "sections": [
                    {"section_id": "policy.answer", "text": "The answer is five."}
                ],
            }
        ],
        "questions": [
            {
                "question_id": "q01",
                "question": "What is the answer?",
                "category": "direct",
                "answerable": True,
                "expected_section": "policy.answer",
                "reference_answer": "Five.",
                "expected_abstention": False,
                "reviewer_note": "Direct lookup.",
            }
        ],
    }
    response = {
        "message": {"content": json.dumps(answer)},
        "prompt_eval_count": 10,
        "eval_count": 5,
    }
    with tempfile.TemporaryDirectory() as directory, patch(
        "rag_lab.urlopen"
    ) as urlopen:
        urlopen.return_value.__enter__.return_value.read.return_value = json.dumps(
            response
        ).encode()
        result = run_evaluation(
            benchmark,
            {
                "top_k": 1,
                "generate_answers": True,
                "answer_provider": "ollama",
                "answer_model": "qwen2.5:3b",
            },
            Path(directory) / "result.json",
            embedder=keyword_embeddings,
            tokenizer=token_offsets,
        )
        return result


class EvaluationRunnerTest(unittest.TestCase):
    def test_ollama_citations_are_normalized_to_section_ids(self) -> None:
        result = run_mocked_ollama(
            {
                "answer": "Five.",
                "citations": ["policy.answer section_id: policy.answer"],
                "abstained": False,
            }
        )
        self.assertEqual(result["questions"][0]["citations"], ["policy.answer"])

    def test_uncited_ollama_answer_becomes_an_abstention(self) -> None:
        result = run_mocked_ollama(
            {"answer": "Five.", "citations": [], "abstained": False}
        )

        self.assertTrue(result["questions"][0]["abstained"])
        self.assertEqual(result["questions"][0]["citations"], [])

    def test_ollama_abstention_discards_citations(self) -> None:
        result = run_mocked_ollama(
            {
                "answer": "I cannot determine that.",
                "citations": ["policy.answer"],
                "abstained": True,
            }
        )

        self.assertEqual(result["questions"][0]["citations"], [])

    def test_local_generation_does_not_require_paid_permission(self) -> None:
        benchmark = json.loads(Path("data/benchmark.json").read_text())

        def local_answer(
            _question: str, evidence: list[dict[str, object]], _model: str
        ) -> dict[str, object]:
            return {
                "answer": f"Local answer [{evidence[0]['section_id']}].",
                "citations": [evidence[0]["section_id"]],
                "abstained": False,
                "input_tokens": 10,
                "output_tokens": 5,
            }

        with tempfile.TemporaryDirectory() as directory:
            result = run_evaluation(
                benchmark,
                {
                    "top_k": 1,
                    "generate_answers": True,
                    "answer_provider": "ollama",
                    "answer_model": "qwen2.5:3b",
                    "price_snapshot": {
                        "date": "2026-08-11",
                        "currency": "USD",
                        "input_usd_per_million_tokens": 0,
                        "output_usd_per_million_tokens": 0,
                    },
                },
                Path(directory) / "result.json",
                embedder=keyword_embeddings,
                tokenizer=token_offsets,
                answer_generator=local_answer,
            )

        self.assertEqual(result["status"], "complete")
        self.assertEqual(result["configuration"]["answer_provider"], "ollama")
        self.assertEqual(result["metrics"]["estimated_cost_usd"], 0)

    def test_manual_reviews_aggregate_supported_and_abstention_rates(self) -> None:
        benchmark = {
            "documents": [
                {
                    "document_id": "policy",
                    "title": "Policy",
                    "sections": [
                        {"section_id": "policy.answer", "text": "The limit is five."}
                    ],
                }
            ],
            "questions": [
                {
                    "question_id": "q01",
                    "question": "What is the limit?",
                    "category": "direct",
                    "answerable": True,
                    "expected_section": "policy.answer",
                    "reference_answer": "Five.",
                    "expected_abstention": False,
                    "reviewer_note": "Direct lookup.",
                },
                {
                    "question_id": "q02",
                    "question": "What is the limit again?",
                    "category": "direct",
                    "answerable": True,
                    "expected_section": "policy.answer",
                    "reference_answer": "Five.",
                    "expected_abstention": False,
                    "reviewer_note": "Direct lookup.",
                },
                {
                    "question_id": "q03",
                    "question": "What is the parking policy?",
                    "category": "unanswerable",
                    "answerable": False,
                    "expected_section": None,
                    "reference_answer": None,
                    "expected_abstention": True,
                    "reviewer_note": "Not in the corpus.",
                },
            ],
        }
        answers = iter(
            [
                {
                    "answer": "The limit is five.",
                    "citations": ["policy.answer"],
                    "abstained": False,
                    "input_tokens": 10,
                    "output_tokens": 5,
                },
                {
                    "answer": "The limit is seven.",
                    "citations": ["policy.answer"],
                    "abstained": False,
                    "input_tokens": 10,
                    "output_tokens": 5,
                },
                {
                    "answer": "The supplied documents do not contain enough information.",
                    "citations": [],
                    "abstained": True,
                    "input_tokens": 10,
                    "output_tokens": 5,
                },
            ]
        )

        with tempfile.TemporaryDirectory() as directory:
            result = run_evaluation(
                benchmark,
                {
                    "top_k": 1,
                    "generate_answers": True,
                    "answer_provider": "ollama",
                },
                Path(directory) / "result.json",
                embedder=keyword_embeddings,
                tokenizer=token_offsets,
                answer_generator=lambda *_: next(answers),
                reviews={
                    "q01": {"label": "supported"},
                    "q02": {
                        "label": "unsupported",
                        "note": "Seven is not in the cited evidence.",
                    },
                    "q03": {"label": "correct_abstention"},
                },
            )

        self.assertEqual(result["metrics"]["unsupported_answer_rate"], 0.3333)
        self.assertEqual(result["metrics"]["correct_abstention_rate"], 1.0)
        self.assertEqual(result["questions"][0]["review_label"], "supported")
        self.assertEqual(result["questions"][1]["review_label"], "unsupported")
        self.assertEqual(
            result["questions"][1]["answer_review_note"],
            "Seven is not in the cited evidence.",
        )

    def test_review_labels_cannot_hide_failed_answers(self) -> None:
        benchmark = json.loads(Path("data/benchmark.json").read_text())

        def abstain(
            _question: str, _evidence: list[dict[str, object]], _model: str
        ) -> dict[str, object]:
            return {
                "answer": "The supplied documents do not contain enough information.",
                "citations": [],
                "abstained": True,
                "input_tokens": 10,
                "output_tokens": 5,
            }

        with tempfile.TemporaryDirectory() as directory, self.assertRaisesRegex(
            ValueError, "contradicts"
        ):
            run_evaluation(
                {**benchmark, "questions": benchmark["questions"][:1]},
                {
                    "top_k": 1,
                    "generate_answers": True,
                    "answer_provider": "ollama",
                },
                Path(directory) / "result.json",
                embedder=keyword_embeddings,
                tokenizer=token_offsets,
                answer_generator=abstain,
                reviews={"q01": {"label": "supported"}},
            )

    def test_retrieval_miss_can_be_a_correct_abstention(self) -> None:
        benchmark = json.loads(Path("data/benchmark.json").read_text())
        question = benchmark["questions"][18]
        unanswerable = benchmark["questions"][24]

        def abstain(
            _question: str, _evidence: list[dict[str, object]], _model: str
        ) -> dict[str, object]:
            return {
                "answer": "The supplied documents do not contain enough information.",
                "citations": [],
                "abstained": True,
                "input_tokens": 10,
                "output_tokens": 5,
            }

        with tempfile.TemporaryDirectory() as directory:
            result = run_evaluation(
                {**benchmark, "questions": [question, unanswerable]},
                {
                    "top_k": 1,
                    "generate_answers": True,
                    "answer_provider": "ollama",
                },
                Path(directory) / "result.json",
                embedder=lambda texts: [[0.0] for _ in texts],
                tokenizer=token_offsets,
                answer_generator=abstain,
                reviews={
                    question["question_id"]: {"label": "correct_abstention"},
                    unanswerable["question_id"]: {"label": "correct_abstention"},
                },
            )

        self.assertFalse(result["questions"][0]["retrieval_hit"])
        self.assertEqual(result["questions"][0]["review_label"], "correct_abstention")

    def test_paid_generation_requires_explicit_permission(self) -> None:
        benchmark = json.loads(Path("data/benchmark.json").read_text())

        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "result.json"
            with self.assertRaisesRegex(PermissionError, "allow_paid_calls"):
                run_evaluation(
                    benchmark,
                    {"top_k": 1, "generate_answers": True},
                    output,
                    embedder=keyword_embeddings,
                    tokenizer=token_offsets,
                )
            self.assertFalse(output.exists())

    def test_paid_answers_are_checkpointed_and_resumed(self) -> None:
        benchmark = json.loads(Path("data/benchmark.json").read_text())
        configuration = {
            "top_k": 1,
            "generate_answers": True,
            "answer_model": "deterministic-answer-model",
            "price_snapshot": {
                "date": "2026-08-11",
                "currency": "USD",
                "input_usd_per_million_tokens": 0.2,
                "output_usd_per_million_tokens": 1.2,
            },
        }
        first_run_calls: list[str] = []

        def fail_third_question(
            question: str, evidence: list[dict[str, object]], _model: str
        ) -> dict[str, object]:
            first_run_calls.append(question)
            if len(first_run_calls) == 3:
                raise RuntimeError("provider failed")
            return {
                "answer": "Up to five unused PTO days [pto.carryover].",
                "citations": [evidence[0]["section_id"]],
                "abstained": False,
                "input_tokens": 10,
                "output_tokens": 5,
            }

        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "result.json"
            with self.assertRaisesRegex(RuntimeError, "provider failed"):
                run_evaluation(
                    benchmark,
                    configuration,
                    output,
                    embedder=keyword_embeddings,
                    tokenizer=token_offsets,
                    answer_generator=fail_third_question,
                    allow_paid_calls=True,
                )

            checkpoint = json.loads(output.read_text())
            self.assertEqual(checkpoint["status"], "in_progress")
            self.assertEqual(len(checkpoint["questions"]), 2)
            checkpointed_question = checkpoint["questions"][0]
            self.assertEqual(checkpointed_question["citations"], ["pto.carryover"])
            self.assertFalse(checkpointed_question["abstained"])
            self.assertEqual(checkpointed_question["input_tokens"], 10)
            self.assertEqual(checkpointed_question["output_tokens"], 5)
            self.assertEqual(
                checkpointed_question["answer_model"], "deterministic-answer-model"
            )
            self.assertEqual(checkpoint["pricing"], configuration["price_snapshot"])

            embedding_calls = 0

            def fail_while_rebuilding(
                texts: list[str],
            ) -> list[list[float]]:
                nonlocal embedding_calls
                embedding_calls += 1
                if embedding_calls == 3:
                    raise RuntimeError("retrieval failed")
                return keyword_embeddings(texts)

            with self.assertRaisesRegex(RuntimeError, "retrieval failed"):
                run_evaluation(
                    benchmark,
                    configuration,
                    output,
                    embedder=fail_while_rebuilding,
                    tokenizer=token_offsets,
                    answer_generator=lambda *_: self.fail("paid answer was regenerated"),
                    allow_paid_calls=True,
                )
            self.assertEqual(len(json.loads(output.read_text())["questions"]), 2)

            resume_calls: list[str] = []

            def complete_answer(
                question: str, evidence: list[dict[str, object]], _model: str
            ) -> dict[str, object]:
                resume_calls.append(question)
                return {
                    "answer": f"Grounded answer [{evidence[0]['section_id']}].",
                    "citations": [evidence[0]["section_id"]],
                    "abstained": False,
                    "input_tokens": 10,
                    "output_tokens": 5,
                }

            result = run_evaluation(
                benchmark,
                configuration,
                output,
                embedder=keyword_embeddings,
                tokenizer=token_offsets,
                answer_generator=complete_answer,
                allow_paid_calls=True,
            )

        self.assertFalse(
            {
                benchmark["questions"][0]["question"],
                benchmark["questions"][1]["question"],
            }
            & set(resume_calls)
        )
        self.assertEqual(len(resume_calls), 28)
        self.assertEqual(result["status"], "complete")
        self.assertEqual(result["questions"][0]["estimated_cost_usd"], 0.000008)
        self.assertGreaterEqual(result["questions"][0]["generation_latency_ms"], 0)
        self.assertEqual(result["metrics"]["input_tokens"], 300)
        self.assertEqual(result["metrics"]["output_tokens"], 150)
        self.assertEqual(result["metrics"]["estimated_cost_usd"], 0.00024)

    def test_baseline_retrieval_returns_ranked_source_chunks_and_metrics(self) -> None:
        benchmark = {
            "documents": [
                {
                    "document_id": "pto-policy",
                    "title": "PTO Policy (Synthetic)",
                    "sections": [
                        {
                            "section_id": "pto.carryover",
                            "text": "Employees may carry five unused days into next year.",
                        }
                    ],
                },
                {
                    "document_id": "payroll-guide",
                    "title": "Payroll Guide (Synthetic)",
                    "sections": [
                        {
                            "section_id": "payroll.schedule",
                            "text": "Payroll is issued every other Friday.",
                        }
                    ],
                },
            ],
            "questions": [
                {
                    "question_id": "q01",
                    "question": "How many days can I carry forward?",
                    "category": "paraphrase",
                    "answerable": True,
                    "expected_section": "pto.carryover",
                    "reference_answer": "Five days.",
                    "expected_abstention": False,
                    "reviewer_note": "Tests carryover wording.",
                },
                {
                    "question_id": "q02",
                    "question": "Where is employee parking?",
                    "category": "unanswerable",
                    "answerable": False,
                    "expected_section": None,
                    "reference_answer": None,
                    "expected_abstention": True,
                    "reviewer_note": "Parking is absent.",
                },
            ],
        }
        configuration = {
            "chunk_size": 4,
            "chunk_overlap": 1,
            "top_k": 3,
            "reranking": False,
            "embedding_model": "deterministic-test",
        }

        with tempfile.TemporaryDirectory() as directory:
            result = run_evaluation(
                benchmark,
                configuration,
                Path(directory) / "result.json",
                embedder=keyword_embeddings,
                tokenizer=token_offsets,
            )

        first_question = result["questions"][0]
        evidence = first_question["retrieved_evidence"]
        self.assertEqual(len(evidence), 3)
        self.assertEqual(evidence[0]["section_id"], "pto.carryover")
        self.assertEqual(evidence[0]["document_id"], "pto-policy")
        self.assertEqual(evidence[0]["text"], "Employees may carry five")
        self.assertEqual((evidence[0]["start_char"], evidence[0]["end_char"]), (0, 24))
        self.assertTrue(first_question["retrieval_hit"])
        self.assertGreaterEqual(first_question["retrieval_latency_ms"], 0)
        self.assertEqual(result["metrics"]["retrieval_hit_rate"], 1.0)
        self.assertGreaterEqual(result["metrics"]["average_retrieval_latency_ms"], 0)

        with tempfile.TemporaryDirectory() as directory:
            reranked = run_evaluation(
                benchmark,
                {
                    **configuration,
                    "reranking": True,
                    "candidate_pool_size": 6,
                    "reranker_model": "deterministic-test",
                },
                Path(directory) / "reranked.json",
                embedder=keyword_embeddings,
                tokenizer=token_offsets,
                reranker=prefer_payroll,
            )

        reranked_question = reranked["questions"][0]
        reranked_evidence = reranked_question["retrieved_evidence"]
        self.assertEqual(len(reranked_evidence), 3)
        self.assertEqual(reranked_evidence[0]["section_id"], "payroll.schedule")
        self.assertGreater(reranked_evidence[0]["original_rank"], 1)
        self.assertEqual(reranked_evidence[0]["reranked_position"], 1)
        self.assertGreaterEqual(reranked_question["reranking_latency_ms"], 0)
        self.assertGreaterEqual(reranked["metrics"]["average_reranking_latency_ms"], 0)

        with tempfile.TemporaryDirectory() as directory:
            top_five = run_evaluation(
                benchmark,
                {**configuration, "top_k": 5},
                Path(directory) / "top-five.json",
                embedder=keyword_embeddings,
                tokenizer=token_offsets,
            )

        self.assertTrue(
            all(
                len(question["retrieved_evidence"]) == 5
                for question in top_five["questions"]
            )
        )
        self.assertEqual(top_five["metrics"]["retrieval_hit_rate"], 1.0)

        with tempfile.TemporaryDirectory() as directory:
            large_chunks = run_evaluation(
                benchmark,
                {**configuration, "chunk_size": 20},
                Path(directory) / "large.json",
                embedder=keyword_embeddings,
                tokenizer=token_offsets,
            )

        self.assertGreater(
            result["benchmark_summary"]["chunk_count"],
            large_chunks["benchmark_summary"]["chunk_count"],
        )
        self.assertEqual(
            large_chunks["questions"][0]["retrieved_evidence"][0]["section_id"],
            "pto.carryover",
        )

    def test_invalid_benchmark_explains_what_is_wrong(self) -> None:
        benchmark = json.loads(Path("data/benchmark.json").read_text())

        duplicate_document = deepcopy(benchmark)
        duplicate_document["documents"].append(deepcopy(benchmark["documents"][0]))

        unknown_section = deepcopy(benchmark)
        unknown_section["questions"][0]["expected_section"] = "missing.section"

        incomplete_question = deepcopy(benchmark)
        del incomplete_question["questions"][0]["reviewer_note"]

        inconsistent_question = deepcopy(benchmark)
        inconsistent_question["questions"][0]["reference_answer"] = None

        cases = [
            (duplicate_document, "Duplicate document_id: pto-policy"),
            (
                unknown_section,
                "Question q01 references unknown section_id: missing.section",
            ),
            (incomplete_question, "Question q01 is missing: reviewer_note"),
            (
                inconsistent_question,
                "Answerable question q01 requires a reference answer and cannot abstain",
            ),
        ]

        for invalid_benchmark, message in cases:
            with self.subTest(message=message), tempfile.TemporaryDirectory() as directory:
                with self.assertRaisesRegex(ValueError, message):
                    run_evaluation(
                        invalid_benchmark,
                        {"top_k": 1},
                        Path(directory) / "result.json",
                    )

    def test_complete_policy_benchmark_is_visible_in_the_result(self) -> None:
        benchmark = json.loads(Path("data/benchmark.json").read_text())

        with tempfile.TemporaryDirectory() as directory:
            result = run_evaluation(
                benchmark,
                {"top_k": 1},
                Path(directory) / "result.json",
                embedder=keyword_embeddings,
                tokenizer=token_offsets,
            )

        self.assertEqual(
            result["benchmark_summary"],
            {
                "document_count": 5,
                "section_count": 15,
                "chunk_count": 19,
                "question_count": 30,
                "answerable_count": 24,
                "unanswerable_count": 6,
                "category_counts": {
                    "direct": 12,
                    "paraphrase": 6,
                    "similar_policy": 6,
                    "unanswerable": 6,
                },
            },
        )
        self.assertEqual(len(result["questions"]), 30)

    def test_tiny_benchmark_can_be_evaluated_and_reopened(self) -> None:
        benchmark = {
            "documents": [
                {
                    "document_id": "pto-policy",
                    "title": "Paid Time Off Policy (Synthetic)",
                    "sections": [
                        {
                            "section_id": "pto.carryover",
                            "text": "Employees may carry over five PTO days.",
                        }
                    ],
                }
            ],
            "questions": [
                {
                    "question_id": "q01",
                    "question": "How many PTO days can employees carry over?",
                    "category": "direct",
                    "answerable": True,
                    "expected_section": "pto.carryover",
                    "reference_answer": "Five days.",
                    "expected_abstention": False,
                    "reviewer_note": "Direct lookup.",
                }
            ],
        }
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "result.json"

            result = run_evaluation(
                benchmark,
                {"top_k": 1},
                output,
                embedder=keyword_embeddings,
                tokenizer=token_offsets,
            )

            self.assertEqual(
                result["configuration"],
                {
                    "chunk_size": 30,
                    "chunk_overlap": 5,
                    "top_k": 1,
                    "reranking": False,
                    "candidate_pool_size": 10,
                    "embedding_model": "Alibaba-NLP/gte-modernbert-base",
                    "reranker_model": "cross-encoder/ms-marco-MiniLM-L6-v2",
                },
            )
            self.assertNotIn("pricing", result)
            self.assertNotIn("answer", result["questions"][0])
            self.assertNotIn("estimated_cost_usd", result["metrics"])
            self.assertTrue(result["questions"][0]["retrieval_hit"])
            self.assertEqual(
                result["questions"][0]["retrieved_evidence"][0]["section_id"],
                "pto.carryover",
            )
            self.assertEqual(json.loads(output.read_text()), result)


if __name__ == "__main__":
    unittest.main()
