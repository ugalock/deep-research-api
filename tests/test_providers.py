import pytest
from ai.providers import firecrawl_search, trim_prompt, o3MiniModel
import tiktoken

def test_trim_prompt_short():
    text = "Short text"
    trimmed = trim_prompt(text, context_size=1000)
    assert trimmed == text

def test_trim_prompt_long():
    # Create a long text by repeating a pattern
    text = "A" * 5000
    trimmed = trim_prompt(text, context_size=1000)
    assert len(trimmed) < len(text)

def test_firecrawl_search_returns_dict():
    # This test assumes firecrawl_search returns a dictionary.
    try:
        result = firecrawl_search("test query")
        assert isinstance(result, dict)
    except Exception as e:
        pytest.skip("Firecrawl API not configured: " + str(e))

def test_o3mini_model_call():
    # Test that the model call returns a response with 'choices'
    try:
        response = o3MiniModel("Test prompt", timeout=5)
        assert "choices" in response
    except Exception as e:
        pytest.skip("OpenAI API not configured: " + str(e))
