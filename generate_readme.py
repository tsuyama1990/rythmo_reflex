import sys
import base64
import os
import subprocess

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "playwright"])
    subprocess.check_call([sys.executable, "-m", "playwright", "install"])
    from playwright.sync_api import sync_playwright

try:
    import google.generativeai as genai
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "google-generativeai"])
    import google.generativeai as genai

def capture_page():
    print("Capturing page using Playwright...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        # Navigate to the local reflex app
        page.goto("http://localhost:3000", wait_until="networkidle")
        page.wait_for_timeout(3000) # Ensure charts/components load if necessary

        html_content = page.content()
        screenshot_bytes = page.screenshot(full_page=True)

        browser.close()
        return html_content, screenshot_bytes

def generate_markdown(html_content, screenshot_bytes):
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Warning: GEMINI_API_KEY not found in environment variables.")
        print("Falling back to a mock generation to demonstrate functionality.")
        return fallback_markdown(html_content, screenshot_bytes)

    print("Sending data to Gemini API...")
    genai.configure(api_key=api_key)

    # Use gemini-1.5-flash as it supports image inputs
    model = genai.GenerativeModel('gemini-1.5-flash')

    # We pass the image directly as a dictionary as expected by the python SDK
    prompt = "この画面の利用手順を初心者向けのREADME形式でMarkdownとして出力して"
    image_part = {
        "mime_type": "image/png",
        "data": screenshot_bytes
    }

    # Truncate HTML slightly if it's too large, though Gemini 1.5 has a large context
    truncated_html = html_content[:50000]

    response = model.generate_content([
        prompt,
        image_part,
        f"HTML Structure reference:\n{truncated_html}"
    ])

    return response.text

def fallback_markdown(html_content, screenshot_bytes):
    # This acts as a mock output if the user runs the script without an API key
    return f"""# Japan Stock Anomaly Analyzer - 使い方ガイド

こんにちは！このアプリは、日本の株式市場における「アノマリー（経験則）」を簡単に分析できるツールです。
初心者の方でもすぐに使えるように、画面の使い方をステップバイステップで説明します。

## 画面の構成

画面左側には設定項目が、右側には分析結果が表示されます。

## 利用手順

### ステップ 1: 分析したい銘柄の入力
左側の「**Add Tickers:**」の下にある入力欄に、分析したい銘柄の証券コードを入力します。
*   例：`6599`, `7713` のようにカンマ区切りで複数入力できます。

### ステップ 2: データの取得
入力欄の横にある「**Fetch**」ボタンをクリックします。
*   すると、システムがデータを取得し始めます。少しお待ちください。
*   取得が完了すると、「**Target Tickers:**」の下に選択可能な銘柄が表示されます（チェックボックスで選択可能です）。

### ステップ 3: 分析条件の設定
データの準備ができたら、分析の条件を設定します。

*   **Anomaly Type:** ドロップダウンから分析したいアノマリー（例：day_of_week）を選びます。
*   **Trade Duration:** 取引の期間（例：daily）を選びます。
*   **Slippage:** スライダーを動かして、実際の取引で発生する可能性のあるコスト（ズレ）を設定します（初期値は0.1%です）。

### ステップ 4: 分析の開始
設定が完了したら、一番下の「**START ANALYSIS**」ボタンをクリックします！

### ステップ 5: 結果の確認
分析が完了すると、画面の右側に結果が表示されます。

*   **Status Info:** 分析に利用可能なデータ期間などが表示されます。
*   **Chart:** 資産の推移などがグラフで表示されます（初期状態では "No chart data available. Run analysis first." と表示されています）。
*   **Backtest Results:** バックテスト（過去データでの検証）の結果が表示されます。
*   **Statistical Significance:** 統計的な有意性（その結果が偶然ではないかどうか）が表示されます。

---
最初は難しいかもしれませんが、色々な銘柄や条件を試して、アノマリー分析を楽しんでみてください！

*(Note: Generated via fallback mock since no GEMINI_API_KEY was provided)*
"""

def main():
    try:
        html_content, screenshot_bytes = capture_page()

        md_output = generate_markdown(html_content, screenshot_bytes)

        with open("OUTPUT_README.md", "w", encoding="utf-8") as f:
            f.write(md_output)

        print("Generated OUTPUT_README.md successfully.")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
