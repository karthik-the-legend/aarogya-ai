# ================================================================
# frontend\streamlit_app.py — Aarogya AI Frontend
# Run: streamlit run streamlit_app.py
# Requires: FastAPI backend running at http://localhost:8000
# ================================================================

import streamlit as st
import requests
from datetime import datetime

# ── Page config — MUST be first ─────────────────────────────────
st.set_page_config(
    page_title="Aarogya AI",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS ───────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

/* ── Root variables ── */
:root {
    --green:  #00c853;
    --yellow: #ffd600;
    --red:    #ff1744;
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

/* ── Main container ── */
.main .block-container {
    padding: 1.5rem 2rem !important;
    max-width: 1100px !important;
}

/* ── Hero header ── */
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
    top: -50%;
    right: -10%;
    width: 300px;
    height: 300px;
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
.hero-sub {
    color: #94a3b8;
    font-size: 0.9rem;
    font-weight: 400;
    margin: 0;
}

/* ── Triage badges ── */
.badge-green {
    background: #00c85318;
    color: #00c853;
    border: 1px solid #00c85340;
    padding: 4px 14px;
    border-radius: 100px;
    font-size: 0.75rem;
    font-weight: 600;
    display: inline-block;
    margin-top: 8px;
}
.badge-yellow {
    background: #ffd60018;
    color: #ffd600;
    border: 1px solid #ffd60040;
    padding: 4px 14px;
    border-radius: 100px;
    font-size: 0.75rem;
    font-weight: 600;
    display: inline-block;
    margin-top: 8px;
}
.badge-red {
    background: #ff174418;
    color: #ff1744;
    border: 1px solid #ff174440;
    padding: 4px 14px;
    border-radius: 100px;
    font-size: 0.75rem;
    font-weight: 600;
    display: inline-block;
    margin-top: 8px;
    animation: pulse 1.5s infinite;
}
@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.6; }
}

/* ── Source cards ── */
.source-card {
    background: #0f172a;
    border: 1px solid #1e293b;
    border-radius: 10px;
    padding: 10px 14px;
    margin-top: 8px;
    font-size: 0.78rem;
    color: #94a3b8;
    font-family: 'JetBrains Mono', monospace;
}
.source-card strong {
    color: #60a5fa;
}

/* ── Chat messages ── */
.stChatMessage {
    background: #111827 !important;
    border: 1px solid #1e293b !important;
    border-radius: 12px !important;
    margin-bottom: 12px !important;
}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: #0d1424 !important;
    border-right: 1px solid #1e293b !important;
}
section[data-testid="stSidebar"] .block-container {
    padding: 1.5rem 1rem !important;
}

/* ── Selectbox ── */
.stSelectbox > div > div {
    background: #111827 !important;
    border: 1px solid #1e293b !important;
    border-radius: 8px !important;
    color: #e2e8f0 !important;
}

/* ── Chat input ── */
.stChatInputContainer {
    border: 1px solid #1e40af55 !important;
    border-radius: 12px !important;
    background: #111827 !important;
}

/* ── Buttons ── */
.stButton > button {
    background: #1e293b !important;
    color: #94a3b8 !important;
    border: 1px solid #334155 !important;
    border-radius: 8px !important;
    font-family: 'Sora', sans-serif !important;
    transition: all 0.2s !important;
}
.stButton > button:hover {
    background: #334155 !important;
    color: #e2e8f0 !important;
}

/* ── Stat cards ── */
.stat-row {
    display: flex;
    gap: 12px;
    margin-bottom: 20px;
}
.stat-card {
    flex: 1;
    background: #111827;
    border: 1px solid #1e293b;
    border-radius: 10px;
    padding: 14px 16px;
    text-align: center;
}
.stat-num {
    font-size: 1.6rem;
    font-weight: 700;
    color: #60a5fa;
}
.stat-label {
    font-size: 0.72rem;
    color: #64748b;
    margin-top: 2px;
}

/* ── Spinner ── */
.stSpinner > div {
    border-top-color: #3b82f6 !important;
}

/* ── Warning ── */
.stAlert {
    background: #ffd60010 !important;
    border: 1px solid #ffd60030 !important;
    border-radius: 10px !important;
    color: #ffd600 !important;
}

/* ── Divider ── */
hr {
    border-color: #1e293b !important;
}
</style>
""", unsafe_allow_html=True)

# ── Constants ────────────────────────────────────────────────────
API_BASE = "http://localhost:8000"

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

EXAMPLE_QUERIES = {
    "hi": ["मुझे बुखार है", "डेंगू के लक्षण क्या हैं", "मलेरिया का इलाज"],
    "ta": ["எனக்கு காய்ச்சல்", "டெங்கு அறிகுறிகள்"],
    "te": ["నాకు జ్వరం వచ్చింది", "డెంగీ లక్షణాలు"],
    "kn": ["ನನಗೆ ಜ್ವರ ಬಂದಿದೆ", "ಡೆಂಗ್ಯೂ ಲಕ್ಷಣಗಳು"],
    "en": ["Symptoms of dengue fever", "Can I take ibuprofen for dengue?", "Malaria treatment"],
}

# ── Session state ────────────────────────────────────────────────
if "messages"    not in st.session_state: st.session_state.messages    = []
if "query_count" not in st.session_state: st.session_state.query_count = 0
if "total_ms"    not in st.session_state: st.session_state.total_ms    = 0

# ── API call ─────────────────────────────────────────────────────
def ask_api(query: str, lang_code: str, language_name: str) -> dict:
    try:
        r = requests.post(
            f"{API_BASE}/ask",
            json={"query": query, "lang_code": lang_code, "language_name": language_name},
            timeout=30
        )
        r.raise_for_status()
        return r.json()
    except requests.exceptions.ConnectionError:
        return {
            "answer"        : "❌ Cannot connect to backend. Make sure FastAPI is running at localhost:8000",
            "triage_level"  : "green",
            "triage_override": False,
            "sources"       : [],
            "latency_ms"    : 0,
        }
    except Exception as e:
        return {
            "answer"        : f"❌ Error: {str(e)}",
            "triage_level"  : "green",
            "triage_override": False,
            "sources"       : [],
            "latency_ms"    : 0,
        }

def check_backend() -> bool:
    try:
        r = requests.get(f"{API_BASE}/health", timeout=3)
        return r.json().get("rag_loaded", False)
    except:
        return False

# ── Sidebar ──────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="text-align:center;padding:10px 0 20px">
        <div style="font-size:2.5rem">🩺</div>
        <div style="font-size:1.1rem;font-weight:700;color:#60a5fa">Aarogya AI</div>
        <div style="font-size:0.72rem;color:#64748b;margin-top:4px">Vernacular Health Assistant</div>
    </div>
    """, unsafe_allow_html=True)

    # Backend status
    is_ready = check_backend()
    if is_ready:
        st.markdown('<div style="background:#00c85315;border:1px solid #00c85340;border-radius:8px;padding:8px 12px;font-size:0.78rem;color:#00c853;text-align:center">● Backend Connected</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div style="background:#ff174415;border:1px solid #ff174440;border-radius:8px;padding:8px 12px;font-size:0.78rem;color:#ff1744;text-align:center">● Backend Offline</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Language selector
    st.markdown('<div style="font-size:0.78rem;color:#64748b;font-weight:600;margin-bottom:6px">LANGUAGE</div>', unsafe_allow_html=True)
    selected_lang_display = st.selectbox("", options=list(LANG_MAP.keys()), label_visibility="collapsed")
    lang_code    = LANG_MAP[selected_lang_display]
    language_name = selected_lang_display.split(" ", 1)[1]

    st.markdown("<br>", unsafe_allow_html=True)

    # Example queries
    st.markdown('<div style="font-size:0.78rem;color:#64748b;font-weight:600;margin-bottom:8px">EXAMPLE QUERIES</div>', unsafe_allow_html=True)
    examples = EXAMPLE_QUERIES.get(lang_code, EXAMPLE_QUERIES["en"])
    for ex in examples:
        if st.button(ex, key=f"ex_{ex}", use_container_width=True):
            st.session_state["prefill"] = ex

    st.markdown("<br>", unsafe_allow_html=True)

    # Knowledge base
    st.markdown('<div style="font-size:0.78rem;color:#64748b;font-weight:600;margin-bottom:8px">KNOWLEDGE BASE</div>', unsafe_allow_html=True)
    st.markdown("""
    <div style="font-size:0.78rem;color:#94a3b8;line-height:2">
    📄 WHO Fact Sheets (4 PDFs)<br>
    📄 CDC Yellow Book 2024 (4 PDFs)<br>
    📄 NIH MedlinePlus (4 PDFs)<br>
    <span style="color:#64748b">12 verified medical documents</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Stats
    avg_ms = st.session_state.total_ms // max(st.session_state.query_count, 1)
    st.markdown(f"""
    <div style="font-size:0.78rem;color:#64748b;font-weight:600;margin-bottom:8px">SESSION STATS</div>
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

    st.warning("⚠️ General health info only — not a medical diagnosis. Always consult a doctor.")

    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages    = []
        st.session_state.query_count = 0
        st.session_state.total_ms    = 0
        st.rerun()

# ── Main area ────────────────────────────────────────────────────
st.markdown(f"""
<div class="hero">
    <div class="hero-title">🩺 Aarogya AI</div>
    <p class="hero-sub">
        RAG-powered health assistant for rural India &nbsp;·&nbsp;
        WHO · CDC · NIH verified sources &nbsp;·&nbsp;
        Hindi · Tamil · Telugu · Kannada · English
    </p>
</div>
""", unsafe_allow_html=True)

# ── Chat history ─────────────────────────────────────────────────
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg["role"] == "assistant":
            level  = msg.get("triage", "green")
            emoji, cls, label = TRIAGE_CONFIG.get(level, TRIAGE_CONFIG["green"])
            st.markdown(f'<span class="{cls}">{emoji} {label}</span>', unsafe_allow_html=True)

            # Sources
            sources = msg.get("sources", [])
            if sources:
                with st.expander(f"📚 {len(sources)} source(s) used", expanded=False):
                    for s in sources:
                        name = s['source'].split('\\')[-1].split('/')[-1]
                        st.markdown(f"""
                        <div class="source-card">
                            <strong>{name}</strong> · page {s['page']}<br>
                            <span style="color:#475569">{s['content'][:120]}...</span>
                        </div>
                        """, unsafe_allow_html=True)

            if msg.get("latency"):
                st.caption(f"⏱️ {msg['latency']}ms")

# ── Prefill from example buttons ─────────────────────────────────
prefill = st.session_state.pop("prefill", "")

# ── Chat input ───────────────────────────────────────────────────
query = st.chat_input(f"Ask in {language_name}... e.g. symptoms of dengue") or prefill

if query:
    # Show user message
    with st.chat_message("user"):
        st.markdown(query)
    st.session_state.messages.append({"role": "user", "content": query})

    # Get response
    with st.chat_message("assistant"):
        with st.spinner("Searching medical knowledge base..."):
            result  = ask_api(query, lang_code, language_name)

        answer  = result.get("answer", "No response.")
        triage  = result.get("triage_level", "green")
        latency = result.get("latency_ms", 0)
        sources = result.get("sources", [])

        st.markdown(answer)

        # Triage badge
        emoji, cls, label = TRIAGE_CONFIG.get(triage, TRIAGE_CONFIG["green"])
        st.markdown(f'<span class="{cls}">{emoji} {label}</span>', unsafe_allow_html=True)

        # Sources expander
        if sources:
            with st.expander(f"📚 {len(sources)} source(s) used", expanded=triage == "red"):
                for s in sources:
                    name = s['source'].split('\\')[-1].split('/')[-1]
                    st.markdown(f"""
                    <div class="source-card">
                        <strong>{name}</strong> · page {s['page']}<br>
                        <span style="color:#475569">{s['content'][:120]}...</span>
                    </div>
                    """, unsafe_allow_html=True)

        st.caption(f"⏱️ {latency}ms")

    # Save to history
    st.session_state.messages.append({
        "role"   : "assistant",
        "content": answer,
        "triage" : triage,
        "latency": latency,
        "sources": sources,
    })
    st.session_state.query_count += 1
    st.session_state.total_ms    += latency

# ── Voice Upload ─────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<div style="font-size:0.78rem;color:#64748b;font-weight:600;margin-bottom:8px">🎙️ VOICE INPUT</div>', unsafe_allow_html=True)

uploaded = st.file_uploader(
    "Upload audio file",
    type=["mp3", "wav", "ogg", "m4a"],
    label_visibility="collapsed",
    help="Upload an audio file to transcribe and ask"
)

if uploaded is not None:
    with st.spinner("🎙️ Transcribing audio..."):
        try:
            files = {
                "audio": (
                    uploaded.name,
                    uploaded.read(),
                    uploaded.type
                )
            }
            r = requests.post(
                f"{API_BASE}/ask-voice",
                files=files,
                timeout=60
            )
            r.raise_for_status()
            data = r.json()

            transcript = data.get("transcript", {})
            answer     = data.get("answer", "")
            triage     = data.get("triage_level", "green")
            sources    = data.get("sources", [])
            latency    = data.get("latency_ms", 0)

            # Show transcript
            st.markdown(f"""
            <div style="background:#0f172a;border:1px solid #1e40af33;
            border-radius:10px;padding:12px 16px;margin-bottom:12px">
                <div style="font-size:0.72rem;color:#64748b;margin-bottom:4px">
                    🎙️ WHISPER TRANSCRIPT · {transcript.get('language','Unknown')}
                </div>
                <div style="color:#e2e8f0">{transcript.get('text','')}</div>
            </div>
            """, unsafe_allow_html=True)

            # Show in chat
            with st.chat_message("user"):
                st.markdown(f"🎙️ {transcript.get('text','')}")

            with st.chat_message("assistant"):
                st.markdown(answer)
                emoji, cls, label = TRIAGE_CONFIG.get(triage, TRIAGE_CONFIG["green"])
                st.markdown(f'<span class="{cls}">{emoji} {label}</span>', unsafe_allow_html=True)

                if sources:
                    with st.expander(f"📚 {len(sources)} source(s) used"):
                        for s in sources:
                            name = s['source'].split('\\')[-1].split('/')[-1]
                            st.markdown(f"""
                            <div class="source-card">
                                <strong>{name}</strong> · page {s['page']}<br>
                                <span style="color:#475569">{s['content'][:120]}...</span>
                            </div>
                            """, unsafe_allow_html=True)

                st.caption(f"⏱️ {latency}ms")

            # Save to history
            st.session_state.messages.append({
                "role"   : "user",
                "content": f"🎙️ {transcript.get('text','')}",
            })
            st.session_state.messages.append({
                "role"   : "assistant",
                "content": answer,
                "triage" : triage,
                "latency": latency,
                "sources": sources,
            })
            st.session_state.query_count += 1
            st.session_state.total_ms    += latency

        except Exception as e:
            st.error(f"Voice upload failed: {str(e)}")