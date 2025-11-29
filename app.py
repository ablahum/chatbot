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

    ADMIN_SESSIONS = getattr(app, "ADMIN_SESSIONS", None)
    if ADMIN_SESSIONS is None:
      ADMIN_SESSIONS = {}
      setattr(app, "ADMIN_SESSIONS", ADMIN_SESSIONS)
    lower_text = text.strip().lower()

    if lower_text.startswith("/admin"):
      if ADMIN_SESSIONS.get(chat_id, False):
        sent_message(chat_id, "Anda sudah berada dalam mode Admin.")
      else:
        ADMIN_SESSIONS[chat_id] = True
        sent_message(
          chat_id,
          (
            'Anda telah masuk ke mode Admin. Perintah yang tersedia:\n'
            '- /insert [informasi baru...]: Menambahkan knowledge baru ke database\n\n'
            'Anda juga bisa mengirimkan pertanyaan untuk diproses lebih dalam oleh bot (hanya di mode Admin).'
          )
        )
    elif ADMIN_SESSIONS.get(chat_id, False):
      if lower_text.startswith("/insert"):
        new_knowledge = text[len("/insert"):].strip()

        if not new_knowledge:
          sent_message(chat_id, (
            "Tolong sertakan informasi yang ingin dimasukkan setelah /insert"
            )
          )
        else:
          if len(new_knowledge.strip()) <= 10:
            sent_message(chat_id, (
              "Informasi yang ingin dimasukkan harus lebih dari 10 karakter. Tolong masukkan informasi yang lebih detail."
              )
            )
          else:
            insert_result = process_text(new_knowledge, 'insert')
            if isinstance(insert_result, dict) and insert_result.get("success"):
              sent_message(chat_id, "Berhasil menambahkan knowledge")
            else:
              sent_message(chat_id, f"Gagal menambahkan knowledge: {insert_result.get('error','Unknown error')}")
      if lower_text.startswith("/user"):
        ADMIN_SESSIONS[chat_id] = False

        sent_message(chat_id, "Anda telah keluar dari mode Admin dan sekarang kembali menjadi User.")
      else:
        #todo: prediction
        sent_message(chat_id, "Anda akan bertanya lebih dalam sebagai Admin.")
        # matches = process_text(text, 'retrieve')

        # if isinstance(matches, list):
        #   context = "\n".join([match["content"] for match in matches])
        # elif isinstance(matches, dict) and "error" in matches:
        #   context = ""
        # else:
        #   context = ""

        # answer = ask_gemini(context, text)
        # insert_chat(chat_id, Role.USER, text)
        # insert_chat(chat_id, Role.BOT, answer)
        # sent_message(chat_id, answer)
    else:
        #* user role
      if lower_text.startswith("/insert"):
        sent_message(chat_id, (
          "Anda harus masuk ke mode Admin terlebih dahulu untuk menambahkan informasi baru. Ketik /admin untuk masuk ke mode Admin."
          )
        )
      elif lower_text.startswith("/user"):
        sent_message(chat_id, "Anda sudah berada di mode User.")
      else:
        # retrieve knowledge
        matches = process_text(text, 'retrieve')

        if isinstance(matches, list):
          context = "\n".join([match["content"] for match in matches])
        elif isinstance(matches, dict) and "error" in matches:
          context = ""
        else:
          context = ""
        
        # ask ai
        answer = ask_gemini(context, text)
        insert_chat(chat_id, Role.USER, text)
        insert_chat(chat_id, Role.BOT, answer)
        sent_message(chat_id, answer)

  return {"ok": True}