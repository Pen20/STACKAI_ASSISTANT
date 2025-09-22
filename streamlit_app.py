import streamlit as st
from pathlib import Path
from scripts.llm_chat import ask_llm




st.set_page_config(
    page_title="Educational Feedback Analysis Assistant",
    page_icon="🤖",
    layout="wide",
)


# === GLOBAL SIDEBAR OPENAI KEY HANDLING ===
CACHE_PATH = Path(".openai_key_cache.txt")

with st.sidebar:
    st.subheader("🔑 API Key")
    default_key = ""
    if CACHE_PATH.exists():
        default_key = CACHE_PATH.read_text().strip()

    user_key = st.text_input("Enter your OpenAI API key", type="password", value=default_key)
    if user_key:
        st.session_state.OPENAI_API_KEY = user_key
        if st.checkbox("💾 Remember key on this device"):
            CACHE_PATH.write_text(user_key)


# --- PAGE SETUP ---
about_page = st.Page(
    "views/about_me.py",
    title="About Me",
    icon=":material/account_circle:",
    default=True,
)
project_1_page = st.Page(
    "views/dashboard.py",
    title="Dashboard",
    icon=":material/bar_chart:",
)
project_2_page = st.Page(
    "views/chatbot.py",
    title="Chat Bot",
    icon=":material/smart_toy:",
)


# --- NAVIGATION SETUP [WITH SECTIONS] ---
pg = st.navigation(
    {
        "Info": [about_page],
        "Projects": [project_1_page, project_2_page],
        
    }
)

# --- RUN NAVIGATION ---
pg.run()
