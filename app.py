import streamlit as st
from google import genai
from google.genai import types
import os

# 1. Page Configuration
st.set_page_config(
    page_title="JI Web Assistant AI",
    page_icon="🤖",
    layout="wide"
)

# Title & Description
st.title("🤖 JI Web Assistant AI")
st.caption("Your Personal AI Text Assistant")

# 2. API Key Setup
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    api_key = st.sidebar.text_input("Enter Gemini API Key", type="password")

if not api_key:
    st.info("Please enter your Gemini API Key in the sidebar to continue.", icon="🔑")
    st.stop()

# Initialize Gemini Client
client = genai.Client(api_key=api_key)

# 3. Session State Initialization
if "messages" not in st.session_state:
    st.session_state.messages = []

# Sidebar Controls
st.sidebar.header("⚙️ Settings")
clear_chat = st.sidebar.button("Clear Chat History")
if clear_chat:
    st.session_state.messages = []
    st.rerun()

# 4. Display Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 5. Input Option (Text Only)
user_prompt = st.chat_input("Ask JI Web Assistant AI anything...")

# 6. Processing Input and Generating Response
if user_prompt:
    # Save User message to history
    st.session_state.messages.append({"role": "user", "content": user_prompt})
    with st.chat_message("user"):
        st.markdown(user_prompt)

    # Generate Response from Gemini
    with st.chat_message("assistant"):
        with st.spinner("JI Web Assistant AI is thinking..."):
            try:
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=user_prompt,
                )
                
                bot_response = response.text
                st.markdown(bot_response)
                
                # Save Assistant response to history
                st.session_state.messages.append({"role": "assistant", "content": bot_response})

            except Exception as e:
                st.error(f"Error generating response: {e}")
