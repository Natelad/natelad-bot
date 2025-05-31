import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Optional: Check available models
def list_available_models():
    try:
        print("Available models:")
        models = genai.list_models()
        for model in models:
            print(f" - {model.name}")
    except Exception as e:
        print("Error listing models:", e)

list_available_models()

# Create a chat session with correct Gemini model
try:
    model = genai.GenerativeModel("models/gemini-1.5-pro-latest")
    chat = model.start_chat(history=[])
except Exception as e:
    print("Error initializing Gemini model:", e)
    chat = None

def generate_response(message):
    if chat is None:
        return "Sorry, the AI chat is currently unavailable."
    try:
        response = chat.send_message(message)
        return response.text.strip()
    except Exception as e:
        print("Gemini error:", e)
        return "Sorry, something went wrong. Please try again later."
