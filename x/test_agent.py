import unittest
from unittest.mock import MagicMock, patch
import os
import sys

# Mock google.generativeai before importing modules that use it
mock_genai = MagicMock()
sys.modules["google"] = MagicMock()
sys.modules["google.generativeai"] = mock_genai

import google.generativeai as genai

from x.interviewer import Interviewer
from x.prd_generator import generate_prd
from x.main import main

class TestJTBDInterviewer(unittest.TestCase):
    def setUp(self):
        os.environ["GOOGLE_API_KEY"] = "TEST_KEY"

    @patch('builtins.input', side_effect=["I want a better toaster", "It burns my toast", "I hate burnt toast", "It ruins my morning", "I want to be happy", "exit"])
    def test_interviewer_flow(self, mock_input):
        # Setup mock model
        mock_model = MagicMock()
        mock_chat = MagicMock()
        genai.GenerativeModel.return_value = mock_model
        mock_model.start_chat.return_value = mock_chat
        
        # Simulate responses
        mock_chat.send_message.side_effect = [
            MagicMock(text="Why is that important?"),
            MagicMock(text="Why does that matter?"),
            MagicMock(text="Why is that bad?"), 
            MagicMock(text="Why?"),
            MagicMock(text="Thank you, I have enough information to generate your PRD.")
        ]
        
        interviewer = Interviewer()
        transcript = interviewer.start_interview()
        
        print(f"Transcript generated: {transcript}")
        self.assertIn("User: I want a better toaster", transcript)
        self.assertIn("Agent: Why is that important?", transcript)
        self.assertTrue(len(transcript) > 0)

    def test_prd_generator(self):
        # Setup mock model
        mock_model = MagicMock()
        genai.GenerativeModel.return_value = mock_model
        mock_model.generate_content.return_value = MagicMock(text="# Mock PRD")
        
        transcript = "User: I need X\nAgent: Why?"
        prd = generate_prd(transcript)
        
        self.assertEqual(prd, "# Mock PRD")
        mock_model.generate_content.assert_called_once()

if __name__ == '__main__':
    unittest.main()
