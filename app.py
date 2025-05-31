import os
import openai
import requests
from flask import Flask, request, jsonify
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Load keys and tokens
OPENAI_API_KEY = os.getenv("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")
WHATSAPP_TOKEN = os.getenv("EAAO3jgdm2V4BO8wQavxoqH3QyoG4tXxN6JoGskAXGzOlrELCTUZAnpyNZBePN9d0EWWA47GT1qKwnbcZADDdHT0ghLoWLEcgldgWw1ZBZBCa7Y9hhp0hO7blGWnZCqIAbhb1sgv9yNw4GaRmzygXho5zPhQQNgnQquFG8cl18Dt7wVZCQDBqogXpKg1Jj3OgxwaZBxUhpqP6YY7KTWulhDBtdvRE90KHWlutdpUZD")
WHATSAPP_PHONE_NUMBER_ID = os.getenv("664876586702764")
VERIFY_TOKEN = os.getenv("natelad_custom_token")

client = openai.OpenAI(api_key=OPENAI_API_KEY)

def send_whatsapp_message(recipient_id, message_text):
    url = f"https://graph.facebook.com/v19.0/{WHATSAPP_PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "messaging_product": "whatsapp",
        "to": recipient_id,
        "type": "text",
        "text": {
            "body": message_text
        }
    }

    response = requests.post(url, headers=headers, json=data)
    print("WhatsApp API response:", response.status_code, response.text)
    return response

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        # Verification from Meta
        verify_token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')
        mode = request.args.get('hub.mode')

        if mode == 'subscribe' and verify_token == VERIFY_TOKEN:
            print("Webhook verified successfully.")
            return challenge, 200
        else:
            print("Webhook verification failed.")
            return "Verification token mismatch", 403

    if request.method == 'POST':
        data = request.get_json()
        print("Incoming data:", data)

        try:
            message = data['entry'][0]['changes'][0]['value']['messages'][0]
            user_message = message['text']['body']
            sender_id = message['from']

            # Generate reply using OpenAI
            completion = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant for Natelad Agency."},
                    {"role": "user", "content": user_message}
                ]
            )

            reply = completion.choices[0].message.content.strip()
            print("AI Reply:", reply)

            # Send reply to user
            send_whatsapp_message(sender_id, reply)
            return jsonify({"status": "success"}), 200

        except Exception as e:
            print("Error:", e)
            return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/', methods=['GET'])
def index():
    return "Natelad Bot is live!", 200

if __name__ == '__main__':
    app.run(debug=True)
