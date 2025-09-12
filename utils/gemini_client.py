import os
from dotenv import load_dotenv
import google.generativeai as genai
# from google import genai


load_dotenv()
# genai.configure(api_key = os.getenv("GEMINI_API_KEY"))
# client = genai.Client()


#* GET GEMINI'S RESPONSE/ANSWER
# def ask_gemini(context, text):
#   prompt = f"""
#   Context:
#   {context}

#   User's message:
#   {text}
#   """
  
#   # model = genai.GenerativeModel('gemini-2.5-flash')
  
#   # response = model.generate_content(
#   #     prompt,
#   #     generation_config = genai.types.GenerationConfig(
#   #         temperature = 0.7,
#   #         top_p = 0.8,
#   #         top_k = 40,
#   #         max_output_tokens = 1024,
#   #     )
#   # )
  
#   # return response.text

#   response = client.models.generate_content(
#     model = "gemini-2.5-flash",
#     contents = prompt,
#   )

#   return response.text


import google.generativeai as genai

genai.configure(api_key = os.getenv("GEMINI_API_KEY"))

def ask_gemini(context: str, text: str) -> str:
  prompt = f"""
  Context:
  {context}

  User's message:
  {text}
  """

  try:
    model = genai.GenerativeModel("gemini-2.5-flash")
    response = model.generate_content(prompt)
    return response.text
  except Exception as error:
    print("Gemini error:", error)
    return "Maaf, sistem sedang tidak bisa memberikan jawaban."


def embedding_with_gemini(text: str):
  try:
    result = genai.embed_content(
        model="models/embedding-001",   # pastikan pakai "models/" prefix
        content=text
    )
    return result["embedding"]
  except Exception as error:
    print(f"Error dalam embedding_with_gemini: {error}")
    return None
