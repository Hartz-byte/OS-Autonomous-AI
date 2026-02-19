from playwright.sync_api import sync_playwright

def browser_search(payload):
    query = payload["query"]

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--disable-dev-shm-usage",
                "--no-sandbox",
                "--disable-gpu",
                "--single-process"
            ]
        )

        page = browser.new_page()
        page.goto(f"https://www.google.com/search?q={query}", timeout=60000)

        page.wait_for_timeout(2000)

        results = page.locator("h3").all_inner_texts()

        browser.close()

        return {"results": results[:5]}
