import streamlit as st
import re
from pymongo import MongoClient
from datetime import datetime

def is_valid_email(email):
    return re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", email)

def save_message_to_mongo(name, email, message):
    client = MongoClient(st.secrets["MONGO_URI"])
    db = client[st.secrets["MONGO_DB"]]
    collection = db[st.secrets["MONGO_COLLECTION"]]
    
    doc = {
        "name": name,
        "email": email,
        "message": message,
        "timestamp": datetime.utcnow()
    }

    collection.insert_one(doc)
    client.close()

def contact_form():
    with st.form("contact_form"):
        name = st.text_input("First Name")
        email = st.text_input("Email Address")
        message = st.text_area("Your Message or Comments")
        submit_button = st.form_submit_button("Submit")

    if submit_button:
        if not name:
            st.error("Please provide your name.", icon="🧑")
            return
        if not email:
            st.error("Please provide your email address.", icon="📨")
            return
        if not is_valid_email(email):
            st.error("Please enter a valid email address.", icon="📧")
            return
        if not message:
            st.error("Please provide a message.", icon="💬")
            return

        try:
            save_message_to_mongo(name, email, message)
            st.success("🎉 Your message has been submitted successfully!")
        except Exception as e:
            st.error(f"Error saving message: {e}")
