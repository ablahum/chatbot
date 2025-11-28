import unittest
from unittest.mock import patch
from utils.telegram_client import sent_message

class TestSentMessage(unittest.TestCase):
  @patch("utils.telegram_client.requests.post")
  def test_sent_message_success(self, mock_post):
    chat_id = 123456789
    text = "Hello, Telegram!"
    mock_response = mock_post.return_value
    mock_response.status_code = 200
    mock_response.json.return_value = {
      "ok": True,
      "result": {
        "message_id": 1
      }
    }
    
    sent_message(chat_id, text)
    mock_post.assert_called_once()
    called_url = mock_post.call_args[0][0]
    called_payload = mock_post.call_args[1]['json']
    self.assertIn("/sendMessage", called_url)
    self.assertEqual(called_payload["chat_id"], chat_id)
    self.assertEqual(called_payload["text"], text)
  
  @patch("utils.telegram_client.requests.post")
  def test_sent_message_api_failure(self, mock_post):
    chat_id = 123456789
    text = "Halo"
    mock_response = mock_post.return_value
    mock_response.status_code = 400
    mock_response.json.return_value = {
      "ok": False,
      "error_code": 400,
      "description": "Bad Request: chat not found"
    }
    
    sent_message(chat_id, text)
    mock_post.assert_called_once()

if __name__ == "__main__":
  unittest.main()
