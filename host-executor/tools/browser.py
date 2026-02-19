from playwright.sync_api import sync_playwright

def browser_search(payload):
    query = payload["query"]
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(f"https://www.google.com/search?q={query}")
        results = page.locator("h3").all_inner_texts()
        browser.close()
        return {"results": results[:5]}
