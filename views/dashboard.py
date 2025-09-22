import streamlit as st
import pandas as pd

from app import visualizations as vis

st.set_page_config(page_title="Educational Feedback Analysis Assistant", layout="wide")
st.title("📊 Educational Feedback Analysis Assistant")

# === Page Description and Instructions ===
st.markdown(
    """
    ### 🎯 What This Page Does

    This **Dashboard** allows you to explore and analyze student performance data through a set of **interactive visualizations**.
    You can:
    - Analyze **grade distribution**
    - Evaluate **question difficulty and discrimination**
    - View **common error types** and their proportions
    - Identify patterns from **NEA error categories**

    ### 📂 Dataset Options

    - By default, the platform loads a **sample dataset** (`predicting_students_errors.csv`) for demonstration and testing purposes.
    - You can also **upload your own CSV file** using the sidebar, as long as it meets the expected criteria.
    """
)

uploaded_file = st.sidebar.file_uploader("Upload CSV file", type="csv")

# Initialize session state for toggles
for key in ["show_grade_dist", "show_difficulty", "show_top_errors", "show_pie_chart"]:
    if key not in st.session_state:
        st.session_state[key] = False

# Load dataset
df = None
if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)
        st.success("✅ Data loaded successfully!")
    except Exception as e:
        st.error(f"Error loading file: {e}")
        df = None
else:
    try:
        df = pd.read_csv("data/predicting_students_errors.csv")
        st.info("Default dataset loaded.")
    except FileNotFoundError:
        st.warning("Please upload a dataset to begin.")

if df is not None:
    REQUIRED_COLS = ["question", "grade", "student_id"]
    missing = [col for col in REQUIRED_COLS if col not in df.columns]
    if missing:
        st.error(f"Missing required columns: {', '.join(missing)}")
        st.stop()

    st.header("📈 Visualizations")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("📊 Toggle Grade Distribution"):
            st.session_state.show_grade_dist = not st.session_state.show_grade_dist
        if st.button("📉 Toggle Difficulty & Discrimination Indices"):
            st.session_state.show_difficulty = not st.session_state.show_difficulty

    question_list = sorted(df["question"].dropna().unique())
    if question_list:
        with col2:
            selected_question = st.selectbox("Select a question", question_list, key="q_select")
            top_n = st.slider("Top N Error Types", 3, 20, 10, key="top_n_slider")

            if st.button("🔍 Toggle Top N Error Types"):
                st.session_state.show_top_errors = not st.session_state.show_top_errors
            if st.button("🥧 Toggle NEA Error Category Pie Chart"):
                st.session_state.show_pie_chart = not st.session_state.show_pie_chart
    else:
        st.info("No valid questions found in dataset.")
        selected_question = None

    # Show visualizations based on toggle state
    if st.session_state.show_grade_dist:
        with st.spinner("Generating grade distribution..."):
            vis.grade_distribution(df)

    if st.session_state.show_difficulty:
        with st.spinner("Calculating difficulty and discrimination indices..."):
            vis.difficulty_discrimination(df)
            
                # --- Interpretation Help Section ---
        with st.expander("ℹ️ How to Interpret Difficulty & Discrimination Indices"):
            st.markdown(
                """
                **Difficulty Index (DI):**
                - Measures how easy or hard a question is for students.
                - **< 0.30** → Highly difficult (few students succeed).
                - **0.30 – 0.70** → Moderate difficulty (balanced).
                - **> 0.70** → Easy (most students succeed).

                **Discrimination Index (DiscI):**
                - Indicates how well a question separates **high-performing students from low-performing students**.

                **Interpretation (with ranges):**

                | Discrimination Index (DiscI) | Interpretation | Action |
                |------------------------------|----------------|--------|
                | **≥ 0.40**                   | Excellent discrimination | Keep the item; highly reliable |
                | **0.30 – 0.39**              | Good discrimination | Acceptable, but could be improved |
                | **0.20 – 0.29**              | Fair discrimination | Marginal; may need revision |
                | **< 0.20**                   | Poor discrimination | Weak item; likely needs redesign |
                | **= 0.00**                   | No discrimination | Does not differentiate at all |
                | **Negative (< 0.00)**        | Flawed item | Inverse relation: weaker students perform better than stronger ones → item is problematic |

                ✅ *Tip: Ideally, a good question has **moderate difficulty (0.30–0.70)** and **strong discrimination (≥ 0.30)**.*
                """
            )
    

    if st.session_state.show_top_errors and selected_question:
        with st.spinner("Creating error type plot..."):
            vis.top_n_error_types(df, selected_question, st.session_state.top_n_slider)

    if st.session_state.show_pie_chart and selected_question:
        with st.spinner("Generating NEA pie chart..."):
            vis.pie_chart_nea(df, selected_question)

        # --- Interpretation Help Section for NEA Errors ---
        with st.expander("ℹ️ How to Interpret NEA Error Categories"):
            st.markdown(
                """
                **Newman’s Error Analysis (NEA) Categories:**

                1. **Reading Error** 📝  
                   - Misreading or misinterpreting a mathematical problem’s text or symbols. 
                   - This stage involves assessing whether the learner correctly identifies all components of the question. 
                   - Example: confusing a “+” sign with a “–” sign.  

                2. **Comprehension Error** 🤔  
                   - Student reads correctly but fails to grasp the meaning of the problem. 
                   - Difficulties in this stage are often related to language barriers, cognitive overload, or lack of prior knowledge. 
                   - Example: doesn’t understand what the question is asking.  

                3. **Transformation Error** 🔄  
                   - Student understands the problem but fails to convert it into a mathematical representation.  
                   - Example: setting up the wrong equation or establishing an incorrect logical sequence of steps.  

                4. **Process Skills Error** ⚙️  
                   - Correct transformation but incorrect calculations, methods, or procedures.  
                   - Example: arithmetic mistakes.  

                5. **Encoding Error** ✍️  
                   - Correct solution reached but expressed incorrectly in the final answer.  
                   - Example: decimal point error, miswriting units, or notation mistakes.  

                ✅ *Tip: Use these categories to see not just whether students are wrong, but **why** they are wrong — this helps target teaching interventions.*
                """
            )

else:
    st.info("Awaiting dataset to proceed with visualizations.")
