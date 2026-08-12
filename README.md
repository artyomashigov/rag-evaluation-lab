# RAG Evaluation Lab

An offline RAG benchmark over five synthetic employee-policy documents and 30 labeled questions.

## Run locally

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python run_demo.py
streamlit run app.py
```

The first benchmark run downloads the embedding and reranking models. Later runs are local; the Streamlit app only reads the saved experiment results.

Answer generation is disabled by default. To explicitly permit paid model calls, set `OPENAI_API_KEY` locally and run:

```bash
python run_demo.py --allow-paid-calls
```

For a free local run, install Ollama and use the 1.9 GB Qwen 2.5 model:

```bash
ollama pull qwen2.5:3b
python run_demo.py --local-answers
```

Paid runs write separate `results/answered-*.json` checkpoints, so rerunning the free retrieval benchmark cannot erase completed paid work. The dashboard reads those files when present and never calls the API itself.

The committed answer artifacts use local Qwen 2.5 3B, so their estimated API cost is $0. Every answer has a manual support label in `data/reviews.json`; the dashboard exposes those labels, notes, cited evidence, stage latency, and token counts.

## Check

```bash
python3 -m unittest discover -s tests
```
