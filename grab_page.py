from playwright.sync_api import sync_playwright

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto("http://localhost:3000", wait_until="networkidle")
        # Wait for the app to render
        page.wait_for_timeout(5000)
        html = page.content()
        page.screenshot(path="screenshot.png")
        with open("page.html", "w") as f:
            f.write(html)
        browser.close()

if __name__ == "__main__":
    main()
