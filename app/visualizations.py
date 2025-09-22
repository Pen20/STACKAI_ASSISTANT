# app/visualizations.py
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from collections import Counter

def grade_distribution(df):
    if "grade" not in df.columns:
        st.warning("Column 'grade' is required for grade distribution visualization.")
        return

    df['grade'] = pd.to_numeric(df['grade'], errors='coerce')
    df = df.dropna(subset=["grade"])

    fig, ax = plt.subplots(figsize=(8, 5))
    sns.histplot(df['grade'], bins=10, kde=True, ax=ax)
    ax.set_title("Grade Distribution")
    ax.set_xlabel("Grade")
    ax.set_ylabel("Frequency")
    ax.grid(True)
    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

def difficulty_discrimination(df):
    if not all(col in df.columns for col in ["question", "grade", "student_id"]):
        st.warning("Dataset must include 'question', 'grade', and 'student_id' columns.")
        return

    df = df.dropna(subset=["question", "grade", "student_id"])
    df["grade"] = pd.to_numeric(df["grade"], errors='coerce')
    df = df.dropna(subset=["grade"])

    difficulty_indices = (
        df.groupby("question")["grade"]
        .agg(["sum", "count"])
        .rename(columns={"sum": "sum_fx", "count": "n"})
    )
    difficulty_indices["difficulty_index"] = difficulty_indices["sum_fx"] / difficulty_indices["n"]
    difficulty_indices = difficulty_indices.reset_index()

    total_grade_per_student = df.groupby("student_id")["grade"].sum().reset_index()
    total_grade_per_student = total_grade_per_student.sort_values(by="grade", ascending=False)

    n_students = len(total_grade_per_student)
    group_size = int(np.ceil(n_students * 0.27))

    if group_size < 1:
        st.warning("Not enough students to compute discrimination index.")
        return

    upper_group_ids = total_grade_per_student.head(group_size)["student_id"]
    lower_group_ids = total_grade_per_student.tail(group_size)["student_id"]

    def discrimination_index(q_df):
        up = q_df[q_df["student_id"].isin(upper_group_ids) & (q_df["grade"] > 0)].shape[0]
        lp = q_df[q_df["student_id"].isin(lower_group_ids) & (q_df["grade"] > 0)].shape[0]
        return (up - lp) / group_size

    discrimination_results = (
        df.groupby("question")
        .apply(discrimination_index)
        .reset_index(name="discrimination_index")
    )

    analysis_results = pd.merge(difficulty_indices, discrimination_results, on="question")

    fig, ax = plt.subplots(figsize=(10, 6))
    x = np.arange(len(analysis_results["question"]))
    bar_width = 0.35

    bars1 = ax.bar(
        x - bar_width / 2,
        analysis_results["difficulty_index"],
        width=bar_width,
        label='Difficulty Index',
    )
    bars2 = ax.bar(
        x + bar_width / 2,
        analysis_results["discrimination_index"],
        width=bar_width,
        label='Discrimination Index',
        color='orange',
    )

    ax.set_xlabel('Question')
    ax.set_ylabel('Index Value')
    ax.set_title('Difficulty and Discrimination Indices per Question')
    ax.set_xticks(x)
    ax.set_xticklabels(analysis_results["question"], rotation=45)
    ax.set_ylim(0, 1.1)
    ax.legend()

    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax.annotate(
                f'{height:.2f}',
                xy=(bar.get_x() + bar.get_width() / 2, height),
                xytext=(0, 3),
                textcoords="offset points",
                ha='center',
                va='bottom',
            )

    st.pyplot(fig)
    plt.close(fig)

def top_n_error_types(df, question, n=10):
    if "question" not in df.columns or "error_summary" not in df.columns:
        st.warning("Dataset must include 'question' and 'error_summary' columns.")
        return

    df_filtered = df[df["question"] == question]
    if df_filtered.empty:
        st.info("No responses available for the selected question.")
        return

    errors = df_filtered["error_summary"].dropna().str.lower().str.split(", ").explode()
    if errors.empty:
        st.info("No error summaries available to visualize.")
        return

    counts = Counter(errors)
    summary_df = (
        pd.DataFrame(counts.items(), columns=["Error Type", "Frequency"])
        .sort_values(by="Frequency", ascending=False)
        .reset_index(drop=True)
    )

    total = summary_df["Frequency"].sum()
    if total == 0:
        st.info("No error occurrences found for the selected question.")
        return

    summary_df["Percentage"] = (summary_df["Frequency"] / total * 100).round(2)
    top_df = summary_df.head(n)

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.barh(top_df["Error Type"], top_df["Percentage"], color="#1f77b4")
    ax.invert_yaxis()
    ax.set_xlabel("Percentage (%)")
    ax.set_ylabel("Error Type")
    ax.set_title(f"Top {len(top_df)} Error Types for {question}")
    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

def pie_chart_nea(df, question):
    if "question" not in df.columns or "error_category" not in df.columns:
        st.warning("Dataset must include 'question' and 'error_category' columns.")
        return

    q_error_cat = df[df["question"] == question]["error_category"].dropna()
    error_cat_types = q_error_cat.str.lower().str.split(", ").explode()
    if error_cat_types.empty:
        st.info("No NEA error categories available for the selected question.")
        return

    error_cat_counts = Counter(error_cat_types)

    error_cat_df = (
        pd.DataFrame(error_cat_counts.items(), columns=["Error Category", "Frequency"])
        .sort_values(by="Frequency", ascending=False)
        .reset_index(drop=True)
    )
    total_cat_errors = error_cat_df["Frequency"].sum()
    if total_cat_errors == 0:
        st.info("No NEA error categories available for the selected question.")
        return

    error_cat_df["Percentage"] = (error_cat_df["Frequency"] / total_cat_errors * 100).round(2)

    top_cat_df = error_cat_df.head(4)
    others_pct = round(100 - top_cat_df["Percentage"].sum(), 2)

    labels = top_cat_df["Error Category"].tolist() + (["Others"] if others_pct > 0 else [])
    sizes = top_cat_df["Percentage"].tolist() + ([others_pct] if others_pct > 0 else [])
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#9467bd', '#8c564b'][:len(labels)]

    fig, ax = plt.subplots()
    ax.pie(sizes, labels=labels, autopct='%1.1f%%', colors=colors)
    ax.axis('equal')
    ax.set_title(f'Distribution of NEA Categories for {question}')
    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)
