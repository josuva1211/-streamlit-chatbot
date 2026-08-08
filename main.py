import os

import streamlit as st
from dotenv import load_dotenv
from google import genai

# -----------------------------
# Load Environment Variables
# -----------------------------
load_dotenv()

API_KEY = st.secrets.get("GOOGLE_API_KEY", os.getenv("GOOGLE_API_KEY"))

if not API_KEY:
    st.error("GOOGLE_API_KEY not found in .env file.")
    st.stop()

# -----------------------------
# Cache Gemini Client
# -----------------------------
@st.cache_resource
def get_client():
    return genai.Client(api_key=API_KEY)

client = get_client()

MODEL = "gemini-3.5-flash-lite"
# You can also use:
# MODEL = "gemini-2.5-flash"

# -----------------------------
# Streamlit UI
# -----------------------------
st.set_page_config(
    page_title="Gemini Chatbot",
    page_icon="🤖",
    layout="centered",
)

st.title("🤖 Gemini Chatbot")

# -----------------------------
# Session State
# -----------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# -----------------------------
# Sidebar
# -----------------------------
with st.sidebar:

    st.header("Options")

    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()

# -----------------------------
# Display Previous Messages
# -----------------------------
for message in st.session_state.messages:

    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# -----------------------------
# Chat Input
# -----------------------------
prompt = st.chat_input("Ask me anything...")

if prompt:

    # Store user message
    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt,
        }
    )

    with st.chat_message("user"):
        st.markdown(prompt)

    # -----------------------------
    # Convert history to Gemini format
    # -----------------------------
    history = []

    for msg in st.session_state.messages:

        history.append(
            {
                "role": "user" if msg["role"] == "user" else "model",
                "parts": [
                    {
                        "text": msg["content"]
                    }
                ],
            }
        )

    # -----------------------------
    # Generate Response
    # -----------------------------
    with st.chat_message("assistant"):

        with st.spinner("Thinking..."):

            try:

                response = client.models.generate_content(
                    model=MODEL,
                    contents=history,
                )

                answer = response.text

            except Exception as e:

                answer = f"❌ Error:\n\n{e}"

            st.markdown(answer)

    # Store assistant response
    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer,
        }
    )