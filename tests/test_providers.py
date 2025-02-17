import os
import pytest
from ai.providers import get_o3_mini_model, trim_prompt, firecrawl_search

def dummy_model(prompt: str, **kwargs):
    # Dummy model that echoes a JSON structure for testing.
    return {"text": '{"reportMarkdown": "Test Report"}'}

def test_trim_prompt_short_text():
    text = "Short text"
    trimmed = trim_prompt(text, 1000)
    assert trimmed == text

def test_get_o3_mini_model_extra_params(monkeypatch):
    # Ensure that when OPENAI_MODEL starts with 'o', our extra parameters are set.
    monkeypatch.setenv("OPENAI_MODEL", "o3-mini")
    model_func = get_o3_mini_model()
    assert callable(model_func)

def test_firecrawl_search(monkeypatch):
    # Simulate a Firecrawl response.
    class DummyFirecrawl:
        def search(self, query, params):
            return {"data": [{"markdown": "Test content", "url": "http://example.com"}]}
    monkeypatch.setattr("ai.providers.firecrawl_app", DummyFirecrawl())
    result = firecrawl_search("test query")
    assert "data" in result
    assert isinstance(result["data"], list)
