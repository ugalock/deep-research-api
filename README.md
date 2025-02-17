# Deep Research - Python Mirror

An AI-powered research assistant that performs iterative, deep research on any topic by combining search engines, web scraping, and large language models.

This repository is a Python mirror of the TypeScript version (deep-research-og). The goal is to replicate the functionality using Python while ensuring consistency in API calls, concurrency, and output formatting.

## Features

- **Iterative Research:** Conducts deep research by recursively generating SERP queries and processing results.
- **Intelligent Query Generation:** Uses LLMs to create targeted search queries based on research goals and previous learnings.
- **Depth & Breadth Control:** Configure research parameters for customized exploration.
- **Smart Follow-up:** Generates follow-up questions to refine research direction.
- **Comprehensive Reports:** Produces detailed Markdown reports with findings and sources.
- **Concurrent Processing:** Utilizes asyncio for parallel processing of queries.
- **Cross-Platform Console Output:** Provides dynamic progress updates in the terminal.

## Requirements

- Python 3.12+
- API keys for:
  - Firecrawl API (for web search and content extraction)
  - OpenAI API (for the o3-mini model)

## Setup

1. Clone the repository.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
