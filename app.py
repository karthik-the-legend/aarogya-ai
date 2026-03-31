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

import warnings
warnings.filterwarnings("ignore", message=".*torchvision.*")
warnings.filterwarnings("ignore", message=".*Accessing `__path__`.*")

# Keep Streamlit Cloud awake
import threading
import time
import urllib.request

def keep_alive():
    while True:
        try:
            urllib.request.urlopen(
                "https://aarogya-ai-8gqvuucanpgm5vqmcrgyin.streamlit.app"
            )
        except:
            pass
        time.sleep(300)  # ping every 5 minutes

import warnings
import logging
warnings.filterwarnings("ignore")
logging.getLogger("transformers").setLevel(logging.ERROR)
os.environ["TRANSFORMERS_VERBOSITY"] = "error"

# Start keepalive thread
threading.Thread(target=keep_alive, daemon=True).start()

# ── Page config ──────────────────────────────────────────────────
st.set_page_config(
    page_title="Aarogya AI",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── CSS (same as streamlit_app.py) ───────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Sora', sans-serif !important; background-color: #0a0f1e !important; color: #e2e8f0 !important; }
#MainMenu, footer, header { visibility: hidden; }
.main .block-container { padding: 1.5rem 2rem !important; max-width: 1100px !important; }
.hero { background: linear-gradient(135deg, #0f172a 0%, #1e3a5f 50%, #0f172a 100%); border: 1px solid #1e40af33; border-radius: 16px; padding: 28px 32px; margin-bottom: 24px; }
.hero-title { font-size: 2rem; font-weight: 700; background: linear-gradient(135deg, #60a5fa, #a78bfa, #34d399); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin: 0 0 6px 0; }
.hero-sub { color: #94a3b8; font-size: 0.9rem; margin: 0; }
.badge-green { background: #00c85318; color: #00c853; border: 1px solid #00c85340; padding: 4px 14px; border-radius: 100px; font-size: 0.75rem; font-weight: 600; display: inline-block; margin-top: 8px; }
.badge-yellow { background: #ffd60018; color: #ffd600; border: 1px solid #ffd60040; padding: 4px 14px; border-radius: 100px; font-size: 0.75rem; font-weight: 600; display: inline-block; margin-top: 8px; }
.badge-red { background: #ff174418; color: #ff1744; border: 1px solid #ff174440; padding: 4px 14px; border-radius: 100px; font-size: 0.75rem; font-weight: 600; display: inline-block; margin-top: 8px; }
.source-card { background: #0f172a; border: 1px solid #1e293b; border-radius: 10px; padding: 10px 14px; margin-top: 8px; font-size: 0.78rem; color: #94a3b8; }
.stChatMessage { background: #111827 !important; border: 1px solid #1e293b !important; border-radius: 12px !important; margin-bottom: 12px !important; }
section[data-testid="stSidebar"] { background: #0d1424 !important; border-right: 1px solid #1e293b !important; }
.stSelectbox > div > div { background: #111827 !important; border: 1px solid #1e293b !important; border-radius: 8px !important; }
.stButton > button { background: #1e293b !important; color: #94a3b8 !important; border: 1px solid #334155 !important; border-radius: 8px !important; }
.stAlert { background: #ffd60010 !important; border: 1px solid #ffd60030 !important; border-radius: 10px !important; color: #ffd600 !important; }
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
    "hi": ["मुझे बुखार है", "डेंगू के लक्षण क्या हैं"],
    "ta": ["எனக்கு காய்ச்சல்", "டெங்கு அறிகுறிகள்"],
    "te": ["నాకు జ్వరం వచ్చింది", "డెంగీ లక్షణాలు"],
    "kn": ["ನನಗೆ ಜ್ವರ ಬಂದಿದೆ"],
    "en": ["Symptoms of dengue fever", "Can I take ibuprofen for dengue?"],
}

@st.cache_resource(show_spinner="Loading AI pipeline...")
def load_pipeline():
    return RAGPipeline()

pipeline = load_pipeline()

# ── Session state ────────────────────────────────────────────────
if "messages"    not in st.session_state: st.session_state.messages    = []
if "query_count" not in st.session_state: st.session_state.query_count = 0
if "total_ms"    not in st.session_state: st.session_state.total_ms    = 0
if "pipeline"    not in st.session_state: st.session_state.pipeline    = None
pipeline = load_pipeline()

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
    
    
# ── Load pipeline lazily on first query (saves RAM) ─────────────
def get_pipeline():
    if st.session_state.pipeline is None:
        with st.spinner("Loading AI pipeline... (30 seconds on first load)"):
            st.session_state.pipeline = RAGPipeline()
    return st.session_state.pipeline

# ── Query function (direct pipeline call — no FastAPI needed) ────
def ask_pipeline(query: str, lang_code: str, language_name: str) -> dict:
    try:
        t0       = time.time()
        query_en = to_english(query, lang_code)
        result   = pipeline.ask(query_en, language_name)
        triage   = classify(query, result["answer"])

        if triage.level == TriageLevel.RED:
            final_answer = triage.message
        else:
            final_answer = from_english(result["answer"], lang_code)
            if triage.level.value == "yellow":
                final_answer += f"\n\n⚠️ Please see a doctor within 24 hours."

        return {
            "answer"        : final_answer,
            "triage_level"  : triage.level.value,
            "triage_override": triage.override,
            "sources"       : result["sources"],
            "latency_ms"    : int((time.time() - t0) * 1000),
        }
    except Exception as e:
        return {
            "answer"        : f"❌ Error: {str(e)}",
            "triage_level"  : "green",
            "triage_override": False,
            "sources"       : [],
            "latency_ms"    : 0,
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

    st.markdown('<div style="background:#00c85315;border:1px solid #00c85340;border-radius:8px;padding:8px 12px;font-size:0.78rem;color:#00c853;text-align:center">● Pipeline Ready</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown('<div style="font-size:0.78rem;color:#64748b;font-weight:600;margin-bottom:6px">LANGUAGE</div>', unsafe_allow_html=True)
    selected_lang_display = st.selectbox("", options=list(LANG_MAP.keys()), label_visibility="collapsed")
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
    uploaded = st.file_uploader(
        "Upload audio",
        type=["mp3", "wav", "ogg", "m4a"],
        key="voice_upload",
        label_visibility="collapsed"
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
    <p class="hero-sub">RAG-powered health assistant · WHO · CDC · NIH · Hindi · Tamil · Telugu · Kannada</p>
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
                        name = s['source'].split('\\')[-1].split('/')[-1]
                        st.markdown(f'<div class="source-card"><strong>{name}</strong> · page {s["page"]}</div>', unsafe_allow_html=True)
            if msg.get("latency"):
                st.caption(f"⏱️ {msg['latency']}ms")


# ── Handle voice upload ──────────────────────────────────────────
if uploaded is not None:
    with st.spinner("🎙️ Transcribing audio..."):
        try:
            import tempfile
            import os
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

            # Process through pipeline
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
                            name = s['source'].split('\\')[-1].split('/')[-1]
                            st.markdown(f'<div class="source-card"><strong>{name}</strong> · page {s["page"]}</div>', unsafe_allow_html=True)

                st.caption(f"⏱️ {latency}ms")

                # Audio response
                audio_bytes = text_to_speech(answer, detected)
                if audio_bytes:
                    st.markdown("**🔊 Listen:**")
                    st.audio(audio_bytes, format="audio/mp3", start_time=0)
                    st.download_button("⬇️ Download", audio_bytes, "response.mp3", "audio/mp3")

        except Exception as e:
            st.error(f"Voice processing failed: {str(e)}")

# Voice upload - disabled on cloud to save memory
IS_CLOUD = os.getenv("STREAMLIT_SHARING_MODE") is not None or os.getenv("HOME") == "/home/adminuser"

if not IS_CLOUD:
    uploaded = st.file_uploader("Upload audio", type=["mp3","wav"])
else:
    st.markdown('<div style="font-size:0.75rem;color:#64748b">🎙️ Voice input available in local version</div>', unsafe_allow_html=True)
    uploaded = None

# ── Prefill ──────────────────────────────────────────────────────
prefill = st.session_state.pop("prefill", "")
query   = st.chat_input(f"Ask in {language_name}...") or prefill

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
                    name = s['source'].split('\\')[-1].split('/')[-1]
                    st.markdown(f'<div class="source-card"><strong>{name}</strong> · page {s["page"]}<br><span style="color:#475569">{s["content"][:120]}...</span></div>', unsafe_allow_html=True)

        st.caption(f"⏱️ {latency}ms")

        if auto_tts and triage != "red":
            with st.spinner("🔊 Generating audio..."):
                audio_bytes = text_to_speech(answer, lang_code)
            if audio_bytes:
                st.markdown("**🔊 Listen to response:**")
                st.audio(audio_bytes, format="audio/mp3", start_time=0)
                # Show download button as backup
                st.download_button(
                    label="⬇️ Download audio",
                    data=audio_bytes,
                    file_name="response.mp3",
                    mime="audio/mp3"
                )

    st.session_state.messages.append({
        "role": "assistant", "content": answer,
        "triage": triage, "latency": latency, "sources": sources
    })
    st.session_state.query_count += 1
    st.session_state.total_ms    += latency