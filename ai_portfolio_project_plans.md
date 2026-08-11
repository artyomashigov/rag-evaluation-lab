# AI / LLM Portfolio Project Plans

## Goal

Build a portfolio that is:

- cheap or free to run
- safe to build without company data or systems
- easy for recruiters and hiring managers to view
- strong for AI engineering, data analyst, analytics engineer, and BI-related roles
- realistic to finish in small steps

The main rule:

> Public app = cached and free.  
> Local app = fully live with API key.

Do not expose your paid API key in a public demo. Recruiters should be able to click and explore a demo without causing API costs.

---

# Overall Ranking With Cost Included

| Rank | Project | Best For | Estimated Cost | Public Demo Difficulty | Time |
|---:|---|---|---:|---|---:|
| **1** | **RAG Evaluation Lab** | AI engineering interviews | **$0–$5** | Easy | 1–2 weeks |
| **2** | **Agentic Workflow Simulator** | LangGraph / workflow AI | **$0–$10** | Easy-medium | 1–2 weeks |
| **3** | **AI Data Analyst Copilot** | Your data analyst background | **$0–$15** | Medium | 2–4 weeks |
| **4** | **IT Helpdesk Triage** | Quick extra project | **$0–$5** | Easy | 3–7 days |
| **5** | **Generic Employee Service Assistant** | Enterprise AI story | **$5–$20+** | Medium-hard | 3–5 weeks |

## Recommended Build Order

| Build Order | Project | Why |
|---:|---|---|
| **1** | **RAG Evaluation Lab** | Cheapest, fastest, strongest AI engineering signal |
| **2** | **Agentic Workflow Simulator** | Shows controlled agentic workflows and structured outputs |
| **3** | **AI Data Analyst Copilot** | Best connection to your data/SQL/analytics background |
| **4** | **AI Helpdesk Triage** | Quick weekend mini-project |
| **5** | **Generic Employee Service Assistant** | Bigger enterprise-style project to build later |

## Recommended Portfolio Display Order

| Display Order | Project |
|---:|---|
| **1** | AI Data Analyst Copilot |
| **2** | RAG Evaluation Lab |
| **3** | Agentic Workflow Simulator |
| **4** | Generic Employee Service Assistant |
| **5** | AI Helpdesk Triage |

Why different from build order? Because the fastest project to build is not always the strongest one to show first on a resume.

---

# Cheapest Public Demo Strategy

Use this pattern for every project:

```text
GitHub repo
↓
Streamlit app
↓
cached demo mode
↓
optional live mode with user-provided API key
↓
README with screenshots and architecture
```

## Recommended Hosting

| Need | Best Option |
|---|---|
| Fastest public demo | Streamlit Community Cloud |
| More ML/AI-looking profile | Hugging Face Spaces |
| More backend/API-looking project | Render free tier |
| Best professional portfolio | GitHub repo + hosted Streamlit demo |

## Cost Protection

| Mode | What Recruiter Sees | Cost To You |
|---|---|---:|
| **Demo mode** | Preloaded questions and cached answers | **$0** |
| **Live mode** | Optional, limited, password-protected | Small |
| **Local mode** | Recruiter can clone repo and run with own key | $0 |

---

# 1. RAG Evaluation Lab

## Project Title

**RAG Evaluation Lab: Chunking, Retrieval, and Hallucination Testing**

## Main Idea

Instead of building a basic “chat with PDF” app, build a tool that tests how good a RAG system actually is.

The app answers questions like:

- Does smaller or larger chunk size work better?
- Does top-3 retrieval beat top-5?
- Does reranking improve answers?
- Does the model cite the correct source?
- How often does the model hallucinate?
- What is the cost and latency per answer?

This is stronger than a normal chatbot because real companies care about evaluation, not just connecting LangChain to OpenAI.

## Public/Fake Data

Use public documents or fake documents.

| Data Type | Example |
|---|---|
| Public policy docs | university HR policies, public benefits docs, government FAQs |
| Public finance docs | IRS FAQ pages, public SEC filings, bank product disclosures |
| Fake enterprise docs | fake employee handbook, fake payroll policy, fake PTO policy |
| Technical docs | public API docs, open-source documentation |

For version 1, fake company policy docs are probably easiest.

Example fake documents:

```text
BrightGrid Energy Employee Handbook
Payroll FAQ
Benefits Enrollment Guide
PTO Policy
Remote Work Policy
Expense Reimbursement Policy
```

Avoid real company names, NextEra, SAP, ServiceNow, SuccessFactors, or anything confidential.

## Core Features

| Feature | Description |
|---|---|
| Document loader | Loads 3–5 public/fake documents |
| Chunking comparison | Compare chunk size 15, 30, 60 tokens |
| Embeddings | Use local sentence-transformers first |
| Vector DB | FAISS or Chroma |
| Test questions | 30–50 predefined questions |
| Retrieval results | Show top retrieved chunks |
| Answer generation | Generate answer with citations |
| Evaluation metrics | Retrieval hit rate, citation accuracy, groundedness |
| Dashboard | Compare settings side-by-side |

## Cheap Stack

| Layer | Tool |
|---|---|
| UI | Streamlit |
| Hosting | Streamlit Community Cloud |
| Embeddings | `sentence-transformers` |
| Vector DB | FAISS or Chroma |
| LLM | Optional OpenAI, optional local model |
| Data storage | local JSON / CSV / parquet |
| Charts | Streamlit charts or Plotly |
| Repo | GitHub |

## Cost-Control Strategy

Do not let random visitors freely call your paid API.

Use three modes:

| Mode | Description | Cost |
|---|---|---:|
| **Demo mode** | Precomputed results and cached answers | **$0** |
| **Live mode** | Optional, maybe password-protected | Small |
| **Local mode** | Recruiter can clone repo and use own API key | $0 |

The public app should work even if no API key exists.

## App Pages

### Page 1: Overview

Explain what the app tests:

```text
This project compares RAG configurations across chunk size, top-k retrieval, embedding model, reranking, answer quality, latency, and estimated cost.
```

### Page 2: Document Explorer

Show:

- source documents
- chunks
- chunk size
- chunk count
- sample chunks

### Page 3: Retrieval Test

User selects:

- question
- chunk size
- top-k
- embedding model
- reranker on/off

Then app shows:

- retrieved chunks
- similarity scores
- correct source yes/no

### Page 4: Answer Evaluation

Show:

- generated answer
- citations
- expected source
- whether answer is grounded
- hallucination warning

### Page 5: Metrics Dashboard

Show:

| Metric | Example |
|---|---|
| Retrieval hit rate | 84% |
| Citation accuracy | 78% |
| Faithfulness score | 0.82 |
| Average latency | 1.4 sec |
| Estimated cost | $0.002 per query |

## Minimal Version

Build only this first:

1. Load fake policy docs.
2. Create chunks.
3. Embed chunks.
4. Retrieve top-k chunks.
5. Run 30 test questions.
6. Show hit rate by chunk size and top-k.
7. Add cached sample answers.

That alone is enough for a portfolio.

## Advanced Version

Add later:

- reranking
- different embedding models
- answer faithfulness scoring
- LLM-as-judge evaluation
- cost simulator
- export results to CSV

## GitHub README Structure

```text
# RAG Evaluation Lab

## Problem
RAG systems can answer from documents, but quality depends heavily on chunking, retrieval, embeddings, and evaluation.

## What this project does
Compares multiple RAG configurations and measures retrieval quality, answer groundedness, citation accuracy, latency, and cost.

## Tech stack
Streamlit, Python, FAISS/Chroma, sentence-transformers, optional OpenAI API.

## Demo
Public Streamlit link.

## Architecture
Document loader → chunking → embeddings → vector search → answer generation → evaluation dashboard.

## Results
Table comparing chunk sizes, top-k values, and retrieval performance.

## How to run locally
pip install -r requirements.txt
streamlit run app.py
```

## Resume Bullets

- Built a RAG evaluation lab to compare chunking, top-k retrieval, embeddings, reranking, and citation accuracy across policy-style documents.
- Implemented retrieval quality metrics including hit rate, source accuracy, groundedness checks, latency, and estimated cost per query.
- Designed a public Streamlit demo with cached results to demonstrate RAG behavior without exposing paid API usage.

## Interview Talking Point

> “I didn’t just build a chatbot. I built an evaluation harness to understand why RAG answers fail.”

## Final Verdict

This should be the first project.

---

# 2. Agentic Workflow Simulator

## Project Title

**Agentic Workflow Simulator: Controlled LLM Routing with Human Approval**

## Main Idea

Build a small system where an LLM does not freely act like a random chatbot. Instead, it follows a controlled workflow:

```text
classify request
→ check missing information
→ retrieve policy/context
→ choose next action
→ generate structured output
→ require human approval when needed
```

The main portfolio angle:

> “I built a controlled, auditable agentic workflow.”

## Use Case

Use a fake business operations request system.

Example requests:

```text
“I need access to the Q3 revenue dashboard.”
“My reimbursement from last month was rejected.”
“Can I change my direct deposit?”
“I need a laptop replacement.”
“Please update my address.”
```

The agent decides:

| Request | Action |
|---|---|
| Simple policy question | answer directly |
| Missing details | ask clarification |
| Access request | create approval task |
| Sensitive payroll issue | escalate |
| IT hardware issue | route to IT queue |

## Fake Data

Use fake request types:

```text
Access requests
Payroll questions
Expense reimbursement
IT support
Benefits questions
Policy questions
```

Fake tools:

```text
create_ticket()
send_to_manager_approval()
retrieve_policy()
check_required_fields()
escalate_to_human()
```

These are not real tools. They only write to local JSON or a local database.

## Core Features

| Feature | Description |
|---|---|
| Intent classifier | Classifies the request |
| State machine | Controls workflow steps |
| Fake tool calling | Simulates ticket creation, approvals, escalation |
| Human-in-loop | User approves/rejects action |
| Audit trail | Shows each step taken |
| Structured JSON output | Shows category, confidence, action |
| Dashboard | Shows routing distribution and escalation rate |

## Cheap Stack

| Layer | Tool |
|---|---|
| UI | Streamlit |
| Workflow | LangGraph or simple Python state machine |
| LLM | Optional OpenAI / local / cached |
| Storage | SQLite or JSON |
| Hosting | Streamlit Community Cloud |
| Visualization | Streamlit tables/charts |

## Cost-Control Strategy

Make the app work with preloaded examples.

Public recruiter demo:

- user selects from 10 sample requests
- app shows precomputed workflow trace
- optional “run live” button disabled unless API key is entered

This protects API cost.

## App Pages

### Page 1: Workflow Overview

Show the workflow:

```text
User request → classifier → validator → policy lookup → action decision → human approval → final result
```

### Page 2: Try a Request

Recruiter selects a sample request:

```text
“I need access to payroll reports.”
```

App shows:

```json
{
  "intent": "access_request",
  "confidence": 0.91,
  "missing_fields": ["manager_approval"],
  "recommended_action": "create_approval_task",
  "risk_level": "medium"
}
```

### Page 3: Workflow Trace

Show each step:

| Step | Result |
|---|---|
| Classify | access_request |
| Validate | missing manager approval |
| Retrieve policy | access policy found |
| Decide | approval required |
| Tool call | fake approval task created |
| Human approval | pending |

### Page 4: Audit Log

Show:

- timestamp
- state
- action
- confidence
- reason
- output

### Page 5: Metrics

Show:

| Metric | Meaning |
|---|---|
| % auto-resolved | simple cases handled |
| % escalated | sensitive/unclear cases |
| average steps | workflow complexity |
| low confidence cases | need human review |

## Minimal Version

Build this:

1. 10 sample requests.
2. Classifier returns JSON.
3. Simple state machine routes each request.
4. Fake tool calls.
5. Workflow trace in Streamlit.
6. Human approval button.

## Advanced Version

Add later:

- LangGraph
- memory/state persistence
- policy retrieval
- approval rules
- evaluation test cases
- retry/fallback logic

## GitHub README Structure

```text
# Agentic Workflow Simulator

## Problem
LLM agents can be unreliable if they are allowed to act freely.

## Solution
This project uses a controlled workflow with classification, validation, routing, tool simulation, human approval, and audit logs.

## Architecture
Request → classifier → state graph → fake tools → approval → final response.

## Tech stack
Python, Streamlit, LangGraph/simple state machine, SQLite/JSON.

## Demo
Public app with cached workflow examples.
```

## Resume Bullets

- Built a controlled agentic workflow simulator using structured LLM outputs, state transitions, fake tool calls, and human approval gates.
- Designed an audit log for each workflow step, including intent classification, missing-field validation, action selection, and escalation.
- Created a public demo with cached examples to show agent behavior without exposing paid API keys or enterprise systems.

## Interview Talking Point

> “I wanted to show that I understand agents as workflows, not magic. The model proposes actions, but the system controls permissions, state, and approval.”

## Final Verdict

Build this second after the RAG Evaluation Lab.

---

# 3. AI Data Analyst Copilot

## Project Title

**AI Data Analyst Copilot: Natural Language to SQL with Validation and Dashboards**

## Main Idea

User asks a business question in plain English. The app turns it into SQL, validates the query, runs it against fake business data, and explains the result.

Example:

```text
“Which customer segment had the highest churn last quarter?”
```

System flow:

```text
question → SQL generation → SQL validation → query execution → chart → explanation → caveats
```

This is very relevant to data analyst, BI analyst, analytics engineer, and AI data roles.

## Data

Use fake SaaS business data.

Tables:

```text
customers
subscriptions
invoices
payments
product_usage
support_tickets
marketing_campaigns
sales_opportunities
```

Example questions:

```text
Which segment has the highest churn?
What is MRR by month?
Which acquisition channel has the best conversion rate?
Which customers are at risk of churn?
What are the top support ticket categories?
Which sales opportunities have the highest expected revenue?
```

## Core Features

| Feature | Description |
|---|---|
| Natural language input | User asks business question |
| SQL generation | LLM generates SQL |
| SQL validation | Prevents unsafe/bad queries |
| Query execution | Runs against SQLite/Postgres |
| Chart generation | Creates simple chart |
| Explanation | Explains result in business terms |
| Caveats | Mentions limitations |
| Query history | Stores previous questions |
| Sample questions | Recruiter can click examples |

## Cheap Stack

| Layer | Tool |
|---|---|
| UI | Streamlit |
| Database | SQLite for public demo |
| Data generation | Python Faker / custom scripts |
| SQL engine | SQLite |
| LLM | Optional OpenAI / local / cached |
| Charts | Plotly or Streamlit |
| Hosting | Streamlit Community Cloud |
| Repo | GitHub |

Use SQLite, not cloud Postgres, for version 1. It is free and easy to deploy.

## Cost-Control Strategy

For the public demo:

- include 15 sample questions
- precompute SQL + results + charts
- allow live mode only with user-provided API key

This way recruiters can click around for free.

## App Pages

### Page 1: Business Dataset

Show schema:

```text
customers(customer_id, segment, signup_date, acquisition_channel, country)
subscriptions(subscription_id, customer_id, plan, mrr, status, start_date, end_date)
invoices(invoice_id, customer_id, amount, invoice_date, paid_date)
product_usage(customer_id, active_days, feature_count, last_login_date)
support_tickets(ticket_id, customer_id, category, priority, created_date, resolved_date)
```

### Page 2: Ask a Question

User selects or types:

```text
“What is MRR trend by month?”
```

App shows:

- generated SQL
- validation result
- query result
- chart
- explanation

### Page 3: SQL Safety

This is a strong differentiator.

Show checks:

| Check | Example |
|---|---|
| only SELECT allowed | blocks DELETE/UPDATE |
| table allowlist | only known tables |
| limit rows | prevents huge output |
| syntax validation | checks SQL before running |
| explanation required | no silent result |

### Page 4: Dashboard

Show predefined business dashboard:

- MRR trend
- churn rate
- tickets by category
- top segments
- acquisition channel performance

### Page 5: Evaluation

Test whether generated SQL matches expected SQL/output for predefined questions.

Metrics:

| Metric | Meaning |
|---|---|
| SQL execution success | query runs |
| result accuracy | output matches expected |
| chart relevance | chart type makes sense |
| explanation quality | readable business explanation |

## Minimal Version

Build:

1. Fake SaaS SQLite database.
2. 10 predefined natural language questions.
3. Precomputed SQL and results.
4. Streamlit UI showing schema, SQL, result, chart.
5. Optional live SQL generation.

## Advanced Version

Add:

- live LLM-to-SQL
- SQL validation
- query repair
- semantic layer
- metric definitions
- dashboard generation
- comparison against expected SQL

## GitHub README Structure

```text
# AI Data Analyst Copilot

## Problem
Business users ask data questions in natural language, but SQL generation needs validation, schema awareness, and explainable outputs.

## Solution
A natural-language-to-SQL assistant over a fake SaaS dataset with SQL validation, charts, explanations, and cached demo mode.

## Dataset
Synthetic SaaS revenue, customer, subscription, usage, and support data.

## Architecture
Question → schema context → SQL generation → validation → execution → chart → explanation.

## Demo
Public Streamlit app.
```

## Resume Bullets

- Built an AI data analyst copilot that converts natural language business questions into validated SQL over a synthetic SaaS dataset.
- Implemented SQL safety checks, schema-aware prompting, result explanations, and chart generation for MRR, churn, customer segments, and support analytics.
- Created a public demo with cached examples and optional live LLM mode to control API cost.

## Interview Talking Point

> “The hard part is not generating SQL. The hard part is validating it, grounding it in the schema, and explaining the result correctly.”

## Final Verdict

This is probably the best resume project overall, but not the fastest. Build it third.

---

# 4. AI Helpdesk Triage

## Project Title

**AI Helpdesk Triage: Ticket Classification, Priority Scoring, and Routing**

## Main Idea

User submits an IT support ticket. The system classifies it, assigns priority, routes it to the right team, and drafts a response.

Example:

```text
“My laptop will not connect to VPN and I have a client meeting in 30 minutes.”
```

Output:

```json
{
  "category": "vpn_access",
  "priority": "high",
  "assignment_group": "network_support",
  "urgency_reason": "client meeting in 30 minutes",
  "suggested_response": "Please try..."
}
```

## Why It Is Lower Ranked

It is useful, but generic. Many people build ticket classifiers.

To make it stronger, add:

- confidence score
- escalation logic
- dashboard
- evaluation set
- fake SLA rules

## Data

Create 100 fake tickets manually or with an LLM once, then save them.

Categories:

```text
password_reset
vpn_access
laptop_hardware
email_issue
software_install
account_access
network_outage
printer_issue
security_incident
```

Priority rules:

| Condition | Priority |
|---|---|
| security incident | critical |
| outage affecting many users | critical |
| executive/client meeting soon | high |
| one user, normal issue | medium |
| simple password reset | low |

## Core Features

| Feature | Description |
|---|---|
| Ticket classifier | predicts category |
| Priority scorer | low/medium/high/critical |
| Routing engine | assigns fake team |
| Suggested response | drafts first reply |
| SLA estimate | fake response time |
| Dashboard | ticket volume by category |
| Evaluation | classification accuracy on test set |

## Cheap Stack

| Layer | Tool |
|---|---|
| UI | Streamlit |
| Classifier | rules first, optional LLM |
| Data | fake CSV |
| Storage | CSV/SQLite |
| Hosting | Streamlit Community Cloud |
| Cost | almost free |

## Cost-Control Strategy

This can be mostly non-LLM:

- use rules or traditional ML for classification
- use cached drafted responses
- optional LLM only for live response generation

This makes it very cheap.

## App Pages

### Page 1: Submit Ticket

User enters or selects ticket text.

### Page 2: Triage Result

Show:

- category
- priority
- assignment group
- confidence
- SLA
- suggested response

### Page 3: Dashboard

Show:

- tickets by category
- tickets by priority
- average SLA
- unresolved critical tickets

### Page 4: Evaluation

Show accuracy on fake labeled tickets.

## Minimal Version

Build:

1. Fake ticket dataset.
2. Classification logic.
3. Priority rules.
4. Streamlit form.
5. Dashboard.

You can finish this in a weekend.

## Advanced Version

Add:

- LLM-generated response
- embeddings for similar tickets
- duplicate ticket detection
- SLA breach prediction
- human review queue

## GitHub README Structure

```text
# AI Helpdesk Triage

## Problem
Support teams receive many unstructured tickets that need classification, prioritization, and routing.

## Solution
A lightweight triage system that classifies tickets, assigns priority, routes them, and drafts responses using fake support data.

## Tech stack
Python, Streamlit, pandas, optional LLM.
```

## Resume Bullets

- Built an AI helpdesk triage app that classifies support tickets, assigns priority, routes to support groups, and generates suggested replies.
- Created a synthetic labeled ticket dataset and evaluation dashboard to measure classification accuracy and routing quality.
- Designed a low-cost public demo using cached outputs and rule-based fallbacks.

## Final Verdict

Good as a quick extra project, but not the main one.

---

# 5. Generic Employee Service Assistant

## Project Title

**Employee Service Assistant: Policy RAG, Request Classification, and Case Routing**

## Main Idea

An employee asks a question or submits a request. The system decides whether to:

- answer from policy docs
- ask clarification
- create a fake case
- route to payroll/benefits/IT/HR
- escalate to human

Example:

```text
“I moved to another state. How do I update my address and tax information?”
```

Output:

```json
{
  "intent": "employee_data_change",
  "case_needed": true,
  "assignment_group": "hr_operations",
  "required_information": ["new address", "effective date"],
  "answer": "You can update your address..."
}
```

## Why Not First

This is strong, but not first because:

- it overlaps with current work too much
- it may become big
- you need to be careful not to copy workplace logic
- recruiters may not understand it faster than RAG Lab or Data Copilot
- quick wins matter first

Later, this could be the strongest enterprise AI project.

## Fake Data

Use a fake company:

```text
Northstar Utilities
BrightGrid Energy
Atlas Manufacturing
```

Fake docs:

```text
Employee Handbook
Benefits Guide
Payroll FAQ
PTO Policy
Remote Work Policy
Onboarding Guide
Offboarding Guide
Data Change Policy
```

Fake case categories:

```text
payroll
benefits
pto
employee_data
onboarding
offboarding
system_access
policy_question
manager_request
```

## Core Features

| Feature | Description |
|---|---|
| Intent classification | determines request type |
| RAG answer | answers from policy docs |
| Case decision | deflect or create case |
| Routing | assigns fake team |
| Missing info detection | asks for required fields |
| Escalation | sensitive/unclear cases go to human |
| Confidence score | low confidence = escalate |
| Analytics dashboard | deflection and routing metrics |

## Cheap Stack

| Layer | Tool |
|---|---|
| UI | Streamlit |
| RAG | LlamaIndex or LangChain |
| Workflow | simple Python logic first, LangGraph later |
| Vector DB | FAISS/Chroma |
| Embeddings | local sentence-transformers |
| LLM | optional OpenAI/local/cached |
| Storage | SQLite/JSON |
| Hosting | Streamlit Community Cloud |

## Cost-Control Strategy

Same pattern:

| Mode | Description |
|---|---|
| Demo mode | preloaded questions and cached outputs |
| Live mode | optional API key |
| Local mode | clone and run locally |

Do not expose your API key to everyone.

## App Pages

### Page 1: Employee Assistant

User asks a question.

Example:

```text
“How do I add my spouse to benefits?”
```

App outputs:

- answer
- source policy section
- whether case is needed
- confidence

### Page 2: Case Routing

Show fake case:

```json
{
  "case_id": "HR-1024",
  "category": "benefits",
  "priority": "medium",
  "assignment_group": "benefits_team",
  "status": "new"
}
```

### Page 3: Missing Information

For some requests:

```text
“I need to update my address.”
```

System asks:

```text
What is the effective date of the address change?
```

### Page 4: Deflection Dashboard

Show:

| Metric | Example |
|---|---|
| total requests | 250 |
| deflected | 62% |
| routed | 28% |
| escalated | 10% |
| top category | payroll |
| low confidence cases | 18 |

### Page 5: Evaluation

Use 50 test cases:

| Test | Metric |
|---|---|
| intent classification | accuracy |
| retrieval | source hit rate |
| routing | correct team |
| escalation | sensitive cases caught |
| deflection | correct answer vs case needed |

## Minimal Version

Build later:

1. Fake policy docs.
2. 50 fake employee questions.
3. Intent classifier.
4. RAG answer with citations.
5. Fake case routing.
6. Dashboard.

## Advanced Version

Add:

- LangGraph workflow
- human approval
- policy versioning
- duplicate case detection
- multilingual support
- case volume simulation
- cost/ROI calculator

## GitHub README Structure

```text
# Employee Service Assistant

## Problem
Employee service teams receive repeated policy questions and operational requests that require routing, clarification, or escalation.

## Solution
A synthetic-data AI assistant that combines RAG, intent classification, case routing, missing-information detection, and deflection analytics.

## Important
This project uses only synthetic data and fake company documents. It is not connected to any enterprise systems.
```

## Resume Bullets

- Built a synthetic employee service assistant using RAG, intent classification, case routing, and deflection analytics over fake HR policy documents.
- Implemented missing-information detection, confidence-based escalation, and structured case creation for payroll, benefits, PTO, onboarding, and employee data requests.
- Designed a public demo with synthetic data only, showing how AI can reduce repetitive service requests while preserving human review for sensitive cases.

## Final Verdict

Build this later, not first.

---

# Final Recommendation

Start with:

## 1. RAG Evaluation Lab

Do not overbuild it. The goal is to finish and publish.

Deliverables:

- GitHub repo
- public Streamlit demo
- README
- screenshots
- 30 test questions
- evaluation dashboard

Then build:

## 2. Agentic Workflow Simulator

Deliverables:

- public demo
- fake tools
- workflow trace
- human approval
- audit log

Then build:

## 3. AI Data Analyst Copilot

Deliverables:

- fake SaaS database
- natural language questions
- SQL validation
- charting
- business explanation

After these three, the portfolio will already look much better for AI/data roles. The HR/employee assistant can wait.

---

# Strongest One-Sentence Portfolio Summary

> I built a set of AI engineering portfolio projects focused on RAG evaluation, controlled agentic workflows, and natural-language analytics, using only synthetic or public data and low-cost public demos.
