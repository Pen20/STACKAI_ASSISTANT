import re
from datetime import datetime
from typing import Tuple

import streamlit as st
from pymongo import MongoClient
from pymongo.errors import PyMongoError


@st.cache_resource(show_spinner=False)
def _get_mongo_client(uri: str) -> MongoClient:
    return MongoClient(uri, serverSelectionTimeoutMS=5000)


def _get_mongo_settings() -> Tuple[str, str, str]:
    required_keys = ("MONGO_URI", "MONGO_DB", "MONGO_COLLECTION")
    missing = [key for key in required_keys if key not in st.secrets]
    if missing:
        raise RuntimeError(
            "MongoDB connection details are not configured. "
            "Please add MONGO_URI, MONGO_DB, and MONGO_COLLECTION to Streamlit secrets."
        )

    return tuple(st.secrets[key] for key in required_keys)

def is_valid_email(email):
    return re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", email)

def save_message_to_mongo(name, email, message):
    uri, database, collection_name = _get_mongo_settings()
    client = _get_mongo_client(uri)
    collection = client[database][collection_name]

    doc = {
        "name": name,
        "email": email,
        "message": message,
        "timestamp": datetime.utcnow()
    }

    collection.insert_one(doc)

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
        except RuntimeError as exc:
            st.error(str(exc))
        except PyMongoError as exc:
            st.error(f"Error saving message: {exc}")
