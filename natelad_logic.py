import os
import re
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

MODEL_NAME = "models/gemini-2.5-flash-preview-05-20"

SYSTEM_PROMPT = (
    "You are Natelad Bot, a professional AI assistant for Natelad Agency, "
    "a web design and development company in Harare, Zimbabwe.\n\n"
    "Natelad specializes in:\n"
    "- User-friendly website design\n"
    "- Custom web development\n"
    "- E-commerce platforms\n"
    "- Maintenance and updates\n\n"
    "Pricing Packages:\n"
    "- Lite Website Package: $1000\n"
    "- Standard Website Package: Contact for quote\n"
    "- E-commerce Website Package: Contact for quote\n"
    "- Maintenance Plans: Starting at $50/month\n\n"
    "Learn more at: https://nateladagency.com\n"
    "Contact: +263 7xx xxx xxx\n"
    "Respond only in plain text. Do not use Markdown formatting like *, _, ~, or links."
)

def start_chat():
    try:
        model = genai.GenerativeModel(MODEL_NAME)
        chat = model.start_chat(history=[])
        chat.send_message(SYSTEM_PROMPT)
        return chat
    except Exception as e:
        print(f"[Gemini] Failed to start chat model: {e}")
        return None

chat = start_chat()

def generate_response(message):
    if chat:
        try:
            response = chat.send_message(message)
            plain_text = response.text.strip()

            # Strip Markdown formatting: asterisks, underscores, tildes, backticks
            clean_text = re.sub(r'[*_~`]', '', plain_text)

            # Remove markdown-style links [text](url)
            clean_text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', clean_text)

            print("[Gemini] Generated response:", clean_text)
            return clean_text
        except Exception as e:
            print("[Gemini] Failed to generate response:", e)

    return "⚠️ Sorry, the AI service is currently unavailable. Please try again later."
