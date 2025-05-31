import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

MODEL_NAME = "models/gemini-2.5-flash-preview-05-20"

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
            system_prompt = (
                "You are a helpful assistant for Natelad Agency, a web design and development agency based in Harare, Zimbabwe. "
                "Natelad specializes in creating user-friendly and conversion-focused websites. "
                "Services include website design, development, maintenance, and e-commerce solutions. "
                "Pricing packages are as follows:\n"
                "- Lite Website Package: [Price details]\n"
                "- Standard Website Package: [Price details]\n"
                "- E-commerce Website Package: [Price details]\n"
                "Maintenance plans start at $50/month. "
                "For more information, visit https://nateladagency.com."
            )
            chat.send_message(system_prompt)
            response = chat.send_message(message)
            print("[Gemini] Generated response:", response.text)
            return response.text.strip()
        except Exception as e:
            print("[Gemini] Failed to generate response:", e)

    return "Sorry, the AI service is currently unavailable. Please try again later."
