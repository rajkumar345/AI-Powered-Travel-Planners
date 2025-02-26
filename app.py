import streamlit as st
import google.generativeai as genai
from deep_translator import GoogleTranslator
import textwrap
from datetime import datetime, timedelta

# Get API Key from Streamlit Secrets
try:
    API_KEY = st.secrets["GOOGLE_API_KEY"]
except KeyError:
    st.error("⚠️ API Key is missing! Please add it to .streamlit/secrets.toml.")
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

# Translations for "Travel Recommendations:"
HEADINGS_TRANSLATION = {
    "English": "📍 Travel Recommendations:",
    "Hindi (हिन्दी)": "📍 यात्रा अनुशंसाएँ:",
    "Telugu (తెలుగు)": "📍 ప్రయాణ సూచనలు:",
    "Tamil (தமிழ்)": "📍 பயண பரிந்துரைகள்:",
    "Kannada (ಕನ್ನಡ)": "📍 ಪ್ರಯಾಣ ಶಿಫಾರಸುಗಳು:"
}

TRANSLATION_LIMIT = 5000  # Limit for translation API

# Initialize session state variables
if "source" not in st.session_state:
    st.session_state["source"] = ""

if "destination" not in st.session_state:
    st.session_state["destination"] = ""

def main():
    st.title("🚀 AI-Powered Travel Planner")
    st.markdown("### ✈️ Enter Your Travel Details Below:")

    col1, col2, col3 = st.columns([3, 1, 3])

    with col1:
        st.session_state["source"] = st.text_input(
            "📍 Enter Source Location", value=st.session_state["source"], key="source_input"
        )

    with col2:
        if st.button("🔄 Swap"):
            st.session_state["source"], st.session_state["destination"] = (
                st.session_state["destination"],
                st.session_state["source"],
            )
            st.rerun()

    with col3:
        st.session_state["destination"] = st.text_input(
            "📍 Enter Destination Location", value=st.session_state["destination"], key="destination_input"
        )

    # Travel Dates
    today = datetime.today().date()
    max_date = today + timedelta(days=365 * 10)  # 10 years limit

    travel_date = st.date_input("📅 Departure Date", today, min_value=today, max_value=max_date)
    return_date = st.date_input("📅 Return Date (Optional)", travel_date, min_value=travel_date, max_value=max_date)

    # Travel Mode Selection
    travel_mode = st.radio("🚗 Select Mode of Travel", ("Flights", "Trains", "Cars", "Buses"))

    # Special Needs
    special_needs = st.radio(
        "Do you need special travel assistance?",
        ("None", "Elderly Assistance", "Disability Support"),
        index=0,
    )

    # Language Selection
    language = st.selectbox("🌍 Select Language for Information", list(LANGUAGES.keys()))

    if st.button("🔍 Find Travel Options"):
        if not st.session_state["source"] or not st.session_state["destination"]:
            st.warning("⚠️ Please enter both source and destination locations!")
            return

        with st.spinner("🔄 Fetching travel recommendations... Please wait!"):
            travel_options = find_travel_options(
                st.session_state["source"],
                st.session_state["destination"],
                travel_mode,
                travel_date,
                return_date,
                special_needs,
            )

            # Get translated heading
            translated_heading = HEADINGS_TRANSLATION.get(language, "📍 Travel Recommendations:")

            st.subheader(translated_heading)
            translated_text = translate_text(travel_options, LANGUAGES[language])
            st.markdown(translated_text)

def find_travel_options(source, destination, travel_mode, travel_date, return_date, special_needs):
    assistance_text = {
        "Elderly Assistance": " Provide senior-friendly travel options with rest stops and easy access.",
        "Disability Support": " Suggest wheelchair-accessible transport and travel assistance.",
        "None": "",
    }[special_needs]

    model = genai.GenerativeModel("gemini-1.5-pro-latest")

    formatted_date = f"on {travel_date.strftime('%B %d, %Y')}"
    return_date_text = f" and return on {return_date.strftime('%B %d, %Y')}" if return_date else ""

    prompt = f"Find {travel_mode.lower()} travel options from {source} to {destination} {formatted_date}{return_date_text}.{assistance_text}"

    # AI should include details about travelers and car rentals instead of form inputs
    if travel_mode == "Flights":
        prompt += " Suggest the best class options based on budget and comfort."
    elif travel_mode == "Cars":
        prompt += " Recommend suitable car rental services and pricing."

    try:
        response = model.generate_content(prompt)
        return response.text if response and hasattr(response, "text") else "No response generated."
    except Exception as e:
        return f"⚠️ Error generating response: {str(e)}"

def translate_text(text, target_lang):
    try:
        translator = GoogleTranslator(source="auto", target=target_lang)
        if len(text) > TRANSLATION_LIMIT:
            chunks = textwrap.wrap(text, TRANSLATION_LIMIT)
            translated_chunks = [translator.translate(chunk) for chunk in chunks]
            return " ".join(translated_chunks)
        return translator.translate(text)
    except Exception:
        return f"⚠️ Translation failed, showing original English text:\n\n{text}"

if __name__ == "__main__":
    main()
