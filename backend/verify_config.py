import sys

sys.path.insert(0, "backend")

from config import (
    BASE_DIR,
    DATA_DIR,
    VECTORSTORE_DIR,
    GEMINI_API_KEY,
    EMBEDDING_MODEL,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
    TOP_K_RETRIEVAL,
    LLM_MODEL,
    LLM_TEMPERATURE,
    SUPPORTED_LANGUAGES,
    API_PORT,
)

print("config.py: OK")
print(f"  BASE_DIR:      {BASE_DIR}")
print(f"  DATA_DIR:      {DATA_DIR}")
print(f"  VECTORSTORE:   {VECTORSTORE_DIR}")
print(f"  EMBEDDING:     {EMBEDDING_MODEL[-20:]}")
print(f"  CHUNK_SIZE:    {CHUNK_SIZE}")
print(f"  CHUNK_OVERLAP: {CHUNK_OVERLAP}")
print(f"  TOP_K:         {TOP_K_RETRIEVAL}")
print(f"  LLM_MODEL:     {LLM_MODEL}")
print(f"  TEMP:          {LLM_TEMPERATURE}")
print(f"  LANGUAGES:     {list(SUPPORTED_LANGUAGES.keys())}")
print(f"  API_PORT:      {API_PORT}")
print(f"  KEY set:       {bool(GEMINI_API_KEY)}")
