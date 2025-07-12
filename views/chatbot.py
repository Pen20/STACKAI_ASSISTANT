import streamlit as st
import pandas as pd
import io
from scripts.llm_chat import ask_llm

st.set_page_config(layout="wide")
st.title("🤖 Educational Feedback Chatbot")

# === File Upload ===
uploaded_file = st.sidebar.file_uploader("Upload CSV file", type="csv")

df = None
if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)
        st.success("✅ Your dataset was loaded successfully.")
    except Exception as e:
        st.error(f"Failed to read uploaded file: {e}")
else:
    try:
        df = pd.read_csv("data/predicting_students_errors.csv")
        st.info("📁 Using default dataset: `data/predicting_students_errors.csv`")
    except FileNotFoundError:
        st.warning("⚠️ Please upload a dataset to begin.")
        df = None

# === Chat history session ===
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# === Chatbot UI ===
if df is not None:
    st.header("💬 Ask the Educational Chatbot")

    user_query = st.text_input("Type your question:")

    if user_query and st.button("Ask"):
        context = df.head(100).to_csv(index=False)
        chat_history_text = "\n".join([f"User: {q}\nBot: {a}" for q, a in st.session_state.chat_history])
        try:
            answer = ask_llm(user_query, context, chat_history_text)
            st.session_state.chat_history.append((user_query, answer))
            st.markdown(f"**Answer:** {answer}")
        except Exception as e:
            st.error(f"Error during GPT processing: {e}")

    if st.session_state.chat_history:
        st.subheader("🗒️ Chat History")
        for i, (q, a) in enumerate(st.session_state.chat_history):
            st.markdown(f"**Q{i+1}:** {q}")
            st.markdown(f"**A{i+1}:** {a}")

        # Export chat history
        chat_text = "\n\n".join([f"Q: {q}\nA: {a}" for q, a in st.session_state.chat_history])
        chat_bytes = io.BytesIO(chat_text.encode("utf-8"))
        st.download_button("📥 Download Chat History", data=chat_bytes, file_name="chat_history.txt", mime="text/plain")
else:
    st.info("Upload or use the default dataset to begin interacting with the chatbot.")
