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

## Check

```bash
python3 -m unittest discover -s tests
```
