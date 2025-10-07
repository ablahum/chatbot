from transformers import pipeline

def ask_huggingface(context: str, text: str):
  try:
    # Beralih ke extractive QA agar jawaban selalu diambil dari konteks
    qa = pipeline(
      "question-answering",
      model = "indolem/indobert-base-uncased-squad"
    )

    if context is None:
      context = ""

    result = qa({
      "question": text,
      "context": context
    })

    answer = (result.get("answer") or "").strip()
    score = float(result.get("score") or 0.0)

    # Jika keyakinan rendah atau tidak ada jawaban, beri respon netral sesuai kebijakan
    if not answer or score < 0.2:
      return "Maaf, informasi tersebut tidak ditemukan dalam konteks yang tersedia."

    return answer
  except Exception as err:
    return {
      "success": False,
      "error": f"Error occurred while using HuggingFace: {str(err)}"
    }
