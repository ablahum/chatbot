import os
import requests
from fastapi import FastAPI, Request
from dotenv import load_dotenv
from enum import Enum
from utils.gemini_client import ask_gemini
# from utils.openai_client import ask_openai
from utils.supabase_client import insert_chat, search_knowledge
from utils.telegram_client import send_message


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

  print(data)

  if "message" in data:
    chat_id = data["message"]["chat"]["id"]
    text = data["message"].get("text", "")

    matches = search_knowledge(text)
    context = "\n".join([m["content"] for m in matches])

    # answer = ask_openai(context, text)
    answer = ask_gemini(context, text)

    #* INSERT CHAT HISTORY FOR LOGGING
    insert_chat(chat_id, Role.USER, text)
    insert_chat(chat_id, Role.BOT, answer)

    #* SEND MESSAGE TO CLIENT
    # send_message(chat_id, answer)
    send_message(text)

  return {"ok": True}