import pytest
from unittest.mock import patch
from deep_research import deep_research

@pytest.mark.asyncio
@patch("deep_research.generate_serp_queries")
@patch("deep_research.process_serp_result")
async def test_deep_research_integration(mock_process_serp, mock_generate_serp_queries):
    # Mock generate_serp_queries to return one SERP query
    mock_generate_serp_queries.return_value = [
        {"query": "test query", "researchGoal": "test goal"}
    ]
    # Mock process_serp_result to return dummy learnings
    mock_process_serp.return_value = {
        "learnings": ["Mock learning"],
        "followUpQuestions": ["Mock follow-up question"]
    }

    result = await deep_research(
        query="Initial test query",
        breadth=1,
        depth=1,
    )
    # We expect one round of SERP queries
    mock_generate_serp_queries.assert_called_once()
    mock_process_serp.assert_called_once()
    assert "learnings" in result
    assert result["learnings"] == ["Mock learning"]
    assert "visited_urls" in result
    assert result["visited_urls"] == []
