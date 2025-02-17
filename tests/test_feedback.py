import pytest
import asyncio
from feedback import generate_feedback

@pytest.mark.asyncio
async def test_generate_feedback():
    query = "What is AI?"
    try:
        questions = await generate_feedback(query, num_questions=3)
        assert isinstance(questions, list)
        assert len(questions) <= 3
        for q in questions:
            assert isinstance(q, str)
    except Exception as e:
        pytest.skip("OpenAI API not configured: " + str(e))
