# ================================================================
# backend\models.py
# Pydantic schemas for every FastAPI request and response.
# FastAPI uses these to: validate input, auto-generate /docs,
# serialise responses, and catch type errors instantly.
# ================================================================

from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from enum import Enum


# ── Enums ────────────────────────────────────────────────────────
class TriageLevel(str, Enum):
    """Maps to badge colours in the frontend UI."""
    GREEN  = "green"   # home care safe
    YELLOW = "yellow"  # see doctor today
    RED    = "red"     # emergency — LLM overridden


# ── Request Models ───────────────────────────────────────────────
class QueryRequest(BaseModel):
    """
    Sent by the frontend when user submits a text query.
    Example JSON the frontend sends:
    {
        "query": "मुझे बुखार है और सिरदर्द है",
        "lang_code": "hi",
        "language_name": "Hindi"
    }
    """
    query         : str = Field(
        ..., min_length=3, max_length=500,
        description="User health question in their native language"
    )
    lang_code     : str = Field(
        default="en", min_length=2, max_length=5,
        description="ISO 639-1 language code e.g. 'hi' for Hindi"
    )
    language_name : str = Field(
        default="English",
        description="Full language name for the LLM system prompt"
    )

    # Validator: strip leading/trailing whitespace from query
    @field_validator("query")
    def strip_query(cls, v: str) -> str:
        return v.strip()


# ── Sub-models ───────────────────────────────────────────────────
class Source(BaseModel):
    """
    One retrieved document chunk shown in the UI for transparency.
    This is the XAI (Explainable AI) layer — users can see exactly
    which PDF and page the answer came from.
    """
    source  : str  # filename: "06_cdc_dengue_clinical.pdf"
    page    : int  # page number (0-indexed)
    content : str  # first 200 chars of the chunk text


# ── Response Models ──────────────────────────────────────────────
class QueryResponse(BaseModel):
    """
    Returned by POST /ask and POST /ask-voice.
    Example JSON returned to frontend:
    {
        "answer": "आपको वायरल बुखार हो सकता है...",
        "triage_level": "green",
        "triage_override": false,
        "sources": [
            {"source": "09_ncbi_fever.pdf", "page": 1, "content": "..."}
        ],
        "latency_ms": 1842,
        "detected_language": "hi"
    }
    """
    answer            : str
    triage_level      : str          # "green" | "yellow" | "red"
    triage_override   : bool         # True = RED overrode LLM
    sources           : List[Source] # retrieved chunks for XAI
    latency_ms        : int          # total pipeline time
    detected_language : Optional[str] = "en"  # ISO code


class VoiceTranscript(BaseModel):
    """
    Returned alongside voice response — shows what Whisper heard.
    Displayed in the UI so user can verify transcription was correct.
    """
    text      : str  # transcribed text from audio
    lang_code : str  # language Whisper detected
    language  : str  # full name: "Hindi", "Tamil" etc.


class VoiceQueryResponse(QueryResponse):
    """
    Extends QueryResponse with the Whisper transcript.
    Used by POST /ask-voice only.
    """
    transcript : VoiceTranscript


class HealthResponse(BaseModel):
    """GET /health — tells the frontend if the server is ready."""
    status     : str   # "ok"
    rag_loaded : bool  # False until RAGPipeline finishes loading
    version    : str   # "1.0.0"


class ErrorResponse(BaseModel):
    """Returned when something goes wrong — standard error shape."""
    error   : str            # short error code: "VALIDATION_ERROR"
    message : str            # human-readable explanation
    detail  : Optional[str] = None  # stack trace in development