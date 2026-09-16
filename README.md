# Northwind Cloud – Sales Lead Qualifier

An AI-powered B2B sales lead qualification assistant. Paste a prospect's requirement, get a scored analysis with matched products, customer needs, and follow-up questions — all in under 5 seconds.

## What it does

1. Accepts a lead (company name, email, requirement text) via a web form.
2. Runs TF-IDF retrieval to find the 3 most relevant products from a 12-entry knowledge base.
3. Sends the requirement + retrieved context to a Groq LLM (Llama 4 Scout) for structured JSON analysis.
4. Persists the lead and analysis to SQLite, then returns a scored result to the UI.

## Setup (4 steps)

```bash
# 1. Clone and enter the directory
git clone <repo-url> && cd sales-lead-qualifier

# 2. Create a virtual environment
python -m venv .venv && .venv\Scripts\activate   # Windows
# or: source .venv/bin/activate                  # macOS/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure your Groq API key
cp .env.example .env
# Edit .env and set: GROQ_API_KEY=your_key_here

# Start the server
uvicorn app.main:app --reload
# Open http://localhost:8000/static/index.html
```

## Endpoints

| Method | Path                   | Description                                     |
|--------|------------------------|-------------------------------------------------|
| GET    | `/api/health`          | Liveness check + whether API key is configured  |
| POST   | `/api/leads`           | Submit a lead → retrieval → LLM → persist       |
| GET    | `/api/leads`           | List all leads, newest first                    |
| GET    | `/api/leads/{id}`      | Fetch one lead by ID (404 if missing)           |
| GET    | `/api/knowledge-base`  | Return all 12 product entries                   |

## Architecture

```
Browser → POST /api/leads
            │
            ▼
    Pydantic validation (schemas.py)
            │
            ▼
    TF-IDF search (retrieval.py) ← knowledge_base.py index (built at startup)
            │  top-3 products with relevance scores
            ▼
    Groq LLM call (llm.py) – grounded prompt with retrieved context
            │  JSON: summary, products, needs, score, priority
            ▼
    Python enforces priority mapping (High/Medium/Low) on score
            │
            ▼
    SQLite persist (models.py) → LeadResponse → JSON to browser
```

## Running tests

```bash
pytest tests/ -v
# All tests pass with no API key (LLM is mocked)
```

## Docker

```bash
docker build -t lead-qualifier .
docker run -p 8000:8000 -e GROQ_API_KEY=your_key lead-qualifier
```

## Design decisions and tradeoffs

**Why TF-IDF over embeddings?**  
TF-IDF is deterministic, has zero latency (local matrix multiply), and requires no extra API dependency. For a 12-document corpus with product-domain vocabulary, term overlap is sufficient. The tradeoff is no semantic/synonym matching: "login" won't hit "authentication" unless both tokens appear. Embeddings would be the right upgrade for a larger corpus.

**Why SQLite?**  
Zero infrastructure overhead for a prototype and assessment. SQLAlchemy's ORM means swapping to Postgres is a one-line `DATABASE_URL` change; no queries need to be rewritten.

**Why enforce priority in Python rather than trusting the model?**  
LLMs are stochastic. The model might label a score of 68 as "High" or format the string differently under temperature variance. Enforcing `High >= 70, Medium 40–69, Low < 40` in `_classify_priority()` guarantees the rule is always applied and is easy to test deterministically.

**What I'd add with more time:**  
- Lead status workflow (new → contacted → qualified → closed)  
- Authentication (API key header) on the POST endpoint  
- Streaming LLM responses to reduce perceived latency  
- Alembic migrations for production schema changes  
- Prometheus metrics endpoint for request count and latency percentiles  
