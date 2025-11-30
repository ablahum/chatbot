import pytest
from utils.processes import chunk_text, embed_chunked, process_text

@pytest.mark.parametrize(
    "text, expected_type, exception",
    [
      ("Kucing adalah hewan peliharaan yang lucu.", list, False),
      ("", list, False),
      ("Kucing adalah hewan peliharaan. Sering dijumpai di rumah.", list, False),
      ("Anjing adalah hewan penjaga rumah.", list, False),
      ("Ikan hidup di air.", list, False),
      (None, dict, True),
    ]
)
def test_chunk_text(text, expected_type, exception):
    result = chunk_text(text)

    assert isinstance(result, expected_type)
    if exception:
      assert result == {
        "success": False,
        "error": result.get("error"),
        "result": []
      }
      assert isinstance(result["error"], str) and result["error"]
    elif isinstance(result, list):
      for chunk in result:
        assert isinstance(chunk, str)
        assert len(chunk) > 0

@pytest.mark.parametrize(
  "text, mode, expected_type, exception",
  [
    ("Kucing adalah hewan.", "retrieve", list, False),
    (["Kucing adalah hewan.", "Anjing adalah hewan."], "insert", list, False),
    (None, "retrieve", dict, True),
  ]
)
def test_embed_chunked(text, mode, expected_type, exception):
  result = embed_chunked(text, mode)

  assert isinstance(result, expected_type)
  if not exception:
    if mode == "retrieve":
      assert all(isinstance(v, (float, int)) for v in result)
    elif mode == "insert":
      assert all(isinstance(chunk, list) and all(isinstance(v, (float, int)) for v in chunk) for chunk in result)
  else:
    assert result.get("success") is False
    assert "error" in result and result["error"]
    assert "result" in result

@pytest.mark.parametrize(
  "text, mode, expect_types, is_error, err_msg",
  [
    ("Apa itu kucing?", "retrieve", (dict, list), False, None),
    ("Pengetahuan baru tentang kucing.", "insert", (dict, list), False, None),
    ("Uji", "something_invalid", dict, True, "Unknown"),
    (None, "retrieve", dict, True, "error"),
  ]
)
def test_process_text(text, mode, expect_types, is_error, err_msg):
    result = process_text(text, mode)

    if isinstance(expect_types, tuple):
        assert type(result) in expect_types
    else:
        assert isinstance(result, expect_types)
    
    if is_error:
        assert isinstance(result, dict)
        assert result.get("success") is False
        assert err_msg in result["error"]