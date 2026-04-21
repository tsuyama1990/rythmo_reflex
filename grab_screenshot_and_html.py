import sys
import subprocess

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "playwright"])
    subprocess.check_call([sys.executable, "-m", "playwright", "install"])
    from playwright.sync_api import sync_playwright

import os
import base64
import json

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("http://localhost:3000", wait_until="networkidle")
        page.wait_for_timeout(3000)

        html = page.content()
        screenshot_bytes = page.screenshot()
        b64_img = base64.b64encode(screenshot_bytes).decode('utf-8')

        with open("page_info.json", "w") as f:
            json.dump({"html": html, "image_b64": b64_img}, f)

        browser.close()

if __name__ == "__main__":
    main()
