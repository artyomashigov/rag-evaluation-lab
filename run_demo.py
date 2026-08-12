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
    parser.add_argument(
        "--local-answers",
        action="store_true",
        help="Generate free local answers with Ollama and qwen2.5:3b.",
    )
    arguments = parser.parse_args()
    benchmark = json.loads(Path("data/benchmark.json").read_text())
    reviews = json.loads(Path("data/reviews.json").read_text())
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
    if arguments.local_answers:
        print("Free local answers enabled; each completed answer will be checkpointed.")
    for configuration, output in experiments:
        if arguments.allow_paid_calls or arguments.local_answers:
            configuration = {**configuration, "generate_answers": True}
            output = output.with_name(f"answered-{output.name}")
        if arguments.local_answers:
            configuration.update(
                {
                    "answer_provider": "ollama",
                    "answer_model": "qwen2.5:3b",
                    "price_snapshot": {
                        "date": "2026-08-11",
                        "currency": "USD",
                        "input_usd_per_million_tokens": 0,
                        "output_usd_per_million_tokens": 0,
                    },
                }
            )
        run_evaluation(
            benchmark,
            configuration,
            output,
            reviews=reviews.get(output.stem.removeprefix("answered-"))
            if arguments.local_answers
            else None,
            allow_paid_calls=arguments.allow_paid_calls,
        )
    print("Saved five controlled evaluation configurations")
