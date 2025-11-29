from fastapi.testclient import TestClient
from app import app
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

  monkeypatch.setattr("utils.processes.process_text", fake_process_text)
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