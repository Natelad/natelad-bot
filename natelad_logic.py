from flask import Flask, request
import google.generativeai as genai
from dotenv import load_dotenv
import os

load_dotenv()

# Use fallback model as primary
MODEL_NAME = "models/gemini-2.5-flash-preview-05-20"

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
chat = genai.GenerativeModel(MODEL_NAME).start_chat()

app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return "Natelad Bot is live 🚀"

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.get_json()
        print("Received data:", data)

        # EXAMPLE format for WhatsApp from Meta or 360dialog
        message = data["messages"][0]["text"]["body"]
        sender = data["contacts"][0]["wa_id"]
        
        print(f"Message from {sender}: {message}")

        response = chat.send_message(message)
        reply = response.text.strip()

        print("Generated reply:", reply)

        # 👉 IMPORTANT: Render does not send the reply back to WhatsApp. You must use a WhatsApp API provider.
        # For now, just return 200 OK so the webhook doesn't error.
        return "OK", 200

    except Exception as e:
        print("Error handling webhook:", e)
        return "Error", 500
