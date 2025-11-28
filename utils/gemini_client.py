from google import genai
from google.genai import types
import os
from dotenv import load_dotenv

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key = GEMINI_API_KEY)

# def embed_with_gemini(text: str):
#   try:
#     response = client.embeddings.create(
#       model="models/embedding-001",
#       content=text
#     )
#     # Response Gemini biasanya fieldnya 'embedding' -> 'values'
#     vector = response.embedding.values if hasattr(response.embedding, "values") else response.embedding
#     return vector
#   except Exception as err:
#     return {
#       "success": False,
#       "error": f"Error occurred while embedding with Gemini: {str(err)}",
#       "result": []
#     }

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