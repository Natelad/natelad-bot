import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

MODEL_NAME = "models/gemini-2.5-flash-preview-05-20"  # Now the main model

def start_chat():
    model = genai.GenerativeModel(MODEL_NAME)
    return model.start_chat(history=[])

try:
    chat = start_chat()
except Exception as e:
    print(f"Model failed to start: {e}")
    chat = None

def generate_response(message):
    if chat:
        try:
            response = chat.send_message(message)
            return response.text.strip()
        except Exception as e:
            print("Model failed to generate response:", e)

    return "Sorry, the AI service is currently unavailable. Please try again later."
