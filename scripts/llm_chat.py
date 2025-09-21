import streamlit as st
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

DEFAULT_MODEL_NAME = "gpt-4o"


@st.cache_resource(show_spinner=False)
def _load_llm(api_key: str, model_name: str) -> ChatOpenAI:
    """Create (and cache) a ChatOpenAI client for the provided API key."""

    return ChatOpenAI(model=model_name, temperature=0.2, api_key=api_key)


# --- Prompt Template ---

chat_prompt = ChatPromptTemplate.from_messages([
    ("system", 
     "You are an expert educational assistant specializing in diagnosing student learning patterns, misconceptions, and performance gaps. "
     "You analyze LLM responses, error summaries, and error categories to identify the root causes of misunderstanding.\n\n"
     "Your objectives are to:\n"
     "1. Interpret and explain student errors and misconceptions.\n"
     "2. Recommend targeted learning resources or remedial strategies.\n"
     "3. Provide clear, evidence-based, and pedagogically sound explanations.\n"
     "4. Avoid labeling or referencing answers using formats like 'ansa', 'ansb', or 'ansc'; instead, refer to the content directly and naturally within the feedback.\n"
     "5. Tailor your feedback based on each student's question, grade, and response history.\n\n"

     "Always begin your response by explicitly recalling both the student's response and the correct answer before giving any explanation, diagnosis, or categorization. "
     "Always format the student's response and the correct answer using inline code syntax with backticks, like: `student_answer` and `correct_answer`. "
     "This ensures they are highlighted in a distinct color block for readability.\n\n"

     "If the user request involves categorizing student mistakes according to Newman’s Error Categories, use the `error_category` column from the dataset when available, and follow the definitions below:\n\n"
     "Newman’s Error Categories:\n"
     "1. Reading Error: Misreading or misinterpreting a mathematical problem's text or symbols.\n"
     "2. Comprehension Error: Correct reading but failure to grasp the meaning.\n"
     "3. Transformation Error: Understanding the problem but failing to convert it into a mathematical representation.\n"
     "4. Process Skills Error: Correct transformation but incorrect calculations, methods, or algorithms.\n"
     "5. Encoding Error: Correct solution reached but expressed incorrectly (notation, decimal placement, miswriting).\n\n"

     "Always respond in a supportive, constructive tone. Assume the user is seeking actionable insights to support student learning and improvement.\n\n"
     "Note: If the student ID is not present in the data provided, assume the student answered correctly and no errors were detected. You can say it."
    ),
    ("human", "Context:\n{context}\n\nChat History:\n{chat_history}\n\nQuestion: {question}")
])


# --- LLM Interaction Function ---
def ask_llm(question: str, context: str = "", chat_history: str = "") -> str:
    api_key = st.session_state.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("A valid OpenAI API key is required. Please enter it in the sidebar.")

    model_name = st.secrets.get("OPENAI_MODEL", DEFAULT_MODEL_NAME)

    llm = _load_llm(api_key, model_name)

    try:
        chain = chat_prompt | llm
        response = chain.invoke(
            {
                "question": question,
                "context": context,
                "chat_history": chat_history,
            }
        )
    except Exception as exc:  # pragma: no cover - network interaction
        raise RuntimeError(f"Failed to fetch response from LLM: {exc}") from exc

    return response.content.strip()
