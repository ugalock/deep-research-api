# Deep Research

Perform iterative research on any topic using Firecrawl for web scraping and OpenAI for LLM-driven query generation.

## Key Features
- Generates targeted SERP queries based on goals and previous learnings
- Recursively researches a topic with configurable breadth/depth
- Gathers insights, follow-up questions, and compiles a final Markdown report
- Uses asyncio for parallel search handling and Rich for CLI progress

## Requirements
- **Python** 3.12+
- **OpenAI** API key in `.env` (`OPENAI_KEY`)
- **Firecrawl** API key in `.env` (`FIRECRAWL_KEY`)

## Installation
1. Clone this repo.
2. Copy `.env.example` to `.env` and insert valid API keys.
3. `pip install -r requirements.txt`.

## Usage
1. `python src/run.py`
2. Answer prompts for your research topic, breadth, and depth.
3. The app saves the final report to `output.md`.

## Testing
- `pytest` runs unit and integration tests.

## Docker
1. Build with `docker build -t deep-research .`
2. Run with `docker-compose up`

Enjoy deep research!