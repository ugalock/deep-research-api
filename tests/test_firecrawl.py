import pytest
from unittest.mock import patch, MagicMock
from ai.providers import firecrawl_search, FIRECRAWL_BASE_URL, FIRECRAWL_KEY

@patch("ai.providers.requests.Session.post")
def test_simple_search(mock_post):
    mock_post.return_value.json.return_value = {
        "success": True,
        "data": [
            {"url": "http://example.com", "markdown": "Example content"}
        ]
    }
    mock_post.return_value.raise_for_status = MagicMock()

    result = firecrawl_search("test query", limit=1, timeout=5000)

    assert "data" in result
    assert len(result["data"]) == 1
    assert result["data"][0]["url"] == "http://example.com"
    assert result["success"] is True
    mock_post.assert_called_once()

@patch("ai.providers.requests.Session.post")
def test_no_results_search(mock_post):
    mock_post.return_value.json.return_value = {
        "success": True,
        "data": []
    }
    mock_post.return_value.raise_for_status = MagicMock()

    result = firecrawl_search("empty results", limit=1, timeout=5000)
    assert "data" in result
    assert len(result["data"]) == 0

@patch("ai.providers.requests.Session.post")
def test_error_handling(mock_post):
    mock_post.side_effect = Exception("Request failed")

    # Our code catches Exception and returns {"data": []}
    result = firecrawl_search("error query", limit=1, timeout=5000)
    assert "data" in result
    assert len(result["data"]) == 0

@patch("ai.providers.FIRECRAWL_KEY", new="")
def test_missing_firecrawl_key_empty():
    # With FIRECRAWL_KEY = "", we expect an Exception
    with pytest.raises(Exception) as exc_info:
        firecrawl_search("test query")
    assert "FIRECRAWL_KEY not configured" in str(exc_info.value)

@patch("ai.providers.FIRECRAWL_KEY", new=None)
def test_missing_firecrawl_key_none():
    # With FIRECRAWL_KEY = None, also expect an Exception
    with pytest.raises(Exception) as exc_info:
        firecrawl_search("test query")
    assert "FIRECRAWL_KEY not configured" in str(exc_info.value)
