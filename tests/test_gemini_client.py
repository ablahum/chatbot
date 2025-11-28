import unittest
from unittest.mock import patch, MagicMock

from utils.gemini_client import ask_gemini

class TestAskGemini(unittest.TestCase):
    @patch("utils.gemini_client.client")
    def test_ask_gemini_success(self, mock_client):
        mock_answered = MagicMock()
        mock_answered.text = "Ini adalah jawaban dari Gemini."
        mock_client.models.generate_content.return_value = mock_answered

        context = "Pengetahuan tentang hewan"
        text = "Apa itu kucing?"

        result = ask_gemini(context, text)

        mock_client.models.generate_content.assert_called_once()
        self.assertEqual(result, "Ini adalah jawaban dari Gemini.")

    @patch("utils.gemini_client.client")
    def test_ask_gemini_exception(self, mock_client):
        mock_client.models.generate_content.side_effect = Exception("Test error")
        context = "Pengetahuan tentang hewan"
        text = "Apa itu kucing?"

        result = ask_gemini(context, text)

        self.assertIsInstance(result, dict)
        self.assertEqual(result["success"], False)
        self.assertIn("error", result)
        self.assertIn("Test error", result["error"])

if __name__ == "__main__":
    unittest.main()
