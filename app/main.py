"""
FastAPI application – 5 routes, CORS, StaticFiles mount.
Data flow per POST /api/leads:
  1. Pydantic validates the request body (LeadCreate)
  2. retrieval.search() finds top-3 relevant products via TF-IDF
  3. llm.call_llm() calls Groq with the requirement + retrieved context
  4. We persist the lead to SQLite via SQLAlchemy
  5. Return the full lead as LeadResponse
"""

import json
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.models import Lead, create_tables, get_session
from app.retrieval import search
from app.schemas import HealthResponse, LeadCreate, LeadResponse

# Import llm lazily inside the route so that the module-level API key check
# happens at app startup (when uvicorn imports main.py) rather than at
# test-collection time. Tests mock llm before importing main.
import app.llm as _llm_module


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create DB tables once on startup; nothing to do on shutdown."""
    create_tables()
    yield


app = FastAPI(title="Sales Lead Qualifier", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # fine for a single-file static frontend
    allow_methods=["*"],
    allow_headers=["*"],
)




# ---------------------------------------------------------------------------
# Static file mount – serves index.html at /
# ---------------------------------------------------------------------------
_static_dir = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=_static_dir, html=True), name="static")


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/api/health", response_model=HealthResponse)
def health() -> HealthResponse:
    """Quick liveness check. Returns whether the API key is configured."""
    return HealthResponse(
        status="ok",
        api_key_configured=bool(os.getenv("GROQ_API_KEY")),
    )


@app.get("/api/knowledge-base")
def list_knowledge_base() -> list[dict]:
    """Return all 12 product entries so the reviewer can inspect the corpus."""
    from app.knowledge_base import PRODUCTS
    return PRODUCTS


@app.get("/api/leads", response_model=list[LeadResponse])
def list_leads() -> list[LeadResponse]:
    """Return all leads, newest first."""
    with get_session() as session:
        leads = (
            session.query(Lead)
            .order_by(Lead.created_at.desc())
            .all()
        )
        return [LeadResponse.model_validate(lead) for lead in leads]


@app.get("/api/leads/{lead_id}", response_model=LeadResponse)
def get_lead(lead_id: int) -> LeadResponse:
    """Return one lead by ID, or 404."""
    with get_session() as session:
        lead = session.get(Lead, lead_id)
        if lead is None:
            raise HTTPException(status_code=404, detail=f"Lead {lead_id} not found")
        return LeadResponse.model_validate(lead)


@app.post("/api/leads", response_model=LeadResponse, status_code=201)
def create_lead(body: LeadCreate) -> LeadResponse:
    """
    Main qualification endpoint.
    1. Retrieve top-3 products via TF-IDF
    2. Call Groq LLM for analysis
    3. Persist to SQLite
    4. Return full lead response
    """
    # Step 1: TF-IDF retrieval
    context_entries = search(body.requirement_text, k=3)

    # Step 2: LLM analysis – wrap provider errors in a clean 502
    try:
        analysis = _llm_module.call_llm(body.requirement_text, context_entries)
    except ValueError as exc:
        # JSON parse failure after retries
        raise HTTPException(status_code=502, detail=f"LLM parse error: {exc}")
    except Exception as exc:
        # Network / auth / quota errors
        raise HTTPException(status_code=502, detail=f"LLM provider error: {exc}")

    # Step 3: Persist
    lead = Lead(
        company_name=body.company_name,
        contact_email=str(body.contact_email),
        requirement_text=body.requirement_text,
        retrieved_context=json.dumps(context_entries),
        ai_analysis=json.dumps(analysis),
        lead_score=analysis["lead_score"],
        priority=analysis["priority"],
        status="new",
    )
    with get_session() as session:
        session.add(lead)
        session.commit()
        session.refresh(lead)
        return LeadResponse.model_validate(lead)
