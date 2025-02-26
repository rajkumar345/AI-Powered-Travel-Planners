import google.generativeai as genai
import streamlit as st

# Get API Key from Streamlit Secrets
API_KEY = st.secrets["GOOGLE_API_KEY"]


if not API_KEY:
    print("⚠️ API Key is missing! Please check your .env file.")
    exit()

# Configure GenAI with secured API key
genai.configure(api_key=API_KEY)

# List available models
try:
    available_models = genai.list_models()
    print("✅ Available Models:")
    for model in available_models:
        print(f"- {model.name}: {model.supported_generation_methods}")
except Exception as e:
    print(f"⚠️ Error fetching model list: {e}")
