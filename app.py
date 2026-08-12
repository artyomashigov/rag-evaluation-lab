import json
from pathlib import Path
from typing import Any, Mapping

import streamlit as st


RESULT_PATHS = {
    "Baseline": Path("results/answered-baseline.json"),
    "Small chunks": Path("results/answered-chunk-15.json"),
    "Large chunks": Path("results/answered-chunk-60.json"),
    "More retrieved evidence": Path("results/answered-top-5.json"),
    "Reranking": Path("results/answered-reranked.json"),
}
COMPARISON_METRICS = {
    "Retrieval hit rate": "retrieval_hit_rate",
    "Unsupported-answer rate": "unsupported_answer_rate",
    "Average latency (ms)": "average_total_latency_ms",
    "Estimated cost (USD)": "estimated_cost_usd",
}


class SavedResultError(ValueError):
    pass


def _require_fields(value: Any, fields: set[str], location: str) -> None:
    if not isinstance(value, dict):
        raise SavedResultError(f"{location} must be a JSON object.")
    missing = sorted(fields - value.keys())
    if missing:
        raise SavedResultError(f"{location} is missing: {', '.join(missing)}.")


def _require_types(value: dict[str, Any], types: Mapping[str, Any], location: str) -> None:
    wrong = [name for name, expected in types.items() if not isinstance(value[name], expected)]
    if wrong:
        raise SavedResultError(f"{location} has invalid values for: {', '.join(wrong)}.")


def _validate_result(result: Any, name: str) -> None:
    _require_fields(
        result,
        {"configuration", "benchmark_summary", "metrics", "pricing", "questions"},
        name,
    )
    _require_fields(
        result["configuration"],
        {"chunk_size", "chunk_overlap", "top_k", "reranking"},
        f"{name} configuration",
    )
    _require_types(
        result["configuration"],
        {"chunk_size": int, "chunk_overlap": int, "top_k": int, "reranking": bool},
        f"{name} configuration",
    )
    _require_fields(result["pricing"], {"date"}, f"{name} pricing")
    _require_types(result["pricing"], {"date": str}, f"{name} pricing")
    _require_fields(
        result["benchmark_summary"],
        {"document_count", "section_count", "question_count", "unanswerable_count"},
        f"{name} benchmark summary",
    )
    _require_types(
        result["benchmark_summary"],
        {
            "document_count": int,
            "section_count": int,
            "question_count": int,
            "unanswerable_count": int,
        },
        f"{name} benchmark summary",
    )
    _require_fields(
        result["metrics"],
        {
            "retrieval_hit_rate",
            "unsupported_answer_rate",
            "correct_abstention_rate",
            "average_total_latency_ms",
            "estimated_cost_usd",
        },
        f"{name} metrics",
    )
    _require_types(
        result["metrics"],
        {
            "retrieval_hit_rate": (int, float),
            "unsupported_answer_rate": (int, float),
            "correct_abstention_rate": (int, float),
            "average_total_latency_ms": (int, float),
            "estimated_cost_usd": (int, float),
        },
        f"{name} metrics",
    )
    if not isinstance(result["questions"], list) or not result["questions"]:
        raise SavedResultError(f"{name} questions must be a non-empty JSON list.")
    for index, question in enumerate(result["questions"], 1):
        location = f"{name} question {index}"
        _require_fields(
            question,
            {
                "question_id",
                "question",
                "expected_section",
                "retrieval_hit",
                "retrieved_evidence",
                "answer",
                "citations",
                "abstained",
                "generation_latency_ms",
                "estimated_cost_usd",
                "answer_model",
                "review_label",
            },
            location,
        )
        _require_types(
            question,
            {
                "question_id": str,
                "question": str,
                "retrieval_hit": bool,
                "retrieved_evidence": list,
                "answer": str,
                "citations": list,
                "abstained": bool,
                "generation_latency_ms": (int, float),
                "estimated_cost_usd": (int, float),
                "answer_model": str,
                "review_label": str,
            },
            location,
        )
        if question["expected_section"] is not None and not isinstance(
            question["expected_section"], str
        ):
            raise SavedResultError(f"{location} has invalid expected_section.")
        if not all(isinstance(citation, str) for citation in question["citations"]):
            raise SavedResultError(f"{location} citations must contain strings.")
        for rank, evidence in enumerate(question["retrieved_evidence"], 1):
            _require_fields(
                evidence,
                {"document_title", "section_id", "similarity_score", "text"},
                f"{location} evidence {rank}",
            )
            _require_types(
                evidence,
                {
                    "document_title": str,
                    "section_id": str,
                    "similarity_score": (int, float),
                    "text": str,
                },
                f"{location} evidence {rank}",
            )


def load_saved_results(paths: Mapping[str, Path]) -> dict[str, dict[str, Any]]:
    missing = [name for name, path in paths.items() if not path.exists()]
    if missing:
        raise SavedResultError(
            f"Missing saved results for {', '.join(missing)}. "
            "Run `python run_demo.py --local-answers` first."
        )

    results = {}
    for name, path in paths.items():
        try:
            result = json.loads(path.read_text())
        except json.JSONDecodeError as error:
            raise SavedResultError(f"{path} is not valid JSON: {error.msg}.") from error
        except OSError as error:
            raise SavedResultError(f"Could not read {path}: {error}.") from error
        _validate_result(result, str(path))
        results[name] = result
    return results


def _comparison_rows(results: Mapping[str, dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "Configuration": name,
            **{
                label: item["metrics"][metric]
                for label, metric in COMPARISON_METRICS.items()
            },
        }
        for name, item in results.items()
    ]


def _configuration_description(result: dict[str, Any]) -> str:
    config = result["configuration"]
    return (
        f"{config['chunk_size']}-token chunks, {config['chunk_overlap']}-token overlap, "
        f"top-{config['top_k']} retrieval, "
        f"reranking {'on' if config['reranking'] else 'off'}"
    )


def main() -> None:
    st.set_page_config(page_title="RAG Evaluation Lab", page_icon="🔎", layout="wide")
    st.title("RAG Evaluation Lab")
    st.write(
        "Retrieval-augmented generation (RAG) first finds relevant source passages, "
        "then asks a language model to answer from that evidence. This lab tests how "
        "five retrieval choices affect answer quality, speed, and cost."
    )
    st.caption("Offline portfolio demo · saved results only · no API or model calls")

    try:
        results = load_saved_results(RESULT_PATHS)
    except SavedResultError as error:
        st.error(f"The dashboard could not load its saved results. {error}")
        st.stop()

    baseline = results["Baseline"]
    strongest_name = min(
        results,
        key=lambda name: results[name]["metrics"]["unsupported_answer_rate"],
    )
    strongest = results[strongest_name]
    overview, comparison, explorer = st.tabs(
        ["1 · What I found", "2 · Compare configurations", "3 · Inspect evidence"]
    )

    with overview:
        st.header("The result in one minute")
        st.success(
            f"Strongest finding: {strongest_name} had the lowest unsupported-answer "
            f"rate at {strongest['metrics']['unsupported_answer_rate']:.1%}, compared "
            f"with {baseline['metrics']['unsupported_answer_rate']:.1%} for the baseline."
        )
        columns = st.columns(4)
        columns[0].metric(
            "Baseline retrieval hit rate",
            f"{baseline['metrics']['retrieval_hit_rate']:.1%}",
        )
        columns[1].metric(
            "Baseline unsupported answers",
            f"{baseline['metrics']['unsupported_answer_rate']:.1%}",
        )
        columns[2].metric(
            "Baseline average latency",
            f"{baseline['metrics']['average_total_latency_ms']:.0f} ms",
        )
        columns[3].metric(
            "Baseline estimated cost",
            f"${baseline['metrics']['estimated_cost_usd']:.2f}",
        )
        st.caption(f"Baseline: {_configuration_description(baseline)}.")

        st.subheader("What this means")
        st.write(
            "Retrieval coverage was high in every run, but high retrieval hit rate did "
            "not guarantee a supported answer. In this experiment, smaller chunks gave "
            "the local answer model more focused evidence and produced the fewest "
            "unsupported answers. Reranking recovered a retrieval miss, but its answers "
            "were less reliable, so adding a retrieval stage was not automatically better."
        )

        with st.expander("Methodology and limitations"):
            summary = baseline["benchmark_summary"]
            st.write(
                f"I evaluated {summary['question_count']} labeled questions over "
                f"{summary['document_count']} fictional policy documents. Each run changed "
                "one retrieval setting. Answers came from local Qwen 2.5 3B and all 150 "
                "answers were manually labeled as supported, unsupported, or a correct "
                "abstention."
            )
            st.warning(
                "These conclusions apply only to this synthetic corpus, benchmark, "
                "embedding and reranking models, local answer model, and manual review. "
                "Latency reflects the machine used for the recorded run, not hosting speed."
            )

    with comparison:
        st.header("Compare the five configurations")
        rows = _comparison_rows(results)
        st.dataframe(rows, hide_index=True, width="stretch")

        selected_metric = st.selectbox(
            "Chart metric",
            COMPARISON_METRICS,
            help="Choose one outcome to compare across retrieval configurations.",
        )
        st.bar_chart(rows, x="Configuration", y=selected_metric)

        metric_key = COMPARISON_METRICS[selected_metric]
        lowest = min(results, key=lambda name: results[name]["metrics"][metric_key])
        highest = max(results, key=lambda name: results[name]["metrics"][metric_key])
        suffix = "%" if "rate" in metric_key else " ms" if "latency" in metric_key else " USD"
        scale = 100 if suffix == "%" else 1
        st.caption(
            f"Chart summary: {lowest} recorded the lowest {selected_metric.lower()} "
            f"({results[lowest]['metrics'][metric_key] * scale:.2f}{suffix}); {highest} "
            f"recorded the highest ({results[highest]['metrics'][metric_key] * scale:.2f}{suffix})."
        )
        st.info(
            "All cost estimates are $0 because the saved answers were generated with a "
            "local model. Latency is recorded experiment time, not live dashboard latency."
        )

    with explorer:
        st.header("Inspect one answer and its evidence")
        selected_name = st.selectbox(
            "Retrieval configuration",
            results,
            help="Each option changes one retrieval choice from the baseline.",
        )
        selected_result = results[selected_name]
        st.caption(_configuration_description(selected_result))
        questions = {
            question["question_id"]: question for question in selected_result["questions"]
        }
        question_id = st.selectbox(
            "Benchmark question",
            questions,
            format_func=lambda identifier: f"{identifier}: {questions[identifier]['question']}",
        )
        question = questions[question_id]

        st.subheader(question["question"])
        status_columns = st.columns(3)
        status_columns[0].metric(
            "Expected section retrieved", "Yes" if question["retrieval_hit"] else "No"
        )
        status_columns[1].metric("Manual review", question["review_label"].replace("_", " ").title())
        status_columns[2].metric("Abstained", "Yes" if question["abstained"] else "No")
        st.write("Expected section:", question["expected_section"] or "No answer exists in the corpus")

        st.subheader("Retrieved evidence and ranking changes")
        rank_rows = []
        for rank, evidence in enumerate(question["retrieved_evidence"], 1):
            rank_rows.append(
                {
                    "Final rank": evidence.get("reranked_position") or rank,
                    "Initial rank": evidence.get("original_rank") or rank,
                    "Section": evidence["section_id"],
                    "Similarity": evidence["similarity_score"],
                }
            )
        st.dataframe(rank_rows, hide_index=True, width="stretch")
        for rank, evidence in enumerate(question["retrieved_evidence"], 1):
            with st.expander(
                f"Rank {rank}: {evidence['document_title']} — {evidence['section_id']}"
            ):
                st.write(evidence["text"])

        st.subheader("Saved answer")
        st.write(question["answer"])
        st.write("Citations:", ", ".join(question["citations"]) or "None")
        st.write("Reviewer note:", question.get("answer_review_note") or "No additional note")
        st.caption(
            f"{question['answer_model']} · {question['generation_latency_ms']:.0f} ms generation "
            f"· ${question['estimated_cost_usd']:.6f} estimated cost · pricing snapshot "
            f"{selected_result['pricing']['date']}"
        )


if __name__ == "__main__":
    main()
