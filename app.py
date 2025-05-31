from flask import Flask, request
import requests
import openai
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")

openai.api_key = OPENAI_API_KEY

# 1. Verification webhook setup
@app.route("/webhook", methods=["GET"])
def verify():
    if request.args.get("hub.verify_token") == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return "Verification failed", 403

# 2. Message handling webhook
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    try:
        message = data["entry"][0]["changes"][0]["value"]["messages"][0]
        user_message = message["text"]["body"]
        user_number = message["from"]

        # Process user message with OpenAI
        response_text = generate_response(user_message)

        # Send reply to WhatsApp user
        send_whatsapp_message(user_number, response_text)
    except Exception as e:
        print("Error:", e)

    return "ok", 200

# 3. Function to generate smart response
def generate_response(user_message):
    prompt = f"""You are Natelad Bot, a helpful assistant from Natelad Agency.
You offer digital solutions to businesses, freelancers, and startups.

If a user says:
- "pricing", respond with: "Our prices vary by service. Branding starts at $50, websites from $100, and social media management from $60/month."
- "call", respond with: "You can call Natelad Agency directly at +263xxxxxxxx"
- "website", respond with: "Visit our website at https://natelad.agency"
- If they ask what they need, ask them what they do or what their business is, then suggest a solution.

User: {user_message}
Natelad Bot:"""

    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=150,
        temperature=0.7
    )
    return response.choices[0].text.strip()

# 4. Send message to WhatsApp user
def send_whatsapp_message(user_number, message_text):
    url = f"https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "messaging_product": "whatsapp",
        "to": user_number,
        "text": {"body": message_text}
    }
    requests.post(url, headers=headers, json=data)

