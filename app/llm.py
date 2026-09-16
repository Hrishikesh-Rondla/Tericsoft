"""
LLM integration layer – the ONLY file that touches the Groq API.
To swap to Gemini: replace this file and keep the call_llm(prompt) -> dict
signature; nothing else needs to change.

Model note (verified September 2026 against live client.models.list()):
  llama-3.3-70b-versatile is DEPRECATED on Groq.
  meta-llama/llama-4-scout-17b-16e-instruct requires specific account access.
  Current confirmed free-tier model: openai/gpt-oss-120b
  Source: verified via groq.Client.models.list() on account
"""

import json
import os

import httpx
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

# ---------------------------------------------------------------------------
# Fail fast on startup if the API key is missing.
# We check here (module level) so the server refuses to start rather than
# silently failing on the first real request.
# ---------------------------------------------------------------------------
_GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not _GROQ_API_KEY:
    raise RuntimeError(
        "GROQ_API_KEY environment variable is not set. "
        "Copy .env.example to .env and add your key."
    )

_client = Groq(
    api_key=_GROQ_API_KEY,
    http_client=httpx.Client(timeout=30.0),  # explicit: SDK default is ~60s via httpx
)

# Model verified via client.models.list() on this Groq account (September 2026).
# llama-3.3-70b-versatile deprecated; llama-4-scout requires specific access.
# openai/gpt-oss-120b is the highest-capability model available here.
MODEL = "openai/gpt-oss-120b"
TEMPERATURE = 0.3

# ---------------------------------------------------------------------------
# Priority mapping enforced in Python – we do NOT trust the model to apply
# the correct boundary consistently. The model scores 0-100; we classify here.
# ---------------------------------------------------------------------------
def _classify_priority(score: int) -> str:
    if score >= 70:
        return "High"
    elif score >= 40:
        return "Medium"
    return "Low"


# ---------------------------------------------------------------------------
# Prompt builder
# ---------------------------------------------------------------------------
def _build_prompt(requirement: str, context_entries: list[dict]) -> str:
    context_block = "\n".join(
        f"{i+1}. {e['name']} ({e['category']}): {e['description']} "
        f"Key features: {', '.join(e['key_features'])}. "
        f"Ideal for: {e['ideal_for']}. Tier: {e['pricing_tier']}."
        for i, e in enumerate(context_entries)
    )

    return f"""You are a senior B2B sales qualification analyst at Northwind Cloud.

RETRIEVED PRODUCT CONTEXT (use ONLY these products – do not mention any product not listed here):
{context_block}

CUSTOMER REQUIREMENT:
{requirement}

SCORING CRITERIA (0-100):
- Budget / urgency signals in the requirement (0-25 pts)
- Fit with the retrieved products above (0-25 pts)
- Buying authority implied by the language (0-25 pts)
- Specificity and clarity of the requirement (0-25 pts)

Score mapping: High >= 70, Medium 40-69, Low < 40.

Return ONLY valid JSON matching this exact schema, no extra text:
{{
  "lead_summary": "<2-3 sentence summary of this lead>",
  "relevant_products": [{{"name": "<product name from context>", "why": "<one sentence>"}}],
  "customer_needs": ["<need 1>", "<need 2>"],
  "recommended_next_step": "<one sentence>",
  "follow_up_questions": ["<question 1>", "<question 2>", "<question 3>"],
  "lead_score": <integer 0-100>,
  "priority": "<High | Medium | Low>",
  "score_rationale": "<one sentence explaining the score>"
}}"""


# ---------------------------------------------------------------------------
# Public interface: call_llm(prompt) -> dict
# ---------------------------------------------------------------------------
def call_llm(requirement: str, context_entries: list[dict]) -> dict:
    """
    Call the Groq LLM with the customer requirement and retrieved context.
    Returns the parsed JSON dict with priority enforced by _classify_priority.
    Retries once on JSON parse failure; raises ValueError on second failure.
    """
    prompt = _build_prompt(requirement, context_entries)
    last_error: Exception | None = None

    for attempt in range(2):
        retry_note = ""
        if attempt == 1 and last_error:
            retry_note = (
                f"\n\nPREVIOUS ATTEMPT FAILED JSON PARSING: {last_error}\n"
                "Please return ONLY valid JSON with no markdown fences or extra text."
            )

        response = _client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "user", "content": prompt + retry_note},
            ],
            temperature=TEMPERATURE,
            response_format={"type": "json_object"},
        )

        raw = response.choices[0].message.content
        try:
            result = json.loads(raw)
            break
        except json.JSONDecodeError as exc:
            last_error = exc
            if attempt == 1:
                raise ValueError(
                    f"LLM returned invalid JSON after 2 attempts. "
                    f"Last error: {exc}. Raw: {raw[:200]}"
                )

    # Enforce priority mapping in Python – don't trust the model's label
    score = int(result.get("lead_score", 0))
    result["lead_score"] = max(0, min(100, score))  # clamp to [0, 100]
    result["priority"] = _classify_priority(result["lead_score"])

    return result
