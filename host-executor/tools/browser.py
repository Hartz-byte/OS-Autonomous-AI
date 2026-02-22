import os
import requests
from logger import log

SERP_API_KEY = os.getenv("SERP_API_KEY")

def browser_search(payload):
    query = payload.get("query")
    
    # Check if user specifically asked for news
    is_news_request = any(word in query.lower() for word in ["news", "latest", "breaking", "update"])

    try:
        params = {
            "engine": "google",
            "q": query,
            "api_key": SERP_API_KEY,
            "num": 8
        }

        # If it's a news request, add tbm=nws
        if is_news_request:
            params["tbm"] = "nws"

        response = requests.get("https://serpapi.com/search", params=params, timeout=20)
        data = response.json()

        results = []

        # Try to get news results if requested
        if is_news_request:
            news = data.get("news_results", [])
            for item in news[:5]:
                results.append(f"{item.get('title')} - {item.get('link')}")

        # Always fallback or add organic results
        organic = data.get("organic_results", [])
        for item in organic[:5]:
            # Avoid duplicates if news was already added
            title_link = f"{item.get('title')} - {item.get('link')}"
            if title_link not in results:
                results.append(title_link)

        log(f"browser_search query={query} results={results}")
        return {"results": results}

    except Exception as e:
        log(f"browser_search ERROR: {str(e)}")
        return {"error": str(e)}
