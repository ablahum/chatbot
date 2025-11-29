from fastapi.testclient import TestClient
from app import app, Role
import pytest

client = TestClient(app)

@pytest.fixture(autouse=True)
def reset_admin_sessions():
  if hasattr(app, "ADMIN_SESSIONS"):
    app.ADMIN_SESSIONS.clear()
  else:
    setattr(app, "ADMIN_SESSIONS", {})

@pytest.fixture
def sent_msgs(monkeypatch):
  msgs = []
  monkeypatch.setattr("app.sent_message", lambda chat_id, msg: msgs.append((chat_id, msg)))
  return msgs

def post_webhook(body):
  return client.post("/webhook", json=body)

def test_set_webhook_on_startup(monkeypatch):
  calls = {}

  def mock_post(url, json):
    calls["url"] = url
    calls["json"] = json
    class Resp:
      def json(self_inner):
        return {"ok": True, "result": True}
    return Resp()

  monkeypatch.setattr("requests.post", mock_post)
  with TestClient(app):
    pass
  assert "url" in calls
  assert "/setWebhook" in calls["url"]

def test_telegram_webhook_message_admin(sent_msgs, monkeypatch):
  chat_id = 5678
  body = {
    "message": {
      "chat": {"id": chat_id},
      "text": "/admin"
    }
  }
  response = post_webhook(body)
  assert response.status_code in (200, 204)
  assert any("mode Admin" in msg for _, msg in sent_msgs), f"Messages: {sent_msgs}"

def test_telegram_webhook_insert_knowledge(monkeypatch, sent_msgs):
  chat_id = 1357

  def fake_process_text(new_knowledge, mode):
    if len(new_knowledge) > 10:
      return {"success": True}
    else:
      return {"success": False, "error": "too short"}

  monkeypatch.setattr("app.process_text", fake_process_text)
  app.ADMIN_SESSIONS[chat_id] = True

  body_short = {
    "message": {
      "chat": {"id": chat_id},
      "text": "/insert pendek"
    }
  }
  response_short = post_webhook(body_short)
  assert response_short.status_code == 200
  assert any("lebih dari 10 karakter" in msg for _, msg in sent_msgs), f"Messages: {sent_msgs}"

  sent_msgs.clear()
  body_valid = {
    "message": {
      "chat": {"id": chat_id},
      "text": "/insert ini pengetahuan baru yang valid"
    }
  }
  response_valid = post_webhook(body_valid)
  assert response_valid.status_code == 200
  assert any("Berhasil menambahkan knowledge" in msg for _, msg in sent_msgs), f"Messages: {sent_msgs}"

def test_telegram_webhook_user_mode(sent_msgs):
  chat_id = 2468
  app.ADMIN_SESSIONS[chat_id] = True
  body = {
    "message": {
      "chat": {"id": chat_id},
      "text": "/user"
    }
  }
  response = post_webhook(body)
  assert response.status_code == 200
  assert app.ADMIN_SESSIONS[chat_id] == False

def test_telegram_webhook_no_message():
  body = {
    "not_message": True
  }
  response = post_webhook(body)
  assert response.status_code == 200

def test_telegram_webhook_user_insert_without_admin(sent_msgs):
  chat_id = 9999
  body = {
    "message": {
      "chat": {"id": chat_id},
      "text": "/insert pengetahuan baru"
    }
  }
  response = post_webhook(body)
  assert response.status_code == 200
  assert any("harus masuk ke mode Admin" in msg for _, msg in sent_msgs), f"Messages: {sent_msgs}"

def test_telegram_webhook_insert_empty_text(monkeypatch, sent_msgs):
  chat_id = 1111

  def fake_process_text(new_knowledge, mode):
    return {"success": True}

  monkeypatch.setattr("app.process_text", fake_process_text)
  app.ADMIN_SESSIONS[chat_id] = True

  body = {
    "message": {
      "chat": {"id": chat_id},
      "text": "/insert"
    }
  }
  response = post_webhook(body)
  assert response.status_code == 200
  assert any("sertakan informasi" in msg for _, msg in sent_msgs), f"Messages: {sent_msgs}"

def test_telegram_webhook_user_normal_question(monkeypatch, sent_msgs):
  chat_id = 3333
  user_question = "Apa itu kucing?"
  expected_matches = [
    {
      "content": "Kucing adalah hewan mamalia yang lucu."
    },
    {
      "content": "Kucing memiliki empat kaki dan ekor."
    }
  ]
  expected_answer = "Kucing adalah hewan mamalia yang lucu."

  process_calls = []
  gemini_calls = []
  insert_calls = []

  def fake_process_text(text, mode):
    process_calls.append((text, mode))
    if mode == 'retrieve':
      return expected_matches
    return {"success": True}

  def fake_ask_gemini(context, text):
    gemini_calls.append((context, text))
    return expected_answer

  def fake_insert_chat(chat_id_param, role, message):
    insert_calls.append((chat_id_param, role, message))
    return {"success": True}

  monkeypatch.setattr("app.process_text", fake_process_text)
  monkeypatch.setattr("app.ask_gemini", fake_ask_gemini)
  monkeypatch.setattr("app.insert_chat", fake_insert_chat)

  body = {
    "message": {
      "chat": {"id": chat_id},
      "text": user_question
    }
  }
  response = post_webhook(body)

  assert response.status_code == 200
  
  assert len(process_calls) == 1
  assert process_calls[0] == (user_question, 'retrieve')

  assert len(gemini_calls) == 1
  expected_context = "\n".join([match["content"] for match in expected_matches])
  assert gemini_calls[0][0] == expected_context
  assert gemini_calls[0][1] == user_question

  assert len(insert_calls) == 2
  assert insert_calls[0][0] == chat_id
  assert insert_calls[0][1].value == "user"
  assert insert_calls[0][2] == user_question
  assert insert_calls[1][0] == chat_id
  assert insert_calls[1][1].value == "bot"
  assert insert_calls[1][2] == expected_answer

  assert any(expected_answer in msg for _, msg in sent_msgs), f"Messages: {sent_msgs}"

def test_telegram_webhook_user_normal_question_with_error(monkeypatch, sent_msgs):
  """Test: User mode - question flow ketika process_text mengembalikan error"""
  chat_id = 4444
  user_question = "Apa itu anjing?"
  expected_answer = "Maaf, terjadi kesalahan."

  process_calls = []
  gemini_calls = []

  def fake_process_text(text, mode):
    process_calls.append((text, mode))
    if mode == 'retrieve':
      return {"error": "Database connection failed"}
    return {"success": True}

  def fake_ask_gemini(context, text):
    gemini_calls.append((context, text))
    return expected_answer

  def fake_insert_chat(chat_id_param, role, message):
    return {"success": True}

  monkeypatch.setattr("app.process_text", fake_process_text)
  monkeypatch.setattr("app.ask_gemini", fake_ask_gemini)
  monkeypatch.setattr("app.insert_chat", fake_insert_chat)

  body = {
    "message": {
      "chat": {"id": chat_id},
      "text": user_question
    }
  }
  response = post_webhook(body)

  assert response.status_code == 200
  
  assert len(process_calls) == 1
  assert process_calls[0] == (user_question, 'retrieve')

  assert len(gemini_calls) == 1
  assert gemini_calls[0][0] == ""
  assert gemini_calls[0][1] == user_question

  assert any(expected_answer in msg for _, msg in sent_msgs), f"Messages: {sent_msgs}"

def test_telegram_webhook_user_already_in_user_mode(sent_msgs):
  chat_id = 5555
  body = {
    "message": {
      "chat": {"id": chat_id},
      "text": "/user"
    }
  }
  response = post_webhook(body)
  assert response.status_code == 200
  assert any("sudah berada di mode User" in msg for _, msg in sent_msgs), f"Messages: {sent_msgs}"

def test_telegram_webhook_insert_failed_with_error(monkeypatch, sent_msgs):
  chat_id = 6666
  
  def fake_process_text(new_knowledge, mode):
    return {"success": False, "error": "Database connection timeout"}

  monkeypatch.setattr("app.process_text", fake_process_text)
  app.ADMIN_SESSIONS[chat_id] = True

  body = {
    "message": {
      "chat": {"id": chat_id},
      "text": "/insert ini adalah pengetahuan yang cukup panjang untuk validasi"
    }
  }
  response = post_webhook(body)
  assert response.status_code == 200
  assert any("Gagal menambahkan knowledge" in msg for _, msg in sent_msgs), f"Messages: {sent_msgs}"
  assert any("Database connection timeout" in msg for _, msg in sent_msgs), f"Messages: {sent_msgs}"

def test_telegram_webhook_admin_already_in_admin_mode(sent_msgs):
  chat_id = 7777
  app.ADMIN_SESSIONS[chat_id] = True
  
  body = {
    "message": {
      "chat": {"id": chat_id},
      "text": "/admin"
    }
  }
  response = post_webhook(body)
  assert response.status_code == 200
  assert any("sudah berada dalam mode Admin" in msg for _, msg in sent_msgs), f"Messages: {sent_msgs}"

def test_telegram_webhook_user_question_with_gemini_error(monkeypatch, sent_msgs):
  chat_id = 8888
  user_question = "Apa itu burung?"
  expected_matches = [
    {
      "content": "Burung adalah hewan yang bisa terbang."
    }
  ]
  error_response = {"success": False, "error": "Gemini API rate limit exceeded"}

  def fake_process_text(text, mode):
    if mode == 'retrieve':
      return expected_matches
    return {"success": True}

  def fake_ask_gemini(context, text):
    return error_response

  def fake_insert_chat(chat_id_param, role, message):
    return {"success": True}

  monkeypatch.setattr("app.process_text", fake_process_text)
  monkeypatch.setattr("app.ask_gemini", fake_ask_gemini)
  monkeypatch.setattr("app.insert_chat", fake_insert_chat)

  body = {
    "message": {
      "chat": {"id": chat_id},
      "text": user_question
    }
  }
  response = post_webhook(body)
  
  assert response.status_code == 200
  assert any(error_response == msg or str(error_response) in str(msg) or "error" in str(msg).lower() for _, msg in sent_msgs), f"Messages: {sent_msgs}"

def test_telegram_webhook_user_question_with_unexpected_matches_type(monkeypatch, sent_msgs):
  chat_id = 9998
  user_question = "Apa itu ikan?"
  expected_answer = "Ikan adalah hewan air."

  def fake_process_text(text, mode):
    if mode == 'retrieve':
      return None
    return {"success": True}

  def fake_ask_gemini(context, text):
    return expected_answer

  def fake_insert_chat(chat_id_param, role, message):
    return {"success": True}

  monkeypatch.setattr("app.process_text", fake_process_text)
  monkeypatch.setattr("app.ask_gemini", fake_ask_gemini)
  monkeypatch.setattr("app.insert_chat", fake_insert_chat)

  body = {
    "message": {
      "chat": {"id": chat_id},
      "text": user_question
    }
  }
  response = post_webhook(body)
  
  assert response.status_code == 200
  assert any(expected_answer in msg for _, msg in sent_msgs), f"Messages: {sent_msgs}"

def test_telegram_webhook_insert_with_unknown_error(monkeypatch, sent_msgs):
  chat_id = 9997
  
  def fake_process_text(new_knowledge, mode):
    return {"success": False}

  monkeypatch.setattr("app.process_text", fake_process_text)
  app.ADMIN_SESSIONS[chat_id] = True

  body = {
    "message": {
      "chat": {"id": chat_id},
      "text": "/insert ini adalah pengetahuan yang cukup panjang untuk validasi minimal"
    }
  }
  response = post_webhook(body)
  assert response.status_code == 200
  assert any("Gagal menambahkan knowledge" in msg for _, msg in sent_msgs), f"Messages: {sent_msgs}"
  assert any("Unknown error" in msg for _, msg in sent_msgs), f"Messages: {sent_msgs}"