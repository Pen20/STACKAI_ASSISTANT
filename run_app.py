# run_app.py
import streamlit as st
import pandas as pd
from app import visualizations as vis

st.set_page_config(layout="wide")
st.title("📊 Educational Feedback Analysis Chatbot")

uploaded_file = st.sidebar.file_uploader("Upload CSV file", type="csv")

df = None
if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)
        st.success("Data loaded successfully!")

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

    except Exception as e:
        st.error(f"Error loading file: {e}")
else:
    st.info("Please upload a dataset to begin.")
