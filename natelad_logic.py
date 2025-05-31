import openai
import os
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_response(user_input):
    try:
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful, professional assistant for Natelad Agency. Respond clearly and politely."},
                {"role": "user", "content": user_input}
            ]
        )
        return completion.choices[0].message['content'].strip()
    except Exception as e:
        print("OpenAI error:", e)
        return "Sorry, I couldn't process your request. Please try again later."
