import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# List models for debug purposes
def list_available_models():
    try:
        print("Available models:")
        models = genai.list_models()
        for model in models:
            print(f" - {model.name}")
    except Exception as e:
        print("Error listing models:", e)

list_available_models()

# Preferred and fallback model
PRIMARY_MODEL = "models/gemini-2.5-pro-preview-05-06"
FALLBACK_MODEL = "models/gemini-2.5-flash-preview-05-20"

# Try to create chat session with primary or fallback model
def initialize_chat():
    try:
        print(f"Trying primary model: {PRIMARY_MODEL}")
        model = genai.GenerativeModel(PRIMARY_MODEL)
        return model.start_chat(history=[])
    except Exception as e:
        print(f"Primary model failed: {e}")
        try:
            print(f"Trying fallback model: {FALLBACK_MODEL}")
            model = genai.GenerativeModel(FALLBACK_MODEL)
            return model.start_chat(history=[])
        except Exception as e2:
            print(f"Fallback model also failed: {e2}")
            return None

chat = initialize_chat()

def generate_response(message):
    if chat is None:
        return "Sorry, the AI chat is currently unavailable."
    try:
        response = chat.send_message(message)
        return response.text.strip()
    except Exception as e:
        print("Gemini error during message send:", e)
        return "Sorry, something went wrong. Please try again later."
