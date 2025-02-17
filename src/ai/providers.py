import os
from dotenv import load_dotenv
load_dotenv()

import openai
import tiktoken
from firecrawl import FirecrawlApp
from text_splitter import RecursiveCharacterTextSplitter
from typing import Any, Dict, Optional, Callable

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
openai.api_key = OPENAI_KEY
openai.api_base = OPENAI_ENDPOINT

# Initialize Firecrawl client
firecrawl_app = FirecrawlApp(api_key=FIRECRAWL_KEY, api_url=FIRECRAWL_BASE_URL)

MIN_CHUNK_SIZE: int = 140
# Using tiktoken.get_encoding for a fixed encoding as in the TS version ('o200k_base')
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
    if len(trimmed) == len(prompt):
        return trim_prompt(prompt[:chunk_size], context_size)
    return trim_prompt(trimmed, context_size)

def firecrawl_search(query: str, timeout: int = 15000, limit: int = 5, 
                      scrape_options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Search via Firecrawl using default scrape options (markdown)."""
    if scrape_options is None:
        scrape_options = {"formats": ["markdown"]}
    result = firecrawl_app.search(query, params={
        "limit": limit,
        "scrapeOptions": scrape_options,
        "timeout": timeout
    })
    return result

def get_o3_mini_model() -> Callable[..., Any]:
    """
    Returns a callable wrapping OpenAI ChatCompletion.create.
    Adds extra parameters (e.g. reasoning_effort, structured_outputs) if OPENAI_MODEL starts with 'o',
    mirroring the TS configuration.
    """
    extra_params: Dict[str, Any] = {}
    if OPENAI_MODEL.startswith("o"):
        extra_params["reasoning_effort"] = "medium"  # Not officially supported by OpenAI API.
        extra_params["structured_outputs"] = True
    def call_model(prompt: str, **kwargs: Any) -> Any:
        params = {**extra_params, **kwargs}
        response = openai.ChatCompletion.create(
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
