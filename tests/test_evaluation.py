import json
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path

from rag_lab import run_evaluation


class EvaluationRunnerTest(unittest.TestCase):
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
            )

        self.assertEqual(
            result["benchmark_summary"],
            {
                "document_count": 5,
                "section_count": 15,
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
        expected = {
            "configuration": {"top_k": 1},
            "benchmark_summary": {
                "document_count": 1,
                "section_count": 1,
                "question_count": 1,
                "answerable_count": 1,
                "unanswerable_count": 0,
                "category_counts": {"direct": 1},
            },
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
                    "retrieved_evidence": [
                        {
                            "section_id": "pto.carryover",
                            "text": "Employees may carry over five PTO days.",
                            "document_id": "pto-policy",
                            "document_title": "Paid Time Off Policy (Synthetic)",
                        }
                    ],
                    "retrieval_hit": True,
                }
            ],
        }

        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "result.json"

            result = run_evaluation(benchmark, {"top_k": 1}, output)

            self.assertEqual(result, expected)
            self.assertEqual(json.loads(output.read_text()), expected)


if __name__ == "__main__":
    unittest.main()
