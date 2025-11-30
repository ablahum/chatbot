import pytest
from unittest.mock import patch
from utils.telegram_client import sent_message

@pytest.mark.parametrize(
  "chat_id, text, status_code, response_json",
  [
    (
      123456789,
      "Hello, Telegram!",
      200,
      {
        "ok": True,
        "result": {"message_id": 1}
      }
    ),
    (
      123456789,
      "Halo",
      400,
      {
        "ok": False,
        "error_code": 400,
        "description": "Bad Request: chat not found"
      }
    ),
  ]
)
@patch("utils.telegram_client.requests.post")
def test_sent_message(mock_post, chat_id, text, status_code, response_json):
  mock_response = mock_post.return_value
  mock_response.status_code = status_code
  mock_response.json.return_value = response_json

  sent_message(chat_id, text)
  
  mock_post.assert_called_once()
  called_url = mock_post.call_args[0][0]
  called_payload = mock_post.call_args[1]['json']
  assert "/sendMessage" in called_url
  assert called_payload["chat_id"] == chat_id
  assert called_payload["text"] == text

