# run_app.py
import streamlit as st
st.set_page_config(layout="wide")

import pandas as pd
import io
from app import visualizations as vis
from scripts.llm_chat import ask_llm

st.title("📊 Educational Feedback Analysis Assistant")

uploaded_file = st.sidebar.file_uploader("Upload CSV file", type="csv")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

df = None
if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)
        st.success("✅ Data loaded successfully!")

        st.sidebar.subheader("📈 Visualizations")
        if st.sidebar.button("Show Grade Distribution"):
            vis.grade_distribution(df)

        if st.sidebar.button("Show Difficulty & Discrimination Indices"):
            vis.difficulty_discrimination(df)

        question_list = sorted(df["question"].dropna().unique()) if "question" in df.columns else []
        selected_question = st.sidebar.selectbox("Select a question", question_list) if question_list else None
        top_n = st.sidebar.slider("Top N Error Types", min_value=3, max_value=20, value=10)

        if st.sidebar.button("Top N Error Types for Selected Question") and selected_question:
            vis.top_n_error_types(df, selected_question, top_n)

        if st.sidebar.button("NEA Error Category Pie Chart") and selected_question:
            vis.pie_chart_nea(df, selected_question)

        st.header("💬 Ask the Educational Chatbot")
        user_query = st.text_input("Type your question:")
        if user_query and st.button("Ask"):
            context = df.head(100).to_csv(index=False)
            chat_history_text = "\n".join([f"User: {q}\nBot: {a}" for q, a in st.session_state.chat_history])
            answer = ask_llm(user_query, context, chat_history_text)
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

    except Exception as e:
        st.error(f"Error loading file: {e}")
else:
    st.info("Please upload a dataset to begin.")
