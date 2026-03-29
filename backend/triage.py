# ================================================================
# backend\triage.py
# Rule-based safety classifier. Runs AFTER the LLM generates
# a response. Can completely override the LLM answer.
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


# ── RED: Life-threatening keywords ──────────────────────────────
EMERGENCY_KEYWORDS = [
    # ── English ─────────────────────────────────────────────────
    "chest pain",
    "chest tightness",
    "chest pressure",
    "difficulty breathing",
    "can't breathe",
    "cannot breathe",
    "shortness of breath",
    "trouble breathing",
    "unconscious",
    "not responding",
    "unresponsive",
    "seizure",
    "convulsion",
    "fitting",
    "heavy bleeding",
    "bleeding won't stop",
    "bleeding heavily",
    "heart attack",
    "stroke",
    "paralysis",
    "face drooping",
    "arm weakness",
    "sudden weakness",
    "104 fever",
    "104°f",
    "105 fever",
    "very high fever",
    "poisoning",
    "overdose",
    "suicide",
    "severe headache",
    "worst headache",
    "sudden vision loss",
    "vision gone",
    "anaphylaxis",
    "allergic shock",
    "chest hurts",
    "chest is hurting",
    "chest is tight",
    "heart is beating fast",
    "heart racing",
    "heart pounding",
    "blood is flowing",
    "blood flowing from",
    "wound won't stop",
    "bleeding from wound",
    "my chest hurts",
    # ── Transliterated Hindi (Roman script) ─────────────────────
    "chhati mein dard",
    "chhati mein bahut dard",
    "sans nahi",
    "sans lene mein",
    "behosh ho gaya",
    "behosh ho gayi",
    "mera beta behosh",
    "daura pada",
    "khoon nahi ruk",
    "lakwa maar gaya",
    # ── Hindi (Devanagari) ───────────────────────────────────────
    "सीने में दर्द",
    "छाती में दर्द",
    "सीने में जकड़न",
    "सांस नहीं",
    "सांस लेने में तकलीफ",
    "सांस नहीं आ रही",
    "बेहोश",
    "होश नहीं",
    "दौरा",
    "मिर्गी",
    "बहुत तेज बुखार",
    "खून नहीं रुक रहा",
    "लकवा",
    "अचानक कमजोरी",
    # ── Tamil ────────────────────────────────────────────────────
    "மார்பு வலி",
    "மூச்சு திணறல்",
    "மூச்சு வரவில்லை",
    "நினைவு இழந்தார்",
    "வலிப்பு",
    "இரத்தம் நிற்கவில்லை",
    # ── Telugu ───────────────────────────────────────────────────
    "ఛాతీ నొప్పి",
    "శ్వాస తీసుకోలేను",
    "స్పృహ కోల్పోయాను",
    "మూర్ఛ",
    "రక్తం ఆగడం లేదు",
    "తీవ్రమైన జ్వరం",
    # ── Kannada ──────────────────────────────────────────────────
    "ಎದೆ ನೋವು",
    "ಉಸಿರಾಡಲು ಕಷ್ಟ",
    "ಉಸಿರಾಡಲು ಕಷ್ಟ ಆಗುತ್ತಿದೆ",  # ← add this
    "ಎಚ್ಚರ ತಪ್ಪಿದೆ",
    "ಎಚ್ಚರ ತಪ್ಪಿದ",  # ← add this variant
    "ರಕ್ತ ನಿಲ್ಲುತ್ತಿಲ್ಲ",
    "ಉసಿರಾಡಲು ಕಷ್ಟ ಆಗುತ್ತಿದೆ",
    "ತೀವ್ರ ಜ್ವರ",
]

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


def classify(query: str, llm_response: str = "") -> TriageResult:
    """
    Scan both user query AND LLM response for emergency keywords.

    WHY RULE-BASED (not neural classifier)?
    ✓ 100% reliable — no probability thresholds
    ✓ Deterministic — same input always same output
    ✓ Interpretable — show exactly which keyword triggered
    ✓ A false negative (missed emergency) costs a life.
      A false positive (unnecessary alert) wastes time.
      Asymmetry justifies deterministic rules.
    """
    combined = (query + " " + llm_response).lower()

    # Check RED first — life-threatening
    for kw in EMERGENCY_KEYWORDS:
        if kw.lower() in combined:
            return TriageResult(
                level=TriageLevel.RED,
                triggered=kw,
                message=_emergency_message(kw),
                override=True,
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


def _emergency_message(triggered_kw: str) -> str:
    """Return emergency message in the detected script language."""

    if any(ord(c) > 0x0900 for c in triggered_kw):  # Hindi
        return "🚨 यह आपातकाल है। तुरंत 108 पर कॉल करें " "या नजदीकी अस्पताल जाएं। देरी मत करें।"
    elif any(ord(c) > 0x0B80 for c in triggered_kw):  # Tamil
        return "🚨 இது அவசரநிலை. உடனடியாக 108 ஐ அழைக்கவும்."
    elif any(ord(c) > 0x0C00 for c in triggered_kw):  # Telugu
        return "🚨 ఇది అత్యవసరం. వెంటనే 108 కి కాల్ చేయండి."
    elif any(ord(c) > 0x0C80 for c in triggered_kw):  # Kannada
        return "🚨 ಇದು ತುರ್ತುಪರಿಸ್ಥಿತಿ. ತಕ್ಷಣ 108 ಗೆ ಕರೆ ಮಾಡಿ."

    return (
        "🚨 EMERGENCY. Call 108 NOW or go to nearest hospital. "
        "Do NOT wait. Do NOT try home remedies."
    )
