import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

MODEL_NAME = "models/gemini-1.5-flash"  # More stable than the preview

# Initial context for the bot to remember who it represents
AGENCY_CONTEXT = """
You are Natelad Bot, the virtual assistant for Natelad Agency — a professional digital services company.

Natelad Agency offers:
- Website design and development
- AI chatbot integration
- Branding and digital marketing
- Social media management

Our pricing is flexible and project-based. Common packages start from:
- Basic Website: $150+
- AI Chatbot Integration: $100+
- Branding Package: $120+
- Social Media Mgmt: $80/month+

If the user asks for a quote or details, ask qualifying questions like:
- What service are you interested in?
- Do you have an existing website or brand?
- What's your budget or timeline?

Speak politely, clearly, and professionally.
"""

def generate_response(message):
    try:
        model = genai.GenerativeModel(MODEL_NAME)
        response = model.generate_content(f"{AGENCY_CONTEXT}\n\nUser: {message}\nAssistant:")
        print("[Gemini] Generated response:", response.text)
        return response.text.strip()
    except Exception as e:
        print("[Gemini] Failed to generate response:", e)
        return "Sorry, the AI service is currently unavailable. Please try again later."
