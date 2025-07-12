import streamlit as st

st.title("🔐 OpenAI Key Status")

if "OPENAI_API_KEY" in st.session_state:
    st.success("✅ API key is set for this session.")
    st.code(st.session_state.OPENAI_API_KEY, language="text")
else:
    st.warning("⚠️ API key is not set. Use the sidebar to enter it.")
