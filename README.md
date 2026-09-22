# AIコツ図鑑

生成AI（ChatGPT / Claude / Gemini / Copilot）の「使い方のコツ」を集めた個人用のまとめページです。

- 毎日 朝7時（日本時間）に自動更新されます
- 情報源は `data/sources.json` に一覧があります
- ページ本体は `index.html`（GitHub Pages で公開）

## 構成

| ファイル | 役割 |
|---|---|
| `update_all.py` | これ1本で全部更新 |
| `collect_sources.py` | 指定のYouTube・noteを巡回 |
| `collect_news.py` | ニュースサイトを巡回 |
| `build.py` | 集めたデータから `index.html` を作る |
| `data/tips.json` | コツの本体（手で育てる部分） |
