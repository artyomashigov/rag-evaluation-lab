# RAG Evaluation Lab

A minimal offline tracer for evaluating whether retrieval finds the expected policy section.

## Run locally

```bash
python3 -m pip install -r requirements.txt
python3 run_demo.py
streamlit run app.py
```

## Check

```bash
python3 -m unittest discover -s tests
```
