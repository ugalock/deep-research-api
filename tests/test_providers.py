import pytest
from unittest.mock import patch, MagicMock
from ai.providers import firecrawl_search, trim_prompt, get_o3_mini_model
import asyncio

@patch("ai.providers.firecrawl_app.search")
def test_firecrawl_search(mock_search):
    mock_search.return_value = {"data": [{"url": "http://example.com", "markdown": "some content"}]}
    result = firecrawl_search("test query", timeout=15000, limit=5)
    assert "data" in result
    assert len(result["data"]) == 1
    assert result["data"][0]["url"] == "http://example.com"
    mock_search.assert_called_once()

def test_trim_prompt_no_trim():
    long_text = "Short text"
    trimmed = trim_prompt(long_text, context_size=1000)
    assert trimmed == long_text

def test_trim_prompt_with_trim():
    text = "A" * 200000
    trimmed = trim_prompt(text, context_size=1000)
    assert len(trimmed) < len(text)
    assert len(trimmed) >= 140

@pytest.mark.asyncio
@patch("openai.ChatCompletion.acreate")
async def test_get_o3_mini_model(mock_acreate):
    # Mock the async create call
    mock_acreate.return_value = {"text": '{"test":"ok"}'}
    model_fn = get_o3_mini_model()
    resp = await model_fn("prompt here")
    mock_acreate.assert_called_once()
    assert resp["text"] == '{"test":"ok"}'
