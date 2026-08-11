import argparse
import json
from pathlib import Path

from rag_lab import run_evaluation


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--allow-paid-calls",
        action="store_true",
        help="Generate answers with the configured paid model and checkpoint each one.",
    )
    arguments = parser.parse_args()
    benchmark = json.loads(Path("data/benchmark.json").read_text())
    baseline = {
        "chunk_overlap": 5,
        "top_k": 3,
        "reranking": False,
        "embedding_model": "Alibaba-NLP/gte-modernbert-base",
    }
    experiments = [
        ({**baseline, "chunk_size": 15}, Path("results/chunk-15.json")),
        ({**baseline, "chunk_size": 30}, Path("results/baseline.json")),
        ({**baseline, "chunk_size": 60}, Path("results/chunk-60.json")),
        (
            {**baseline, "chunk_size": 30, "top_k": 5},
            Path("results/top-5.json"),
        ),
        (
            {**baseline, "chunk_size": 30, "reranking": True},
            Path("results/reranked.json"),
        ),
    ]
    if arguments.allow_paid_calls:
        print("Paid model calls enabled; each completed answer will be checkpointed.")
    for configuration, output in experiments:
        if arguments.allow_paid_calls:
            configuration = {**configuration, "generate_answers": True}
            output = output.with_name(f"answered-{output.name}")
        run_evaluation(
            benchmark,
            configuration,
            output,
            allow_paid_calls=arguments.allow_paid_calls,
        )
    print("Saved five controlled evaluation configurations")
