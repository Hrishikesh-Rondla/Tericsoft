"""
Pydantic v2 request and response schemas.
Validation lives here; routes stay thin and only call business logic.
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, EmailStr, Field, field_validator


# ---------------------------------------------------------------------------
# Request
# ---------------------------------------------------------------------------

class LeadCreate(BaseModel):
    company_name: str = Field(min_length=2, max_length=100)
    contact_email: EmailStr
    requirement_text: str = Field(min_length=20, max_length=2000)


# ---------------------------------------------------------------------------
# Response – mirrors the Lead ORM model but uses parsed JSON for analysis
# ---------------------------------------------------------------------------

class LeadResponse(BaseModel):
    id: int
    company_name: str
    contact_email: str
    requirement_text: str
    retrieved_context: list[dict]   # parsed from JSON string in DB
    ai_analysis: dict               # parsed from JSON string in DB
    lead_score: int
    priority: str
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}

    @field_validator("retrieved_context", mode="before")
    @classmethod
    def parse_retrieved_context(cls, v: Any) -> list[dict]:
        if isinstance(v, str):
            import json
            return json.loads(v)
        return v

    @field_validator("ai_analysis", mode="before")
    @classmethod
    def parse_ai_analysis(cls, v: Any) -> dict:
        if isinstance(v, str):
            import json
            return json.loads(v)
        return v


# ---------------------------------------------------------------------------
# Health check response
# ---------------------------------------------------------------------------

class HealthResponse(BaseModel):
    status: str
    api_key_configured: bool  # boolean only – never the value
