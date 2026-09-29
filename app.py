# ================================================================
# app.py — HuggingFace Spaces entry point
# HuggingFace Streamlit Spaces requires app.py at project root
# Calls RAGPipeline directly (no FastAPI server needed)
# ================================================================

import os
import sys
import io
import time
import requests

import streamlit as st
from gtts import gTTS
from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, 'backend')

from rag_pipeline import RAGPipeline
from triage import classify, TriageLevel
from translate import to_english, from_english
from observability import new_request_id, log_request

import warnings
warnings.filterwarnings("ignore", message=".*torchvision.*")
warnings.filterwarnings("ignore", message=".*Accessing `__path__`.*")

import warnings
import logging
warnings.filterwarnings("ignore")
logging.getLogger("transformers").setLevel(logging.ERROR)
os.environ["TRANSFORMERS_VERBOSITY"] = "error"

# ── Page config ──────────────────────────────────────────────────
st.set_page_config(
    page_title="Aarogya AI",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="auto"
)

# ── CSS + Force sidebar open on desktop ─────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
    --bg:        #0a0f1e;
    --bg-side:   #0d1424;
    --card:      #111827;
    --card-2:    #0f172a;
    --border:    #1e293b;
    --border-hi: #2d3f5c;
    --text:      #e2e8f0;
    --muted:     #94a3b8;
    --muted-2:   #64748b;
    --accent:    #3b82f6;
    --accent-2:  #8b5cf6;
    --green:     #00c853;
    --yellow:    #ffd600;
    --red:       #ff1744;
}

html, body, [class*="css"] { font-family: 'Sora', sans-serif !important; background-color: var(--bg) !important; color: var(--text) !important; }
#MainMenu, footer, header { visibility: hidden; }
.main .block-container { padding: 1.5rem 2rem 3rem !important; max-width: 1100px !important; }

/* ── Thin dark scrollbar ── */
::-webkit-scrollbar { width: 8px; height: 8px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--border-hi); border-radius: 8px; }
::-webkit-scrollbar-thumb:hover { background: var(--accent); }

/* ── Hero ── */
.hero {
    position: relative;
    overflow: hidden;
    background: linear-gradient(135deg, #0f172a 0%, #1e3a5f 55%, #0f172a 100%);
    border: 1px solid #1e40af40;
    border-radius: 18px;
    padding: 32px 36px;
    margin-bottom: 24px;
    box-shadow: 0 8px 30px -12px rgba(59, 130, 246, 0.25);
}
.hero::before {
    content: '';
    position: absolute;
    top: -60%;
    right: -8%;
    width: 320px;
    height: 320px;
    background: radial-gradient(circle, #3b82f625 0%, transparent 70%);
    border-radius: 50%;
    pointer-events: none;
}
.hero::after {
    content: '';
    position: absolute;
    bottom: -70%;
    left: 10%;
    width: 260px;
    height: 260px;
    background: radial-gradient(circle, #8b5cf620 0%, transparent 70%);
    border-radius: 50%;
    pointer-events: none;
}
.hero-title { position: relative; font-size: clamp(1.5rem, 4vw, 2.1rem); font-weight: 700; background: linear-gradient(135deg, #60a5fa, #a78bfa, #34d399); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin: 0 0 10px 0; }
.hero-sub { position: relative; color: var(--muted); font-size: 0.88rem; margin: 0 0 12px 0; }
.hero-chips { position: relative; display: flex; flex-wrap: wrap; gap: 8px; }
.hero-chip { background: #ffffff0d; border: 1px solid #ffffff1a; color: #cbd5e1; padding: 3px 12px; border-radius: 100px; font-size: 0.72rem; font-weight: 500; }

/* ── Triage badges ── */
.badge-green, .badge-yellow, .badge-red {
    display: inline-flex; align-items: center; gap: 6px;
    padding: 5px 14px 5px 10px; border-radius: 100px;
    font-size: 0.75rem; font-weight: 600; margin-top: 10px;
    letter-spacing: 0.01em;
}
.badge-green  { background: #00c85316; color: var(--green);  border: 1px solid #00c85345; box-shadow: 0 0 16px -6px #00c85360; }
.badge-yellow { background: #ffd60016; color: var(--yellow); border: 1px solid #ffd60045; box-shadow: 0 0 16px -6px #ffd60060; }
.badge-red    { background: #ff174416; color: var(--red);    border: 1px solid #ff174450; box-shadow: 0 0 18px -4px #ff174480; animation: badgePulse 1.6s ease-in-out infinite; }
@keyframes badgePulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.72; } }

/* ── Source citation cards ── */
.source-card {
    background: var(--card-2); border: 1px solid var(--border); border-radius: 10px;
    padding: 10px 14px; margin-top: 8px; font-size: 0.78rem; color: var(--muted);
    font-family: 'JetBrains Mono', monospace;
    transition: border-color 0.15s ease, transform 0.15s ease;
}
.source-card:hover { border-color: var(--border-hi); transform: translateX(2px); }
.source-card strong { color: #60a5fa; font-family: 'Sora', sans-serif; }

/* ── Chat messages ── */
.stChatMessage {
    background: var(--card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 14px !important;
    margin-bottom: 14px !important;
    padding: 4px 2px !important;
    transition: border-color 0.15s ease;
}
.stChatMessage:hover { border-color: var(--border-hi) !important; }
.stChatMessage p { line-height: 1.65 !important; }
.stChatMessage ul, .stChatMessage ol { line-height: 1.65 !important; padding-left: 1.3em !important; margin: 0.4em 0 !important; }
.stChatMessage li { margin-bottom: 0.25em !important; }

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: var(--bg-side) !important;
    border-right: 1px solid var(--border) !important;
}
section[data-testid="stSidebar"] > div { position: relative; }
section[data-testid="stSidebar"] > div::before {
    content: '';
    position: absolute; top: 0; left: 0; right: 0; height: 3px;
    background: linear-gradient(90deg, #60a5fa, #a78bfa, #34d399);
}

/* ── Form controls ── */
.stSelectbox > div > div { background: var(--card) !important; border: 1px solid var(--border) !important; border-radius: 8px !important; transition: border-color 0.15s ease; }
.stSelectbox > div > div:hover { border-color: var(--border-hi) !important; }
.stButton > button {
    background: var(--border) !important; color: var(--muted) !important;
    border: 1px solid #334155 !important; border-radius: 8px !important;
    transition: all 0.15s ease !important;
}
.stButton > button:hover { background: #253449 !important; color: var(--text) !important; border-color: var(--accent) !important; transform: translateY(-1px); }
.stAlert { background: #ffd60010 !important; border: 1px solid #ffd60030 !important; border-radius: 10px !important; color: var(--yellow) !important; }

/* ── Chat input ── */
[data-testid="stChatInput"] { border-radius: 14px !important; }
[data-testid="stChatInput"]:focus-within { box-shadow: 0 0 0 2px #3b82f655 !important; }

/* ── Status pill ── */
.status-pill {
    background: #00c85315; border: 1px solid #00c85340; border-radius: 8px;
    padding: 8px 12px; font-size: 0.78rem; color: var(--green); text-align: center;
    box-shadow: 0 0 14px -6px #00c85350;
}

/* ── Sidebar sizing on wide screens (Streamlit's own "auto" state already
   handles expand-on-desktop / collapse-on-mobile — we only set width) ── */
@media (min-width: 769px) {
    section[data-testid="stSidebar"] { width: 21rem !important; min-width: 21rem !important; }
}

/* ── Mobile: tighter padding so chat isn't squeezed ── */
@media (max-width: 768px) {
    .hero { padding: 20px 20px; }
    .main .block-container { padding: 1rem 1rem 3rem !important; }
}
</style>
""", unsafe_allow_html=True)

# ── Constants ────────────────────────────────────────────────────
LANG_MAP = {
    "🇮🇳 Hindi"   : "hi",
    "🇮🇳 Tamil"   : "ta",
    "🇮🇳 Telugu"  : "te",
    "🇮🇳 Kannada" : "kn",
    "🌐 English"  : "en",
}
TRIAGE_CONFIG = {
    "green" : ("🟢", "badge-green",  "Safe — Manage at home"),
    "yellow": ("🟡", "badge-yellow", "Caution — See doctor today"),
    "red"   : ("🔴", "badge-red",    "EMERGENCY — Call 108 NOW"),
}
GTTS_LANG_MAP = {"hi": "hi", "ta": "ta", "te": "te", "kn": "kn", "en": "en"}
EXAMPLE_QUERIES = {
    "hi": ["मुझे बुखार है", "डेंगू के लक्षण क्या हैं", "मलेरिया का इलाज"],
    "ta": ["எனக்கு காய்ச்சல்", "டெங்கு அறிகுறிகள்"],
    "te": ["నాకు జ్వరం వచ్చింది", "డెంగీ లక్షణాలు"],
    "kn": ["ನನಗೆ ಜ್ವರ ಬಂದಿದೆ"],
    "en": ["Symptoms of dengue fever", "Can I take ibuprofen for dengue?"],
}

# ── Pipeline ─────────────────────────────────────────────────────
@st.cache_resource(show_spinner="Loading AI pipeline...")
def load_pipeline():
    return RAGPipeline()

pipeline = load_pipeline()

# ── Source card rendering ────────────────────────────────────────
def render_source_card(s: dict, show_content: bool = False) -> str:
    """Shared HTML for a single citation card, used by every place a
    source list is rendered. Shows the org (WHO/CDC/NIH) when the
    chunk's metadata was matched against data/sources.txt."""
    name = s["source"].split("\\")[-1].split("/")[-1]
    org = s.get("organization", "")
    org_html = f'<span style="color:#64748b"> · {org}</span>' if org else ""
    content_html = ""
    if show_content and s.get("content"):
        content_html = f'<br><span style="color:#475569">{s["content"][:120]}...</span>'
    return (
        f'<div class="source-card"><strong>{name}</strong> · page {s["page"]}'
        f'{org_html}{content_html}</div>'
    )


LANG_NAMES = {"hi": "Hindi", "ta": "Tamil", "te": "Telugu", "kn": "Kannada", "en": "English"}
INTENT_LABELS = {
    "symptom": "Symptom check", "disease_information": "Disease information",
    "medication": "Medication safety", "first_aid": "First aid",
    "prevention": "Prevention", "emergency": "Emergency",
    "child_health": "Child health", "pregnancy": "Pregnancy",
    "elderly_health": "Elderly health", "chronic_condition": "Chronic condition",
    "nutrition": "Nutrition", "vaccination": "Vaccination", "hygiene": "Hygiene",
    "general_health": "General health", "unknown": "Unknown",
}


def render_explainability(msg: dict) -> None:
    """
    'Why this answer?' panel — task 28's explainability requirement.
    Shows the automated reasoning metadata (language, intent, risk
    level, evidence confidence, whether emergency override fired) —
    never hidden chain-of-thought, just the same signals that already
    drove the pipeline's own decisions.
    """
    triage_level = msg.get("triage") or msg.get("triage_level", "green")
    intent = msg.get("intent")
    lang = msg.get("detected_lang")
    evidence_score = msg.get("evidence_score")
    grounded = msg.get("grounded")

    if intent is None and evidence_score is None and lang is None:
        return  # nothing to show (e.g. an error response)

    rows = []
    if lang:
        rows.append(f"**Detected language:** {LANG_NAMES.get(lang, lang)}")
    if intent:
        rows.append(f"**Query type:** {INTENT_LABELS.get(intent, intent)}")
    rows.append(f"**Risk level:** {triage_level.upper()}"
                + (" — emergency override, answer replaced" if triage_level == "red" else ""))
    if evidence_score is not None:
        rows.append(f"**Evidence confidence:** {evidence_score:.0%}")
    if grounded is not None:
        rows.append(f"**Fact-checked against sources:** {'✅ passed' if grounded else '⚠️ failed — answer withheld'}")

    with st.expander("🔍 Why this answer?"):
        st.markdown("\n\n".join(rows))


# ── Session state ────────────────────────────────────────────────
if "messages"    not in st.session_state: st.session_state.messages    = []
if "query_count" not in st.session_state: st.session_state.query_count = 0
if "total_ms"    not in st.session_state: st.session_state.total_ms    = 0

# ── TTS function ─────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def text_to_speech(text: str, lang_code: str) -> bytes:
    try:
        tts = gTTS(text=text, lang=GTTS_LANG_MAP.get(lang_code, "en"), slow=False)
        buf = io.BytesIO()
        tts.write_to_fp(buf)
        buf.seek(0)
        return buf.read()
    except Exception:
        return b""

# ── Query function ────────────────────────────────────────────────
def ask_pipeline(query: str, lang_code: str, language_name: str) -> dict:
    try:
        t0 = time.time()

        # PRE-triage: check the raw query BEFORE any RAG/LLM call.
        # An obvious emergency never reaches the LLM — it's a wasted,
        # slower round-trip for a response that gets thrown away
        # anyway, and it delays a life-critical instruction.
        request_id = new_request_id()

        pre_triage = classify(query)
        if pre_triage.level == TriageLevel.RED:
            latency_ms = int((time.time() - t0) * 1000)
            log_request(
                request_id, lang_code, "emergency", pre_triage.level.value,
                pre_triage.override, None, None, False, 0, [], latency_ms,
            )
            return {
                "answer"         : pre_triage.message,
                "triage_level"   : pre_triage.level.value,
                "triage_override": pre_triage.override,
                "triage_category": pre_triage.category,
                "sources"        : [],
                "evidence_score" : None,
                "refused"        : False,
                "grounded"       : None,
                "intent"         : "emergency",
                "detected_lang"  : lang_code,
                "latency_ms"     : latency_ms,
            }

        query_en = to_english(query, lang_code)
        result   = pipeline.ask(query_en, language_name)

        # POST-triage: second safety net — also scans the LLM's own
        # answer, in case retrieved evidence surfaces something the
        # raw query alone didn't.
        triage = classify(query, result["answer"])

        if triage.level == TriageLevel.RED:
            final_answer = triage.message
        else:
            final_answer = from_english(result["answer"], lang_code)
            if triage.level.value == "yellow":
                final_answer += f"\n\n⚠️ Please see a doctor within 24 hours."

        latency_ms = int((time.time() - t0) * 1000)
        source_files = [s["source"].split("\\")[-1].split("/")[-1] for s in result["sources"]]
        log_request(
            request_id, lang_code, result.get("intent"), triage.level.value,
            triage.override, result.get("evidence_score"), result.get("grounded"),
            result.get("refused", False), len(result["sources"]), source_files, latency_ms,
        )

        return {
            "answer"         : final_answer,
            "triage_level"   : triage.level.value,
            "triage_override": triage.override,
            "triage_category": triage.category,
            "sources"        : result["sources"],
            "evidence_score" : result.get("evidence_score"),
            "refused"        : result.get("refused", False),
            "grounded"       : result.get("grounded"),
            "intent"         : result.get("intent"),
            "entities"       : result.get("entities"),
            "detected_lang"  : lang_code,
            "latency_ms"     : latency_ms,
        }
    except Exception as e:
        return {
            "answer"         : f"❌ Error: {str(e)}",
            "triage_level"   : "green",
            "triage_override": False,
            "sources"        : [],
            "latency_ms"     : 0,
        }

# ── Sidebar ──────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="text-align:center;padding:10px 0 20px">
        <div style="font-size:2.5rem">🩺</div>
        <div style="font-size:1.1rem;font-weight:700;color:#60a5fa">Aarogya AI</div>
        <div style="font-size:0.72rem;color:#64748b;margin-top:4px">Vernacular Health Assistant</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="status-pill">● Pipeline Ready</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown('<div style="font-size:0.78rem;color:#64748b;font-weight:600;margin-bottom:6px">LANGUAGE</div>', unsafe_allow_html=True)
    selected_lang_display = st.selectbox("Language", options=list(LANG_MAP.keys()), label_visibility="collapsed")
    lang_code     = LANG_MAP[selected_lang_display]
    language_name = selected_lang_display.split(" ", 1)[1]

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div style="font-size:0.78rem;color:#64748b;font-weight:600;margin-bottom:8px">EXAMPLE QUERIES</div>', unsafe_allow_html=True)
    for ex in EXAMPLE_QUERIES.get(lang_code, EXAMPLE_QUERIES["en"]):
        if st.button(ex, key=f"ex_{ex}", use_container_width=True):
            st.session_state["prefill"] = ex

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div style="font-size:0.78rem;color:#64748b;font-weight:600;margin-bottom:8px">KNOWLEDGE BASE</div>', unsafe_allow_html=True)
    st.markdown('<div style="font-size:0.78rem;color:#94a3b8;line-height:2">📄 WHO Fact Sheets (4 PDFs)<br>📄 CDC Yellow Book 2024 (4 PDFs)<br>📄 NIH MedlinePlus (4 PDFs)</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    auto_tts = st.checkbox("🔊 Auto-play audio response", value=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div style="font-size:0.78rem;color:#64748b;font-weight:600;margin-bottom:8px">🎙️ VOICE INPUT</div>', unsafe_allow_html=True)

    # ── Single, authoritative file uploader (lives only in sidebar) ──
    uploaded = st.file_uploader(
        "Upload audio (.mp3, .wav, .ogg, .m4a)",
        type=["mp3", "wav", "ogg", "m4a"],
        key="voice_upload",
        label_visibility="collapsed",
    )

    st.markdown("<br>", unsafe_allow_html=True)
    avg_ms = st.session_state.total_ms // max(st.session_state.query_count, 1)
    st.markdown(f"""
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px">
        <div style="background:#0f172a;border:1px solid #1e293b;border-radius:8px;padding:10px;text-align:center">
            <div style="font-size:1.3rem;font-weight:700;color:#60a5fa">{st.session_state.query_count}</div>
            <div style="font-size:0.65rem;color:#64748b">Queries</div>
        </div>
        <div style="background:#0f172a;border:1px solid #1e293b;border-radius:8px;padding:10px;text-align:center">
            <div style="font-size:1.3rem;font-weight:700;color:#a78bfa">{avg_ms}ms</div>
            <div style="font-size:0.65rem;color:#64748b">Avg Speed</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.warning("⚠️ General health info only — not a diagnosis. Always consult a doctor.")

    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages    = []
        st.session_state.query_count = 0
        st.session_state.total_ms    = 0
        st.rerun()

# ── Main area ────────────────────────────────────────────────────
st.markdown(f"""
<div class="hero">
    <div class="hero-title">🩺 Aarogya AI</div>
    <p class="hero-sub">Grounded health answers from WHO, CDC & NIH — in your own language</p>
    <div class="hero-chips">
        <span class="hero-chip">📚 WHO · CDC · NIH sourced</span>
        <span class="hero-chip">🗣️ Hindi · Tamil · Telugu · Kannada</span>
        <span class="hero-chip">🚨 Emergency triage built in</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Chat history ─────────────────────────────────────────────────
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg["role"] == "assistant":
            emoji, cls, label = TRIAGE_CONFIG.get(msg.get("triage","green"), TRIAGE_CONFIG["green"])
            st.markdown(f'<span class="{cls}">{emoji} {label}</span>', unsafe_allow_html=True)
            sources = msg.get("sources", [])
            if sources:
                with st.expander(f"📚 {len(sources)} source(s)"):
                    for s in sources:
                        st.markdown(render_source_card(s), unsafe_allow_html=True)
            render_explainability(msg)
            if msg.get("latency"):
                st.caption(f"⏱️ {msg['latency']}ms")

# ── Handle voice upload (uses sidebar's `uploaded` variable) ─────
# The uploader keeps its file across reruns, so without this check the
# same clip was transcribed and answered again on every later click.
voice_id = None
if uploaded is not None:
    voice_id = getattr(uploaded, "file_id", None) or f"{uploaded.name}:{uploaded.size}"
if voice_id is not None and st.session_state.get("voice_done") != voice_id:
    st.session_state["voice_done"] = voice_id
    with st.spinner("🎙️ Transcribing audio..."):
        try:
            import tempfile
            ext = "." + uploaded.name.split(".")[-1]
            with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp:
                tmp.write(uploaded.read())
                tmp_path = tmp.name

            from voice_handler import transcribe
            transcript_data = transcribe(tmp_path)
            os.unlink(tmp_path)

            st.markdown(f"""
            <div style="background:#0f172a;border:1px solid #1e40af33;
            border-radius:10px;padding:12px 16px;margin:12px 0">
                <div style="font-size:0.72rem;color:#64748b;margin-bottom:4px">
                    🎙️ WHISPER TRANSCRIPT · {transcript_data.get('language','Unknown')}
                </div>
                <div style="color:#e2e8f0;font-size:1rem">{transcript_data.get('text','')}</div>
            </div>
            """, unsafe_allow_html=True)

            query    = transcript_data.get('text', '')
            detected = transcript_data.get('lang_code', 'en')
            lang_n   = transcript_data.get('language', 'English')

            with st.chat_message("user"):
                st.markdown(f"🎙️ {query}")

            with st.chat_message("assistant"):
                with st.spinner("Searching medical knowledge base..."):
                    result  = ask_pipeline(query, detected, lang_n)

                answer  = result.get("answer", "")
                triage  = result.get("triage_level", "green")
                sources = result.get("sources", [])
                latency = result.get("latency_ms", 0)

                st.markdown(answer)
                emoji, cls, label = TRIAGE_CONFIG.get(triage, TRIAGE_CONFIG["green"])
                st.markdown(f'<span class="{cls}">{emoji} {label}</span>', unsafe_allow_html=True)

                if sources:
                    with st.expander(f"📚 {len(sources)} source(s)"):
                        for s in sources:
                            st.markdown(render_source_card(s), unsafe_allow_html=True)

                render_explainability(result)

                st.caption(f"⏱️ {latency}ms")

                audio_bytes = text_to_speech(answer, detected)
                if audio_bytes:
                    st.markdown("**🔊 Listen:**")
                    st.audio(audio_bytes, format="audio/mp3", start_time=0)
                    st.download_button("⬇️ Download", audio_bytes, "response.mp3", "audio/mp3")

            st.session_state.messages.append({"role": "user", "content": f"🎙️ {query}"})
            st.session_state.messages.append({
                "role": "assistant", "content": answer,
                "triage": triage, "latency": latency, "sources": sources,
                "intent": result.get("intent"), "detected_lang": result.get("detected_lang"),
                "evidence_score": result.get("evidence_score"), "grounded": result.get("grounded"),
            })
            st.session_state.query_count += 1
            st.session_state.total_ms    += latency

        except Exception as e:
            st.error(f"Voice processing failed: {str(e)}")

# ── Prefill & chat input ─────────────────────────────────────────
prefill = st.session_state.pop("prefill", "")
query   = st.chat_input(f"Ask in {language_name}... e.g. symptoms of dengue") or prefill

if query:
    with st.chat_message("user"):
        st.markdown(query)
    st.session_state.messages.append({"role": "user", "content": query})

    with st.chat_message("assistant"):
        with st.spinner("Searching medical knowledge base..."):
            result  = ask_pipeline(query, lang_code, language_name)

        answer  = result.get("answer", "")
        triage  = result.get("triage_level", "green")
        latency = result.get("latency_ms", 0)
        sources = result.get("sources", [])

        st.markdown(answer)
        emoji, cls, label = TRIAGE_CONFIG.get(triage, TRIAGE_CONFIG["green"])
        st.markdown(f'<span class="{cls}">{emoji} {label}</span>', unsafe_allow_html=True)

        if sources:
            with st.expander(f"📚 {len(sources)} source(s)", expanded=triage=="red"):
                for s in sources:
                    st.markdown(render_source_card(s, show_content=True), unsafe_allow_html=True)

        render_explainability(result)

        st.caption(f"⏱️ {latency}ms")

        if auto_tts and triage != "red":
            with st.spinner("🔊 Generating audio..."):
                audio_bytes = text_to_speech(answer, lang_code)
            if audio_bytes:
                st.markdown("**🔊 Listen to response:**")
                st.audio(audio_bytes, format="audio/mp3", start_time=0)
                st.download_button(
                    label="⬇️ Download audio",
                    data=audio_bytes,
                    file_name="response.mp3",
                    mime="audio/mp3"
                )

    st.session_state.messages.append({
        "role": "assistant", "content": answer,
        "triage": triage, "latency": latency, "sources": sources,
        "intent": result.get("intent"), "detected_lang": result.get("detected_lang"),
        "evidence_score": result.get("evidence_score"), "grounded": result.get("grounded"),
    })
    st.session_state.query_count += 1
    st.session_state.total_ms    += latency