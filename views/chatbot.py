import io
from typing import Optional

import pandas as pd
import streamlit as st
from streamlit.runtime.uploaded_file_manager import UploadedFile

from scripts.data_loader import resolve_dataframe
from scripts.llm_chat import ask_llm


DEFAULT_DATA_PATH = "data/predicting_students_errors.csv"


def load_dataframe(uploaded_file: Optional[UploadedFile]) -> Optional[pd.DataFrame]:
    if uploaded_file is not None:
        try:
            df = resolve_dataframe(uploaded_file, default_path=DEFAULT_DATA_PATH)
            st.success("✅ Your dataset was loaded successfully.")
            return df
        except Exception as exc:  # pragma: no cover - streamlit runtime feedback
            st.error(f"Failed to read uploaded file: {exc}")
            return None
    try:
        df = resolve_dataframe(None, default_path=DEFAULT_DATA_PATH)
        st.info(f"📁 Using default dataset: `{DEFAULT_DATA_PATH}`")
        return df
    except FileNotFoundError:
        st.warning("⚠️ Please upload a dataset to begin.")
        return None


st.title("🤖 Educational Feedback Chatbot")

# === File Upload ===
uploaded_file = st.sidebar.file_uploader("Upload CSV file", type="csv")

df = load_dataframe(uploaded_file)

# === Chat history session ===
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


def _build_chat_history_text() -> str:
    return "\n".join([f"User: {q}\nBot: {a}" for q, a in st.session_state.chat_history])


# === Chatbot UI ===
if df is not None:
    api_key = st.session_state.get("OPENAI_API_KEY")
    if not api_key:
        st.info("Enter your OpenAI API key in the sidebar to chat with the assistant.")
    else:
        st.header("💬 Ask the Educational Chatbot")

        with st.form("chat_form", clear_on_submit=True):
            user_query = st.text_input("Type your question:")
            submitted = st.form_submit_button("Ask")

        if submitted:
            if not user_query.strip():
                st.warning("Please enter a question before submitting.")
            else:
                context = df.head(100).to_csv(index=False)
                chat_history_text = _build_chat_history_text()
                try:
                    with st.spinner("Thinking..."):
                        answer = ask_llm(user_query, context, chat_history_text)
                except RuntimeError as exc:
                    st.error(str(exc))
                else:
                    st.session_state.chat_history.append((user_query, answer))
                    st.markdown(f"**Answer:** {answer}")

    if st.session_state.chat_history:
        st.subheader("🗒️ Chat History")
        for i, (q, a) in enumerate(st.session_state.chat_history):
            st.markdown(f"**Q{i+1}:** {q}")
            st.markdown(f"**A{i+1}:** {a}")

        chat_text = "\n\n".join([f"Q: {q}\nA: {a}" for q, a in st.session_state.chat_history])
        chat_bytes = io.BytesIO(chat_text.encode("utf-8"))
        st.download_button("📥 Download Chat History", data=chat_bytes, file_name="chat_history.txt", mime="text/plain")
else:
    st.info("Upload or use the default dataset to begin interacting with the chatbot.")
