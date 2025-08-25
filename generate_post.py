import os, openai, datetime, json

api_key = os.environ.get("OPENAI_API_KEY")
if not api_key:
    print("ERROR: No OpenAI API key found.")
    exit(1)

openai.api_key = api_key
today_date = datetime.date.today().strftime("%Y-%m-%d")
today_display = datetime.date.today().strftime("%A, %B %d, %Y")
topic = os.getenv("INPUT_TOPIC", "trending AI topic")

print(f"Generating post for {today_display} (filename: {today_date})")

meta_prompt = f"Generate a catchy blog title and a 2-sentence summary for {topic} as of {today_display}. Respond in JSON with keys: title, summary."
try:
    resp = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": meta_prompt}],
        max_tokens=200,
        response_format={"type": "json_object"}
    )
    raw = resp.choices[0].message.content.strip()
    meta = json.loads(raw)
    print(f"Generated meta: {meta}")
except Exception as e:
    print("Meta generation failed:", e)
    meta = {"title": f"Weekly Blog Post - {today_display}", "summary": "Fallback summary."}

title = meta.get("title")
summary = meta.get("summary")

article_prompt = f"Write a 600-word blog article titled '{title}' for {today_display}. Use proper HTML formatting with <h2> tags for subheadings, <p> tags for paragraphs. Do not include <html>, <head>, or <body> tags - just the content."
try:
    resp2 = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": article_prompt}],
        max_tokens=1000,
    )
    article_text = resp2.choices[0].message.content
    print("Article generated successfully")
except Exception as e:
    print("Article generation failed:", e)
    article_text = "<p>Fallback: No article generated.</p>"

html = f"""<!DOCTYPE html>
<html>
<head>
    <title>{title}</title>
    <style>
        body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }}
        h1 {{ color: #333; }}
        h2 {{ color: #666; border-bottom: 1px solid #eee; padding-bottom: 10px; }}
        p {{ line-height: 1.6; }}
    </style>
</head>
<body>
<h1>{title}</h1>
<p><em>{summary}</em></p>
<div>{article_text}</div>
</body></html>"""

os.makedirs("posts", exist_ok=True)
filename = f"posts/post-{today_date}.html"
with open(filename, "w") as f:
    f.write(html)
print(f"Article saved as: {filename}")

with open("post_meta.json", "w") as f:
    json.dump({"title": title, "summary": summary}, f)
print("Metadata saved")
