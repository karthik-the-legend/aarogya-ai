# ================================================================
# backend\main.py
# FastAPI server exposing the full pipeline as a REST API.
# Run: uvicorn backend.main:app --reload
# Docs: http://localhost:8000/docs
# ================================================================

import sys
import time
from contextlib import asynccontextmanager
from pathlib import Path

sys.path.insert(0, "backend")

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from models import (
    QueryRequest,
    QueryResponse,
    VoiceQueryResponse,
    VoiceTranscript,
    HealthResponse,
    Source,
)
from rag_pipeline import RAGPipeline
from triage import classify, TriageLevel
from voice_handler import transcribe_bytes, load_whisper_model
from translate import to_english, from_english
from config import DATA_DIR, SUPPORTED_LANGUAGES


# ── Startup / Shutdown lifecycle ─────────────────────────────────
# RAGPipeline and Whisper are loaded ONCE at startup.
# Never load them inside endpoint functions — too slow.
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("[Startup] Loading RAGPipeline...")
    app.state.rag = RAGPipeline()
    print("[Startup] Pre-loading Whisper model...")
    load_whisper_model()
    print("[Startup] All models loaded. Server ready.")
    yield
    print("[Shutdown] Goodbye.")


# ── App definition ───────────────────────────────────────────────
app = FastAPI(
    title="Aarogya AI — Vernacular Health Assistant",
    description="RAG-powered health assistant for rural India. "
    "Supports Hindi, Tamil, Telugu, Kannada.",
    version="1.0.0",
    lifespan=lifespan,
)

# Allow frontend to call this API from any origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── POST /ask — Main text query endpoint ─────────────────────────
@app.post("/ask", response_model=QueryResponse)
async def ask_text(request: QueryRequest):
    """
    Full pipeline for text queries.
    Flow: translate → FAISS → LLM → triage → translate back
    """
    t0 = time.time()

    # Step 1: Translate user query to English for FAISS
    query_en = to_english(request.query, request.lang_code)
    # Fallback unknown language to English
    if request.lang_code not in SUPPORTED_LANGUAGES:
        request = request.model_copy(
            update={"lang_code": "en", "language_name": "English"}
        )

    # Step 2: RAG — retrieve chunks + generate response
    rag_result = app.state.rag.ask(query=query_en, language=request.language_name)

    # Step 3: Run triage on query + LLM response
    triage_result = classify(request.query, rag_result["answer"])

    # Step 4: Decide final answer
    if triage_result.level == TriageLevel.RED:
        # Override LLM with emergency message
        final_answer = triage_result.message
    else:
        # Translate response back to user's language
        final_answer = from_english(rag_result["answer"], request.lang_code)
        if triage_result.level == TriageLevel.YELLOW:
            final_answer += f"\n\n{triage_result.message}"

    return QueryResponse(
        answer=final_answer,
        triage_level=triage_result.level.value,
        triage_override=triage_result.override,
        sources=[Source(**s) for s in rag_result["sources"]],
        latency_ms=round((time.time() - t0) * 1000),
        detected_language=request.lang_code,
    )


# ── POST /ask-voice — Audio file upload endpoint ─────────────────
@app.post("/ask-voice", response_model=VoiceQueryResponse)
async def ask_voice(audio: UploadFile = File(...)):
    """
    Voice query endpoint.
    Whisper transcribes audio → feeds into /ask pipeline.
    Accepted formats: .mp3, .wav, .ogg, .m4a
    """
    allowed = ["audio/mpeg", "audio/wav", "audio/ogg", "audio/mp4", "audio/x-m4a"]
    if audio.content_type not in allowed:
        raise HTTPException(
            status_code=400, detail=f"Unsupported audio format: {audio.content_type}"
        )

    audio_bytes = await audio.read()
    ext = "." + audio.filename.split(".")[-1]

    # Whisper transcription
    transcript_data = transcribe_bytes(audio_bytes, ext)

    # Reuse ask_text pipeline
    text_request = QueryRequest(
        query=transcript_data["text"],
        lang_code=transcript_data["lang_code"],
        language_name=transcript_data["language"],
    )
    text_response = await ask_text(text_request)

    return VoiceQueryResponse(
        **text_response.model_dump(),
        transcript=VoiceTranscript(
            text=transcript_data["text"],
            lang_code=transcript_data["lang_code"],
            language=transcript_data["language"],
        ),
    )


# ── GET /health ──────────────────────────────────────────────────
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Frontend calls this on startup to confirm server is ready."""
    return HealthResponse(
        status="ok", rag_loaded=hasattr(app.state, "rag"), version="1.0.0"
    )


# ── GET /sources ─────────────────────────────────────────────────
@app.get("/sources")
async def list_sources():
    """List all PDFs in the knowledge base from sources.txt."""
    sources_file = DATA_DIR / "sources.txt"
    if not sources_file.exists():
        return {"sources": [], "count": 0}
    lines = sources_file.read_text(encoding="utf-8").splitlines()
    pdfs = [l.strip() for l in lines if l.strip().endswith(".pdf")]
    return {"sources": pdfs, "count": len(pdfs)}
