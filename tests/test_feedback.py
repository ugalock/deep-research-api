import pytest
from unittest.mock import patch
from feedback import generate_feedback

@pytest.mark.asyncio
@patch("ai.ai.generate_object")
async def test_generate_feedback(mock_generate_object):
    # Mock the model response to return 3 questions
    mock_generate_object.return_value = {
        "object": {
            "questions": [
                "Are you focusing on a global perspective of coral reefs or specific geographical regions?",
                "Do you want an emphasis on coral biodiversity shifts and adaptation strategies?",
                "Are you exploring socio-economic impacts on local communities?"
            ]
        },
        "raw": {}
    }

    # If you truly want to test the default num_questions=3:
    questions = await generate_feedback("Research climate change effects on coral reefs")
    assert len(questions) == 3

    # Alternatively, if you want to see it truncated to 2, call generate_feedback with num_questions=2
    # questions = await generate_feedback("Research climate change effects on coral reefs", num_questions=2)
    # assert len(questions) == 2
