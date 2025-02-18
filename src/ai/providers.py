import os
from dotenv import load_dotenv
load_dotenv()

from openai import AsyncOpenAI
import tiktoken
import requests
from langchain.text_splitter import RecursiveCharacterTextSplitter
from typing import Any, Dict, Optional, Callable, Awaitable

# Environment Variables
OPENAI_KEY: str = os.getenv("OPENAI_KEY", "")
OPENAI_ENDPOINT: str = os.getenv("OPENAI_ENDPOINT", "https://api.openai.com/v1")
OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "o3-mini")
CONTEXT_SIZE: int = int(os.getenv("CONTEXT_SIZE", "128000"))
FIRECRAWL_KEY: str = os.getenv("FIRECRAWL_KEY", "")
FIRECRAWL_BASE_URL: str = os.getenv("FIRECRAWL_BASE_URL", "https://api.firecrawl.dev/v1")

if not OPENAI_KEY:
    print("Warning: OPENAI_KEY is not set. Please ensure it is defined in your .env file.")
if not FIRECRAWL_KEY:
    print("Warning: FIRECRAWL_KEY is not set. Please ensure it is defined in your .env file.")

# Configure OpenAI
client = AsyncOpenAI(api_key=OPENAI_KEY, base_url=OPENAI_ENDPOINT)

MIN_CHUNK_SIZE: int = 140
tokenizer = tiktoken.get_encoding("o200k_base")

def trim_prompt(prompt: str, context_size: int = CONTEXT_SIZE) -> str:
    """Trim the prompt recursively to ensure the token count fits within context_size."""
    if not prompt:
        return ""
    token_count = len(tokenizer.encode(prompt))
    if token_count <= context_size:
        return prompt
    overflow_tokens = token_count - context_size
    chunk_size = len(prompt) - (overflow_tokens * 3)
    if chunk_size < MIN_CHUNK_SIZE:
        return prompt[:MIN_CHUNK_SIZE]

    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=0)
    chunks = splitter.split_text(prompt)
    if not chunks:
        return ""
    trimmed = chunks[0]
    # If the chunk is still the same size as the whole prompt, do a direct cut
    if len(trimmed) == len(prompt):
        return trim_prompt(prompt[:chunk_size], context_size)
    return trim_prompt(trimmed, context_size)

def firecrawl_search(query: str, timeout: int = 15000, limit: int = 5,
                     scrape_options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Search via Firecrawl using default scrape options (markdown) by making a direct requests call.
    """
    if not FIRECRAWL_KEY:
        raise Exception("FIRECRAWL_KEY not configured. Please set in .env file.")

    if scrape_options is None:
        scrape_options = {}

    clean_query = query.strip().strip('"')
    if not clean_query:
        raise Exception("Empty query after cleaning")

    print(f"Making Firecrawl request to: {FIRECRAWL_BASE_URL}/search")
    print(f"Query: {clean_query}")

    url = f"{FIRECRAWL_BASE_URL}/search"
    payload = {
        "query": clean_query,
        "limit": limit,
        "timeout": timeout,
        "tbs": "",
        "lang": "en",
        "country": "us",
        "location": "",
        "scrapeOptions": scrape_options
    }
    headers = {
        "Authorization": f"Bearer {FIRECRAWL_KEY}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        result = response.json()
        if result.get("success"):
            return result
        else:
            print(f"Unexpected response format: {result}")
            return {"data": []}
    except Exception as e:
        print(f"Firecrawl error details: {str(e)}")
        print(f"Error type: {type(e)}")
        return {"data": []}

def get_o3_mini_model() -> Callable[..., Awaitable[Dict[str, Any]]]:
    """
    Returns an async callable that calls the OpenAI ChatCompletion endpoint,
    matching the TS approach with 'reasoningEffort' if model starts with 'o'.
    """
    extra_params: Dict[str, Any] = {}
    if OPENAI_MODEL.startswith("o"):
        extra_params["reasoning_effort"] = "medium"

    async def call_model(prompt: str, **kwargs: Any) -> Dict[str, Any]:
        params = {**extra_params, **kwargs}
        response = await client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "You are an expert research assistant."},
                {"role": "user", "content": prompt},
            ],
            **params
        )
        return response

    return call_model

o3MiniModel = get_o3_mini_model()
