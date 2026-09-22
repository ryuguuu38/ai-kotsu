# -*- coding: utf-8 -*-
"""ニュース速報を自動収集して data/news.json に貯める（Python標準ライブラリのみ）"""
from __future__ import unicode_literals
import urllib.request, urllib.parse, xml.etree.ElementTree as ET
import json, io, os, re, sys
from datetime import datetime, timedelta
from email.utils import parsedate_to_datetime

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "data", "news.json")
UA = {"User-Agent": "Mozilla/5.0 (Macintosh) AIMatome/1.0"}
ATOM = "{http://www.w3.org/2005/Atom}"

FEEDS = [
    ("Zenn ClaudeCode", "https://zenn.dev/topics/claudecode/feed", "ja"),
    ("Zenn 生成AI", "https://zenn.dev/topics/" + urllib.parse.quote("生成ai") + "/feed", "ja"),
    ("Zenn ChatGPT", "https://zenn.dev/topics/chatgpt/feed", "ja"),
    ("Qiita Claude", "https://qiita.com/tags/claude/feed", "ja"),
    ("Qiita 生成AI", "https://qiita.com/tags/" + urllib.parse.quote("生成ai") + "/feed", "ja"),
    ("ITmedia AI+", "https://rss.itmedia.co.jp/rss/2.0/aiplus.xml", "ja"),
    ("Publickey", "https://www.publickey1.jp/atom.xml", "ja"),
    ("OpenAI", "https://openai.com/blog/rss.xml", "en"),
    ("Google AI", "https://blog.google/technology/ai/rss/", "en"),
    ("TechCrunch AI", "https://techcrunch.com/category/artificial-intelligence/feed/", "en"),
    ("Simon Willison", "https://simonwillison.net/atom/everything/", "en"),
    ("HuggingFace", "https://huggingface.co/blog/feed.xml", "en"),
    ("Zenn Claude", "https://zenn.dev/topics/claude/feed", "ja"),
    ("Zenn プロンプト", "https://zenn.dev/topics/" + urllib.parse.quote("プロンプトエンジニアリング") + "/feed", "ja"),
    ("note AI", "https://note.com/hashtag/AI/rss", "ja"),
    ("HackerNews AI", "https://hnrss.org/newest?q=Claude+OR+ChatGPT+OR+Gemini&points=50", "en"),
    ("r/ClaudeAI", "https://www.reddit.com/r/ClaudeAI/top/.rss?t=day", "en"),
]

# Redditはまとめて叩くと弾かれるので、r/ClaudeAI以外は日替わりで1つだけ回す
_ROTATE = [("r/ChatGPT", "https://www.reddit.com/r/ChatGPT/top/.rss?t=day"),
           ("r/GeminiAI", "https://www.reddit.com/r/GeminiAI/top/.rss?t=day"),
           ("r/PromptEngineering", "https://www.reddit.com/r/PromptEngineering/top/.rss?t=week")]
_today = datetime.now().timetuple().tm_yday % len(_ROTATE)
FEEDS.append((_ROTATE[_today][0], _ROTATE[_today][1], "en"))

# どのAIの話かを見出しから推定する
RULES = [
    ("ChatGPT", ["chatgpt", "openai", "gpt-", "gpt5", "gpt-5", "sora", "dall-e"]),
    ("Claude", ["claude", "anthropic", "claude.md", "skill.md", "mcp"]),
    ("Gemini", ["gemini", "notebooklm", "google ai", "deepmind", "veo", "imagen"]),
    ("Copilot", ["copilot", "microsoft 365", "m365", "azure openai"]),
]

def classify(title):
    t = title.lower()
    for name, keys in RULES:
        for k in keys:
            if k in t:
                return name
    return "その他"

def parse_date(el):
    for tag in ("pubDate", "published", ATOM + "published", ATOM + "updated", "updated"):
        node = el.find(tag)
        if node is not None and node.text:
            raw = node.text.strip()
            try:
                if "," in raw or raw.endswith("GMT"):
                    return parsedate_to_datetime(raw)
                return datetime.fromisoformat(raw.replace("Z", "+00:00"))
            except Exception:
                continue
    return None

def text_of(el, *tags):
    for tag in tags:
        node = el.find(tag)
        if node is not None:
            if node.text:
                return node.text.strip()
            href = node.get("href")
            if href:
                return href.strip()
    return ""

def strip_html(s):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", s or "")).strip()

def collect():
    import time as _t
    items = []
    for name, url, lang in FEEDS:
        headers = dict(UA)
        if "reddit.com" in url:
            _t.sleep(8)
            headers["User-Agent"] = "AIKotsuZukan/1.0 (personal reading list)"
        try:
            req = urllib.request.Request(url, headers=headers)
            raw = urllib.request.urlopen(req, timeout=20).read()
            root = ET.fromstring(raw)
            entries = root.findall(".//item") or root.findall(".//" + ATOM + "entry")
            got = 0
            for e in entries[:25]:
                title = text_of(e, "title", ATOM + "title")
                link = text_of(e, "link", ATOM + "link")
                if not title or not link:
                    continue
                d = parse_date(e)
                summary = strip_html(text_of(e, "description", "summary", ATOM + "summary", ATOM + "content"))[:160]
                items.append({
                    "title": title,
                    "url": link,
                    "source": name,
                    "lang": lang,
                    "ai": classify(title + " " + summary),
                    "summary": summary,
                    "date": d.strftime("%Y-%m-%d") if d else "",
                })
                got += 1
            sys.stderr.write("OK  %-18s %d件\n" % (name, got))
        except Exception as ex:
            sys.stderr.write("NG  %-18s %s\n" % (name, str(ex)[:50]))
    return items

def main():
    old = []
    if os.path.exists(OUT):
        try:
            old = json.load(io.open(OUT, encoding="utf-8")).get("news", [])
        except Exception:
            old = []
    seen = set()
    merged = []
    for it in collect() + old:
        if it["url"] in seen:
            continue
        seen.add(it["url"])
        merged.append(it)
    merged.sort(key=lambda x: x.get("date") or "", reverse=True)
    # 90日より古いものは捨てる（ただし最低200件は残す）
    cutoff = (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d")
    kept = [m for m in merged if (m.get("date") or "9999") >= cutoff]
    if len(kept) < 100:
        kept = merged
    out = {"updated": datetime.now().strftime("%Y-%m-%d %H:%M"), "news": kept[:400]}
    io.open(OUT, "w", encoding="utf-8").write(json.dumps(out, ensure_ascii=False, indent=1))
    print("news.json に %d 件" % len(out["news"]))

if __name__ == "__main__":
    main()
