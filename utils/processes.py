import numpy as np
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
from utils.supabase_client import insert_knowledge, search_knowledge


#* CHUNK RAW TEXT
def chunk_text(text: str):
  try:
    text_splitter = RecursiveCharacterTextSplitter(
      chunk_size = 100,
      chunk_overlap = 0
    )
    return text_splitter.split_text(text)
  except Exception as err:
    return {
      "success": False,
      "error": f"Error occurred while chunking: {str(err)}",
      "result": []
    }


#* EMBED CHUNKED TEXT
def embed_chunked(source, type: str):
  model = SentenceTransformer('all-mpnet-base-v2')

  if type == 'retrieve':
    try:
      embedding = model.encode(source)

      if isinstance(embedding, np.ndarray):
        embedding = embedding.tolist()

      if len(embedding) == 768:
        embedding = embedding + embedding

      return embedding
    except Exception as err:
      return {
        "success": False,
        "error": f"Error occurred while embedding: {str(err)}",
        "result": []
      }
  elif type == 'insert':
    try:
      embedding = model.encode(source)

      if isinstance(embedding, np.ndarray):
        embedding = embedding.tolist()
      
      embedded = []
      for embed in embedding:
        if len(embed) == 768:
          emb_1536 = embed + embed
        else:
          emb_1536 = embed
        embedded.append(emb_1536)
      
      return embedded
    except Exception as err:
      return {
        "success": False,
        "error": f"Error occurred while embedding: {str(err)}",
        "result": []
      }


#* PROCESS THE GIVEN TEXT/MESSAGE
def process_text(text: str, type: str):
  try:
    if type == 'retrieve':
      embedded = embed_chunked(text, type)

      return search_knowledge(embedded)
    elif type == 'insert':
      chunked = chunk_text(text)
      embedded = embed_chunked(chunked, type)

      return insert_knowledge(chunked, embedded)
    else:
      return {
        "success": False,
        "error": f"Unknown '{type}' process."
      }
  except Exception as err:
    return {
      "success": False,
      "error": f"Error occurred while processing: {str(err)}"
    }

