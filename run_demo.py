import json
from pathlib import Path

from rag_lab import run_evaluation


if __name__ == "__main__":
    benchmark = json.loads(Path("data/benchmark.json").read_text())
    result = run_evaluation(benchmark, {"top_k": 1}, Path("results/baseline.json"))
    print(f"Saved {result['benchmark_summary']['question_count']} question results")
