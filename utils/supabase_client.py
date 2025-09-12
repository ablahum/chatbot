import os
from supabase import create_client, Client
from enum import Enum
from utils.gemini_client import embedding_with_gemini
from utils.openai_client import embedding_with_openai


SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

class Role(Enum):
  USER = "user"
  BOT = "bot"


def insert_chat(chat_id: int, role: Role, message: str):
  supabase.table('chat_history').insert({
    "chat_id": chat_id,
    "role": role,
    "message": message
  }).execute


def insert_knowledge(text):
  embedded = embedding_with_openai(text)

  data, count = supabase.table("knowledge_base").insert({
    "content": text,
    "embedding": embedded.data[0].embedding
  }).execute()

  return data


def search_knowledge(text: str, match_count: int = 3):
  embedded = embedding_with_openai(text)
  # embedded = embedding_with_gemini(text)
  
  response = supabase.rpc("match_documents", {
      "query_embedding": embedded,
      "match_count": match_count
  }).execute()

  return response.data