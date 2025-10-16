import os
from openai import OpenAI
from jinja2 import Template  # テンプレ埋め込み用（pip install jinja2）
from dotenv import load_dotenv  # pip install python-dotenv

# APIキー読み込み
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# --- 1️⃣ プロンプトを受け取る ---
prompt = input("スライドのテーマや構成を指示してください：\n")

# --- 2️⃣ GPTにスライド内容を生成させる ---
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "あなたはスライド構成のプロです。"},
        {"role": "user", "content": f"""
        次の指示に基づいてHTMLスライド用のコンテンツを生成してください。
        出力はJSON形式で、各スライドに title と body を含めてください。

        指示：{prompt}
        """}
    ]
)

# --- 3️⃣ GPTの出力を解析 ---
import json

raw_output = response.choices[0].message.content.strip()

try:
    # GPTの返したコードブロック（```json ... ```）を除去
    if raw_output.startswith("```"):
        raw_output = raw_output.strip("`").replace("json", "").strip()

    data = json.loads(raw_output)

    # 「slides」キーで包まれている場合の対応
    if isinstance(data, dict) and "slides" in data:
        slides = data["slides"]
    else:
        slides = data

except json.JSONDecodeError:
    print("⚠️ JSONの読み取りに失敗しました。出力内容を確認します：")
    print(raw_output)
    exit()

# --- 4️⃣ HTMLテンプレートを読み込み ---
with open("template.html", "r", encoding="utf-8") as f:
    html_template = f.read()

template = Template(html_template)
rendered_html = template.render(slides=slides)

# --- 5️⃣ テンプレートにスライドを挿入 ---
template = Template(html_template)
rendered_html = template.render(slides=slides)

# --- 6️⃣ 出力ファイル保存 ---
with open("output.html", "w", encoding="utf-8") as f:
    f.write(rendered_html)

print("✅ output.html を生成しました！")