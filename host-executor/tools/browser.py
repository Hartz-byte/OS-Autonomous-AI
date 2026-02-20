import os
import requests
from logger import log

SERP_API_KEY = os.getenv("SERP_API_KEY", "")

def browser_search(payload):
    query = payload.get("query")

    try:
        url = "https://serpapi.com/search"
        params = {
            "q": query,
            "api_key": SERP_API_KEY,
            "engine": "google",
            "num": 5
        }

        response = requests.get(url, params=params, timeout=20)
        data = response.json()

        results = []

        for item in data.get("organic_results", [])[:5]:
            results.append(
                f"{item.get('title')} - {item.get('link')}"
            )

        log(f"browser_search query={query} results={results}")

        return {"results": results}

    except Exception as e:
        log(f"browser_search ERROR: {str(e)}")
        return {"error": str(e)}
