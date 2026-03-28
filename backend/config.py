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
BASE_DIR        = Path(__file__).parent.parent  # project root
DATA_DIR        = BASE_DIR / "data"
VECTORSTORE_DIR = BASE_DIR / "vectorstore"
LOGS_DIR        = BASE_DIR / "logs"
FRONTEND_DIR    = BASE_DIR / "frontend"

for d in [DATA_DIR, VECTORSTORE_DIR, LOGS_DIR, FRONTEND_DIR]:
    d.mkdir(exist_ok=True)

# ────────────────────────────────────────────────────────────────
# SECTION 2: API KEYS
# ────────────────────────────────────────────────────────────────
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
SARVAM_API_KEY = os.getenv("SARVAM_API_KEY", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

if not GEMINI_API_KEY:
    raise ValueError(
        "GEMINI_API_KEY not found.\n"
        "Add to .env: GEMINI_API_KEY=AIzaSy..."
    )

# ────────────────────────────────────────────────────────────────
# SECTION 3: EMBEDDING MODEL
# ────────────────────────────────────────────────────────────────
# paraphrase-multilingual-MiniLM-L12-v2 chosen because:
#   ✓ Supports Hindi, Tamil, Telugu, Kannada natively
#   ✓ 384-dim vectors — fast on CPU, accurate enough
#   ✓ Free, no API key, downloads once (~120MB)
#   ✓ Cross-lingual: Hindi query retrieves English passage correctly
EMBEDDING_MODEL  = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
EMBEDDING_DEVICE = "cpu"  # change to "cuda" if you have NVIDIA GPU
EMBEDDING_DIM    = 384    # output dimensions of this model

# ────────────────────────────────────────────────────────────────
# SECTION 4: CHUNKING
# ────────────────────────────────────────────────────────────────
# Tested: 100, 200, 300, 500 words.
# 300 chosen: one medical topic per chunk, overlap prevents cuts.
CHUNK_SIZE    = 300  # words per chunk (not characters)
CHUNK_OVERLAP =  50  # words shared with previous chunk

# ────────────────────────────────────────────────────────────────
# SECTION 5: RETRIEVAL (RAG)
# ────────────────────────────────────────────────────────────────
# TOP_K_RETRIEVAL: how many chunks to retrieve per query
# Tested k=1 (misses context), k=3 (best), k=5 (dilutes prompt)
TOP_K_RETRIEVAL = 3
RETRIEVAL_TYPE  = "similarity"  # "similarity" or "mmr" (diverse results)

# ────────────────────────────────────────────────────────────────
# SECTION 6: LLM (Gemini Flash)
# ────────────────────────────────────────────────────────────────
LLM_MODEL = "gemini-2.0-flash-lite"  # free tier: 15 req/min
LLM_TEMPERATURE = 0.1   # 0.0 = deterministic, 1.0 = creative
                         # Medical use: always keep below 0.2
LLM_MAX_TOKENS  = 512    # response length cap
LLM_MODEL = "llama-3.1-8b-instant"  # free on Groq
LLM_TEMPERATURE = 0.1
LLM_MAX_TOKENS  = 512

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
TRIAGE_GREEN  = "green"   # home care safe
TRIAGE_YELLOW = "yellow"  # monitor closely, see doctor today
TRIAGE_RED    = "red"     # emergency — LLM response overridden

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
API_HOST = "0.0.0.0"   # accept connections from any IP
API_PORT = 8000
DEBUG    = os.getenv("ENVIRONMENT", "development") == "development"