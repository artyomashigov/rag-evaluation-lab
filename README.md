# RAG Evaluation Lab

[![Tests](https://github.com/artyomashigov/rag-evaluation-lab/actions/workflows/tests.yml/badge.svg)](https://github.com/artyomashigov/rag-evaluation-lab/actions/workflows/tests.yml)
[![Open the live demo](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://rag-evaluation-lab.streamlit.app/)

An offline experiment that measures why retrieval-augmented generation (RAG) answers fail. It compares five controlled retrieval configurations over 30 questions and makes every answer, citation, retrieved passage, and manual review available for inspection.

**[Open the public dashboard](https://rag-evaluation-lab.streamlit.app/)** — no account or API key required.

## Problem

A RAG demo can look convincing while still retrieving the wrong evidence or making unsupported claims. This project evaluates those failures instead of presenting another chatbot. It asks how chunk size, top-k retrieval, and reranking change retrieval coverage, unsupported-answer rate, latency, and cost.

## Results

Smaller 15-token chunks produced the lowest unsupported-answer rate in this experiment: **23.3%**, versus **43.3%** for the baseline. Reranking and top-5 retrieval reached 100% retrieval coverage, but they did not produce the most reliable answers. High retrieval hit rate alone was therefore not enough to guarantee a supported answer.

| Configuration | Retrieval hit | Unsupported answers | Average latency | API cost |
| --- | ---: | ---: | ---: | ---: |
| Baseline: 30-token chunks, top-3 | 95.8% | 43.3% | 1,302 ms | $0 |
| Small chunks: 15 tokens | 95.8% | **23.3%** | 1,880 ms | $0 |
| Large chunks: 60 tokens | 95.8% | 53.3% | 1,285 ms | $0 |
| More evidence: top-5 | 100.0% | 53.3% | 1,428 ms | $0 |
| Reranking | 100.0% | 60.0% | 1,251 ms | $0 |

The dashboard remains useful if hosting is unavailable: the table above captures the main result, and the committed JSON files under `results/` contain all 150 reviewed answers.

## Controlled methodology

- Five fictional employee-policy documents provide safe, known ground truth.
- Thirty fixed questions include direct, paraphrased, distinction, and deliberately unanswerable cases.
- Five configurations change one setting at a time from a 30-token, top-3, no-reranking baseline.
- The same local embedding, reranking, and Qwen 2.5 3B answer models are used throughout.
- A retrieval hit means the returned evidence contains the question's expected source section.
- Every generated answer is manually labeled `supported`, `unsupported`, or `correct_abstention`.
- Saved timings describe the benchmark machine; the dashboard performs no live inference.

## Architecture

```text
Synthetic documents + 30 labeled questions
                  │
                  ▼
     Five controlled RAG configurations
       chunk → embed → retrieve → rerank?
                  │
                  ▼
       Local Qwen answers + manual review
                  │
                  ▼
        Committed JSON result artifacts
                  │
                  ▼
        Read-only Streamlit dashboard
```

`rag_lab.py` owns the evaluation pipeline. `run_demo.py` runs the five experiments and writes ordinary JSON. `app.py` only validates and displays the committed answer artifacts, so the hosted app needs no database, model account, API key, or network call.

## Open the cached dashboard locally

Python 3.12 is recommended.

```bash
git clone https://github.com/artyomashigov/rag-evaluation-lab.git
cd rag-evaluation-lab
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m unittest discover -s tests
streamlit run app.py
```

Open the local URL printed by Streamlit. This path uses the committed results and does not download models or require credentials.

## Reproduce the benchmark

Install the optional model dependencies, then run retrieval locally:

```bash
python -m pip install -r requirements-benchmark.txt
python run_demo.py
```

The first run downloads the embedding and reranking models. To regenerate answers for free, install [Ollama](https://ollama.com/), then run:

```bash
ollama pull qwen2.5:3b
python run_demo.py --local-answers
```

Paid OpenAI answer generation is off by default and requires both a local `OPENAI_API_KEY` and the explicit command `python run_demo.py --allow-paid-calls`. Never commit a key.

## Limitations

The conclusions apply to this small synthetic corpus, these 30 questions, the selected models, and one manual reviewer. They do not establish that 15-token chunks are best for other datasets. Latency depends on the benchmark machine, manual labels can contain judgment errors, and this version does not compare answer models or run statistical significance tests.

## Cost protection

Public visitors only read committed JSON, so browsing the app costs **$0 in model/API usage**. The deployment contains no secrets and cannot make model calls. Free hosting may sleep when inactive; the results above and all source artifacts remain available in GitHub.
