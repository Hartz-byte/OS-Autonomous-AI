import os
import requests
from logger import log

SERP_API_KEY = os.getenv("SERP_API_KEY")

def browser_search(payload):
    query = payload.get("query")

    log(f"SERP_API_KEY: {SERP_API_KEY}")

    try:
        # First try NEWS mode
        params = {
            "engine": "google",
            "q": query,
            "api_key": SERP_API_KEY,
            "tbm": "nws",
            "num": 5
        }

        response = requests.get("https://serpapi.com/search", params=params, timeout=20)
        data = response.json()

        results = []

        news = data.get("news_results", [])
        if news:
            for item in news[:5]:
                results.append(
                    f"{item.get('title')} - {item.get('link')}"
                )

        # Fallback to organic if empty
        if not results:
            params.pop("tbm")
            response = requests.get("https://serpapi.com/search", params=params, timeout=20)
            data = response.json()

            for item in data.get("organic_results", [])[:5]:
                results.append(
                    f"{item.get('title')} - {item.get('link')}"
                )

        log(f"browser_search query={query} results={results}")

        return {"results": results}

    except Exception as e:
        log(f"browser_search ERROR: {str(e)}")
        return {"error": str(e)}
