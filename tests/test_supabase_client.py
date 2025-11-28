import unittest
from unittest.mock import patch, MagicMock
from utils.supabase_client import insert_chat, insert_knowledge, search_knowledge, Role

class TestInsertChat(unittest.TestCase):
  @patch("utils.supabase_client.supabase")
  def test_insert_chat_success(self, mock_supabase):
    chat_id = 123456
    role = Role.USER
    message = "Hello, world!"
    mock_response = MagicMock()
    mock_response.error = None
    mock_supabase.table.return_value.insert.return_value.execute.return_value = mock_response

    result = insert_chat(chat_id, role, message)
    self.assertTrue(result["success"])
    self.assertEqual(result["message"], "Chat successfully inserted.")

    mock_supabase.table.assert_called_with('chat_history')
    mock_supabase.table.return_value.insert.assert_called_once_with({
      "chat_id": chat_id,
      "role": role.value,
      "message": message
    })
    mock_supabase.table.return_value.insert.return_value.execute.assert_called_once()

  @patch("utils.supabase_client.supabase")
  def test_insert_chat_db_error(self, mock_supabase):
    chat_id = 456789
    role = Role.BOT
    message = "Bot says hi!"
    mock_response = MagicMock()
    mock_response.error = "DB Connection Error"
    mock_supabase.table.return_value.insert.return_value.execute.return_value = mock_response

    result = insert_chat(chat_id, role, message)
    self.assertFalse(result["success"])
    self.assertIn("DB Connection Error", result["error"])

  @patch("utils.supabase_client.supabase")
  def test_insert_chat_exception(self, mock_supabase):
    chat_id = 999999
    role = Role.BOT
    message = "Oops!"
    mock_supabase.table.return_value.insert.return_value.execute.side_effect = Exception("Unexpected Failure")

    result = insert_chat(chat_id, role, message)
    self.assertFalse(result["success"])
    self.assertIn("Unexpected Failure", result["error"])

class TestInsertKnowledge(unittest.TestCase):
  @patch("utils.supabase_client.supabase")
  def test_insert_knowledge_success(self, mock_supabase):
    chunked = ["chunk 1", "chunk 2"]
    embedded = [[0.1, 0.2], [0.3, 0.4]]
    mock_response = MagicMock()
    mock_response.error = None
    mock_supabase.table.return_value.insert.return_value.execute.return_value = mock_response

    result = insert_knowledge(chunked, embedded)
    self.assertTrue(result["success"])
    self.assertEqual(result["message"], "Knowledge successfully inserted.")

    expected_data = [
      {"content": chunked[0], "embedding": embedded[0]},
      {"content": chunked[1], "embedding": embedded[1]}
    ]
    mock_supabase.table.assert_called_with("knowledge_base")
    mock_supabase.table.return_value.insert.assert_called_once_with(expected_data)
    mock_supabase.table.return_value.insert.return_value.execute.assert_called_once()

  @patch("utils.supabase_client.supabase")
  def test_insert_knowledge_db_error(self, mock_supabase):
    chunked = ["chunk"]
    embedded = [[0.11, 0.22]]
    mock_response = MagicMock()
    mock_response.error = "Supabase Error"
    mock_supabase.table.return_value.insert.return_value.execute.return_value = mock_response

    result = insert_knowledge(chunked, embedded)
    self.assertFalse(result["success"])
    self.assertIn("Supabase Error", result["error"])

  @patch("utils.supabase_client.supabase")
  def test_insert_knowledge_exception(self, mock_supabase):
    chunked = ["fail"]
    embedded = [[0.99]]
    mock_supabase.table.return_value.insert.return_value.execute.side_effect = Exception("Insert Exception")

    result = insert_knowledge(chunked, embedded)
    self.assertFalse(result["success"])
    self.assertIn("Insert Exception", result["error"])


class TestSearchKnowledge(unittest.TestCase):
  @patch("utils.supabase_client.supabase")
  def test_search_knowledge_success(self, mock_supabase):
    embedded = [0.1, 0.5, 0.9]
    match_count = 3
    mock_response = MagicMock()
    mock_response.data = [
      {"id": 1, "content": "A", "score": 0.92},
      {"id": 2, "content": "B", "score": 0.87},
      {"id": 3, "content": "C", "score": 0.77},
    ]
    mock_supabase.rpc.return_value.execute.return_value = mock_response

    result = search_knowledge(embedded, match_count)

    mock_supabase.rpc.assert_called_once_with("match_documents", {
      "query_embedding": embedded,
      "match_count": match_count
    })
    mock_supabase.rpc.return_value.execute.assert_called_once()
    self.assertEqual(result, mock_response.data)

  @patch("utils.supabase_client.supabase")
  def test_search_knowledge_exception(self, mock_supabase):
    embedded = [1, 2, 3]
    match_count = 2
    mock_supabase.rpc.return_value.execute.side_effect = Exception("RPC Error!")

    from utils.supabase_client import search_knowledge
    result = search_knowledge(embedded, match_count)

    self.assertIsInstance(result, dict)
    self.assertFalse(result["success"])
    self.assertIn("Error occurred while searching", result["error"])
    self.assertIn("RPC Error!", result["error"])

if __name__ == '__main__':
  unittest.main()
