import streamlit as st
from model import process_video, chat_with_video, get_available_languages

# ---------- Page config ----------
st.set_page_config(page_title="YouTube Transcript Chatbot", layout="wide")
st.title("🎥 YouTube Transcript Chatbot")

# ---------- CSS ----------
st.markdown("""
<style>
.app-container { max-width: 900px; margin: 0 auto; }
.controls { background: #0e1117; padding: 12px; border-radius: 10px; box-shadow: 0 2px 6px rgba(0,0,0,0.04); }
.chat-box { background: #0e1117; padding: 14px; border-radius: 12px; }
.msg { padding:10px 14px; border-radius:12px; margin:8px 0; display:inline-block; max-width:85%; }
.user { background: #986988; float:right; text-align:right; }
.bot  { background: #181d27; float:left; text-align:left; }
.clearfix::after { content: ""; display: table; clear: both; }
.hint { color:#5c6b73; font-size:0.95rem; margin-bottom:8px; }
</style>
""", unsafe_allow_html=True)

# ---------- Session state ----------
if "retriever" not in st.session_state:
    st.session_state.retriever = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "query" not in st.session_state:
    st.session_state.query = ""
if "available_languages" not in st.session_state:
    st.session_state.available_languages = []
if "chosen_lang_code" not in st.session_state:
    st.session_state.chosen_lang_code = "en"
if "chosen_lang_display" not in st.session_state:
    st.session_state.chosen_lang_display = ""

# ---------- Handlers ----------
def handle_send():
    query = st.session_state.query
    if query.strip():
        with st.spinner("Thinking..."):
            answer = chat_with_video(st.session_state.retriever, query)
        st.session_state.chat_history.append((query, answer))
        st.session_state.query = ""

def handle_load_languages():
    youtube_url = st.session_state.youtube_url if "youtube_url" in st.session_state else ""
    if youtube_url.strip():
        with st.spinner("Fetching available languages..."):
            langs = get_available_languages(youtube_url)
            if not langs:
                st.error("No transcripts available for this video.")
                return
            st.session_state.available_languages = langs
            st.success("Languages loaded! Please choose from the dropdown.")
    else:
        st.warning("Please enter a valid YouTube link.")

def handle_lang_select():
    # Sync chosen_lang_code with chosen_lang_display
    for name, code in st.session_state.available_languages:
        if st.session_state.chosen_lang_display == f"{name} ({code})":
            st.session_state.chosen_lang_code = code
            break

def handle_process_video():
    youtube_url = st.session_state.youtube_url if "youtube_url" in st.session_state else ""
    chosen_lang = st.session_state.chosen_lang_code
    if youtube_url.strip():
        with st.spinner("Processing video..."):
            try:
                st.session_state.retriever = process_video(youtube_url, chosen_lang)
                st.session_state.chat_history.clear()
                st.session_state.query = ""
                st.success(f"Video processed successfully in '{chosen_lang}' language! You can now chat.")
            except Exception as e:
                st.error(f"Error: {e}")

# ---------- UI ----------
st.markdown("<div class='app-container'>", unsafe_allow_html=True)

with st.container():
    st.markdown("<div class='controls'>", unsafe_allow_html=True)
    st.markdown("<div class='hint'>Paste a YouTube link and load available transcript languages.</div>", unsafe_allow_html=True)
    st.text_input("Enter YouTube Video Link", key="youtube_url")
    st.button("Load Languages", key="load_langs", on_click=handle_load_languages)

    if st.session_state.available_languages:
        display_names = [f"{name} ({code})" for name, code in st.session_state.available_languages]
        st.selectbox(
            "Choose transcript language:", 
            display_names, 
            key="chosen_lang_display",
            on_change=handle_lang_select
        )
        st.button("Process Video", key="process_video", on_click=handle_process_video)

    st.markdown("</div>", unsafe_allow_html=True)

    st.write("")

    # Chat area
    if st.session_state.retriever:
        st.subheader("💬 Chat with the video")
        st.markdown("<div class='chat-box'>", unsafe_allow_html=True)

        if not st.session_state.chat_history:
            st.info("No messages yet — ask a question below.")
        else:
            for q, a in st.session_state.chat_history:
                st.markdown(f"<div class='clearfix'><div class='msg user'>{q}</div></div>", unsafe_allow_html=True)
                st.markdown(f"<div class='clearfix'><div class='msg bot'>{a}</div></div>", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

        st.text_input("Ask something about the video:", key="query")
        st.button("Send", key="send", on_click=handle_send)
    else:
        st.info("ℹ️ Load a YouTube video above to start chatting.")

st.markdown("</div>", unsafe_allow_html=True)
