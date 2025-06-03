# scripts/llm_chat.py
import sys
import warnings
sys.modules['warnings'] = warnings  # Prevents LangChain KeyError

import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()

llm = ChatOpenAI(model="gpt-4o", temperature=0.2)

chat_prompt = ChatPromptTemplate.from_messages([
    ("system", 
     "You are an expert educational assistant specializing in diagnosing student learning patterns, misconceptions, and performance gaps. "
     "You analyze LLM responses, error summaries, and error categories to identify the root causes of misunderstanding.\n\n"
     "Your objectives are to:\n"
     "1. Interpret and explain student errors and misconceptions.\n"
     "2. Recommend targeted learning resources or remedial strategies.\n"
     "3. Provide clear, evidence-based, and pedagogically sound explanations.\n"
     "4. Tailor your feedback based on each student's question, grade, and response history.\n\n"
     "Always respond in a supportive, constructive tone. Assume the user is seeking actionable insights to support student learning and improvement."
    ),
    ("human", "Context:\n{context}\n\nChat History:\n{chat_history}\n\nQuestion: {question}")
])


def ask_llm(question: str, context: str = "", chat_history: str = "") -> str:
    chain = chat_prompt | llm
    response = chain.invoke({
        "question": question,
        "context": context,
        "chat_history": chat_history
    })
    return response.content.strip()
