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
summary = result["benchmark_summary"]
question = result["questions"][0]

columns = st.columns(4)
columns[0].metric("Documents", summary["document_count"])
columns[1].metric("Sections", summary["section_count"])
columns[2].metric("Questions", summary["question_count"])
columns[3].metric("Unanswerable", summary["unanswerable_count"])

st.subheader(question["question"])
st.metric("Expected section retrieved", "Yes" if question["retrieval_hit"] else "No")
st.write("Expected section:", question["expected_section"])

for evidence in question["retrieved_evidence"]:
    st.markdown(f"**{evidence['section_id']}**")
    st.write(evidence["text"])
