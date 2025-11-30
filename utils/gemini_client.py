from google import genai
from google.genai import types
import os
from dotenv import load_dotenv

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key = GEMINI_API_KEY)

#* GET GEMINI'S RESPONSE/ANSWER
def ask_gemini(context: str, text: str):
  try:
    prompt = f"""
    Context:
    {context}

    User's message:
    {text}
    """
    
    answered = client.models.generate_content(
      model = "gemini-2.5-flash",
      config = types.GenerateContentConfig(
        system_instruction = "You are a highly intelligent and professional AI assistant. Your job is to answer user messages accurately, clearly, directly, and relevantly based solely on the information contained in the database. If an answer isn't found within the context of the database, be honest about the lack of information. Don't add or fabricate answers outside the context of the database. Answer in formal, easy-to-understand Bahasa Indonesia."),
      contents = prompt
    )

    return answered.text
  except Exception as err:
    return {
      "success": False,
      "error": f"Error occurred while asking: {str(err)}",
    }