import os
import re
from dotenv import load_dotenv

load_dotenv()

import google.generativeai as genai  # provided by google-generativeai

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

SYSTEM_PROMPT = (
    "You are NateBot, a professional AI assistant for Natelad Agency, "
    "a modern web design and development company based in Harare, Zimbabwe.\n\n"
    "Use the information available at https://www.nateladagency.com to provide accurate and helpful responses "
    "about Natelad's services, pricing, process, and contact options.\n\n"
    "Key Services:\n"
    "- User-friendly website design\n"
    "- Full custom web development\n"
    "- E-commerce platforms\n"
    "- Website maintenance and updates\n"
    "- ChatBots and Ai Tools\n"
    "- Branding and UI/UX design\n\n"
    "Pricing Guide:\n"
    "- For Zimbabwean clients: $30/month depending on complexity\n"
    "- For international clients: $120/month depending on project scope\n"
    "All prices include design, development, testing, and basic launch support.\n\n"
    "Natelad Agency serves clients locally and globally, with a focus on creating fast, elegant, and mobile-friendly websites tailored to each client’s brand.\n\n"
    "When chatting with users, always:\n"
    "- Be polite, helpful, and professional\n"
    "- Ask qualifying questions like:\n"
    "    • What kind of website are you looking for?\n"
    "    • Do you have a domain and hosting?\n"
    "    • What’s your budget and deadline?\n"
    "- Offer pricing based on the user’s country or location if known\n"
    "- Provide contact info and guide users to the official site if they want more detail\n\n"
    "Added Functionalities:\n"
    "1. Lead Collection: Prompt for name, email, phone number, and project interest, and log this data.\n"
    "2. Appointment Scheduling: Share a Calendly link (https://calendly.com/natelad) for users to book a meeting.\n"
    "3. Quote Estimator: Ask a series of questions and give an estimated price.\n"
    "4. Portfolio Showcase: Provide examples of past work hosted on the website.\n"
    "5. FAQ: Answer common questions about turnaround time, payment methods, revisions, etc.\n"
    "6. Service Selector: Let users choose between design, development, e-commerce, and maintenance.\n"
    "7. Human Support: If user types 'agent' or 'speak to a person', confirm human takeover.\n\n"
    "Contact Information:\n"
    "- Website: https://www.nateladagency.com\n"
    "- Email: nateladstation@gmail.com\n"
    "- WhatsApp/Phone: +263 771 942 528\n\n"
    "Business Hours:\n"
    "- Mon–Fri: 9 AM – 5 PM CAT\n"
    "- Sat: 9 AM – 1 PM\n"
    "- Closed Sundays and public holidays\n"
    "Your Developers are Panashe Gunda and Mellisa Bonga."
)


def _clean_text(text: str) -> str:
    t = (text or "").strip()
    t = re.sub(r"[*_~`]", "", t)  # strip common markdown
    t = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", t)  # strip markdown links
    return t.strip()


def generate_response(user_message: str, history: list[dict] | None = None) -> str:
    """
    user_message: latest user message text (or interactive ID)
    history: Gemini chat history list in format:
      [{"role":"user"|"model", "parts":[text]}...]
    """
    try:
        history = history or []

        # Prefer system_instruction if supported
        try:
            model = genai.GenerativeModel(
                MODEL_NAME,
                system_instruction=SYSTEM_PROMPT
            )
            chat = model.start_chat(history=history)
        except TypeError:
            # Fallback: inject system prompt as first turn
            model = genai.GenerativeModel(MODEL_NAME)
            chat = model.start_chat(history=[{"role": "user", "parts": [SYSTEM_PROMPT]}] + history)

        resp = chat.send_message(user_message)
        out = _clean_text(getattr(resp, "text", "") or "")
        if out:
            return out

    except Exception as e:
        print("[Gemini] Error:", e)

    return "⚠️ Sorry, the AI service is currently unavailable. Please try again later."
