from flask import Flask, request, redirect, session, url_for, render_template
import os, requests
from dotenv import load_dotenv
from natelad_logic import generate_response
from chat_store import save_message

load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "supersecret")

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
        user_text = message.get('text', {}).get('body', '')
        if not user_text:
            return "OK", 200
        reply = generate_response(user_text)
        save_message(user_number, user_text, "user")
        save_message(user_number, reply, "bot")
        send_message(user_number, reply)
    except Exception as e:
        print("[Webhook] Error:", e)
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

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form['username'] == "admin" and request.form['password'] == "Thunderking":
            session['logged_in'] = True
            return redirect("/dashboard")
        return render_template("login.html", error="Invalid credentials")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

@app.route("/dashboard")
def dashboard():
    from chat_store import get_conversations
    if not session.get("logged_in"):
        return redirect("/login")
    user_id = request.args.get("user_id")
    return render_template("dashboard.html", conversations=get_conversations(user_id), selected_user=user_id)

@app.route("/messages")
def messages():
    from chat_store import get_messages
    user_id = request.args.get("user_id")
    return get_messages(user_id)

if __name__ == "__main__":
    app.run(debug=True)
