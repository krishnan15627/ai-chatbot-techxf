"""
app.py - TechXfluence AI chatbot (Streamlit user interface).

Run with:   streamlit run app.py

RAG flow used here:
    question -> Retriever.search() -> best text chunks -> Gemini (free API) -> answer + sources
"""

from __future__ import annotations

import html
import hashlib
import json
import os
from pathlib import Path

import streamlit as st

import gemini_llm
import rag_engine

st.set_page_config(page_title="TechXfluence AI", page_icon="⚡", layout="centered")

def saved_settings() -> tuple[str, str]:
    """Key + model from the environment, or from .streamlit/secrets.toml when present."""
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    model = os.getenv("GEMINI_MODEL", gemini_llm.DEFAULT_MODEL).strip()
    try:
        api_key = str(st.secrets.get("GEMINI_API_KEY", api_key)).strip() or api_key
        model = str(st.secrets.get("GEMINI_MODEL", model)).strip() or model
    except Exception:
        pass
    return api_key, model or gemini_llm.DEFAULT_MODEL


def save_settings(api_key: str, model: str) -> tuple[bool, str]:
    """Write the sidebar settings into .streamlit/secrets.toml (gitignored)."""
    path = Path(__file__).parent / ".streamlit" / "secrets.toml"
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            "# Saved from the TechXfluence AI sidebar - never commit this file.\n"
            f"GEMINI_API_KEY = {json.dumps(api_key)}\n"
            f"GEMINI_MODEL = {json.dumps(model)}\n",
            encoding="utf-8",
        )
    except OSError as exc:
        return False, f"Could not save the key: {exc}"
    return True, "Key and model saved for next time."


@st.cache_data(ttl=120, show_spinner=False)
def available_models(api_key: str) -> list[str]:
    return gemini_llm.list_models(api_key=api_key)


@st.cache_data(ttl=60, show_spinner=False)
def gemini_status(api_key: str, model: str) -> dict:
    return gemini_llm.get_status(model=model, api_key=api_key)

# ----------------------------------------------------------------------------
# Custom CSS - dark navy, cyan + purple accents
# ----------------------------------------------------------------------------
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Space+Grotesk:wght@600;700&display=swap');
:root { --navy:#0a1128; --navy2:#101a3a; --card:#131f45; --cyan:#22d3ee; --purple:#a78bfa; --text:#e6ecff; --muted:#93a0c8; }
html, body, [class*="css"], .stApp { font-family:'Inter',sans-serif; color:var(--text); }
.stApp { background: radial-gradient(1200px 600px at 10% -10%, #1b2a6b55, transparent),
                     radial-gradient(900px 500px at 100% 0%, #6d3fd244, transparent), var(--navy); }
header[data-testid="stHeader"] { background:transparent; }
.block-container { padding-top:1.5rem; max-width:860px; }

.brand { display:flex; align-items:center; gap:14px; padding:18px 20px; border-radius:18px;
         background:linear-gradient(135deg,#132155,#1d1650); border:1px solid #2b3b7a; margin-bottom:14px; }
.brand .logo { width:48px; height:48px; border-radius:14px; display:grid; place-items:center; font-size:26px;
               background:linear-gradient(135deg,var(--cyan),var(--purple)); box-shadow:0 0 24px #22d3ee55; }
.brand h1 { font-family:'Space Grotesk',sans-serif; font-size:1.7rem; margin:0; line-height:1.1; color:#fff; }
.brand h1 span { background:linear-gradient(90deg,var(--cyan),var(--purple)); -webkit-background-clip:text; color:transparent; }
.brand p { margin:2px 0 0; color:var(--muted); font-size:.9rem; }

[data-testid="stChatMessage"] { background:var(--card); border:1px solid #243468; border-radius:16px; padding:14px 16px; }
[data-testid="stChatMessage"] p, [data-testid="stChatMessage"] li { line-height:1.6; font-size:.98rem; }
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) { background:linear-gradient(135deg,#1c2a63,#2a1f66); border-color:#4a3fa0; }

.stButton > button, .stButton > button p { color:var(--text) !important; }
.stButton > button { background:var(--navy2); border:1px solid #2f4189; border-radius:999px;
                     padding:.45rem .9rem; font-size:.88rem; transition:all .15s; width:100%; }
.stButton > button:hover { border-color:var(--cyan); color:var(--cyan); box-shadow:0 0 14px #22d3ee33; transform:translateY(-1px); }

.src { display:inline-block; margin:4px 6px 0 0; padding:4px 10px; border-radius:999px; font-size:.78rem;
       background:#0e1a42; border:1px solid #2f4189; color:var(--cyan) !important; text-decoration:none; }
.src:hover { border-color:var(--purple); color:var(--purple) !important; }
.src-label { color:var(--muted); font-size:.78rem; margin-top:10px; }

[data-testid="stSidebar"] { background:#080e22; border-right:1px solid #1d2a5c; }
.step { display:flex; gap:10px; align-items:flex-start; margin:8px 0; font-size:.88rem; color:var(--text); }
.step b { min-width:24px; height:24px; border-radius:50%; display:grid; place-items:center; font-size:.75rem;
          background:linear-gradient(135deg,var(--cyan),var(--purple)); color:#07102a; }
.pill { display:inline-block; padding:3px 10px; border-radius:999px; font-size:.78rem; font-weight:600; }
.ok { background:#06402f; color:#4ade80; } .bad { background:#4a1120; color:#fb7185; } .warn { background:#4a3a0a; color:#fbbf24; }

[data-testid="stChatInput"] { border-radius:14px; background:var(--navy2); border:1px solid #2f4189; }
[data-testid="stChatInput"] textarea { color:var(--text) !important; background:transparent; }
[data-testid="stBottom"], [data-testid="stBottom"] > div { background:var(--navy) !important; }
.stApp, .stApp p, .stApp li, .stApp span, .stApp label, .stApp h1, .stApp h2, .stApp h3, [data-testid="stMarkdownContainer"] { color:var(--text); }
.stCaption, [data-testid="stCaptionContainer"] { color:var(--muted) !important; }
[data-testid="stSidebar"] * { color:var(--text); }
.brand h1 span { color:transparent !important; }
.pill.ok { color:#4ade80 !important; } .pill.bad { color:#fb7185 !important; } .pill.warn { color:#fbbf24 !important; }
.step b { color:#07102a !important; }
.src, .src * { color:var(--cyan) !important; }
.footer { text-align:center; color:var(--muted); font-size:.75rem; margin-top:18px; }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)


@st.cache_data(show_spinner=False, max_entries=20)
def read_resource(data: bytes, name: str):
    """Extract and chunk an uploaded resource, cached by its content."""
    if name.lower().endswith(".pdf"):
        return rag_engine.pdf_to_chunks(data, name)
    return rag_engine.text_resource_to_chunks(data, name), None

# ----------------------------------------------------------------------------
# Session state
# ----------------------------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

_default_api_key, _default_model = saved_settings()
st.session_state.setdefault("api_key", _default_api_key)
st.session_state.setdefault("model", _default_model)


def sources_html(sources: list[dict]) -> str:
    parts = ['<div class="src-label">Sources used</div>']
    for s in sources:
        label = html.escape(f'{s["title"]} · {s["file"]}')
        if s["source"].startswith("http"):
            parts.append(f'<a class="src" href="{html.escape(s["source"])}" target="_blank">🔗 {label}</a>')
        else:
            parts.append(f'<span class="src">📄 {label}</span>')
    return "".join(parts)


# ----------------------------------------------------------------------------
# Sidebar
# ----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### ⚡ TechXfluence AI")
    st.caption("Answers grounded only in resources you upload")

    st.markdown("**🔑 Gemini API key**")
    key_input = st.text_input(
        "Gemini API key",
        key="api_key",
        type="password",
        placeholder="Paste your key from aistudio.google.com/apikey",
        help="Free key: https://aistudio.google.com/apikey — it stays in this browser session unless you save it.",
        label_visibility="collapsed",
    )

    typed_key = (key_input or "").strip()
    model_choices = available_models(typed_key) if typed_key else []
    st.selectbox(
        "Model",
        options=list(dict.fromkeys([st.session_state.model, *model_choices])),
        key="model",
        accept_new_options=True,
        help="Models are loaded live from your API key. Type a name to use one that is not listed.",
    )
    if model_choices:
        st.caption(f"{len(model_choices)} models available for this key")
    elif typed_key:
        st.caption("Could not load the model list — check the key, or keep the model name above.")

    test_col, save_col = st.columns(2)
    with test_col:
        test_clicked = st.button("🔄 Test", help="Check this key and model now")
    with save_col:
        save_clicked = st.button("💾 Save", help="Save the key and model to .streamlit/secrets.toml")
    if test_clicked:
        gemini_status.clear()
        available_models.clear()
    if save_clicked:
        saved_ok, saved_message = save_settings(typed_key, st.session_state.model)
        (st.success if saved_ok else st.warning)(saved_message)

    api_key, model = typed_key, st.session_state.model
    status = gemini_status(api_key, model)
    if status["model_ready"]:
        st.markdown(f'<span class="pill ok">● {html.escape(model)} ready</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="pill bad">● Gemini not ready</span>', unsafe_allow_html=True)
        st.caption(status.get("detail") or "Paste a valid API key above.")

    st.markdown("**📚 Upload resources**")
    uploads = st.file_uploader(
        "Upload PDF, TXT, Markdown, or JSON files",
        type=["pdf", "txt", "md", "json"], accept_multiple_files=True,
        key="resource_uploader",
    )
    resource_chunks = []
    resource_files = [(up.name, up.getvalue()) for up in uploads or []]
    resource_signature = tuple(
        (name, hashlib.sha256(data).hexdigest()) for name, data in resource_files
    )
    if st.session_state.get("resource_signature") != resource_signature:
        st.session_state.messages = []
        st.session_state.resource_signature = resource_signature
    for name, data in resource_files:
        try:
            chunks, total_pages = read_resource(data, name)
        except ValueError as exc:
            st.error(f"{name}: {exc}")
            continue
        if not chunks:
            st.warning(f"{name}: no readable text found (scanned/image PDFs are not supported).")
            continue
        resource_chunks.extend(chunks)
        details = f"{name} · {len(chunks)} chunks"
        if total_pages is not None:
            details = f"{name} · {total_pages} pages · {len(chunks)} chunks"
        st.caption(f"✓ {details}")
    if resource_chunks:
        st.caption(f"Indexed {len(resource_chunks)} chunks from uploaded resources.")
    else:
        st.info("Upload resources to build your searchable knowledge base.")
    st.divider()
    if st.button("🗑️ Clear chat"):
        st.session_state.messages = []
        st.session_state.pending = None
        st.rerun()

# ----------------------------------------------------------------------------
# Header
# ----------------------------------------------------------------------------
st.markdown(
    """
<div class="brand">
  <div class="logo">⚡</div>
  <div><h1>TechXfluence <span>AI</span></h1>
    <p>Ask questions grounded in your uploaded resources</p></div>
</div>
""",
    unsafe_allow_html=True,
)

# Welcome message (shown until the first question)
if not st.session_state.messages:
    with st.chat_message("assistant", avatar="⚡"):
        st.markdown("Upload your resources, then ask a question. Answers use only the uploaded files.")

# ----------------------------------------------------------------------------
# Chat history
# ----------------------------------------------------------------------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar="⚡" if msg["role"] == "assistant" else "🧑"):
        st.markdown(msg["content"])
        if msg.get("sources"):
            st.markdown(sources_html(msg["sources"]), unsafe_allow_html=True)

# ----------------------------------------------------------------------------
# Handle a new question
# ----------------------------------------------------------------------------
question = st.chat_input(
    "Ask about your uploaded resources...",
    disabled=not status["model_ready"] or not resource_chunks,
)


def retrieval_query(q: str) -> str:
    """Short follow-ups ("and the price?") borrow words from the previous question."""
    words = [w for w in q.lower().split() if w not in rag_engine.STOPWORDS]
    prev = [m["content"] for m in st.session_state.messages if m["role"] == "user"]
    return f"{prev[-1]} {q}" if len(words) <= 2 and prev else q


if question:
    history = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user", avatar="🧑"):
        st.markdown(question)

    with st.chat_message("assistant", avatar="⚡"):
        answer, sources = "", []

        if rag_engine.is_greeting(question):
            answer = rag_engine.WELCOME_MESSAGE
            st.markdown(answer)
        elif not resource_chunks:
            answer = "The knowledge base is empty. Upload a resource in the sidebar first."
            st.error(answer)
        else:
            active = rag_engine.Retriever(resource_chunks)
            not_found = rag_engine.NOT_FOUND_MESSAGE
            system_prompt = rag_engine.make_system_prompt(not_found, pdf_mode=True)
            retrieved = active.search(retrieval_query(question), min_score=0.2)
            if not retrieved:
                # Nothing relevant found -> do NOT ask the LLM (prevents made-up answers).
                answer = not_found
                st.markdown(answer)
            else:
                prompt = rag_engine.build_prompt(question, retrieved)
                try:
                    with st.spinner("TechXfluence AI is thinking..."):
                        stream = gemini_llm.stream_answer(
                            prompt, system_prompt, history, model=model, api_key=api_key
                        )
                        first = next(stream, "")  # spinner stays until the first token arrives

                    def chained():
                        yield first
                        yield from stream

                    answer = st.write_stream(chained())
                    if rag_engine.is_not_found(answer):
                        answer = not_found
                    else:
                        sources = rag_engine.unique_sources(retrieved)
                        st.markdown(sources_html(sources), unsafe_allow_html=True)
                except gemini_llm.GeminiError as exc:
                    answer = f"⚠️ {exc}"
                    st.warning(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer, "sources": sources})

st.markdown(
    '<div class="footer">Answers are generated only from the resources uploaded to this session. '
    "Verify prices, dates and openings on the official website.</div>",
    unsafe_allow_html=True,
)
