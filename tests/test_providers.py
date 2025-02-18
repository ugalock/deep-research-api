import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from ai.providers import firecrawl_search, trim_prompt, get_o3_mini_model

@patch("ai.providers.requests.Session.post")
def test_firecrawl_search_basic(mock_post):
    mock_post.return_value.json.return_value = {"success": True, "data": [{"url": "http://example.com"}]}
    mock_post.return_value.raise_for_status = MagicMock()

    result = firecrawl_search("some query")
    assert result.get("data") is not None
    assert len(result["data"]) == 1
    assert result["data"][0]["url"] == "http://example.com"

def test_trim_prompt_no_trim():
    text = "Short text"
    trimmed = trim_prompt(text, context_size=1000)
    assert trimmed == text

def test_trim_prompt_with_trim():
    # Use a longer text so that it actually gets trimmed
    text = "A" * 100000
    trimmed = trim_prompt(text, context_size=1000)
    # It should be smaller than original, but not smaller than MIN_CHUNK_SIZE
    assert len(trimmed) < len(text)
    # From code, MIN_CHUNK_SIZE=140
    assert len(trimmed) >= 140

@pytest.mark.asyncio
@patch("ai.providers.client.chat")
async def test_get_o3_mini_model(mock_chat):
    # Mock an async creation call
    mock_chat.completions.create = AsyncMock(return_value={
        "choices": [
            {
                "message": {
                    "content": "Test response"
                }
            }
        ]
    })

    call_model = get_o3_mini_model()
    response = await call_model("prompt here")
    # Check that we get the expected text
    assert response["choices"][0]["message"]["content"] == "Test response"

    mock_chat.completions.create.assert_called_once()
