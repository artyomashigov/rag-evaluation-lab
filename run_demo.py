import json
from pathlib import Path

from rag_lab import run_evaluation


if __name__ == "__main__":
    benchmark = json.loads(Path("data/benchmark.json").read_text())
    baseline = {
        "chunk_overlap": 5,
        "top_k": 3,
        "reranking": False,
        "embedding_model": "Alibaba-NLP/gte-modernbert-base",
    }
    outputs = {
        15: Path("results/chunk-15.json"),
        30: Path("results/baseline.json"),
        60: Path("results/chunk-60.json"),
    }
    for chunk_size, output in outputs.items():
        run_evaluation(benchmark, {**baseline, "chunk_size": chunk_size}, output)
    run_evaluation(
        benchmark,
        {**baseline, "chunk_size": 30, "top_k": 5},
        Path("results/top-5.json"),
    )
    run_evaluation(
        benchmark,
        {**baseline, "chunk_size": 30, "reranking": True},
        Path("results/reranked.json"),
    )
    print("Saved five controlled retrieval configurations")
