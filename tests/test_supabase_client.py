import pytest
from unittest.mock import patch, MagicMock
from utils.supabase_client import insert_chat, insert_knowledge, search_knowledge, Role

@pytest.mark.parametrize(
  "chat_id, role, message, mock_error, exception, expected_success,expected_message",
  [
    (123456, Role.USER, "Hello, world!", None, None, True, "Chat successfully inserted."),
    (456789, Role.BOT, "Bot says hi!", "DB Connection Error", None, False, "DB Connection Error"),
    (999999, Role.BOT, "Oops!", None, Exception("Unexpected Failure"), False, "Unexpected Failure"),
  ]
)
@patch("utils.supabase_client.supabase")
def test_insert_chat(mock_supabase, chat_id, role, message, mock_error, exception, expected_success, expected_message):
  tbl = mock_supabase.table.return_value
  ins = tbl.insert.return_value
  exec_func = ins.execute

  if exception:
    exec_func.side_effect = exception
  else:
    resp = MagicMock()
    resp.error = mock_error
    exec_func.return_value = resp

  result = insert_chat(chat_id, role, message)

  if expected_success:
    assert result["success"] is True
    assert result["message"] == expected_message
    mock_supabase.table.assert_called_once_with("chat_history")
    tbl.insert.assert_called_once_with({
      "chat_id": chat_id, "role": role.value, "message": message
    })
    exec_func.assert_called_once()
  else:
    assert result["success"] is False
    assert expected_message in result["error"]

@pytest.mark.parametrize(
  "chunked,embedded,mock_error,exception,expected_success,expected_msg",
  [
    (["chunk 1", "chunk 2"], [[0.1, 0.2], [0.3, 0.4]], None, None, True, "Knowledge successfully inserted."),
    (["chunk"], [[0.11, 0.22]], "Supabase Error", None, False, "Supabase Error"),
    (["fail"], [[0.99]], None, Exception("Insert Exception"), False, "Insert Exception"),
  ]
)
@patch("utils.supabase_client.supabase")
def test_insert_knowledge(mock_supabase, chunked, embedded, mock_error, exception, expected_success, expected_msg):
  tbl = mock_supabase.table.return_value
  ins = tbl.insert.return_value
  exec_func = ins.execute

  if exception:
    exec_func.side_effect = exception
  else:
    resp = MagicMock()
    resp.error = mock_error
    exec_func.return_value = resp

  result = insert_knowledge(chunked, embedded)

  if expected_success:
    assert result["success"] is True
    assert result["message"] == expected_msg

    expected_data = [{"content": c, "embedding": e} for c, e in zip(chunked, embedded)]
    mock_supabase.table.assert_called_once_with("knowledge_base")
    tbl.insert.assert_called_once_with(expected_data)
    exec_func.assert_called_once()
  else:
    assert result["success"] is False
    assert expected_msg in result["error"]

@pytest.mark.parametrize(
  "embedded,match_count,mock_data,exception,should_success",
  [
    (
      [0.1, 0.5, 0.9], 3,
      [
        {"id": 1, "content": "A", "score": 0.92},
        {"id": 2, "content": "B", "score": 0.87},
        {"id": 3, "content": "C", "score": 0.77},
      ],
      None, True
    ),
    (
      [1, 2, 3], 2,
      None, Exception("RPC Error!"), False
    ),
  ]
)
@patch("utils.supabase_client.supabase")
def test_search_knowledge(mock_supabase, embedded, match_count, mock_data, exception, should_success):
  rpc = mock_supabase.rpc.return_value
  exec_func = rpc.execute

  if exception:
    exec_func.side_effect = exception
  else:
    resp = MagicMock()
    resp.data = mock_data
    exec_func.return_value = resp

  result = search_knowledge(embedded, match_count)

  if should_success:
    mock_supabase.rpc.assert_called_once_with("match_documents", {
      "query_embedding": embedded,
      "match_count": match_count
    })
    exec_func.assert_called_once()
    assert result == mock_data
  else:
    assert isinstance(result, dict)
    assert result["success"] is False
    assert "Error occurred while searching" in result["error"]
    assert "RPC Error!" in result["error"]