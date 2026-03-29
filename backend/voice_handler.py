# ================================================================
# backend\voice_handler.py
# Speech-to-text using OpenAI Whisper.
# Handles audio files and raw bytes from FastAPI uploads.
# Returns text + detected language code for downstream translation.
# ================================================================

import os
import tempfile
import time
import logging
from pathlib import Path
from typing import Union

import whisper
import sys

sys.path.insert(0, "backend")

from config import WHISPER_MODEL_SIZE, SUPPORTED_LANGUAGES

logger = logging.getLogger(__name__)

# ── Singleton model ──────────────────────────────────────────────
# Loaded once at startup. Loading takes ~3s on first call.
# All subsequent requests reuse the same in-memory model instance.
_MODEL = None


def load_whisper_model(size: str = None) -> whisper.Whisper:
    """
    Load Whisper model — singleton pattern.
    Called at FastAPI startup so the first voice request is instant.

    Model sizes and tradeoffs:
    ┌──────────┬──────────┬─────────┬─────────────────────────┐
    │ Size     │ Disk     │ CPU Time│ Indian Language Quality  │
    ├──────────┼──────────┼─────────┼─────────────────────────┤
    │ tiny     │ 39 MB    │ ~0.5s   │ OK for simple sentences  │
    │ base     │ 74 MB    │ ~1.5s   │ Good — use this ✓        │
    │ small    │ 244 MB   │ ~4.5s   │ Better, 3x slower        │
    │ medium   │ 769 MB   │ ~12.0s  │ Near-perfect, too slow   │
    └──────────┴──────────┴─────────┴─────────────────────────┘
    """
    global _MODEL
    if _MODEL is None:
        model_size = size or WHISPER_MODEL_SIZE
        print(f"[Whisper] Loading '{model_size}' model...")
        t = time.time()
        _MODEL = whisper.load_model(model_size)
        print(f"[Whisper] Loaded in {round(time.time()-t, 1)}s")
    return _MODEL


def transcribe(audio_path: Union[str, Path]) -> dict:
    """
    Transcribe an audio file to text with language detection.

    Args:
        audio_path: Path to .mp3, .wav, .m4a, or .ogg file

    Returns:
        {
            "text"     : str   — transcribed text,
            "lang_code": str   — ISO 639-1 code ("hi", "te", "ta"...),
            "language" : str   — full name ("Hindi", "Telugu"...),
            "duration" : float — transcription time in seconds
        }

    Why task="transcribe" not "translate"?
    "transcribe" keeps the original language.
    "translate" would convert to English — we don't want that here
    because we need the original language for triage detection.
    """
    model = load_whisper_model()

    t = time.time()
    result = model.transcribe(
        str(audio_path),
        task="transcribe",  # keep original language
        fp16=False,  # disable fp16 for CPU stability
        language=None,  # auto-detect language
        verbose=False,
    )
    elapsed = round(time.time() - t, 2)

    lang_code = result.get("language", "en")
    language = SUPPORTED_LANGUAGES.get(lang_code, "English")

    logger.info(f"[Whisper] Transcribed in {elapsed}s | lang={lang_code}")

    return {
        "text": result["text"].strip(),
        "lang_code": lang_code,
        "language": language,
        "duration": elapsed,
    }


def transcribe_bytes(audio_bytes: bytes, extension: str = ".mp3") -> dict:
    """
    Transcribe raw audio bytes — used by FastAPI's /ask-voice endpoint.
    Writes to a temp file, transcribes, then cleans up.

    Args:
        audio_bytes: Raw bytes from FastAPI UploadFile.read()
        extension  : ".mp3", ".wav", ".ogg", ".m4a"

    Returns:
        Same dict as transcribe()
    """
    with tempfile.NamedTemporaryFile(suffix=extension, delete=False) as tmp:
        tmp.write(audio_bytes)
        tmp_path = tmp.name

    try:
        return transcribe(tmp_path)
    finally:
        os.unlink(tmp_path)  # always delete temp file
