import json
import base64
import google.generativeai as genai
import os

with open("page_info.json", "r") as f:
    data = json.load(f)

html_content = data["html"]
b64_img = data["image_b64"]
img_data = base64.b64decode(b64_img)

# Set up Gemini
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    print("GEMINI_API_KEY not set")
    exit(1)

genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-flash-latest')

prompt = "この画面の利用手順を初心者向けのREADME形式でMarkdownとして出力して。"

response = model.generate_content([
    prompt,
    {"mime_type": "image/png", "data": img_data},
    f"HTML Structure:\n{html_content[:5000]}" # Truncate HTML to avoid token limits if needed, or pass full
])

print(response.text)
with open("GENERATED_README.md", "w") as f:
    f.write(response.text)
