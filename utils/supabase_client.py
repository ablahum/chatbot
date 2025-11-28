import os
from dotenv import load_dotenv
from supabase import create_client, Client
from enum import Enum

load_dotenv()
SUPABASE_URL: str = os.getenv("SUPABASE_URL")
SUPABASE_KEY: str = os.getenv("SUPABASE_ANON_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

class Role(Enum):
  USER = "user"
  BOT = "bot"

def insert_chat(chat_id: int, role: Role, message: str):
  try:
    response = supabase.table('chat_history').insert({
      "chat_id": chat_id,
      "role": role.value,
      "message": message
    }).execute()
    
    if hasattr(response, "error") and response.error is not None:
      return {
        "success": False,
        "error": str(response.error)
      }

    return {
      "success": True,
      "message": "Chat successfully inserted."
    }
  except Exception as err:
    return {
      "success": False,
      "error": str(err)
    }

def insert_knowledge(chunked, embedded):
  insert_data = []

  for chunk, embedding in zip(chunked, embedded):
    insert_data.append({
      "content": chunk,
      "embedding": embedding
    })

  try:
    response = supabase.table("knowledge_base").insert(insert_data).execute()
    if hasattr(response, "error") and response.error is not None:
      return {"success": False, "error": str(response.error)}

    return {
      "success": True,
      "message": 'Knowledge successfully inserted.'
    }
  except Exception as err:
    return {
      "success": False,
      "error": str(err)
    }


def search_knowledge(embedded, match_count: int = 3):
  try:
    response = supabase.rpc("match_documents", {
    "query_embedding": embedded,
    "match_count": match_count
  }).execute()

    return response.data
  except Exception as err:
    return {
      "success": False,
      "error": f"Error occurred while searching: {str(err)}",
    }