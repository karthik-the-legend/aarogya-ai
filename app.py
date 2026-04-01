# ================================================================
# app.py — HuggingFace Spaces / Streamlit Cloud entry point
# Calls RAGPipeline directly (no FastAPI server needed)
# ================================================================

import os
import sys
import io
import time

import streamlit as st
from gtts import gTTS
from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, 'backend')

from rag_pipeline import RAGPipeline
from triage import classify, TriageLevel
from translate import to_english, from_english

import warnings
import logging
warnings.filterwarnings("ignore")
logging.getLogger("transformers").setLevel(logging.ERROR)
os.environ["TRANSFORMERS_VERBOSITY"] = "error"

# ── Keep Streamlit Cloud awake ───────────────────────────────────
import threading
import urllib.request

def keep_alive():
    while True:
        try:
            urllib.request.urlopen(
                "https://aarogya-ai-8gqvuucanpgm5vqmcrgyin.streamlit.app"
            )
        except:
            pass
        time.sleep(300)

threading.Thread(target=keep_alive, daemon=True).start()

# ── Page config ──────────────────────────────────────────────────
st.set_page_config(
    page_title="Aarogya AI",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── CSS + floating menu button ───────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

/* ── Root variables ── */
:root {
    --bg:     #0a0f1e;
    --card:   #111827;
    --border: #1e293b;
    --text:   #e2e8f0;
    --muted:  #64748b;
    --accent: #3b82f6;
}

/* ── Global ── */
html, body, [class*="css"] {
    font-family: 'Sora', sans-serif !important;
    background-color: var(--bg) !important;
    color: var(--text) !important;
}

/* ── Hide Streamlit branding ── */
#MainMenu, footer, header { visibility: hidden; }

/* Hide the native Streamlit sidebar toggle visually.
   We keep it in the DOM so JS can still .click() it. */
[data-testid="collapsedControl"] {
    visibility: hidden !important;
    pointer-events: none !important;
    position: absolute !important;
    width: 0 !important;
    height: 0 !important;
    overflow: hidden !important;
}

/* ══════════════════════════════════════════════
   FLOATING MENU BUTTON  (our custom toggle)
   ══════════════════════════════════════════════ */
#aarogya-menu-btn {
    position: fixed;
    top: 14px;
    left: 14px;
    z-index: 99999;
    width: 42px;
    height: 42px;
    border-radius: 50%;
    background: #1e3a5f;
    border: 1.5px solid #3b82f6;
    color: #60a5fa;
    font-size: 1.2rem;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 2px 16px #0008;
    transition: background 0.18s, transform 0.12s, border-color 0.18s;
    user-select: none;
    -webkit-tap-highlight-color: transparent;
    line-height: 1;
}
#aarogya-menu-btn:hover {
    background: #3b82f6;
    border-color: #60a5fa;
    color: #fff;
}
#aarogya-menu-btn:active {
    transform: scale(0.88);
    background: #2563eb;
    color: #fff;
}

/* ══════════════════════════════════════════════
   SIDEBAR
   ══════════════════════════════════════════════ */
section[data-testid="stSidebar"][aria-expanded="true"] {
    width: 21rem !important;
    min-width: 21rem !important;
    background: #0d1424 !important;
    border-right: 1px solid #1e293b !important;
    transition: width 0.28s cubic-bezier(.4,0,.2,1) !important;
}
section[data-testid="stSidebar"][aria-expanded="false"] {
    width: 0px !important;
    min-width: 0px !important;
    overflow: hidden !important;
    transition: width 0.28s cubic-bezier(.4,0,.2,1) !important;
}
section[data-testid="stSidebar"] .block-container {
    padding: 1.5rem 1rem !important;
}

/* ══════════════════════════════════════════════
   MAIN CONTENT
   ══════════════════════════════════════════════ */
.main .block-container {
    padding: 1.5rem 2rem 1.5rem 4rem !important;
    max-width: 1100px !important;
    margin: 0 auto !important;
}

/* ── Hero ── */
.hero {
    background: linear-gradient(135deg, #0f172a 0%, #1e3a5f 50%, #0f172a 100%);
    border: 1px solid #1e40af33;
    border-radius: 16px;
    padding: 28px 32px;
    margin-bottom: 24px;
    position: relative;
    overflow: hidden;
}
.hero::before {
    content: '';
    position: absolute;
    top: -50%; right: -10%;
    width: 300px; height: 300px;
    background: radial-gradient(circle, #3b82f620 0%, transparent 70%);
    border-radius: 50%;
}
.hero-title {
    font-size: 2rem;
    font-weight: 700;
    background: linear-gradient(135deg, #60a5fa, #a78bfa, #34d399);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0 0 6px 0;
}
.hero-sub { color: #94a3b8; font-size: 0.9rem; margin: 0; }

/* ── Triage badges ── */
.badge-green {
    background:#00c85318; color:#00c853; border:1px solid #00c85340;
    padding:4px 14px; border-radius:100px; font-size:0.75rem;
    font-weight:600; display:inline-block; margin-top:8px;
}
.badge-yellow {
    background:#ffd60018; color:#ffd600; border:1px solid #ffd60040;
    padding:4px 14px; border-radius:100px; font-size:0.75rem;
    font-weight:600; display:inline-block; margin-top:8px;
}
.badge-red {
    background:#ff174418; color:#ff1744; border:1px solid #ff174440;
    padding:4px 14px; border-radius:100px; font-size:0.75rem;
    font-weight:600; display:inline-block; margin-top:8px;
    animation:pulse 1.5s infinite;
}
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.6} }

/* ── Source cards ── */
.source-card {
    background:#0f172a; border:1px solid #1e293b; border-radius:10px;
    padding:10px 14px; margin-top:8px; font-size:0.78rem; color:#94a3b8;
    font-family:'JetBrains Mono',monospace;
}
.source-card strong { color:#60a5fa; }

/* ── Chat messages ── */
.stChatMessage {
    background:#111827 !important;
    border:1px solid #1e293b !important;
    border-radius:12px !important;
    margin-bottom:12px !important;
}

/* ── Selectbox ── */
.stSelectbox > div > div {
    background:#111827 !important;
    border:1px solid #1e293b !important;
    border-radius:8px !important;
    color:#e2e8f0 !important;
}

/* ── Chat input ── */
.stChatInputContainer {
    border:1px solid #1e40af55 !important;
    border-radius:12px !important;
    background:#111827 !important;
}

/* ── Buttons ── */
.stButton > button {
    background:#1e293b !important;
    color:#94a3b8 !important;
    border:1px solid #334155 !important;
    border-radius:8px !important;
    font-family:'Sora',sans-serif !important;
    transition:all 0.2s !important;
    min-height:44px !important;
}
.stButton > button:hover { background:#334155 !important; color:#e2e8f0 !important; }
.stButton > button:active {
    background:#3b82f6 !important;
    color:#fff !important;
    border-color:#3b82f6 !important;
    transform:scale(0.97) !important;
}

/* ── Alert / Warning ── */
.stAlert {
    background:#ffd60010 !important;
    border:1px solid #ffd60030 !important;
    border-radius:10px !important;
    color:#ffd600 !important;
}

hr { border-color:#1e293b !important; }

/* ══════════════════════════════════════════════
   MOBILE  <= 768px
   ══════════════════════════════════════════════ */
@media (max-width: 768px) {
    .main .block-container {
        padding: 1rem 1rem 1rem 3.5rem !important;
        max-width: 100% !important;
    }
    section[data-testid="stSidebar"][aria-expanded="true"] {
        position: fixed !important;
        top: 0 !important; left: 0 !important;
        height: 100vh !important;
        width: 85vw !important;
        min-width: 260px !important;
        z-index: 10000 !important;
        overflow-y: auto !important;
    }
    section[data-testid="stSidebar"][aria-expanded="true"] ~ .main {
        margin-left: 0 !important;
    }
    .hero { padding: 16px !important; margin-bottom: 14px !important; }
    .hero-title { font-size: 1.3rem !important; }
    .hero-sub   { font-size: 0.72rem !important; line-height: 1.6 !important; }
    .badge-green,.badge-yellow,.badge-red { font-size:0.7rem !important; padding:3px 10px !important; }
    .source-card { font-size:0.7rem !important; padding:8px 10px !important; }
    audio { width:100% !important; }
    #aarogya-menu-btn { top:10px; left:10px; width:38px; height:38px; font-size:1.05rem; }
}

@media (max-width: 480px) {
    .hero-title { font-size: 1.1rem !important; }
    .hero-sub   { font-size: 0.65rem !important; }
    .hero       { padding: 12px !important; }
}
</style>

<!-- Floating hamburger button -->
<button id="aarogya-menu-btn" title="Open menu" aria-label="Open menu">☰</button>

<script>
(function () {
    var btn = document.getElementById('aarogya-menu-btn');
    if (!btn) return;

    function getSidebar() {
        return window.parent.document.querySelector('[data-testid="stSidebar"]');
    }
    function getNativeBtn() {
        return window.parent.document.querySelector('[data-testid="collapsedControl"]');
    }
    function isOpen() {
        var sb = getSidebar();
        return sb && sb.getAttribute('aria-expanded') === 'true';
    }
    function syncIcon() {
        btn.innerHTML = isOpen() ? '✕' : '☰';
        btn.title     = isOpen() ? 'Close menu' : 'Open menu';
    }

    btn.addEventListener('click', function (e) {
        e.stopPropagation();
        var native = getNativeBtn();
        if (native) {
            native.click();
            setTimeout(syncIcon, 120);
            setTimeout(syncIcon, 450);
        }
    });

    // Sync icon on load
    setTimeout(syncIcon, 300);
    setTimeout(syncIcon, 900);

    // Keep in sync whenever aria-expanded changes (e.g. Streamlit reruns)
    try {
        new MutationObserver(syncIcon).observe(
            window.parent.document.body,
            { subtree: true, attributes: true, attributeFilter: ['aria-expanded'] }
        );
    } catch(e) {}
})();
</script>
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
GTTS_LANG_MAP = {"hi":"hi","ta":"ta","te":"te","kn":"kn","en":"en"}
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

# ── Session state ────────────────────────────────────────────────
if "messages"    not in st.session_state: st.session_state.messages    = []
if "query_count" not in st.session_state: st.session_state.query_count = 0
if "total_ms"    not in st.session_state: st.session_state.total_ms    = 0

# ── TTS ──────────────────────────────────────────────────────────
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

# ── Query ─────────────────────────────────────────────────────────
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
                final_answer += "\n\n⚠️ Please see a doctor within 24 hours."

        return {
            "answer"         : final_answer,
            "triage_level"   : triage.level.value,
            "triage_override": triage.override,
            "sources"        : result["sources"],
            "latency_ms"     : int((time.time() - t0) * 1000),
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
    st.markdown("""
    <div style="font-size:0.78rem;color:#94a3b8;line-height:2">
    📄 WHO Fact Sheets (4 PDFs)<br>
    📄 CDC Yellow Book 2024 (4 PDFs)<br>
    📄 NIH MedlinePlus (4 PDFs)
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    auto_tts = st.checkbox("🔊 Auto-play audio response", value=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div style="font-size:0.78rem;color:#64748b;font-weight:600;margin-bottom:8px">🎙️ VOICE INPUT</div>', unsafe_allow_html=True)
    uploaded = st.file_uploader(
        "Upload audio (.mp3 .wav .ogg .m4a)",
        type=["mp3", "wav", "ogg", "m4a"],
        key="voice_upload",
        label_visibility="collapsed",
    )

    st.markdown("<br>", unsafe_allow_html=True)
    avg_ms = st.session_state.total_ms // max(st.session_state.query_count, 1)
    st.markdown(f"""
    <div style="font-size:0.78rem;color:#64748b;font-weight:600;margin-bottom:8px">SESSION STATS</div>
    <div style="display:flex;flex-wrap:wrap;gap:8px">
        <div style="flex:1;min-width:80px;background:#0f172a;border:1px solid #1e293b;border-radius:8px;padding:10px;text-align:center">
            <div style="font-size:1.3rem;font-weight:700;color:#60a5fa">{st.session_state.query_count}</div>
            <div style="font-size:0.65rem;color:#64748b">Queries</div>
        </div>
        <div style="flex:1;min-width:80px;background:#0f172a;border:1px solid #1e293b;border-radius:8px;padding:10px;text-align:center">
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
st.markdown("""
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
                        st.markdown(f'<div class="source-card"><strong>{name}</strong> · page {s["page"]}<br><span style="color:#475569">{s["content"][:120]}...</span></div>', unsafe_allow_html=True)
            if msg.get("latency"):
                st.caption(f"⏱️ {msg['latency']}ms")

# ── Voice upload handler ─────────────────────────────────────────
if uploaded is not None:
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

            v_query    = transcript_data.get('text', '')
            v_detected = transcript_data.get('lang_code', 'en')
            v_lang_n   = transcript_data.get('language', 'English')

            with st.chat_message("user"):
                st.markdown(f"🎙️ {v_query}")

            with st.chat_message("assistant"):
                with st.spinner("Searching medical knowledge base..."):
                    result  = ask_pipeline(v_query, v_detected, v_lang_n)

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
                audio_bytes = text_to_speech(answer, v_detected)
                if audio_bytes:
                    st.markdown("**🔊 Listen:**")
                    st.audio(audio_bytes, format="audio/mp3", start_time=0)
                    st.download_button("⬇️ Download", audio_bytes, "response.mp3", "audio/mp3")

            st.session_state.messages.extend([
                {"role": "user",      "content": f"🎙️ {v_query}"},
                {"role": "assistant", "content": answer,
                 "triage": triage, "latency": latency, "sources": sources},
            ])
            st.session_state.query_count += 1
            st.session_state.total_ms    += latency

        except Exception as e:
            st.error(f"Voice processing failed: {str(e)}")

# ── Text chat ────────────────────────────────────────────────────
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
            with st.expander(f"📚 {len(sources)} source(s)", expanded=triage == "red"):
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
                st.download_button("⬇️ Download audio", audio_bytes, "response.mp3", "audio/mp3")

    st.session_state.messages.append({
        "role": "assistant", "content": answer,
        "triage": triage, "latency": latency, "sources": sources,
    })
    st.session_state.query_count += 1
    st.session_state.total_ms    += latency