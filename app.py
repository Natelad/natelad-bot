from flask import Flask, request, render_template
import os, requests
from dotenv import load_dotenv
from natelad_logic import generate_response
from database import log_message, init_db, get_all_conversations

load_dotenv()
app = Flask(__name__)
init_db()

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")

@app.route('/webhook', methods=['GET'])
def verify():
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.verify_token") == VERIFY_TOKEN:
        return request.args.get("hub.challenge"), 200
    return "Verification failed", 403

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    try:
        message = data['entry'][0]['changes'][0]['value']['messages'][0]
        user_number = message['from']
        user_text = message.get('text', {}).get('body', '')

        if not user_text:
            return "OK", 200

        log_message(user_number, "user", user_text)
        reply = generate_response(user_text)
        log_message(user_number, "bot", reply)
        send_message(user_number, reply)

    except Exception as e:
        print("[Webhook] Error processing message:", e)

    return "OK", 200

def send_message(recipient_id, message):
    url = f"https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "messaging_product": "whatsapp",
        "to": recipient_id,
        "text": {"body": message}
    }
    requests.post(url, headers=headers, json=data)

@app.route('/dashboard')
def dashboard():
    messages = get_all_conversations()
    return render_template("dashboard.html", messages=messages)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
