import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

PRIMARY_MODEL = "models/gemini-2.5-pro-preview-05-06"
FALLBACK_MODEL = "models/gemini-2.5-flash-preview-05-20"

def start_chat_with_model(model_name):
    model = genai.GenerativeModel(model_name)
    return model.start_chat(history=[])

# Start chats for both models
try:
    primary_chat = start_chat_with_model(PRIMARY_MODEL)
except Exception as e:
    print(f"Primary model failed to start: {e}")
    primary_chat = None

try:
    fallback_chat = start_chat_with_model(FALLBACK_MODEL)
except Exception as e:
    print(f"Fallback model failed to start: {e}")
    fallback_chat = None

def generate_response(message):
    # Try primary
    if primary_chat:
        try:
            response = primary_chat.send_message(message)
            return response.text.strip()
        except Exception as e:
            if "429" in str(e):
                print("Quota exceeded on primary model. Trying fallback.")
            else:
                print("Primary model failed:", e)

    # Try fallback
    if fallback_chat:
        try:
            response = fallback_chat.send_message(message)
            return response.text.strip()
        except Exception as e:
            print("Fallback model failed:", e)

    return "Sorry, the AI service is currently unavailable. Please try again later."
