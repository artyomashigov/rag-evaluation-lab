import json
from pathlib import Path

import streamlit as st


st.set_page_config(page_title="RAG Evaluation Lab", page_icon="🔎")
st.title("RAG Evaluation Lab")
st.caption("An offline benchmark over clearly fictional employee policies.")

result_path = Path("results/baseline.json")
if not result_path.exists():
    st.error("No saved result found. Run `python3 run_demo.py` first.")
    st.stop()

result = json.loads(result_path.read_text())
configuration = result["configuration"]
summary = result["benchmark_summary"]
metrics = result["metrics"]
questions = {question["question_id"]: question for question in result["questions"]}
answered_paths = {
    name: Path(f"results/answered-{name}.json")
    for name in ("baseline", "chunk-15", "chunk-60", "top-5", "reranked")
}
answered_results = {
    name: json.loads(path.read_text())
    for name, path in answered_paths.items()
    if path.exists()
}

columns = st.columns(4)
columns[0].metric("Documents", summary["document_count"])
columns[1].metric("Sections", summary["section_count"])
columns[2].metric("Questions", summary["question_count"])
columns[3].metric("Unanswerable", summary["unanswerable_count"])

metric_columns = st.columns(2)
metric_columns[0].metric("Retrieval hit rate", f"{metrics['retrieval_hit_rate']:.0%}")
metric_columns[1].metric(
    "Average retrieval latency", f"{metrics['average_retrieval_latency_ms']:.1f} ms"
)
st.caption(
    f"Recorded locally with {configuration['chunk_size']}-token chunks, "
    f"{configuration['chunk_overlap']}-token overlap, "
    f"top-{configuration['top_k']}, and "
    f"reranking {'on' if configuration['reranking'] else 'off'}."
)

if len(answered_results) == 5:
    lowest_unsupported = min(
        answered_results,
        key=lambda name: answered_results[name]["metrics"]["unsupported_answer_rate"],
    )
    st.subheader("Audited answer comparison")
    st.dataframe(
        [
            {
                "Configuration": name,
                "Retrieval hit rate": item["metrics"]["retrieval_hit_rate"],
                "Unsupported-answer rate": item["metrics"][
                    "unsupported_answer_rate"
                ],
                "Correct-abstention rate": item["metrics"][
                    "correct_abstention_rate"
                ],
                "Total latency (ms)": item["metrics"]["average_total_latency_ms"],
                "Tokens": item["metrics"]["input_tokens"]
                + item["metrics"]["output_tokens"],
                "Cost (USD)": item["metrics"]["estimated_cost_usd"],
            }
            for name, item in answered_results.items()
        ],
        hide_index=True,
    )
    st.caption(
        f"All 150 answers were generated locally and manually reviewed. "
        f"{lowest_unsupported} had the lowest unsupported-answer rate here; this result "
        "applies only to this synthetic corpus, question set, and Qwen 2.5 3B."
    )

comparison_paths = [
    Path("results/chunk-15.json"),
    result_path,
    Path("results/chunk-60.json"),
]
if all(path.exists() for path in comparison_paths):
    comparisons = [json.loads(path.read_text()) for path in comparison_paths]
    small, _, large = comparisons
    st.subheader("Chunk-size comparison")
    st.dataframe(
        [
            {
                "Chunk size": item["configuration"]["chunk_size"],
                "Chunks": item["benchmark_summary"]["chunk_count"],
                "Hit rate": item["metrics"]["retrieval_hit_rate"],
                "Latency (ms)": item["metrics"]["average_retrieval_latency_ms"],
            }
            for item in comparisons
        ],
        hide_index=True,
    )
    st.caption(
        f"Here, hit rate ranged from "
        f"{min(item['metrics']['retrieval_hit_rate'] for item in comparisons):.0%} to "
        f"{max(item['metrics']['retrieval_hit_rate'] for item in comparisons):.0%}. "
        f"The 15-token run created {small['benchmark_summary']['chunk_count']} chunks, "
        f"versus {large['benchmark_summary']['chunk_count']} with 60-token chunks. "
        "The measured hit rate and latency apply only to this corpus, questions, and machine."
    )

top_five_path = Path("results/top-5.json")
if top_five_path.exists():
    top_k_results = [result, json.loads(top_five_path.read_text())]
    st.subheader("Top-k comparison")
    st.dataframe(
        [
            {
                "Top-k": item["configuration"]["top_k"],
                "Evidence per question": sum(
                    len(question["retrieved_evidence"])
                    for question in item["questions"]
                )
                / len(item["questions"]),
                "Hit rate": item["metrics"]["retrieval_hit_rate"],
                "Latency (ms)": item["metrics"]["average_retrieval_latency_ms"],
            }
            for item in top_k_results
        ],
        hide_index=True,
    )
    st.caption(
        f"Top-5 retrieved two more pieces of evidence per question. Hit rate changed "
        f"from {top_k_results[0]['metrics']['retrieval_hit_rate']:.0%} to "
        f"{top_k_results[1]['metrics']['retrieval_hit_rate']:.0%}; more evidence may "
        "improve coverage, but it also gives the answer stage more text to process."
    )

reranked_path = Path("results/reranked.json")
reranked_result = json.loads(reranked_path.read_text()) if reranked_path.exists() else None
if reranked_result:
    reranking_results = [result, reranked_result]
    additional_hits = round(
        (
            reranked_result["metrics"]["retrieval_hit_rate"]
            - result["metrics"]["retrieval_hit_rate"]
        )
        * summary["answerable_count"]
    )
    st.subheader("Reranking comparison")
    st.dataframe(
        [
            {
                "Reranking": "On" if item["configuration"]["reranking"] else "Off",
                "Hit rate": item["metrics"]["retrieval_hit_rate"],
                "Retrieval (ms)": item["metrics"]["average_retrieval_latency_ms"],
                "Reranking (ms)": item["metrics"]["average_reranking_latency_ms"],
            }
            for item in reranking_results
        ],
        hide_index=True,
    )
    st.caption(
        f"Reranking changed hit rate from "
        f"{result['metrics']['retrieval_hit_rate']:.0%} to "
        f"{reranked_result['metrics']['retrieval_hit_rate']:.0%} and added "
        f"{reranked_result['metrics']['average_reranking_latency_ms']:.1f} ms. "
        f"Here, recovering {additional_hits} missed answerable question makes that extra "
        "step worthwhile when coverage matters more than minimum latency. "
        "That judgment is specific to this small benchmark."
    )

selected_configuration = st.selectbox(
    "Configuration",
    answered_results or {"baseline": result},
)
selected_result = answered_results.get(selected_configuration, result)
review_labels = sorted(
    {item.get("review_label", "unreviewed") for item in selected_result["questions"]}
)
selected_labels = st.multiselect("Review label", review_labels, default=review_labels)
filtered_questions = {
    item["question_id"]: item
    for item in selected_result["questions"]
    if item.get("review_label", "unreviewed") in selected_labels
}
if not filtered_questions:
    st.info("No questions match the selected review labels.")
    st.stop()

question_id = st.selectbox(
    "Question",
    filtered_questions,
    format_func=lambda identifier: filtered_questions[identifier]["question"],
)
question = filtered_questions[question_id]
st.subheader(question["question"])
st.metric("Expected section retrieved", "Yes" if question["retrieval_hit"] else "No")
st.write("Expected section:", question["expected_section"] or "No source expected")

for evidence in question["retrieved_evidence"]:
    st.markdown(f"**{evidence['document_title']} — {evidence['section_id']}**")
    st.caption(
        f"Similarity {evidence['similarity_score']:.3f} · "
        f"characters {evidence['start_char']}–{evidence['end_char']}"
    )
    st.write(evidence["text"])

answered_result = answered_results.get(selected_configuration)
if answered_result:
    answered_question = question
    st.subheader("Saved answer")
    st.write(answered_question["answer"])
    st.write(
        "Citations:",
        ", ".join(answered_question["citations"])
        if answered_question["citations"]
        else "None — model abstained",
    )
    answer_columns = st.columns(3)
    answer_columns[0].metric(
        "Abstained", "Yes" if answered_question["abstained"] else "No"
    )
    answer_columns[1].metric(
        "Generation latency", f"{answered_question['generation_latency_ms']:.1f} ms"
    )
    answer_columns[2].metric(
        "Estimated cost", f"${answered_question['estimated_cost_usd']:.6f}"
    )
    st.caption(
        f"Model {answered_question['answer_model']} · price snapshot "
        f"{answered_result['pricing']['date']} · saved result only; no dashboard API call"
    )
    st.write("Manual review:", answered_question["review_label"])
    if answered_question["answer_review_note"]:
        st.write("Reviewer note:", answered_question["answer_review_note"])

if reranked_result and selected_configuration == "reranked":
    reranked_question = next(
        item for item in reranked_result["questions"] if item["question_id"] == question_id
    )
    st.subheader("Reranked order")
    st.dataframe(
        [
            {
                "Final rank": evidence["reranked_position"],
                "Original rank": evidence["original_rank"],
                "Section": evidence["section_id"],
                "Score": evidence["reranker_score"],
            }
            for evidence in reranked_question["retrieved_evidence"]
        ],
        hide_index=True,
    )
