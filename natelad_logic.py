import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-pro")

def generate_response(message):
    try:
        system_prompt = """
You are Natelad Bot, a friendly and professional assistant for Natelad Agency. You:
- Answer client questions about services like branding, web design, automation, AI solutions
- Offer pricing, advice, and links to our site
- Recommend solutions by asking about client needs
- Are professional, brief, and helpful
"""

        prompt = f"{system_prompt}\n\nClient: {message}\nNatelad Bot:"

        response = model.generate_content(prompt)
        return response.text.strip()

    except Exception as e:
        print("Gemini error:", e)
        return "Sorry, something went wrong. Please try again later."
