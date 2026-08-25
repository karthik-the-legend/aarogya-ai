# ================================================================
# backend\observability.py
# Structured request logging — one JSON line per request, appended to
# logs/requests.jsonl (gitignored, local-only, never shipped anywhere).
#
# Privacy by construction, not by discipline: log_request() only
# accepts the specific fields below. There is no "extra kwargs" escape
# hatch, so a future caller can't accidentally pass the raw query text
# or answer content through this function even by mistake — the
# request_id is enough to correlate log lines without ever writing
# what the user actually asked.
# ================================================================

import json
import time
import uuid
from typing import Optional

from config import LOGS_DIR, LOGGING_ENABLED

_LOG_PATH = LOGS_DIR / "requests.jsonl"


def new_request_id() -> str:
    """Short random id — correlates log lines for one request without
    identifying the user or being derived from anything they typed."""
    return uuid.uuid4().hex[:12]


def log_request(
    request_id: str,
    detected_language: Optional[str],
    intent: Optional[str],
    triage_level: str,
    triage_override: bool,
    evidence_score: Optional[float],
    grounded: Optional[bool],
    refused: bool,
    n_sources: int,
    source_files: list,
    latency_ms: int,
) -> None:
    """
    Append one structured log line. No-op if LOGGING_ENABLED is false.
    Never raises — a logging failure must not break a health query.
    """
    if not LOGGING_ENABLED:
        return

    final_action = "refused" if refused else ("emergency_override" if triage_level == "red" else "answered")

    entry = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "request_id": request_id,
        "language": detected_language,
        "intent": intent,
        "triage_level": triage_level,
        "triage_override": triage_override,
        "evidence_score": evidence_score,
        "grounded": grounded,
        "final_action": final_action,
        "n_sources": n_sources,
        "source_files": source_files,  # filenames only — no chunk content
        "latency_ms": latency_ms,
    }

    try:
        with open(_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception as e:
        print(f"  [observability] Failed to write log entry: {e}")
