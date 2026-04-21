import contextlib
import os
import subprocess
import sys
from pathlib import Path

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "playwright"]) # noqa: S603
    subprocess.check_call([sys.executable, "-m", "playwright", "install"]) # noqa: S603
    from playwright.sync_api import sync_playwright

try:
    import google.generativeai as genai
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "google-generativeai"]) # noqa: S603
    import google.generativeai as genai

def generate_doc(url: str, output_file: str) -> None:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        with contextlib.suppress(Exception):
            page.goto(url, wait_until="networkidle", timeout=15000)

        page.wait_for_timeout(3000) # Give it time to render JS

        html_content = page.content()
        screenshot_bytes = page.screenshot()
        browser.close()

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        placeholder = """# Japan Stock Anomaly Analyzer - 使い方ガイド

こんにちは！このアプリは、日本の株式市場における「アノマリー（経験則）」を簡単に分析できるツールです。
初心者の方でもすぐに使えるように、画面の使い方をステップバイステップで説明します。

## 画面の構成

画面左側には設定項目が、右側には分析結果が表示されます。

## 利用手順

### ステップ 1: 分析したい銘柄の入力
左側の「**Add Tickers**」の下にある入力欄に、分析したい銘柄の証券コードを入力します。
*   例：`6599`, `7713` のようにカンマ区切りで複数入力できます。

### ステップ 2: データの取得
入力欄の横にある「**Fetch**」ボタンをクリックします。
*   すると、システムがデータを取得し始めます。少しお待ちください。
*   取得が完了すると、「Target Tickers」に選択可能な銘柄が表示されます。

### ステップ 3: 分析条件の設定
データの準備ができたら、分析の条件を設定します。

*   **Anomaly Type (アノマリーの種類):** ドロップダウンから分析したいアノマリー（例：day_of_week）を選びます。
*   **Trade Duration (取引期間):** 取引の期間（例：daily）を選びます。
*   **Slippage (スリッページ):** スライダーを動かして、実際の取引で発生する可能性のあるコスト（ズレ）を設定します（初期値は0.1%です）。

### ステップ 4: 分析の開始
設定が完了したら、一番下の「**START ANALYSIS**」ボタンをクリックします！

### ステップ 5: 結果の確認
分析が完了すると、画面の右側に結果が表示されます。

*   **Chart:** 資産の推移などがグラフで表示されます。
*   **Backtest Results:** バックテスト（過去データでの検証）の結果が表示されます。
*   **Statistical Significance:** 統計的な有意性（その結果が偶然ではないかどうか）が表示されます。

---
最初は難しいかもしれませんが、色々な銘柄や条件を試して、アノマリー分析を楽しんでみてください！
"""
        with Path(output_file).open("w") as f:
            f.write(placeholder)
        return

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-pro-latest') # using pro for better reasoning

    prompt = "この画面のスクリーンショットとHTML構造です。この画面の利用手順を初心者向けのREADME形式でMarkdownとして出力してください。"

    try:
        response = model.generate_content([
            prompt,
            {"mime_type": "image/png", "data": screenshot_bytes},
            f"HTML Structure:\n{html_content[:15000]}" # Avoid token limit while giving structure
        ])

        with Path(output_file).open("w") as f:
            f.write(response.text)
    except Exception as e:
        print(f"Failed to generate doc: {e}") # noqa: T201

if __name__ == "__main__":
    url = "http://localhost:3000"
    if len(sys.argv) > 1:
        url = sys.argv[1]

    output_file = "GENERATED_USAGE.md"
    if len(sys.argv) > 2:
        output_file = sys.argv[2]

    generate_doc(url, output_file)
