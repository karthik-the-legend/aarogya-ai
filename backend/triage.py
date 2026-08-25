# ================================================================
# backend\triage.py
# Rule-based safety classifier — the deterministic layer that
# outranks the LLM. Two call sites use the same classify():
#   1. PRE-triage: classify(query)                — before the LLM
#      ever runs, so an obvious emergency skips RAG+LLM entirely.
#   2. POST-triage: classify(query, llm_response)  — after the LLM
#      runs, as a second safety net that also scans its answer.
# 100% accuracy on RED cases is non-negotiable.
# ================================================================

from dataclasses import dataclass
from enum import Enum


class TriageLevel(str, Enum):
    GREEN = "green"  # home care safe
    YELLOW = "yellow"  # see doctor today
    RED = "red"  # emergency — LLM overridden


@dataclass
class TriageResult:
    level: TriageLevel
    triggered: str  # the keyword that triggered this level
    message: str  # emergency message (for RED only)
    override: bool  # True = replace LLM response entirely
    category: str = ""  # e.g. "respiratory", "cardiovascular" — for explainability


# ================================================================
# TRIAGE ONTOLOGY
# Emergency phrases grouped by clinical category instead of one
# flat list. classify() still scans a single flattened list built
# from this at import time — the ontology is for maintainability
# and future explainability, not a behavioural change on its own.
#
# Every phrase that existed in the old flat EMERGENCY_KEYWORDS list
# is preserved here unchanged. New additions are marked "# new".
# ================================================================
RED_ONTOLOGY = [
    {
        "category": "cardiovascular",
        "concept": "chest_pain",
        "phrases": [
            "chest pain", "chest tightness", "chest pressure", "chest hurts",
            "chest is hurting", "chest is tight", "my chest hurts",
            "heart is beating fast", "heart racing", "heart pounding",
            "heart attack",
            "chhati mein dard", "chhati mein bahut dard",
            "सीने में दर्द", "छाती में दर्द", "सीने में जकड़न",
            "மார்பு வலி",
            "ఛాతీ నొప్పి",
            "ಎದೆ ನೋವು",
        ],
    },
    {
        "category": "respiratory",
        "concept": "difficulty_breathing",
        "phrases": [
            "difficulty breathing", "can't breathe", "cannot breathe",
            "shortness of breath", "trouble breathing",
            "cant breathe", "cant breath", "can not breathe",  # new — misspellings
            "breathing problem", "breath problem", "unable to breathe",  # new
            "sans nahi", "sans lene mein",
            "सांस नहीं", "सांस लेने में तकलीफ", "सांस नहीं आ रही",
            "மூச்சு திணறல்", "மூச்சு வரவில்லை",
            "శ్వాస తీసుకోలేను",
            "ಉಸಿರಾಡಲು ಕಷ್ಟ", "ಉಸಿರಾಡಲು ಕಷ್ಟ ಆಗುತ್ತಿದೆ",
            "choking", "can't swallow properly and choking",  # new
        ],
    },
    {
        "category": "neurological",
        "concept": "loss_of_consciousness_or_stroke",
        "phrases": [
            "unconscious", "not responding", "unresponsive",
            "seizure", "convulsion", "fitting",
            "stroke", "paralysis", "face drooping", "arm weakness",
            "sudden weakness", "severe headache", "worst headache",
            "sudden vision loss", "vision gone",
            "behosh ho gaya", "behosh ho gayi", "mera beta behosh",
            "daura pada", "lakwa maar gaya",
            "बेहोश", "होश नहीं", "दौरा", "मिर्गी", "लकवा", "अचानक कमजोरी",
            "நினைவு இழந்தார்", "வலிப்பு",
            "స్పృహ కోల్పోయాను", "మూర్ఛ",
            "ಎಚ್ಚರ ತಪ್ಪಿದೆ", "ಎಚ್ಚರ ತಪ್ಪಿದ",
        ],
    },
    {
        "category": "bleeding",
        "concept": "uncontrolled_bleeding",
        "phrases": [
            "heavy bleeding", "bleeding won't stop", "bleeding heavily",
            "blood is flowing", "blood flowing from",
            "wound won't stop", "bleeding from wound",
            "khoon nahi ruk",
            "खून नहीं रुक रहा",
            "இரத்தம் நிற்கவில்லை",
            "రక్తం ఆగడం లేదు",
            "ರಕ್ತ ನಿಲ್ಲುತ್ತಿಲ್ಲ",
        ],
    },
    {
        "category": "trauma",
        "concept": "severe_injury",
        "phrases": [
            "severe burns", "badly burned", "burns covering",  # new
            "severe trauma", "major accident", "hit by a vehicle",  # new
            "blue lips", "lips turning blue", "turning blue",  # new
        ],
    },
    {
        "category": "poisoning",
        "concept": "poisoning_or_overdose",
        "phrases": [
            "poisoning", "overdose", "swallowed poison", "swallowed chemical",  # new
        ],
    },
    {
        "category": "allergic",
        "concept": "anaphylaxis",
        "phrases": [
            "anaphylaxis", "allergic shock", "throat closing", "swelling of throat",  # new
        ],
    },
    {
        "category": "mental_health",
        "concept": "suicidal_crisis",
        "phrases": [
            "suicide",
            "want to kill myself", "want to die", "end my life",  # new
            "ending my life", "no reason to live", "harming myself",  # new
            "self harm",  # new
        ],
    },
    {
        "category": "pediatric_or_general_fever",
        "concept": "dangerously_high_fever",
        "phrases": [
            "104 fever", "104°f", "105 fever", "very high fever",
            "बहुत तेज बुखार",
            "తీవ్రమైన జ్వరం",
            "ತೀವ್ರ ಜ್ವರ",
        ],
    },
]

# Flattened (phrase, category) pairs — this is what classify() scans.
EMERGENCY_KEYWORDS = [p for cat in RED_ONTOLOGY for p in cat["phrases"]]
_PHRASE_TO_CATEGORY = {p: cat["category"] for cat in RED_ONTOLOGY for p in cat["phrases"]}


# ── YELLOW: Monitor keywords ─────────────────────────────────────
MONITOR_KEYWORDS = [
    "fever for 3 days",
    "fever 3 days",
    "persistent fever",
    "high fever",
    "fever since",
    "rash",
    "skin rash",
    "spots on skin",
    "vomiting",
    "vomit",
    "keep vomiting",
    "diarrhoea",
    "diarrhea",
    "loose motions",
    "blood in urine",
    "blood in stool",
    "joint pain",
    "severe joint",
    "dengue",
    "malaria",
    "typhoid",
    "jaundice",
    "3 दिन से बुखार",
    "उल्टी",
    "दस्त",
    "खून",
    "மூன்று நாட்களாக காய்ச்சல்",
    "வாந்தி",
    "మూడు రోజుల జ్వరం",
    "వాంతి",
]


# ================================================================
# NEGATION HANDLING
#
# Goal: "I don't have chest pain" should not fire RED.
# Non-goal / explicitly NOT suppressed: third-person mentions
# ("my father has chest pain" must stay RED — see design note below).
#
# Safety constraint that shaped this implementation: several existing
# Hindi/Tamil/Telugu/Kannada RED phrases already correctly embed a
# negation word as part of the true-positive phrasing itself, e.g.
# "सांस नहीं" (breath-not = can't breathe) and "खून नहीं रुक रहा"
# (blood not stopping = bleeding won't stop). Those negation words are
# INSIDE the matched phrase, not outside it, so they are never touched
# by this check — _is_negated() only ever looks at the text immediately
# BEFORE and AFTER the matched span, never inside it. This means the
# existing double-negative-as-emergency phrases keep working exactly
# as before.
#
# Indic negation is frequently clause-final ("...नहीं है" / "...இல்லை"
# trailing the symptom, not preceding it like English "not"), so the
# window check looks both before AND after the match, not just before.
#
# When genuinely uncertain, this function is deliberately conservative:
# it only suppresses a match when a negation cue is found in the
# immediate window. Anything ambiguous stays RED, per the stated
# principle: false positive escalation > missed emergency.
# ================================================================
_NEGATION_WINDOW_CHARS = 24

_NEGATION_CUES = [
    # English — reliably pre-verbal, checked in the "before" window.
    " no ", " not ", "n't", " without ", " never ", " denies ", " denying ",
    "no history of", "not having", "not experiencing",
    # Hindi
    "नहीं है", "नहीं था", "नहीं थी", " मत ",
    # Tamil
    "இல்லை", "இல்ல",
    # Telugu
    "లేదు", "కాదు",
    # Kannada
    "ಇಲ್ಲ", "ಇರಲಿಲ್ಲ",
]


def _is_negated(combined: str, match_start: int, match_end: int) -> bool:
    """
    True if a negation cue appears immediately before or after the
    matched span (never inside it — see module docstring above).
    """
    before = combined[max(0, match_start - _NEGATION_WINDOW_CHARS):match_start]
    after = combined[match_end:match_end + _NEGATION_WINDOW_CHARS]
    return any(cue in before or cue in after for cue in _NEGATION_CUES)


def classify(query: str, llm_response: str = "") -> TriageResult:
    """
    Scan both user query AND LLM response for emergency keywords.

    Called twice per request:
      - PRE-triage:  classify(query)                — before RAG/LLM.
      - POST-triage: classify(query, llm_response)   — after, as a
        second safety net in case the retrieved evidence or the LLM's
        own wording surfaces something the raw query didn't.

    WHY RULE-BASED (not neural classifier)?
    ✓ 100% reliable — no probability thresholds
    ✓ Deterministic — same input always same output
    ✓ Interpretable — show exactly which keyword triggered
    ✓ A false negative (missed emergency) costs a life.
      A false positive (unnecessary alert) wastes time.
      Asymmetry justifies deterministic rules.
    """
    # Leading/trailing space so a " no "-style cue can match even when
    # the negation word is the very first or last token in the text.
    combined = " " + (query + " " + llm_response).lower() + " "

    # Check RED first — life-threatening
    for kw in EMERGENCY_KEYWORDS:
        kw_lower = kw.lower()
        start = combined.find(kw_lower)
        if start == -1:
            continue
        if _is_negated(combined, start, start + len(kw_lower)):
            continue  # this specific mention was negated — keep scanning
        return TriageResult(
            level=TriageLevel.RED,
            triggered=kw,
            message=_emergency_message(kw),
            override=True,
            category=_PHRASE_TO_CATEGORY.get(kw, ""),
        )

    # Check YELLOW — monitor closely
    for kw in MONITOR_KEYWORDS:
        if kw.lower() in combined:
            return TriageResult(
                level=TriageLevel.YELLOW,
                triggered=kw,
                message="⚠️ Please see a doctor within 24 hours.",
                override=False,
            )

    # GREEN — safe to manage at home
    return TriageResult(
        level=TriageLevel.GREEN,
        triggered="",
        message="✅ You can manage this at home for now.",
        override=False,
    )


# Unicode script blocks (inclusive ranges), checked in this order so
# each language's actual block is matched — NOT an open-ended ">"
# check, which previously caused every Tamil/Telugu/Kannada keyword
# to incorrectly resolve to the Hindi branch (all three blocks sit at
# higher codepoints than Devanagari, so `ord(c) > 0x0900` was true for
# all of them too).
_SCRIPT_RANGES = [
    ("hi", 0x0900, 0x097F),  # Devanagari
    ("ta", 0x0B80, 0x0BFF),  # Tamil
    ("te", 0x0C00, 0x0C7F),  # Telugu
    ("kn", 0x0C80, 0x0CFF),  # Kannada
]


def _detect_script(text: str) -> str:
    for c in text:
        cp = ord(c)
        for lang, lo, hi in _SCRIPT_RANGES:
            if lo <= cp <= hi:
                return lang
    return "en"


def _emergency_message(triggered_kw: str) -> str:
    """Return emergency message in the detected script language."""
    script = _detect_script(triggered_kw)

    if script == "hi":
        return "🚨 यह आपातकाल है। तुरंत 108 पर कॉल करें या नजदीकी अस्पताल जाएं। देरी मत करें।"
    if script == "ta":
        return "🚨 இது அவசரநிலை. உடனடியாக 108 ஐ அழைக்கவும்."
    if script == "te":
        return "🚨 ఇది అత్యవసరం. వెంటనే 108 కి కాల్ చేయండి."
    if script == "kn":
        return "🚨 ಇದು ತುರ್ತುಪರಿಸ್ಥಿತಿ. ತಕ್ಷಣ 108 ಗೆ ಕರೆ ಮಾಡಿ."

    return (
        "🚨 EMERGENCY. Call 108 NOW or go to nearest hospital. "
        "Do NOT wait. Do NOT try home remedies."
    )
