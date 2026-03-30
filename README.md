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

[![Live Demo](https://img.shields.io/badge/🚀_Live_Demo-HuggingFace_Spaces-orange)](https://huggingface.co/spaces/karthik55555/aarogya-ai)
[![Python](https://img.shields.io/badge/Python-3.11-blue)]()
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-green)]()
[![LangChain](https://img.shields.io/badge/LangChain-RAG-yellow)]()
[![Groq](https://img.shields.io/badge/Groq-Llama3-lightblue)]()

## 🌐 Live Demo — Click to Use Now

**→ [https://huggingface.co/spaces/karthik55555/aarogya-ai](https://huggingface.co/spaces/karthik55555/aarogya-ai)**

No installation needed. Ask a health question in Hindi, Tamil, Telugu, or Kannada.

---

## The Problem

700 million rural Indians have no access to qualified doctors and speak regional
languages — not English. Existing AI health apps hallucinate dangerous medical
advice: a plain language model recommends ibuprofen for dengue fever, a drug that
causes fatal internal bleeding in dengue patients. Aarogya AI does not.

---

## What Aarogya AI Does

- 🗣️ Accepts queries by **voice or text** in Hindi, Tamil, Telugu, Kannada, English
- 📚 Retrieves answers **only from WHO, CDC, and NIH documents** — zero hallucination
- 🚨 Detects life-threatening emergencies **in 4 Indian languages** — calls 108
- 🔊 Reads the response **back to the user in their native language** (gTTS audio)
- 📋 Shows **exactly which PDF page** the answer came from (XAI transparency)

---

## Evaluation Results

| Metric | Plain LLM | Aarogya AI (RAG) |
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

---

## System Architecture
```
Voice/Text Input (Hindi/Tamil/Telugu/Kannada/English)
        ↓
Whisper STT (base model, ~1.5s per clip)
        ↓
Translate → English (Google Translate + Sarvam AI)
        ↓
FAISS Search → Top-3 passages from 87 chunks (12 WHO/CDC/NIH PDFs)
        ↓
Groq LLM — Llama 3.1 (5-rule safety prompt, temp=0.1)
        ↓
Rule-based Triage (97 keywords, RED/YELLOW/GREEN, 100% RED recall)
        ↓
Translate Back → User's language + gTTS Audio
        ↓
Response with source citations (XAI transparency)
```

---

## Screenshots

![Chat Hindi](docs/screenshots/01_chat_hindi.png)
*Hindi query with green triage badge and expandable source citations*

![Emergency](docs/screenshots/02_emergency_red.png)
*RED emergency override — chest pain triggers 108 alert*

![Voice Upload](docs/screenshots/03_voice_upload.png)
*Voice pipeline — upload Hindi audio, Whisper transcribes, gTTS plays response*

---

## Run Locally — 5 Commands
```bash
git clone https://github.com/karthik-the-legend/aarogya-ai && cd aarogya-ai
py -3.11 -m venv env && .\env\Scripts\Activate.ps1
pip install -r requirements.txt
echo GROQ_API_KEY=your_key > .env && python backend\ingest.py
uvicorn backend.main:app --reload
```
Then in a new window: `streamlit run frontend\streamlit_app.py`

---

## Knowledge Base

12 PDFs from WHO, CDC, and NIH — all public domain government health documents.
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
- Not a replacement for a certified doctor — mandatory disclaimer on every response

---

## Tech Stack

| Layer | Technology |
|---|---|
| LLM | Groq — Llama 3.1 8B Instant |
| Embeddings | paraphrase-multilingual-MiniLM-L12-v2 |
| Vector Store | FAISS (IndexFlatL2) |
| Framework | FastAPI + Streamlit |
| Translation | Google Translate + Sarvam AI |
| STT | OpenAI Whisper (base model) |
| TTS | gTTS (Google Text-to-Speech) |
| RAG | LangChain LCEL |

---

## Author

**Karthik K S** — [github.com/karthik-the-legend](https://github.com/karthik-the-legend)

[![Live Demo](https://img.shields.io/badge/🚀_Live_Demo-Streamlit-red)](https://aarogya-ai-8gqvuucanpgm5vqmcrgyin.streamlit.app)