# ランダムWikipedia（randomwikipedia）

ボタンを押すと、日本語版 Wikipedia の記事をランダムで1件表示する小さなツールです。

## 使い方

- **🎲 ランダムで記事を表示**：日本語版 Wikipedia からランダムな記事を1件取得し、タイトル・概要・サムネイル（あれば）を表示します。
- **記事を読む**：その記事の Wikipedia ページを新しいタブで開きます。
- もう一度ボタンを押すと、別の記事が表示されます。

記事の取得はサーバー側で行います（Wikipedia REST API の `https://ja.wikipedia.org/api/rest_v1/page/random/summary` を使用）。通信に失敗した場合はエラーメッセージと再試行ボタンが表示されます。

## ローカル実行

```bash
pip install -r requirements.txt
python app.py
# http://localhost:5000
```

## テスト

```bash
python -m unittest discover -s tests
```

※ テストでは外部通信を行わず、取得処理をモックに差し替えて検証します。

## Render へのデプロイ

`render.yaml` 同梱。無料プラン（free）の Web Service としてデプロイできます（healthCheckPath: `/healthz`）。
