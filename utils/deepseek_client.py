import os
from dotenv import load_dotenv
# from deepseek import DeepSeekAPI
from openai import OpenAI


load_dotenv()

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
deepseek = OpenAI(api_key = DEEPSEEK_API_KEY, base_url = "https://api.deepseek.com")


def ask_deepseek(context: str, text: str):
  try:
    prompt = f"""
    Context:
    {context}

    User's message:
    {text}
    """

    response = deepseek.chat.completions.create(
      model="deepseek-chat",
      messages=[
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

    print(response)
    return response.choices[0].message.content
  except Exception as err:
    return {
      "success": False,
      "error": f"Error occurred while asking: {str(err)}",
    }