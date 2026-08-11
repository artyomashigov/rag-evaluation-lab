# RAG Evaluation Lab

An offline RAG benchmark over five synthetic employee-policy documents and 30 labeled questions.

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
