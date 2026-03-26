# ================================================================
# backend\translate.py
# Bidirectional translation for Indian languages ↔ English.
# Used by the RAG pipeline to:
#   1. Translate user query (Hindi/Tamil/Telugu/Kannada) → English
#      so FAISS can search the English medical knowledge base.
#   2. Translate LLM response (English) → user's language
#      so the farmer reads the answer in their own language.
# ================================================================

import os
import time
import logging
from functools import lru_cache
from typing import Optional

from deep_translator import GoogleTranslator

# Optional: Sarvam AI for better Indian language quality
# Only used if SARVAM_API_KEY is set in .env
try:
    import requests as _requests
    _REQUESTS_AVAILABLE = True
except ImportError:
    _REQUESTS_AVAILABLE = False

logger = logging.getLogger(__name__)

# ── Language Code Maps ───────────────────────────────────────────
# ISO 639-1 code → Sarvam AI's xx-IN format
_SARVAM_CODES: dict = {
    "hi": "hi-IN",  # Hindi
    "ta": "ta-IN",  # Tamil
    "te": "te-IN",  # Telugu
    "kn": "kn-IN",  # Kannada
    "ml": "ml-IN",  # Malayalam
    "mr": "mr-IN",  # Marathi
    "bn": "bn-IN",  # Bengali
    "en": "en-IN",  # English (Indian variant)
}

# ── Core Functions ───────────────────────────────────────────────
# @lru_cache caches the last 512 unique (text, lang_code) pairs.
# Why cache? "fever", "headache", "cold" repeat in 60% of queries.
# A cached translation is ~0ms vs ~200ms network call.
@lru_cache(maxsize=512)
def to_english(text: str, lang_code: str = "hi") -> str:
    """
    Translate Indian language text to English.
    Called BEFORE embedding the user query for FAISS search.

    Args:
        text:      User's health question (e.g. "मुझे बुखार है")
        lang_code: ISO 639-1 code (e.g. "hi", "ta", "te", "kn")

    Returns:
        English translation (e.g. "I have fever")

    Notes:
        - If lang_code is "en", returns text unchanged (no API call)
        - Tries Google Translate first
        - Falls back to Sarvam AI if SARVAM_API_KEY is set
        - lru_cache means identical queries are instant after first call
    """
    # Already English — no translation needed
    if lang_code == "en":
        return text.strip()

    try:
        result = _google_translate(text, source=lang_code, target="en")
        logger.debug(f"[translate] {lang_code}→en: '{text[:40]}' → '{result[:40]}'")
        return result
    except Exception as e:
        logger.warning(f"Google Translate failed: {e}. Trying Sarvam AI...")
        sarvam_key = os.getenv("SARVAM_API_KEY", "")
        if sarvam_key and _REQUESTS_AVAILABLE:
            return _sarvam_translate(text, lang_code, "en", sarvam_key)
        logger.error("Both translators failed. Returning original text.")
        return text.strip()


@lru_cache(maxsize=512)
def from_english(text: str, target_lang: str = "en") -> str:
    """
    Translate English LLM response back to the user's language.
    Called AFTER Gemini generates the answer.

    Args:
        text:        English response from Gemini Flash
        target_lang: ISO 639-1 target language code

    Returns:
        Translated response in the user's language

    Notes:
        - Sarvam AI tried FIRST for responses (better medical terminology)
        - Falls back to Google Translate if Sarvam fails
        - If target_lang is "en", returns text unchanged
    """
    if target_lang == "en":
        return text.strip()

    sarvam_key = os.getenv("SARVAM_API_KEY", "")

    # For responses: try Sarvam first (better Indian language quality)
    if sarvam_key and _REQUESTS_AVAILABLE:
        try:
            result = _sarvam_translate(text, "en", target_lang, sarvam_key)
            logger.debug(f"[translate] en→{target_lang} via Sarvam")
            return result
        except Exception as e:
            logger.warning(f"Sarvam failed: {e}. Using Google Translate...")

    # Fall back to Google Translate
    try:
        result = _google_translate(text, source="en", target=target_lang)
        logger.debug(f"[translate] en→{target_lang} via Google")
        return result
    except Exception as e:
        logger.error(f"Both translators failed for en→{target_lang}: {e}")
        return text.strip()


# ── Private Helper Functions ─────────────────────────────────────
def _google_translate(text: str, source: str, target: str) -> str:
    """
    Translate using Google Translate via the deep-translator library.
    No API key required. Rate limit: ~100 requests/minute.

    Why deep-translator over googletrans?
    googletrans is unmaintained and breaks frequently.
    deep-translator is actively maintained and more stable.
    """
    if not text or not text.strip():
        return ""

    translator = GoogleTranslator(source=source, target=target)
    translated = translator.translate(text.strip())
    return translated if translated else text.strip()


def _sarvam_translate(
    text: str,
    source: str,
    target: str,
    api_key: str
) -> str:
    """
    Translate using Sarvam AI API — purpose-built for Indian languages.
    Better than Google for medical terminology and colloquial phrases.
    Free tier: 1 million characters/month.
    Get key: https://app.sarvam.ai

    Sarvam uses xx-IN format codes, not standard ISO 639-1.
    e.g. "hi" → "hi-IN", "ta" → "ta-IN"
    """
    import requests

    src_sarvam = _SARVAM_CODES.get(source, source)
    tgt_sarvam = _SARVAM_CODES.get(target, target)

    response = requests.post(
        "https://api.sarvam.ai/translate",
        headers={"api-subscription-key": api_key},
        json={
            "input"          : text.strip(),
            "source_language_code": src_sarvam,
            "target_language_code": tgt_sarvam,
            "mode"           : "formal",   # formal = medical-appropriate tone
            "model"          : "mayura:v1"
        },
        timeout=10
    )
    response.raise_for_status()
    return response.json()["translated_text"]


# ── Utility Functions ────────────────────────────────────────────
def get_cache_info() -> dict:
    """Return cache statistics — useful for debugging and interview demos."""
    return {
        "to_english" : to_english.cache_info()._asdict(),
        "from_english": from_english.cache_info()._asdict(),
    }


def clear_cache() -> None:
    """Clear both translation caches. Call if memory usage is too high."""
    to_english.cache_clear()
    from_english.cache_clear()