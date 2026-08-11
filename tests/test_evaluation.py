import json
import tempfile
import unittest
from pathlib import Path

from rag_lab import run_evaluation


class EvaluationRunnerTest(unittest.TestCase):
    def test_tiny_benchmark_can_be_evaluated_and_reopened(self) -> None:
        benchmark = {
            "sections": [
                {
                    "section_id": "pto.carryover",
                    "text": "Employees may carry over five PTO days.",
                }
            ],
            "questions": [
                {
                    "question": "How many PTO days can employees carry over?",
                    "expected_section": "pto.carryover",
                }
            ],
        }
        expected = {
            "configuration": {"top_k": 1},
            "questions": [
                {
                    "question": "How many PTO days can employees carry over?",
                    "expected_section": "pto.carryover",
                    "retrieved_evidence": [
                        {
                            "section_id": "pto.carryover",
                            "text": "Employees may carry over five PTO days.",
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
