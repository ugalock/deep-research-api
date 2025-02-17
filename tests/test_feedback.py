import pytest
from unittest.mock import patch
from feedback import generate_feedback

@pytest.mark.asyncio
@patch("ai.generate_object")
async def test_generate_feedback(mock_generate_object):
    mock_generate_object.return_value = {
        "object": {"questions": ["What is the timeframe?", "Any specific region?"]},
        "raw": {}
    }
    questions = await generate_feedback("Research climate change effects on coral reefs")
    assert len(questions) == 2
    assert "What is the timeframe?" in questions
    mock_generate_object.assert_called_once()
