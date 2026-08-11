import json
import re
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path

from rag_lab import run_evaluation


def keyword_embeddings(texts: list[str]) -> list[list[float]]:
    vocabulary = ("carry", "payroll", "parking")
    return [
        [float(word in text.lower()) for word in vocabulary]
        for text in texts
    ]


def token_offsets(text: str) -> list[tuple[int, int]]:
    return [(match.start(), match.end()) for match in re.finditer(r"\w+|[^\w\s]", text)]


class EvaluationRunnerTest(unittest.TestCase):
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
                    "embedding_model": "Alibaba-NLP/gte-modernbert-base",
                },
            )
            self.assertTrue(result["questions"][0]["retrieval_hit"])
            self.assertEqual(
                result["questions"][0]["retrieved_evidence"][0]["section_id"],
                "pto.carryover",
            )
            self.assertEqual(json.loads(output.read_text()), result)


if __name__ == "__main__":
    unittest.main()
