import os
import requests
from fastapi import FastAPI, Request
from dotenv import load_dotenv
from enum import Enum
from utils.gemini_client import ask_gemini
from utils.huggingface import ask_huggingface
from utils.processes import process_text
from utils.supabase_client import insert_chat
from utils.telegram_client import sent_message


load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
app = FastAPI()

class Role(Enum):
  USER = "user"
  BOT = "bot"


@app.on_event("startup")
def set_webhook():
  url = f"https://api.telegram.org/bot{TOKEN}/setWebhook"
  payload = {
    "url": WEBHOOK_URL
  }
  request = requests.post(url, json = payload)
  print("Webhook set response:", request.json())


@app.post("/webhook")
async def telegram_webhook(request: Request):
  data = await request.json()

  if "message" in data:
    chat_id = data["message"]["chat"]["id"]
    text = data["message"].get("text", "")

    #* ADMIN
    #* insert knowledge
    # data = process_text(text, 'insert')

    #* sent message to client
    # sent_message(chat_id, f"Berhasil menambahkan knowledge")

    #* USER
    #* retrieve knowledge
    matches = process_text(text, 'retrieve')
    context = "\n".join([match["content"] for match in matches])

    #* ai answer
    answer = ask_gemini(context, text)

    #* insert chat history for logging
    insert_chat(chat_id, Role.USER, text)
    insert_chat(chat_id, Role.BOT, answer)

    #* sent message to client
    sent_message(chat_id, answer)

  return {"ok": True}