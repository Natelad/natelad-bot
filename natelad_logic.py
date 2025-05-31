import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Use a safer default model
MODEL_NAME = "models/gemini-pro"

def start_chat():
    try:
        model = genai.GenerativeModel(MODEL_NAME)
        return model.start_chat(history=[])
    except Exception as e:
        print(f"[Gemini] Failed to start chat model: {e}")
        return None

chat = start_chat()

def generate_response(message):
    if chat:
        try:
            response = chat.send_message(message)
            print("[Gemini] Generated response:", response.text)
            return response.text.strip()
        except Exception as e:
            print("[Gemini] Failed to generate response:", e)

    return "Sorry, the AI service is currently unavailable. Please try again later."
