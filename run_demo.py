import json
from pathlib import Path

from rag_lab import run_evaluation


if __name__ == "__main__":
    benchmark = json.loads(Path("data/benchmark.json").read_text())
    configuration = {
        "chunk_size": 700,
        "chunk_overlap": 70,
        "top_k": 3,
        "reranking": False,
        "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
    }
    result = run_evaluation(benchmark, configuration, Path("results/baseline.json"))
    print(f"Saved {result['benchmark_summary']['question_count']} question results")
