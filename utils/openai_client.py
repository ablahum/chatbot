from openai import OpenAI
import os
from dotenv import load_dotenv


load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
open_ai = OpenAI(api_key = OPENAI_API_KEY)


#* GET OPENAI'S RESPONSE/ANSWER
def ask_openai(context: str, text: str):
  try:
    prompt = f"""
    Context:
    {context}

    User's message:
    {text}
    """
    
    answered = open_ai.chat.completions.create(
      model = "gpt-4o-mini",
      messages = [
        {
          "role": "system",
          "content": "You are a highly intelligent and professional AI assistant. Your job is to answer user messages accurately, clearly, and relevantly based solely on the information contained in the database. If an answer isn't found within the context of the database, be honest about the lack of information. Don't add or fabricate answers outside the context of the database. Answer in formal, easy-to-understand Bahasa Indonesia.",
        },
        {
          "role": "user",
          "content": prompt
        }
      ]
    )

    return answered.choices[0].message.content
  except Exception as err:
    return {
      "success": False,
      "error": f"Error occurred while asking: {str(err)}",
    }