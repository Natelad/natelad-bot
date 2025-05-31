import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
openai_client = OpenAI(api_key=os.getenv("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"))

def generate_response(message, conversation_history=None):
    if conversation_history is None:
        conversation_history = []

    conversation_history.append({"role": "user", "content": message})

    try:
        response = openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": (
                    "You are Natelad Bot, a helpful assistant for Natelad Agency. "
                    "Your job is to help clients learn about our services like branding, web design, "
                    "automation, and pricing. Be professional and conversational."
                )},
                *conversation_history
            ],
            max_tokens=300
        )
        reply = response.choices[0].message.content.strip()
        conversation_history.append({"role": "assistant", "content": reply})
        return reply, conversation_history

    except Exception as e:
        print("OpenAI API Error:", e)
        return "Sorry, something went wrong. Please try again.", conversation_history
