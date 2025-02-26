import streamlit as st
import google.generativeai as genai
from deep_translator import GoogleTranslator
import textwrap
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")


# Get API Key from Streamlit Secrets
API_KEY = st.secrets["GOOGLE_API_KEY"]

# Validate API Key
if not API_KEY:
    st.error("⚠️ API Key is missing! Please check your .env file.")
    st.stop()

# Configure Google GenAI
genai.configure(api_key=API_KEY)

# Language options
LANGUAGES = {
    "English": "en",
    "Hindi (हिन्दी)": "hi",
    "Telugu (తెలుగు)": "te",
    "Tamil (தமிழ்)": "ta",
    "Kannada (ಕನ್ನಡ)": "kn"
}

TRANSLATION_LIMIT = 5000  # Limit for translation API

def main():
    st.title("🚀 AI-Powered Travel Planner")
    
    st.markdown("### ✈️ Enter Your Travel Details Below:")

    source = st.text_input("🛫 Enter Source Location")
    destination = st.text_input("🛬 Enter Destination Location")
    
    # Date and time selection
    travel_date = st.date_input("📅 Select Travel Date", datetime.today())
    travel_time = st.time_input("⏰ Select Travel Time", datetime.now().time())

    special_needs = st.radio(
        "Do you need special travel assistance?",
        ("None", "Elderly Assistance", "Disability Support"),
        index=0
    )

    language = st.selectbox("🌐 Select Language for Information", list(LANGUAGES.keys()))

    if st.button("🔍 Find Travel Options"):
        if not source or not destination:
            st.warning("⚠️ Please enter both source and destination locations!")
            return

        with st.spinner("🔄 Fetching travel recommendations... Please wait!"):
            travel_options = find_travel_options(source, destination, special_needs, travel_date, travel_time)
            
            st.subheader("🔹 Travel Recommendations:")
            translated_text = translate_text(travel_options, LANGUAGES[language])
            st.markdown(translated_text)

def find_travel_options(source, destination, special_needs, travel_date, travel_time):
    assistance_text = ""
    if special_needs == "Elderly Assistance":
        assistance_text = " Provide senior-friendly travel options with rest stops and easy access."
    elif special_needs == "Disability Support":
        assistance_text = " Suggest wheelchair-accessible transport and travel assistance."
    
    model = genai.GenerativeModel('gemini-1.5-pro-latest')
    
    formatted_date_time = f"on {travel_date.strftime('%B %d, %Y')} at {travel_time.strftime('%I:%M %p')}"
    
    try:
        response = model.generate_content(
            f"Find travel options from {source} to {destination} {formatted_date_time}.{assistance_text}"
        )
        travel_info = response.text if hasattr(response, "text") else "No response generated."
    
    except Exception as e:
        travel_info = f"⚠️ Error generating response: {str(e)}"
    
    return travel_info

def translate_text(text, target_lang):
    try:
        translator = GoogleTranslator(source="auto", target=target_lang)
        if len(text) > TRANSLATION_LIMIT:
            chunks = textwrap.wrap(text, TRANSLATION_LIMIT)
            translated_chunks = [translator.translate(chunk) for chunk in chunks]
            return " ".join(translated_chunks)
        return translator.translate(text)
    except Exception as e:
        return f"⚠️ Translation failed, showing original English text:\n\n{text}"

if __name__ == "__main__":
    main()
