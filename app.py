"""ランダムWikipedia（randomwikipedia）

ボタンを押すと、日本語版 Wikipedia からランダムで記事を1件表示するツール。
記事の取得はサーバー側で行い、Wikipedia REST API
（/api/rest_v1/page/random/summary）を使う。単一ファイル Flask。
"""
import json
import os
import urllib.request

from flask import Flask, jsonify, render_template_string

app = Flask(__name__)

RANDOM_SUMMARY_URL = "https://ja.wikipedia.org/api/rest_v1/page/random/summary"
USER_AGENT = "randomwikipedia/1.0 (personal hobby tool; Flask)"
FETCH_TIMEOUT = 10


def fetch_random_article():
    """Wikipedia からランダムな記事を1件取得して dict で返す。

    取得できない場合は例外を送出する（呼び出し側でエラー表示にする）。
    """
    req = urllib.request.Request(
        RANDOM_SUMMARY_URL,
        headers={"User-Agent": USER_AGENT, "Accept": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=FETCH_TIMEOUT) as res:
        data = json.loads(res.read().decode("utf-8"))
    title = (data.get("title") or "").strip()
    url = (
        (data.get("content_urls") or {}).get("desktop") or {}
    ).get("page") or ""
    if not title or not url:
        raise ValueError("unexpected API response")
    thumbnail = (data.get("thumbnail") or {}).get("source") or ""
    return {
        "title": title,
        "description": (data.get("description") or "").strip(),
        "extract": (data.get("extract") or "").strip(),
        "thumbnail": thumbnail,
        "url": url,
    }


PAGE = """<!doctype html>
<html lang="ja"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>ランダムWikipedia</title>
<style>
body{font-family:sans-serif;max-width:680px;margin:2em auto;padding:0 1em;color:#222}
h1{font-size:1.5em}
.bigbtn{display:inline-block;font-size:1.15em;padding:.7em 1.6em;margin:.6em 0;
background:#36c;color:#fff;border:none;border-radius:8px;cursor:pointer}
.bigbtn:hover{background:#2a4f9e}
.card{border:1px solid #ccc;border-radius:10px;padding:1em 1.2em;margin-top:1em}
.card img{max-width:220px;max-height:220px;border-radius:6px;float:right;margin:0 0 .6em 1em}
.desc{color:#555;font-size:.9em;margin:.2em 0 .6em}
.extract{line-height:1.7;white-space:pre-wrap}
.error{border:1px solid #d66;background:#fff3f3;border-radius:10px;padding:1em 1.2em;margin-top:1em}
a.read{font-weight:bold}
footer{margin-top:2em;color:#777;font-size:.85em}
</style>
</head><body>
<h1>📚 ランダムWikipedia</h1>
<p>ボタンを押すと、日本語版 Wikipedia の記事をランダムで1件表示します。思いがけない記事との出会いをどうぞ。</p>
<form method="get" action="/random">
  <button type="submit" class="bigbtn">🎲 ランダムで記事を表示</button>
</form>
{% if article %}
<div class="card">
  {% if article.thumbnail %}<img src="{{ article.thumbnail }}" alt="">{% endif %}
  <h2>{{ article.title }}</h2>
  {% if article.description %}<p class="desc">{{ article.description }}</p>{% endif %}
  {% if article.extract %}<p class="extract">{{ article.extract }}</p>{% endif %}
  <p><a class="read" href="{{ article.url }}" target="_blank" rel="noopener">記事を読む →</a></p>
</div>
{% elif error %}
<div class="error">
  <p>⚠️ {{ error }}</p>
  <p>通信がうまくいかなかったようです。もう一度ボタンを押してみてください。</p>
</div>
{% endif %}
<footer>記事データ：<a href="https://ja.wikipedia.org/" target="_blank" rel="noopener">日本語版 Wikipedia</a>（Wikipedia REST API 経由）</footer>
</body></html>
"""


@app.route("/")
def index():
    return render_template_string(PAGE, article=None, error=None)


@app.route("/random")
def random_article():
    try:
        article = fetch_random_article()
    except Exception:
        return render_template_string(
            PAGE, article=None, error="記事を取得できませんでした。"
        )
    return render_template_string(PAGE, article=article, error=None)


@app.route("/healthz")
def healthz():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "5000")))
