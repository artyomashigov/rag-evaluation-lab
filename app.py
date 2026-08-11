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

question_id = st.selectbox(
    "Question",
    questions,
    format_func=lambda identifier: questions[identifier]["question"],
)
question = questions[question_id]
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
