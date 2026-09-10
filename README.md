---
title: Aarogya AI
emoji: 🩺
colorFrom: blue
colorTo: green
sdk: streamlit
sdk_version: "1.35.0"
python_version: "3.11"
app_file: app.py
pinned: false
---

# 🩺 Aarogya AI — Vernacular Health Assistant

[![Live Demo](https://img.shields.io/badge/🚀_Live_Demo-Streamlit-red)](https://aarogya-ai-8gqvuucanpgm5vqmcrgyin.streamlit.app)
[![Python](https://img.shields.io/badge/Python-3.11-blue)]()
[![RAG](https://img.shields.io/badge/RAG-Hybrid_+_Reranked-yellow)]()
[![Groq](https://img.shields.io/badge/Groq-gpt--oss--20b-lightblue)]()
[![Version](https://img.shields.io/badge/version-V2-brightgreen)]()

## 🌐 Live Demo — Click to Use Now

**→ [https://aarogya-ai-8gqvuucanpgm5vqmcrgyin.streamlit.app](https://aarogya-ai-8gqvuucanpgm5vqmcrgyin.streamlit.app)**

No installation needed. Ask a health question in Hindi, Tamil, Telugu, or Kannada.
The app sleeps after inactivity on the free tier — if you see a "waking up" screen,
give it a few seconds and it'll load.

---

## The Problem

700 million rural Indians have no access to qualified doctors and speak regional
languages — not English. Existing AI health apps hallucinate dangerous medical
advice: a plain language model recommends ibuprofen for dengue fever, a drug that
causes fatal internal bleeding in dengue patients. Aarogya AI does not.

---

## What Aarogya AI Does

- 🗣️ Accepts queries by **voice or text** in Hindi, Tamil, Telugu, Kannada, English
- 📚 Retrieves answers **only from WHO, CDC, and NIH documents** — no open-web generation
- 🚨 Detects life-threatening emergencies **in 4 Indian languages** — calls 108
- 🔊 Reads the response **back to the user in their native language** (gTTS audio)
- 📋 Shows **exactly which PDF page** the answer came from (XAI transparency)
- 🛑 **Refuses rather than guesses** when the evidence is weak, self-contradictory,
  or when its own answer fails a post-generation fact-check

---

## What's New in V2

V2 is a safety-and-retrieval overhaul. V1 had one retrieval method and trusted the
LLM to police itself; V2 adds independent, mostly deterministic checks around it,
each of which can refuse on its own.

| # | Layer | What it does | Why |
|---|---|---|---|
| 1 | **Hybrid retrieval** | FAISS dense search **+ BM25 lexical search**, unioned into one candidate pool (10 each) | Dense search buries short specific facts. Real case: *"Can I take ibuprofen for dengue?"* — the chunk saying **"avoid ibuprofen and aspirin"** never appeared in FAISS's top-30, while BM25 ranked it **#2 of 87** on the literal term |
| 2 | **Cross-encoder reranking** | `ms-marco-MiniLM-L-6-v2` rescores the pool, top-3 go to the LLM | Query-document scoring beats embedding proximity for picking which 3 chunks actually answer the question |
| 3 | **Evidence gate** | Top chunk must clear a calibrated score (0.15) or the LLM is **never called** | Deterministic refusal is cheaper and more reliable than trusting the prompt's own "insufficient context" rule to fire every time |
| 4 | **Contradiction check** | Refuses when retrieved chunks give opposing drug guidance ("avoid X" vs "take X") | Prevents merging conflicting sources into a fabricated compromise. Scoped to drug names, and ignores scoped clinical caveats like *"avoid X in children under 6 months"* |
| 5 | **Grounding verification** | After generation, a second LLM pass fact-checks the answer against the evidence — `SUPPORTED` / `UNSUPPORTED` | An unsupported claim discards the **whole answer** rather than shipping it |
| 6 | **Intent + entity extraction** | Rule-based classifier (15 intents) plus conservative age/duration/disease/pregnancy extraction | Deterministic and interpretable; never invents a field it can't find |
| 7 | **Expanded triage** | **135** emergency keywords + 30 monitor keywords, now with categories (respiratory, cardiovascular, …) | Up from 97 in V1; categories make each RED decision explainable |
| 8 | **Translation safety tests** | Regression suite asserting dosages and the **108** emergency number survive translation intact | A mistranslated `500mg` or a dropped `108` is a safety bug, not a cosmetic one |
| 9 | **Observability** | One structured JSON line per request | Privacy by construction: the logger physically cannot accept query or answer text — only a request id and metadata |

**Two rejected approaches, documented in-code** — grounding was *not* done with embedding
similarity (it scored a deliberately fabricated claim **higher** than a genuinely correct
sentence, because similarity measures topical closeness, not truth) nor with a small NLI
cross-encoder (it broke down on this project's markdown-bullet answer format). See the
comment on `RAGPipeline._build_verification_chain()`.

Every V2 layer **fails open to V1 behaviour**: if BM25 can't build, retrieval falls back
to dense-only; if the reranker won't load, it falls back to FAISS ordering (and the
evidence gate is skipped, since its scores no longer exist).

---

## System Architecture
```
Voice/Text Input (Hindi/Tamil/Telugu/Kannada/English)
        ↓
Whisper STT (base model, ~1.5s per clip)
        ↓
Translate → English (Google Translate + Sarvam AI)
        ↓
PRE-TRIAGE — obvious emergency? → skip RAG entirely, return 108 alert
        ↓
Intent classification + entity extraction (rule-based, no model call)
        ↓
HYBRID RETRIEVAL — FAISS dense (10) ∪ BM25 lexical (10), over 87 chunks / 12 PDFs
        ↓
CROSS-ENCODER RERANK — ms-marco-MiniLM-L-6-v2 → top 3
        ↓
EVIDENCE GATE — top score < 0.15? → refuse, LLM never called
        ↓
CONTRADICTION CHECK — opposing drug guidance? → refuse
        ↓
Groq LLM — gpt-oss-20b (5-rule safety prompt, temp=0.1)
        ↓
GROUNDING VERIFICATION — 2nd LLM pass; UNSUPPORTED → discard answer, refuse
        ↓
POST-TRIAGE — rescan query + answer (RED overrides the LLM entirely)
        ↓
Translate Back → User's language + gTTS Audio
        ↓
Response + source citations + evidence confidence % (XAI transparency)
```

---

## Evaluation Results

> ⚠️ **These numbers were measured on V1** and have not been re-run against the V2
> pipeline. They are kept here as the last full measured baseline. V2's changes are
> architectural and each added layer is independently unit-tested (see `backend/test_*.py`),
> but the 50-question benchmark has **not** been re-executed end-to-end — treat the table
> as V1 evidence, not a V2 claim.

| Metric | Plain LLM | Aarogya AI (V1 RAG) |
|---|---|---|
| Answer Accuracy | ~60% | **98% (49/50)** |
| Hallucination Rate | ~8.7% | **<1%** |
| Triage RED Accuracy | N/A | **100% (20/20)** |
| Hindi Emergency Detection | None | **5/5 = 100%** |
| Tamil Emergency Detection | None | **5/5 = 100%** |
| Telugu Emergency Detection | None | **5/5 = 100%** |
| Kannada Emergency Detection | None | **5/5 = 100%** |

*Evaluated on 50 manually annotated questions with ground truth written directly
from WHO/CDC/NIH source PDFs — not by querying the model (avoids circular evaluation).*

**Verified during V2 development** (spot check, not the full benchmark): the ibuprofen/dengue
retrieval failure above went from a refusal at evidence score `0.03` (dense-only) to a
correct grounded answer at `0.75` (hybrid + rerank).

---

## Screenshots

![Chat Hindi](docs/screenshots/01_chat_hindi.png)
*Hindi query with green triage badge and expandable source citations*

![Emergency](docs/screenshots/02_emergency_red.png)
*RED emergency override — chest pain triggers 108 alert*

![Voice Upload](docs/screenshots/03_voice_upload.png)
*Voice pipeline — upload Hindi audio, Whisper transcribes, gTTS plays response*

---

## Run Locally
```bash
git clone https://github.com/karthik-the-legend/aarogya-ai && cd aarogya-ai
py -3.11 -m venv env && .\env\Scripts\Activate.ps1
pip install -r requirements.txt
echo GROQ_API_KEY=your_key > .env && python backend\ingest.py
streamlit run app.py
```
Then open **http://localhost:8501**.

`app.py` loads the RAG pipeline in-process — no separate API server is required.
The FastAPI service in `backend/main.py` is optional, for calling the pipeline over
HTTP: `uvicorn backend.main:app --reload`.

**Environment variables** — `GROQ_API_KEY` is required. `SARVAM_API_KEY` (better Indian
language translation) and `GEMINI_API_KEY` (alternate LLM) are optional. Every V2 layer
can be toggled: `HYBRID_BM25_ENABLED`, `RERANK_ENABLED`, `CONTRADICTION_CHECK_ENABLED`,
`GROUNDING_ENABLED`, `MIN_EVIDENCE_THRESHOLD`.

---

## Knowledge Base

12 PDFs from WHO, CDC, and NIH — all public domain government health documents,
chunked into 87 passages (300 words, 50-word overlap).
See `data/sources.txt` for full citation list with URLs.

| Source | PDFs | Topics |
|---|---|---|
| WHO | 4 | Dengue, Malaria, TB, Cholera |
| CDC | 4 | Typhoid, Dengue Clinical, Malaria Clinical, Influenza |
| NIH | 4 | Fever, Diarrhoea, Common Cold, Skin Infections |

---

## Limitations

- No multi-turn memory — each query is independent
- Covers 10 common diseases; rare conditions return "see a doctor"
- Kannada translation quality lower than Hindi
- Grounding verification costs a second LLM call per answer, adding latency
- The V1 benchmark above has not been re-run against V2
- Not a replacement for a certified doctor — mandatory disclaimer on every response

---

## Tech Stack

| Layer | Technology |
|---|---|
| LLM | Groq — `openai/gpt-oss-20b` |
| Embeddings | paraphrase-multilingual-MiniLM-L12-v2 (384-dim) |
| Vector Store | FAISS (IndexFlatL2) |
| Lexical Search | BM25 (`rank_bm25`) |
| Reranker | `cross-encoder/ms-marco-MiniLM-L-6-v2` |
| Framework | Streamlit (FastAPI optional) |
| Translation | Google Translate + Sarvam AI |
| STT | OpenAI Whisper (base model) |
| TTS | gTTS (Google Text-to-Speech) |
| RAG | LangChain LCEL |

---

## Author

**Karthik K S** — [github.com/karthik-the-legend](https://github.com/karthik-the-legend)

[![Live Demo](https://img.shields.io/badge/🚀_Live_Demo-Streamlit-red)](https://aarogya-ai-8gqvuucanpgm5vqmcrgyin.streamlit.app)
