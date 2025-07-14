import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

# --- Enforce use of user-provided API key only ---
user_key = st.session_state.get("OPENAI_API_KEY")

if not user_key:
    st.error("A valid OpenAI API key is required. Please enter it in the sidebar.")
    st.stop()

# --- Optional model fallback from secrets, default is 'gpt-4' ---
model_name = st.secrets.get("OPENAI_MODEL", "gpt-4o")

# --- Initialize LLM instance with user's key ---
llm = ChatOpenAI(model=model_name, temperature=0.2, api_key=user_key)

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
     "If the user request involves **categorizing student mistakes according to Newman’s Error Categories**, use the `error_category` column from the dataset when available, and follow the definitions below:\n\n"
     "**Newman’s Error Categories:**\n"
     "1. **Reading Error**: Misreading or misinterpreting symbols or text of a problem (e.g., reading t as x).\n"
     "2. **Comprehension Error**: Misunderstanding the meaning of the question despite correct reading, often due to conceptual confusion.\n"
     "3. **Transformation Error**: Difficulty translating a problem into mathematical equations or procedures.\n"
     "4. **Process Skills Error**: Incorrect use of algorithms or computational steps (e.g., applying the wrong derivative).\n"
     "5. **Encoding Error**: Final answer is incorrect due to poor notation, sign errors, or misformatting, even if reasoning was correct.\n\n"
     "Always respond in a supportive, constructive tone. Assume the user is seeking actionable insights to support student learning and improvement.\n\n"
     "Note: If the student ID is not present in the data provided, assume the student answered correctly and no errors were detected. You can say it."
    ),
    ("human", "Context:\n{context}\n\nChat History:\n{chat_history}\n\nQuestion: {question}")
])

# --- LLM Interaction Function ---
def ask_llm(question: str, context: str = "", chat_history: str = "") -> str:
    try:
        chain = chat_prompt | llm
        response = chain.invoke({
            "question": question,
            "context": context,
            "chat_history": chat_history
        })
        return response.content.strip()
    except Exception as e:
        return f"⚠️ Failed to fetch response from LLM: {e}"    
