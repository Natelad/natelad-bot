import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

MODEL_NAME = "models/gemini-2.5-flash-preview-05-20"

# Define system prompt globally
SYSTEM_PROMPT = (
    "You are Natelad Bot, an AI assistant for Natelad Agency, a web design and development agency in Harare, Zimbabwe.\n\n"
    "Natelad specializes in:\n"
    "- Custom Website Design\n"
    "- Responsive Development\n"
    "- E-commerce Solutions\n"
    "- Website Maintenance\n\n"
    "**Pricing Packages:**\n"
    "- *Lite Website Package:* $1000\n"
    "- *Standard Website Package:* Contact us for a quote.\n"
    "- *E-commerce Website Package:* Contact us for a quote.\n"
    "- *Maintenance:* Starting at $50/month\n\n"
    "Website: https://nateladagency.com\n"
    "Phone: +263 7xx xxx xxx\n"
    "You respond professionally, helpfully, and clearly."
)

# Start the Gemini chat model
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

# Command-based routing
def route_command(message):
    lower_msg = message.lower()
    if "pricing" in lower_msg:
        return (
            "**Natelad Pricing** 💰\n"
            "- *Lite Website Package:* $1000\n"
            "- *Standard Website Package:* Contact us for a quote\n"
            "- *E-commerce Website Package:* Contact us for a quote\n"
            "- *Maintenance Plans:* From $50/month\n\n"
            "View more: https://nateladagency.com"
        )
    elif "portfolio" in lower_msg or "examples" in lower_msg:
        return (
            "**Portfolio** 🎨\n"
            "Check out our recent projects here:\n"
            "https://nateladagency.com/portfolio"
        )
    elif "schedule" in lower_msg or "meeting" in lower_msg:
        return (
            "**Schedule a Meeting** 📅\n"
            "We’d love to chat! Book a session here:\n"
            "https://nateladagency.com/contact"
        )
    elif "services" in lower_msg:
        return (
            "**Our Services** 🛠️\n"
            "- Website Design\n"
            "- Web Development\n"
            "- E-commerce Solutions\n"
            "- Website Maintenance\n\n"
            "Details: https://nateladagency.com/services"
        )
    return None  # Fall back to AI

# Generate a smart response
def generate_response(message):
    if chat:
        try:
            # Check if the message matches a known command
            routed_reply = route_command(message)
            if routed_reply:
                return routed_reply

            # If no match, fall back to generative AI
            response = chat.send_message(message)
            print("[Gemini] Generated response:", response.text)
            return response.text.strip()
        except Exception as e:
            print("[Gemini] Failed to generate response:", e)

    return "Sorry, the AI service is currently unavailable. Please try again later."
