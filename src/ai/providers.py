import os
import openai
import tiktoken
from firecrawl import FirecrawlApp
from text_splitter import RecursiveCharacterTextSplitter

# Load environment variables
OPENAI_KEY = os.getenv("OPENAI_KEY", "")
OPENAI_ENDPOINT = os.getenv("OPENAI_ENDPOINT", "https://api.openai.com/v1")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "o3-mini")
CONTEXT_SIZE = int(os.getenv("CONTEXT_SIZE", "128000"))
FIRECRAWL_KEY = os.getenv("FIRECRAWL_KEY", "")
FIRECRAWL_BASE_URL = os.getenv("FIRECRAWL_BASE_URL", "https://api.firecrawl.dev/v1")

# Configure OpenAI
openai.api_key = OPENAI_KEY
openai.api_base = OPENAI_ENDPOINT

MIN_CHUNK_SIZE = 140
tokenizer = tiktoken.get_encoding("o200k_base")

# Initialize Firecrawl client using the current API
firecrawl_app = FirecrawlApp(api_key=FIRECRAWL_KEY, api_url=FIRECRAWL_BASE_URL)

def trim_prompt(prompt: str, context_size: int = CONTEXT_SIZE) -> str:
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

def firecrawl_search(query: str, timeout: int = 15000, limit: int = 5, scrape_options: dict = None) -> dict:
    if scrape_options is None:
        scrape_options = {"formats": ["markdown"]}
    # Call Firecrawl's search endpoint synchronously.
    result = firecrawl_app.search(query, params={
        "limit": limit,
        "scrapeOptions": scrape_options,
        "timeout": timeout
    })
    return result

def get_o3_mini_model():
    def call_model(prompt: str, **kwargs):
        response = openai.ChatCompletion.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "You are an expert research assistant."},
                {"role": "user", "content": prompt},
            ],
            **kwargs
        )
        return response
    return call_model

o3MiniModel = get_o3_mini_model()
