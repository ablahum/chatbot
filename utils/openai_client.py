from openai import OpenAI
import os
from dotenv import load_dotenv


load_dotenv()
client = OpenAI(api_key = os.getenv("OPENAI_API_KEY"))


#* EMBEDDING
def embedding_with_openai(text):
  embedded = client.embeddings.create(
    model = "text-embedding-3-small",
    input = text,
    dimensions = 512
  )

  return embedded


#* GET OPENAI'S RESPONSE/ANSWER
# def ask_openai(context, text):
#   try:
#     prompt = f"""
#     Context:
#     {context}

#     User's message:
#     {text}
#     """
    
#     answered = client.chat.completions.create(
#       model = "gpt-4o-mini",
#       messages = [
#         {
#           "role": "system",
#           "content": "You are a highly intelligent and professional AI assistant. Your job is to answer user questions accurately, clearly, and relevantly based solely on the information contained in the database. If an answer isn't found within the context of the database, be honest about the lack of information. Don't add or fabricate answers outside the context of the database. Answer in formal, easy-to-understand Bahasa Indonesia.",
#         },
#         {
#           "role": "user",
#           "content": prompt
#         }
#       ]
#     )

#     # return answered
#     print("berhasil bertanya pada openai", answered.choices[0].message.content)
#     return answered.choices[0].message.content
#   except Exception as error:
#     print(f"Error dalam ask_openai: {error}")
    
#     return "Maaf, terjadi kesalahan dalam memproses permintaan Anda. Silakan coba lagi."