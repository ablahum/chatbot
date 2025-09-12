import os
from dotenv import load_dotenv
import requests


load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")


def send_message(chat_id: int, text: str):
  url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
  payload = {
    "chat_id": chat_id,
    "text": text
  }

  requests.post(url, json=payload)