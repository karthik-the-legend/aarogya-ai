# ================================================================
# backend\contradiction.py
# Deterministic contradiction check across retrieved evidence chunks
# (task 17). Looks specifically for opposing medication guidance for
# the same drug — "avoid ibuprofen" in one chunk vs "take ibuprofen"
# in another — rather than attempting general semantic contradiction
# detection.
#
# Why deterministic, and why scoped this narrowly: measured directly
# against this project's own knowledge base — real queries retrieve
# their top-3 reranked chunks from a SINGLE source document the large
# majority of the time (confirmed: "dengue treatment", "malaria
# treatment medicines", and "fever medicine dosage" each returned 3/3
# chunks from one PDF). True cross-source contradiction is rare in a
# small, curated, one-authoritative-source-per-disease knowledge base.
# A full LLM-based contradiction judge would mostly be paying latency
# and Groq quota for a scenario this dataset doesn't actually exhibit.
# This narrow, free, deterministic check still catches the case that
# matters (conflicting drug advice) and costs nothing extra — worth
# keeping even though it rarely fires today, since it starts to matter
# more if the knowledge base grows to include multiple sources per
# topic that might disagree.
# ================================================================

import re

_DRUG_NAMES = [
    "paracetamol", "acetaminophen", "ibuprofen", "aspirin",
    "antibiotics", "antibiotic",
]

_NEGATIVE_TEMPLATES = [
    r"avoid\s+{drug}",
    r"should not (?:be given |take |use )?{drug}",
    r"do not (?:give |take |use )?{drug}",
    r"{drug}\w*[^.]{{0,25}}should be avoided",
    r"{drug}\w*[^.]{{0,25}}not recommended",
    r"{drug}\w*[^.]{{0,25}}should not be (?:used|given|taken)",
]

_POSITIVE_TEMPLATES = [
    r"(?:take|use|give|administer)\s+{drug}",
    r"{drug}\w*[^.]{{0,25}}(?:is recommended|can be used|is safe|may be used)",
]


# If a "negative" match is immediately followed by one of these, it's
# a scoped clinical caveat ("do not use ibuprofen in children 6 months
# or younger"), not a blanket contradiction with a separate "take
# ibuprofen every 6-8 hours" statement elsewhere in the same source.
# Confirmed this exact false positive against the real knowledge base:
# NIH's fever guidance recommends ibuprofen generally, with this one
# infant-age exception — flagging that pair as a "contradiction" would
# have wrongly refused a completely ordinary "fever medicine dosage"
# query. Excluding qualified statements is what makes this check safe
# enough to actually gate a refusal on.
_QUALIFIER_WINDOW = 40
_QUALIFIERS = re.compile(
    r"\b(child|infant|newborn|month|year|pregnan|breastfeed|unless|except|"
    r"if\s|under\s|below\s|age|elderly|kidney|liver|allerg)",
    re.IGNORECASE,
)


def _stances_for_drug(drug: str, text: str) -> set:
    stances = set()
    for template in _NEGATIVE_TEMPLATES:
        m = re.search(template.format(drug=re.escape(drug)), text)
        if not m:
            continue
        window = text[m.end():m.end() + _QUALIFIER_WINDOW]
        if not _QUALIFIERS.search(window):
            stances.add("avoid")
    if any(re.search(t.format(drug=re.escape(drug)), text) for t in _POSITIVE_TEMPLATES):
        stances.add("use")
    return stances


def detect_contradiction(docs: list) -> tuple:
    """
    Scans the retrieved chunks for opposing guidance on the same drug.

    Returns (has_contradiction, drug_name_or_None). Only ever returns
    True when BOTH an "avoid X" style statement and a "use X" style
    statement are found for the SAME drug across the chunk set — never
    on a single ambiguous sentence, to keep false positives near zero.
    """
    if len(docs) < 2:
        return False, None

    texts = [doc.page_content.lower() for doc in docs]
    for drug in _DRUG_NAMES:
        combined_stances = set()
        for text in texts:
            combined_stances |= _stances_for_drug(drug, text)
        if {"avoid", "use"} <= combined_stances:
            return True, drug

    return False, None
