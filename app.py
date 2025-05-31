from flask import Flask, request
import requests
import openai
import os

app = Flask(__name__)

# Set OpenAI API key from environment variable
openai.api_key = os.environ.get("OPENAI_API_KEY")

# WhatsApp verification endpoint
@app.route('/webhook', methods=['GET'])
def verify():
    verify_token = os.environ.get("WHATSAPP_VERIFY_TOKEN")
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode and token:
        if mode == "subscribe" and token == verify_token:
            print("WEBHOOK_VERIFIED")
            return challenge, 200
        else:
            return "Forbidden", 403
    return "Bad Request", 400

# Handle incoming messages
@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    print("Incoming data:", data)

    if data.get("object") == "whatsapp_business_account":
        for entry in data.get("entry", []):
            for change in entry.get("changes", []):
                value = change.get("value")
                messages = value.get("messages")

                if messages:
                    for message in messages:
                        phone_number_id = value["metadata"]["phone_number_id"]
                        from_number = message["from"]
                        msg_text = message["text"]["body"]

                        # Get AI-generated response
                        try:
                            completion = openai.ChatCompletion.create(
                                model="gpt-3.5-turbo",
                                messages=[
                                    {"role": "system", "content": "You are a helpful assistant for a digital agency."},
                                    {"role": "user", "content": msg_text}
                                ]
                            )
                            ai_reply = completion.choices[0].message["content"]
                        except Exception as e:
                            print(f"Error with OpenAI: {e}")
                            ai_reply = "Sorry, something went wrong while generating a reply."

                        # Send response back to WhatsApp
                        url = f"https://graph.facebook.com/v18.0/{phone_number_id}/messages"
                        headers = {
                            "Authorization": f"Bearer {os.environ.get('WHATSAPP_ACCESS_TOKEN')}",
                            "Content-Type": "application/json"
                        }
                        payload = {
                            "messaging_product": "whatsapp",
                            "to": from_number,
                            "text": {"body": ai_reply}
                        }
                        try:
                            response = requests.post(url, headers=headers, json=payload)
                            print("Sent message:", response.text)
                        except Exception as e:
                            print(f"Error sending message: {e}")

    return "OK", 200

if __name__ == '__main__':
    app.run(debug=True)
