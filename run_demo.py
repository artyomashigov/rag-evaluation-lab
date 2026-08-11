from pathlib import Path

from rag_lab import run_evaluation


BENCHMARK = {
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


if __name__ == "__main__":
    run_evaluation(BENCHMARK, {"top_k": 1}, Path("results/baseline.json"))
    print("Saved results/baseline.json")
