import os
import requests
from flask import Flask, request

app = Flask(name)

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
OPENROUTER_API_KEY = os.environ["OPENROUTER_API_KEY"]

TELEGRAM_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

SYSTEM_PROMPT = """
أنتِ سيلا، مساعدة ذكية ودودة تتحدث باللغة العربية.
كوني لطيفة وطبيعية ومختصرة في ردودك.
إذا تحدث المستخدم بلغة أخرى، يمكنك الرد بلغته.
"""

def send_message(chat_id, text):
    requests.post(
        f"{TELEGRAM_URL}/sendMessage",
        json={
            "chat_id": chat_id,
            "text": text
        },
        timeout=30
    )

def ask_ai(user_message):
    response = requests.post(
        OPENROUTER_URL,
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": "openrouter/free",
            "messages": [
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT
                },
                {
                    "role": "user",
                    "content": user_message
                }
            ]
        },
        timeout=60
    )

    response.raise_for_status()
    data = response.json()

    return data["choices"][0]["message"]["content"]


@app.route("/", methods=["GET"])
def home():
    return "Sila Bot is running!"


@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(silent=True) or {}

    message = data.get("message", {})
    chat = message.get("chat", {})
    text = message.get("text")

    if not chat or not text:
        return "OK", 200

    chat_id = chat["id"]

    try:
        reply = ask_ai(text)
        send_message(chat_id, reply)
    except Exception as e:
        print("ERROR:", e)
        send_message(
            chat_id,
            "عذرًا، حدث خطأ مؤقتًا. حاولي إرسال رسالتك مرة أخرى."
        )

    return "OK", 200


if name == "main":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
