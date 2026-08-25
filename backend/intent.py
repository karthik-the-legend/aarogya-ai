# ================================================================
# backend\intent.py
# Deterministic medical intent classification + lightweight entity
# extraction, run on the English-translated query before retrieval.
#
# Rule-based, not LLM-based, for the same reason triage.py is:
# deterministic, interpretable, and doesn't add another model call to
# every request just to answer "what kind of question is this?". Entity
# extraction is intentionally conservative — it only reports what it
# can find with a plain regex/keyword match. It never guesses; missing
# fields are None, per the project's "do not invent missing
# information" rule.
# ================================================================

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional


class MedicalIntent(str, Enum):
    SYMPTOM = "symptom"
    DISEASE_INFORMATION = "disease_information"
    MEDICATION = "medication"
    FIRST_AID = "first_aid"
    PREVENTION = "prevention"
    EMERGENCY = "emergency"
    CHILD_HEALTH = "child_health"
    PREGNANCY = "pregnancy"
    ELDERLY_HEALTH = "elderly_health"
    CHRONIC_CONDITION = "chronic_condition"
    NUTRITION = "nutrition"
    VACCINATION = "vaccination"
    HYGIENE = "hygiene"
    GENERAL_HEALTH = "general_health"
    UNKNOWN = "unknown"


# Checked in this order — first match wins. Order encodes priority for
# queries that could plausibly match more than one category (e.g. "is
# it safe to take ibuprofen while pregnant" should read as PREGNANCY,
# not just MEDICATION, since the age/condition context changes what a
# safe answer looks like).
_INTENT_KEYWORDS = [
    (MedicalIntent.EMERGENCY, [
        "emergency", "urgent care", "life threatening", "call 108", "call ambulance",
    ]),
    (MedicalIntent.PREGNANCY, [
        "pregnant", "pregnancy", "expecting a baby", "prenatal", "trimester", "breastfeeding",
    ]),
    (MedicalIntent.CHILD_HEALTH, [
        "infant", "newborn", "toddler", "baby", "my child", "my son", "my daughter", "kids", "months old",
    ]),
    (MedicalIntent.ELDERLY_HEALTH, [
        "elderly", "senior citizen", "old age", "grandmother", "grandfather", "grandma", "grandpa",
    ]),
    (MedicalIntent.VACCINATION, [
        "vaccine", "vaccination", "immunization", "immunisation", "vaccinated",
    ]),
    (MedicalIntent.MEDICATION, [
        "medicine", "medication", "dosage", "dose", "tablet", "pill", "antibiotic",
        "prescription", "can i take", "is it safe to take", "mg ", "ibuprofen",
        "paracetamol", "acetaminophen", "aspirin",
    ]),
    (MedicalIntent.FIRST_AID, [
        "first aid", "what should i do right now", "immediate care", "wound care",
        "how to stop bleeding", "cpr", "choking on",
    ]),
    (MedicalIntent.CHRONIC_CONDITION, [
        "diabetes", "diabetic", "hypertension", "high blood pressure", "asthma",
        "chronic", "long-term condition",
    ]),
    (MedicalIntent.PREVENTION, [
        "prevent", "avoid getting", "protect myself from", "how to avoid", "reduce risk of",
        "stop the spread",
    ]),
    (MedicalIntent.NUTRITION, [
        "diet", "what should i eat", "nutrition", "fluids", "hydration", "food to avoid",
    ]),
    (MedicalIntent.HYGIENE, [
        "hand washing", "hygiene", "sanitation", "clean water", "wash hands",
    ]),
    (MedicalIntent.SYMPTOM, [
        "symptom", "sign of", "signs of", "i have", "i feel", "hurts", "pain",
        "ache", "fever", "rash",
    ]),
    (MedicalIntent.DISEASE_INFORMATION, [
        "what is dengue", "what is malaria", "what is typhoid", "what is tuberculosis",
        "what is cholera", "what is influenza", "about dengue", "about malaria",
        "dengue", "malaria", "typhoid", "tuberculosis", "cholera", "influenza",
    ]),
]


def classify_intent(query_en: str) -> MedicalIntent:
    q = query_en.lower()
    for intent, keywords in _INTENT_KEYWORDS:
        if any(kw in q for kw in keywords):
            return intent
    return MedicalIntent.GENERAL_HEALTH


# ── Entity extraction ────────────────────────────────────────────
_DISEASE_NAMES = [
    "dengue", "malaria", "typhoid", "tuberculosis", "tb", "cholera",
    "influenza", "flu", "common cold", "diarrhoea", "diarrhea", "skin infection",
]

_AGE_YEARS_RE = re.compile(r"(\d{1,3})\s*(?:years?|yrs?|y/o|yo)\s*(?:old)?", re.IGNORECASE)
_AGE_MONTHS_RE = re.compile(r"(\d{1,2})\s*months?\s*old", re.IGNORECASE)
_DURATION_RE = re.compile(
    r"(\d{1,3})\s*(hour|hours|day|days|week|weeks|month|months)\b", re.IGNORECASE
)


@dataclass
class ExtractedEntities:
    age_years: Optional[float] = None
    age_group: Optional[str] = None  # infant | child | adolescent | adult | elderly
    duration_raw: Optional[str] = None
    mentioned_diseases: List[str] = field(default_factory=list)
    pregnancy_mentioned: bool = False

    def is_empty(self) -> bool:
        return (
            self.age_years is None
            and self.age_group is None
            and self.duration_raw is None
            and not self.mentioned_diseases
            and not self.pregnancy_mentioned
        )

    def as_prompt_line(self) -> str:
        """One-line summary for the LLM prompt, empty string if nothing found."""
        if self.is_empty():
            return ""
        parts = []
        if self.age_group:
            age_str = f"{self.age_group}"
            if self.age_years is not None:
                age_str += f" (~{self.age_years:g} years old)"
            parts.append(f"patient age group: {age_str}")
        if self.pregnancy_mentioned:
            parts.append("pregnancy mentioned")
        if self.duration_raw:
            parts.append(f"duration mentioned: {self.duration_raw}")
        if self.mentioned_diseases:
            parts.append("disease(s) mentioned: " + ", ".join(self.mentioned_diseases))
        return "; ".join(parts)


def _age_group_for(age_years: Optional[float], text: str) -> Optional[str]:
    if age_years is not None:
        if age_years < 2:
            return "infant"
        if age_years <= 12:
            return "child"
        if age_years <= 17:
            return "adolescent"
        if age_years < 60:
            return "adult"
        return "elderly"
    # No explicit number — fall back to keyword context, since "my baby
    # has a fever" is a real, common, and clinically relevant phrasing
    # with no number attached at all.
    if any(w in text for w in ["infant", "newborn", "baby"]):
        return "infant"
    if any(w in text for w in ["toddler", "my child", "my son", "my daughter", "kid "]):
        return "child"
    if any(w in text for w in ["elderly", "senior citizen", "old age", "grandmother", "grandfather"]):
        return "elderly"
    return None


def extract_entities(query_en: str) -> ExtractedEntities:
    text = query_en.lower()

    age_years = None
    months_match = _AGE_MONTHS_RE.search(text)
    years_match = _AGE_YEARS_RE.search(text)
    if months_match:
        age_years = round(int(months_match.group(1)) / 12, 2)
    elif years_match:
        age_years = float(years_match.group(1))

    duration_match = _DURATION_RE.search(text)
    duration_raw = duration_match.group(0) if duration_match else None

    diseases = [name for name in _DISEASE_NAMES if name in text]
    # de-dupe overlapping matches like "flu" inside "influenza"
    diseases = sorted(set(diseases), key=diseases.index)

    return ExtractedEntities(
        age_years=age_years,
        age_group=_age_group_for(age_years, text),
        duration_raw=duration_raw,
        mentioned_diseases=diseases,
        pregnancy_mentioned="pregnan" in text or "breastfeeding" in text,
    )
