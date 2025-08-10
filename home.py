import streamlit as st
from model import process_video, chat_with_video

# ---------- Page config ----------
st.set_page_config(page_title="YouTube Transcript Chatbot", layout="wide")
st.title("🎥 YouTube Transcript Chatbot")

# ---------- Custom CSS for nicer look ----------
st.markdown(
    """
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
    """,
    unsafe_allow_html=True,
)

if "retriever" not in st.session_state:
    st.session_state.retriever = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "query" not in st.session_state:
    st.session_state.query = ""

# ---------- Helper functions ----------
def handle_send():
    query = st.session_state.query
    if query.strip():
        with st.spinner("Thinking..."):
            answer = chat_with_video(st.session_state.retriever, query)
        st.session_state.chat_history.append((query, answer))
        st.session_state.query = ""  # safe to reset inside callback

def handle_load():
    youtube_url = st.session_state.youtube_url
    if youtube_url.strip():
        with st.spinner("Processing video..."):
            try:
                st.session_state.retriever = process_video(youtube_url)
                st.session_state.chat_history.clear()
                st.session_state.query = ""
                st.success("Video processed successfully! You can now chat.")
            except Exception as e:
                st.error(f"Error: {e}")
    else:
        st.warning("Please enter a valid YouTube link.")

# ---------- Main container ----------
st.markdown("<div class='app-container'>", unsafe_allow_html=True)

with st.container():
    # Input area
    st.markdown("<div class='controls'>", unsafe_allow_html=True)
    st.markdown("<div class='hint'>Paste a YouTube link (full URL) and click <b>Load Video</b>.</div>", unsafe_allow_html=True)
    st.text_input("Enter YouTube Video Link", key="youtube_url")
    st.button("Load Video", key="load_video", on_click=handle_load)
    st.markdown("</div>", unsafe_allow_html=True)

    st.write("")  # spacing

    # Chat area
    if st.session_state.retriever:
        st.subheader("💬 Chat with the video")
        st.markdown("<div class='chat-box'>", unsafe_allow_html=True)

        if not st.session_state.chat_history:
            st.info("No messages yet — ask a question using the input below.")
        else:
            for q, a in st.session_state.chat_history:
                st.markdown(f"<div class='clearfix'><div class='msg user'>{q}</div></div>", unsafe_allow_html=True)
                st.markdown(f"<div class='clearfix'><div class='msg bot'>{a}</div></div>", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

        # Query input
        st.text_input("Ask something about the video:", key="query")
        st.button("Send", key="send", on_click=handle_send)
    else:
        st.info("ℹ️ Load a YouTube video above to start chatting.")

st.markdown("</div>", unsafe_allow_html=True)
