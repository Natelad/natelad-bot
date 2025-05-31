import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Create a chat session with gemini-pro (v1 endpoint is used under the hood in 0.8+)
chat = genai.GenerativeModel("gemini-pro").start_chat(history=[])

def generate_response(message):
    try:
        response = chat.send_message(message)
        return response.text.strip()
    except Exception as e:
        print("Gemini error:", e)
        return "Sorry, something went wrong. Please try again later."
