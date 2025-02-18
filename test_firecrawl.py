import os
from src.ai.providers import firecrawl_search, FIRECRAWL_BASE_URL, FIRECRAWL_KEY
from firecrawl import FirecrawlApp

def test_simple_search():
    print("\nTesting Firecrawl Search...")
    print("---------------------------")
    print(f"Base URL: {FIRECRAWL_BASE_URL}")
    print(f"API Key present: {'Yes' if FIRECRAWL_KEY else 'No'}")
    
    # Try different endpoint variations
    endpoints = [
        "https://api.firecrawl.dev",
        "https://api.firecrawl.dev/v1",
        "https://api.firecrawl.dev/search",
        "https://api.firecrawl.dev/v1/search"
    ]
    
    for endpoint in endpoints:
        print(f"\nTrying endpoint: {endpoint}")
        try:
            # Create a new client for each test
            app = FirecrawlApp(api_key=FIRECRAWL_KEY, api_url=endpoint)
            
            # Try a direct API call first
            print("Making direct API call...")
            result = app.search(
                "test query",
                params={
                    "limit": 1,
                    "timeout": 5000
                }
            )
            print(f"Direct API call result: {result}")
            
            # Try through our wrapper
            print("\nTrying through wrapper function...")
            result = firecrawl_search(
                query="latest cancer research",
                limit=1,
                timeout=5000
            )
            
            if result.get("data"):
                print("Success! Found results.")
                break
            else:
                print("No results found")
                
        except Exception as e:
            print(f"Error with endpoint {endpoint}: {str(e)}")
            print(f"Error type: {type(e)}")
            continue

if __name__ == "__main__":
    test_simple_search() 