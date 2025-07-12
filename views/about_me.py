import streamlit as st
from forms.contact import contact_form

@st.dialog("Contact Me")
def show_contact_form():
    contact_form()

# --- HERO SECTION ---
col1, col2 = st.columns(2, gap="small", vertical_alignment="center")
with col1:
    st.image("./assets/profile_image.png", width=230)

with col2:
    st.title("Dogbalou Motognon Wastalas d'Assise", anchor=False)
    st.write(
        "PhD Researcher in Applied Data Science & AI at the University of Trieste, "
        "leveraging machine learning and LLMs to personalize mathematics education across African universities."
    )
    if st.button("✉️ Contact Me and Share Your Comments"):
        show_contact_form()

# --- EXPERIENCE & QUALIFICATIONS ---
st.write("\n")
st.subheader("Experience & Qualifications", anchor=False)
st.write(
    """
    - 12+ years experience in mathematics education and pedagogy
    - 5+ years experience in data science, analytics, and AI research
    - PhD in Applied Data Science & AI (focus: adaptive learning with online learning and LLMs)
    - Strong expertise in educational data mining, recommender systems, and intelligent feedback design
    - Presenter at international conferences.
    - Former Mathematics Teacher and Civil Servant in Benin’s General Secondary Education System (Grades 7 - 12) (2013–2017)
    - Active collaborator with research centers and universities across Europe and Africa.
    """
)

# --- SKILLS ---
st.write("\n")
st.subheader("Technical & Research Skills", anchor=False)
st.write(
    """
    - **Programming & Query Languages**: Python, JavaScript/TypeScript, SQL, Cypher  
    - **Machine Learning & AI**: Supervised and Unsupervised Learning, PyTorch, scikit-learn, TensorFlow, LLMs, LangChain, OpenAI GPT-4o, RAG pipelines, Prompt Engineering, Model Evaluation, Time Series Analysis, Reinforcement Learning  
    - **Data Analytics & Visualization**: Pandas, NumPy, Plotly, Seaborn, Streamlit, Dash, A/B Testing, Statistical Testing, EDA, Data Storytelling.  
    - **Databases & Storage**: Neo4j, PostgreSQL, MongoDB, Vector Stores (FAISS, AstraDB, Chroma)  
    - **Backend & APIs**: FastAPI, Flask, Node.js, Express  
    - **Front-End Development**: React.js, Next.js, Angular, Chakra UI  
    - **DevOps & Tools**: Docker, GitHub Actions, Conda, Jest, VSCode, Git. 
    """
)


