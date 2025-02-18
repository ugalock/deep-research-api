# Deep Research

**Note:** This project started as a port of [@dzhng/deep-research](https://github.com/dzhng/deep-research).

Perform iterative research on any topic using Firecrawl for web scraping and OpenAI for LLM-driven query generation.

## Requirements
- **Python** 3.12 (Tested on Python 3.12; compatibility with other versions is not guaranteed)
- **OpenAI** API key in `.env` (`OPENAI_KEY`)
- **Firecrawl** API key in `.env` (`FIRECRAWL_KEY`)
- **OPENAI_MODEL** (optional): Specifies the OpenAI model to be used for AI-powered functionalities. Defaults to `o3-mini`.

## Virtual Environment Setup

It is recommended to use a Python virtual environment to isolate project dependencies. To set one up, run:

```bash
python -m venv venv
source venv/bin/activate
```

Then proceed with the installation steps below.

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