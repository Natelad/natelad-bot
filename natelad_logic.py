from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize OpenAI client with your API key from the environment
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_response(user_text):
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # You can change to gpt-4 if needed
            messages=[
                {"role": "system", "content": "You are a helpful, friendly WhatsApp chatbot for Natelad Agency. Provide clear and professional replies. Ask questions to qualify users and suggest helpful services."},
                {"role": "user", "content": user_text}
            ],
            temperature=0.7,
            max_tokens=500
        )
        return response.choices[0].message.content.strip()

    except Exception as e:
        print("OpenAI error:", e)
        return "Sorry, I couldn't process your request at the moment."
