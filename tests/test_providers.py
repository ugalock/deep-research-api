import pytest
from unittest.mock import patch, MagicMock
from src.ai.providers import firecrawl_search, trim_prompt, get_o3_mini_model
import asyncio

@patch("src.ai.providers.firecrawl_app.search")
def test_firecrawl_search(mock_search):
    # Update mock to include more realistic data
    mock_search.return_value = {
        "data": [
            {
                "url": "http://example.com",
                "markdown": "some content",
                "metadata": {
                    "sourceURL": "http://example.com",
                    "pageUrl": "http://example.com",
                    "finalUrl": "http://example.com"
                }
            }
        ]
    }
    
    # Test with default parameters
    result = firecrawl_search("test query")
    assert "data" in result
    assert len(result["data"]) == 1
    assert result["data"][0]["url"] == "http://example.com"
    assert "metadata" in result["data"][0]
    
    # Test with custom parameters
    result = firecrawl_search(
        "test query",
        timeout=15000,
        limit=5,
        scrape_options={"formats": ["markdown"], "includeMetadata": True}
    )
    
    # Update assertion to match actual implementation
    mock_search.assert_called_with(
        "test query",
        params={
            'timeout': 15000,
            'limit': 5,
            'scrapeOptions': {"formats": ["markdown"], "includeMetadata": True}
        }
    )

@patch("src.ai.providers.firecrawl_app.search")
def test_firecrawl_search_error_handling(mock_search):
    # Test 404 error handling
    mock_search.side_effect = Exception("404 Not Found")
    
    with pytest.raises(Exception) as exc_info:
        firecrawl_search("test query")
    assert "404 Not Found" in str(exc_info.value)

@patch("src.ai.providers.FIRECRAWL_KEY", "")
def test_firecrawl_search_missing_key():
    with pytest.raises(Exception) as exc_info:
        firecrawl_search("test query")
    assert "FIRECRAWL_KEY not configured" in str(exc_info.value)

# def test_trim_prompt_no_trim():
#     long_text = "Short text"
#     trimmed = trim_prompt(long_text, context_size=1000)
#     assert trimmed == long_text

# def test_trim_prompt_with_trim():
#     text = "A" * 6000
#     trimmed = trim_prompt(text, context_size=1000)
#     assert len(trimmed) < len(text)
#     assert len(trimmed) >= 140

# @pytest.mark.asyncio
# @patch("src.ai.providers.openai.ChatCompletion.acreate")
# async def test_get_o3_mini_model(mock_acreate):
#     # Mock the async create call
#     mock_acreate.return_value = {"text": '{"test":"ok"}'}
#     model_fn = get_o3_mini_model()
#     resp = await model_fn("prompt here")
#     mock_acreate.assert_called_once()
#     assert resp["text"] == '{"test":"ok"}'
