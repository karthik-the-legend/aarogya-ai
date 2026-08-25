# ================================================================
# backend\config.py — FINAL VERSION (Day 4 update)
# Every constant in one place. Change values here ONLY.
# All other files import from this — never hardcode elsewhere.
# ================================================================

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# ────────────────────────────────────────────────────────────────
# SECTION 1: PATHS
# ────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).parent.parent  # project root
DATA_DIR = BASE_DIR / "data"
VECTORSTORE_DIR = BASE_DIR / "vectorstore"
LOGS_DIR = BASE_DIR / "logs"
FRONTEND_DIR = BASE_DIR / "frontend"

for d in [DATA_DIR, VECTORSTORE_DIR, LOGS_DIR, FRONTEND_DIR]:
    d.mkdir(exist_ok=True)

# ────────────────────────────────────────────────────────────────
# SECTION 2: API KEYS
# ────────────────────────────────────────────────────────────────
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
SARVAM_API_KEY = os.getenv("SARVAM_API_KEY", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

# NEW — Gemini is optional, we use Groq
if not GEMINI_API_KEY:
    import warnings
    warnings.warn("GEMINI_API_KEY not set — using Groq LLM instead")

# ────────────────────────────────────────────────────────────────
# SECTION 3: EMBEDDING MODEL
# ────────────────────────────────────────────────────────────────
# paraphrase-multilingual-MiniLM-L12-v2 chosen because:
#   ✓ Supports Hindi, Tamil, Telugu, Kannada natively
#   ✓ 384-dim vectors — fast on CPU, accurate enough
#   ✓ Free, no API key, downloads once (~120MB)
#   ✓ Cross-lingual: Hindi query retrieves English passage correctly
EMBEDDING_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
EMBEDDING_DEVICE = "cpu"  # change to "cuda" if you have NVIDIA GPU
EMBEDDING_DIM = 384  # output dimensions of this model

# ────────────────────────────────────────────────────────────────
# SECTION 4: CHUNKING
# ────────────────────────────────────────────────────────────────
# Tested: 100, 200, 300, 500 words.
# 300 chosen: one medical topic per chunk, overlap prevents cuts.
CHUNK_SIZE = 300  # words per chunk (not characters)
CHUNK_OVERLAP = 50  # words shared with previous chunk

# ────────────────────────────────────────────────────────────────
# SECTION 5: RETRIEVAL (RAG)
# ────────────────────────────────────────────────────────────────
# TOP_K_RETRIEVAL: how many chunks are FINALLY fed to the LLM.
# Tested k=1 (misses context), k=3 (best), k=5 (dilutes prompt)
TOP_K_RETRIEVAL = 3
RETRIEVAL_TYPE = "similarity"  # "similarity" or "mmr" (diverse results)

# RETRIEVAL_CANDIDATES_K: how many chunks FAISS returns BEFORE
# reranking. Wider net than TOP_K_RETRIEVAL so the reranker has real
# candidates to choose from instead of just re-sorting an already
# narrow top-3.
RETRIEVAL_CANDIDATES_K = int(os.getenv("RETRIEVAL_CANDIDATES_K", "10"))

# RERANK_ENABLED: second-stage cross-encoder reranker over the FAISS
# candidates. If the model fails to load (e.g. constrained deploy
# environment), RAGPipeline falls back to plain FAISS-similarity
# order automatically — see rag_pipeline.py _load_reranker().
RERANK_ENABLED = os.getenv("RERANK_ENABLED", "true").lower() == "true"
RERANK_MODEL = os.getenv("RERANK_MODEL", "cross-encoder/ms-marco-MiniLM-L-6-v2")

# MIN_EVIDENCE_THRESHOLD: sigmoid-normalized (0-1) cross-encoder score
# the TOP reranked chunk must clear before the LLM is even called.
# Below this, the query is refused deterministically — cheaper and
# more reliable than trusting the LLM's own "insufficient context"
# instruction to fire every time. Calibrated against this project's
# knowledge base: a clearly relevant passage scores ~0.99+, a clearly
# irrelevant one scores ~0.00001 — 0.15 leaves wide margin either way.
# Only enforced when reranking actually ran (not in the FAISS-only
# fallback path, where cross-encoder scores don't exist).
MIN_EVIDENCE_THRESHOLD = float(os.getenv("MIN_EVIDENCE_THRESHOLD", "0.15"))

# ────────────────────────────────────────────────────────────────
# SECTION 6: LLM (Gemini Flash)
# ────────────────────────────────────────────────────────────────
LLM_MODEL = "gemini-2.0-flash-lite"  # free tier: 15 req/min
LLM_TEMPERATURE = 0.1  # 0.0 = deterministic, 1.0 = creative
# Medical use: always keep below 0.2
LLM_MAX_TOKENS = 512  # response length cap
LLM_MODEL = "openai/gpt-oss-20b"  # llama-3.1-8b-instant was deprecated by Groq
LLM_TEMPERATURE = 0.1
LLM_MAX_TOKENS = 512

# ────────────────────────────────────────────────────────────────
# SECTION 7: WHISPER STT
# ────────────────────────────────────────────────────────────────
# Model sizes and tradeoffs:
#   tiny   (39MB)  → fastest, less accurate for Indian languages
#   base   (74MB)  → good balance  ← USE THIS
#   small  (244MB) → better accuracy, 3x slower
#   medium (769MB) → near-perfect, very slow on CPU
WHISPER_MODEL_SIZE = "base"

# ────────────────────────────────────────────────────────────────
# SECTION 8: TRIAGE
# ────────────────────────────────────────────────────────────────
# These levels map directly to UI badge colours
TRIAGE_GREEN = "green"  # home care safe
TRIAGE_YELLOW = "yellow"  # monitor closely, see doctor today
TRIAGE_RED = "red"  # emergency — LLM response overridden

# ────────────────────────────────────────────────────────────────
# SECTION 9: SUPPORTED LANGUAGES
# ────────────────────────────────────────────────────────────────
# ISO 639-1 codes → full names for LLM prompts
SUPPORTED_LANGUAGES = {
    "hi": "Hindi",
    "ta": "Tamil",
    "te": "Telugu",
    "kn": "Kannada",
    "ml": "Malayalam",
    "mr": "Marathi",
    "bn": "Bengali",
    "en": "English",
}

# ────────────────────────────────────────────────────────────────
# SECTION 10: SERVER
# ────────────────────────────────────────────────────────────────
API_HOST = "0.0.0.0"  # accept connections from any IP
API_PORT = 8000
DEBUG = os.getenv("ENVIRONMENT", "development") == "development"
