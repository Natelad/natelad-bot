from flask import Flask, request
import os, requests
from dotenv import load_dotenv
from natelad_logic import generate_response

load_dotenv()

app = Flask(__name__)

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")

@app.route('/webhook', methods=['GET'])
def verify():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge, 200
    return "Verification failed", 403

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    try:
        message = data['entry'][0]['changes'][0]['value']['messages'][0]
        user_number = message['from']
        user_text = message['text']['body']
        reply = generate_response(user_text)
        send_message(user_number, reply)
    except Exception as e:
        print("Webhook error:", e)
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

if __name__ == "__main__":
    app.run()