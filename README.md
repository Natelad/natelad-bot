# 🤖 Natelad Bot — AI WhatsApp Assistant

**Natelad Bot** is an AI-powered WhatsApp chatbot built using **Python**, **Flask**, **Gemini 2.5**, and **Meta’s WhatsApp Cloud API**.  
It serves as a smart virtual assistant for [Natelad Agency](https://nateladagency.com), a web design and development company based in **Harare, Zimbabwe**.

---

## 🧠 Features

- 💬 Conversational AI powered by **Gemini 2.5**
- 📱 WhatsApp integration via **Meta for Developers**
- 🌐 Provides pricing, packages, and advice in real time
- 🤖 Brand-specific assistant — **Natelad Bot**
- 🔐 Secure with `.env` environment variables

---

## 📦 Tech Stack

| Technology               | Purpose                               |
|--------------------------|----------------------------------------|
| Python                   | Backend logic                         |
| Flask                    | Web server                            |
| Gunicorn                 | WSGI server for production            |
| Google Generative AI     | Gemini 2.5 model for intelligent chat |
| 360dialog / WhatsApp API | Messaging via WhatsApp                |
| python-dotenv            | Manage environment variables          |
| Requests                 | Handle outgoing HTTP requests         |

---

## 🚀 Installation & Deployment

### 1. 📁 Clone This Repository

```bash
git clone https://github.com/your-username/natelad-bot.git
cd natelad-bot
```

### 2. 📦 Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. 🔐 Configure Environment Variables

Create a `.env` file in the root directory:

```ini
GEMINI_API_KEY=your_google_api_key
ACCESS_TOKEN=your_whatsapp_access_token
VERIFY_TOKEN=your_webhook_verify_token
PHONE_NUMBER_ID=your_whatsapp_phone_number_id
```

### 4. 🧪 Run the Flask App (Development)

```bash
python app.py
```

### 5. 🚀 Run with Gunicorn (Production)

```bash
gunicorn app:app
```

---

## 🌐 Webhook Setup (Meta for Developers)

1. Set your webhook URL to:

```
https://yourdomain.com/webhook
```

2. Use `GET` for verification and `POST` for receiving messages.

3. For local development, use **ngrok**:

```bash
ngrok http 5000
```

---

## 🗂️ Project Structure

```
natelad-bot/
├── app.py              # Flask webhook handler
├── natelad_logic.py    # AI integration and response logic
├── requirements.txt    # Python dependencies
├── .env                # Environment variables
├── Procfile            # For Gunicorn deployment
└── README.md           # Project documentation
```

---

## 🧹 WhatsApp Formatting Rules

- All Markdown (e.g., `*bold*`, `_italic_`, `~strike~`) is stripped automatically.
- Important terms (like **Natelad Agency**) and section headers are selectively bolded.
- Links are converted to plain text for WhatsApp compatibility.

---

## 👤 Author

**Panashe Gunda**  
Founder & Developer — [Natelad Agency](https://nateladagency.com)

---

## 📄 License

This project is open-source and free to use or modify. Attribution is appreciated but not required.
