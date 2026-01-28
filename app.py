from flask import Flask, request, render_template, redirect, url_for, send_from_directory, jsonify
import os
import requests
import secrets
from dotenv import load_dotenv
from werkzeug.utils import secure_filename

from natelad_logic import generate_response
from db import (
    init_db, upsert_user, get_user, set_username,
    save_message, list_conversations, get_messages,
    set_takeover, is_takeover, get_recent_history_for_ai
)

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("DASHBOARD_SECRET", secrets.token_hex(32))

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")

# This MUST be your public domain when sending media outbound.
# Example: https://yourdomain.com
PUBLIC_BASE_URL = (os.getenv("PUBLIC_BASE_URL") or "").rstrip("/")

UPLOAD_DIR = os.path.abspath("uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

init_db()


# ---------------------------
# WhatsApp Send Helpers
# ---------------------------
def wa_post(payload: dict):
    url = f"https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID}/messages"
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}", "Content-Type": "application/json"}
    r = requests.post(url, headers=headers, json=payload, timeout=30)
    print("[WA] status:", r.status_code, r.text)
    return r


def send_text(to: str, text: str):
    return wa_post({
        "messaging_product": "whatsapp",
        "to": to,
        "text": {"body": text}
    })


def send_media(to: str, media_type: str, link: str, caption: str | None = None, filename: str | None = None):
    media_obj = {"link": link}
    if caption:
        media_obj["caption"] = caption
    if filename and media_type == "document":
        media_obj["filename"] = filename

    return wa_post({
        "messaging_product": "whatsapp",
        "to": to,
        media_type: media_obj
    })


def send_buttons(to: str, body_text: str, buttons: list[tuple[str, str]]):
    return wa_post({
        "messaging_product": "whatsapp",
        "to": to,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {"text": body_text},
            "action": {
                "buttons": [
                    {"type": "reply", "reply": {"id": bid, "title": title}}
                    for (bid, title) in buttons
                ]
            }
        }
    })


def send_list(to: str, body_text: str, button_text: str, sections: list[dict]):
    return wa_post({
        "messaging_product": "whatsapp",
        "to": to,
        "type": "interactive",
        "interactive": {
            "type": "list",
            "body": {"text": body_text},
            "action": {"button": button_text, "sections": sections}
        }
    })


# ---------------------------
# WhatsApp Media Download
# ---------------------------
def download_media(media_id: str) -> tuple[str | None, str | None]:
    """
    Returns (local_path, mime_type)
    """
    try:
        meta_url = f"https://graph.facebook.com/v19.0/{media_id}"
        headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
        meta = requests.get(meta_url, headers=headers, timeout=30).json()

        media_url = meta.get("url")
        mime = meta.get("mime_type")
        if not media_url:
            return None, None

        r = requests.get(media_url, headers=headers, timeout=60)
        r.raise_for_status()

        ext = ""
        if mime:
            if "jpeg" in mime:
                ext = ".jpg"
            elif "png" in mime:
                ext = ".png"
            elif "pdf" in mime:
                ext = ".pdf"
            elif "mp4" in mime:
                ext = ".mp4"

        filename = secure_filename(f"{media_id}{ext}")
        path = os.path.join(UPLOAD_DIR, filename)
        with open(path, "wb") as f:
            f.write(r.content)

        return path, mime
    except Exception as e:
        print("[Media] download error:", e)
        return None, None


def parse_incoming(message: dict) -> dict:
    """
    Normalize incoming WA message into:
    {
      "phone": "...",
      "type": "text|image|video|document|interactive|unknown",
      "text": "...",
      "media_path": "...",
      "mime": "...",
      "wa_id": "wamid...."
    }
    """
    phone = message.get("from")
    wa_id = message.get("id")
    mtype = message.get("type") or "unknown"

    out = {"phone": phone, "type": mtype, "text": None, "media_path": None, "mime": None, "wa_id": wa_id}

    if mtype == "text":
        out["text"] = message.get("text", {}).get("body", "")

    elif mtype in ("image", "video", "document"):
        media_obj = message.get(mtype, {})
        media_id = media_obj.get("id")
        caption = media_obj.get("caption")
        out["text"] = caption
        if media_id:
            path, mime = download_media(media_id)
            out["media_path"] = path
            out["mime"] = mime

    elif mtype == "interactive":
        inter = message.get("interactive", {})
        itype = inter.get("type")
        if itype == "button_reply":
            out["text"] = inter.get("button_reply", {}).get("id")  # store reply id
        elif itype == "list_reply":
            out["text"] = inter.get("list_reply", {}).get("id")    # store row id
        else:
            out["text"] = ""

    return out


# ---------------------------
# Routes: Upload Serve
# ---------------------------
@app.route("/uploads/<path:filename>")
def uploads(filename):
    return send_from_directory(UPLOAD_DIR, filename)


# ---------------------------
# Webhook Verify
# ---------------------------
@app.route("/webhook", methods=["GET"])
def verify():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        print("[Webhook] Verification successful")
        return challenge, 200

    print("[Webhook] Verification failed")
    return "Verification failed", 403


# ---------------------------
# Webhook Receive
# ---------------------------
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json() or {}
    print("[Webhook] Incoming:", data)

    try:
        value = data["entry"][0]["changes"][0]["value"]

        # Sometimes you'll receive statuses instead of messages
        messages = value.get("messages")
        if not messages:
            return "OK", 200

        msg = messages[0]
        parsed = parse_incoming(msg)

        phone = parsed["phone"]
        if not phone:
            return "OK", 200

        upsert_user(phone)

        # Save incoming user message
        save_message(
            phone=phone,
            sender="user",
            msg_type=parsed["type"],
            text=parsed["text"],
            media_path=parsed["media_path"],
            mime_type=parsed["mime"],
            wa_message_id=parsed["wa_id"]
        )

        text_lower = (parsed["text"] or "").strip().lower()

        # Turnover keywords -> enable takeover
        if text_lower in {"agent", "human", "person", "speak to a person", "talk to a person"}:
            set_takeover(phone, True)
            reply = "✅ Okay — a human agent will take over now. Please type your message."
            send_text(phone, reply)
            save_message(phone, "bot", "text", reply)
            return "OK", 200

        # If takeover active -> do NOT auto-reply
        if is_takeover(phone):
            return "OK", 200

        # Optional: handle interactive IDs with your own routing
        # Example:
        # if parsed["type"] == "interactive" and parsed["text"] == "pricing":
        #     send_text(phone, "Pricing: ZW $30/mo | International $120/mo ...")
        #     save_message(phone, "bot", "text", "Pricing: ...")
        #     return "OK", 200

        # AI response (per user history)
        history = get_recent_history_for_ai(phone, limit=18)
        reply = generate_response(parsed["text"] or "", history=history)

        send_text(phone, reply)
        save_message(phone, "bot", "text", reply)

    except Exception as e:
        print("[Webhook] Error:", e)

    return "OK", 200


# ---------------------------
# Dashboard
# ---------------------------
@app.route("/dashboard")
def dashboard():
    conversations = list_conversations()
    active_phone = request.args.get("phone")

    msgs = []
    active_takeover = False
    active_username = None

    if active_phone:
        msgs = get_messages(active_phone)
        active_takeover = is_takeover(active_phone)
        u = get_user(active_phone)
        active_username = u["username"] if u else None

    return render_template(
        "dashboard.html",
        conversations=conversations,
        active_phone=active_phone,
        active_username=active_username,
        active_takeover=active_takeover,
        messages=msgs
    )


@app.route("/toggle_takeover", methods=["POST"])
def toggle_takeover():
    phone = request.form["phone"]
    now = not is_takeover(phone)
    set_takeover(phone, now)

    note = "🔁 Takeover toggled: " + ("HUMAN" if now else "BOT")
    save_message(phone, "human", "text", note)

    return redirect(url_for("dashboard", phone=phone))


@app.route("/set_username", methods=["POST"])
def set_username_route():
    phone = request.form["phone"]
    username = (request.form.get("username") or "").strip()
    if username:
        set_username(phone, username)
    return redirect(url_for("dashboard", phone=phone))


@app.route("/send_human", methods=["POST"])
def send_human():
    phone = request.form["phone"]
    text = (request.form.get("text") or "").strip()
    file = request.files.get("file")

    # Save + send file (requires PUBLIC_BASE_URL)
    if file and file.filename:
        filename = secure_filename(file.filename)
        local_path = os.path.join(UPLOAD_DIR, f"{secrets.token_hex(8)}_{filename}")
        file.save(local_path)

        mime = file.mimetype or ""
        if not PUBLIC_BASE_URL:
            # Still store in DB, but cannot send media without public link
            save_message(phone, "human", "document", text="⚠️ PUBLIC_BASE_URL not set; media saved locally only.")
            save_message(phone, "human", "document", text=text or None, media_path=local_path, mime_type=mime)
            return redirect(url_for("dashboard", phone=phone))

        link = f"{PUBLIC_BASE_URL}/uploads/{os.path.basename(local_path)}"

        if mime.startswith("image/"):
            send_media(phone, "image", link, caption=text or None)
            save_message(phone, "human", "image", text=text or None, media_path=local_path, mime_type=mime)

        elif mime.startswith("video/"):
            send_media(phone, "video", link, caption=text or None)
            save_message(phone, "human", "video", text=text or None, media_path=local_path, mime_type=mime)

        else:
            send_media(phone, "document", link, caption=text or None, filename=filename)
            save_message(phone, "human", "document", text=text or None, media_path=local_path, mime_type=mime)

        return redirect(url_for("dashboard", phone=phone))

    # Send text only
    if text:
        send_text(phone, text)
        save_message(phone, "human", "text", text)

    return redirect(url_for("dashboard", phone=phone))


# ---------------------------
# API for live refresh polling
# ---------------------------
@app.route("/api/messages")
def api_messages():
    phone = request.args.get("phone")
    after = int(request.args.get("after", "0"))

    if not phone:
        return jsonify({"new": []})

    msgs = get_messages(phone, limit=300)
    # after = count at client-side; if DB has more, return "new"
    if len(msgs) > after:
        return jsonify({"new": msgs[after:]})
    return jsonify({"new": []})


if __name__ == "__main__":
    # Use host=0.0.0.0 for server deployments
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")), debug=True)
