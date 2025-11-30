import pytest
from unittest.mock import patch
from utils.gemini_client import ask_gemini

@pytest.mark.parametrize(
  "context, text, expected, is_error",
  [
    ("Pengetahuan tentang hewan", "Apa itu kucing?", "Ini adalah jawaban dari Gemini.", False),
    ("Pengetahuan tentang hewan", "Apa itu kucing?", "Test error", True),
  ]
)
@patch("utils.gemini_client.client")
def test_ask_gemini(mock_client, context, text, expected, is_error):
  if is_error:
    mock_client.models.generate_content.side_effect = Exception(expected)
    result = ask_gemini(context, text)

    assert isinstance(result, dict)
    assert not result["success"]
    assert expected in result["error"]
  else:
    mock_client.models.generate_content.return_value.text = expected
    result = ask_gemini(context, text)
    
    mock_client.models.generate_content.assert_called_once()
    assert result == expected
