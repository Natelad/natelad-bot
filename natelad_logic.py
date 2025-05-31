import os
import re
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

MODEL_NAME = "models/gemini-2.5-flash-preview-05-20"

SYSTEM_PROMPT = (
    "You are Natelad Bot, a professional AI assistant for Natelad Agency, a web design and development company in Harare, Zimbabwe.\n\n"
    "Natelad specializes in:\n"
    "- User-friendly website design\n"
    "- Custom web development\n"
    "- E-commerce platforms\n"
    "- Maintenance and updates\n\n"
    "💰 Pricing Packages:\n"
    "- Lite Website Package: $1000\n"
    "- Standard Website Package: Contact for quote\n"
    "- E-commerce Website Package: Contact for quote\n"
    "- Maintenance Plans: Starting at $50/month\n\n"
    "🌐 Learn more at: https://nateladagency.com\n"
    "📞 Contact: +263 7xx xxx xxx"
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
            formatted = format_response(response.text)
            print("[Gemini] Generated response:", formatted)
            return formatted
        except Exception as e:
            print("[Gemini] Failed to generate response:", e)

    return "⚠️ Sorry, the AI service is currently unavailable. Please try again later."

def format_response(text):
    text = text.strip()

    replacements = {
        r"(?<!\*)\bLite Website Package\b(?!\*)": "💡 *Lite Website Package*",
        r"(?<!\*)\bStandard Website Package\b(?!\*)": "⭐ *Standard Website Package*",
        r"(?<!\*)\bE-commerce Website Package\b(?!\*)": "🛒 *E-commerce Website Package*",
        r"(?<!\*)\bMaintenance\b(?!\*)": "🛠️ *Maintenance*",
        r"(?<!\*)\bNatelad\b(?!\*)": "*Natelad*",
    }

    for pattern, replacement in replacements.items():
        text = re.sub(pattern, replacement, text)

    return text
