import json
import os
from openai import OpenAI
from jinja2 import Environment, FileSystemLoader
from dotenv import load_dotenv

# .envファイルを読み込み
load_dotenv()

# GPTクライアント
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    print("⚠️ OPENAI_API_KEYが設定されていません。")
    print(".envファイルに以下のように設定してください：")
    print("OPENAI_API_KEY=your-api-key-here")
    exit()

client = OpenAI(api_key=api_key)

# ==== CLI入力 ====
print("🧠 スライド自動生成システム：Phase 2")
theme = input("生成したいスライドの内容を入力してください：")
slide_count = input("スライド枚数をおおよそ指定してください（例：5枚程度, 10枚程度）：")
tone = input("テイストを選択してください（例：ビジネス / カジュアル / ナチュラル）：")
text = input("スライドの文章量を生成してください（100文字程度, 200文字程度,・・・）：")

# ==== GPTプロンプト ====
prompt = f"""
あなたはプレゼン資料を設計するAIです。
以下の条件で、スライド構成をJSON形式で出力してください。

---
テーマ: {theme}
スライド枚数: {slide_count}
テイスト（文体・語調）: {tone}
1スライドあたりの本文量: {text}文字程度

type は以下のいずれかを含めてください：
- "title"（表紙）
- "toc"（目次）
- "content"（本文）
- "summary"（まとめ）

出力フォーマット：
{{
  "slides": [
    {{"type": "title", "title": "スライドタイトル", "body": "本文"}},
    ...
  ]
}}

注意：
- 内容に対してスライド枚数が不自然に多い場合は、無理に枚数を合わせず、適切な構成に調整してください。
- 必ず有効なJSON形式で出力してください。
- 各スライドの本文は1スライドあたりの本文量に合わせて生成してください。
"""

# ==== GPT呼び出し ====
print("\n🤖 スライド構成を生成中...")
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "あなたは構成設計が得意な資料作成AIです。"},
        {"role": "user", "content": prompt}
    ],
    temperature=0.7
)

# ==== JSON解析 ====
try:
    slides = json.loads(response.choices[0].message.content)["slides"]
except Exception as e:
    print("⚠️ JSONの解析に失敗しました。出力内容を表示します：")
    print(response.choices[0].message.content)
    exit()

# ==== スライド数制限 ====
if len(slides) > 20:
    print("⚠️ スライドが多すぎるため、20枚までに制限します。")
    slides = slides[:20]

# ==== HTMLレンダリング ====
env = Environment(loader=FileSystemLoader("./templates"))
template = env.get_template("base.html")
rendered = template.render(slides=slides)

# ==== 出力 ====
output_path = "output.html"
with open(output_path, "w", encoding="utf-8") as f:
    f.write(rendered)

print(f"\n✅ スライド生成が完了しました！ → {output_path}")
