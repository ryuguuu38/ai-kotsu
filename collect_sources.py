# -*- coding: utf-8 -*-
"""指定のYouTubeチャンネルとnoteから、動画・記事を集めて data/feed.json に貯める。
   YouTubeは説明欄と目次(チャプター)まで取りに行く＝「その回で何を言ったか」が分かる。
   Python標準ライブラリのみ。"""
from __future__ import unicode_literals
import urllib.request, urllib.parse, xml.etree.ElementTree as ET
import json, io, os, re, sys, time
from datetime import datetime
from email.utils import parsedate_to_datetime

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "data", "sources.json")
OUT = os.path.join(HERE, "data", "feed.json")
UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125 Safari/537.36",
      "Accept-Language": "ja"}
A = "{http://www.w3.org/2005/Atom}"
Y = "{http://www.youtube.com/xml/schemas/2015}"
MD = "{http://search.yahoo.com/mrss/}"
MAX_DESC_FETCH = 40           # 1回の実行で説明欄を取りに行く上限（行儀よく・少しずつ）
POLITE_WAIT = 2.5             # 1本ごとに待つ秒数
GIVE_UP_AFTER = 3             # 連続でこの回数断られたら、その日は説明欄を諦める
VIDEOS_PER_CHANNEL = 12

RULES = [
    ("Claude", ["claude", "anthropic", "claude.md", "skill.md", "mcp", "codex"]),
    ("ChatGPT", ["chatgpt", "openai", "gpt-", "gpt6", "gpt-6", "astra", "sora", "codex app"]),
    ("Gemini", ["gemini", "notebooklm", "notebook lm", "google", "veo", "canvas", "gems"]),
    ("Copilot", ["copilot", "microsoft 365", "m365", "excel", "powerpoint", "パワポ"]),
]

def classify(text):
    t = (text or "").lower()
    hit = []
    for name, keys in RULES:
        for k in keys:
            if k in t:
                hit.append(name); break
    return hit[0] if hit else "その他"

def get(url, timeout=25):
    return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout).read()

def unesc(s):
    try:
        return s.encode().decode("unicode_escape").encode("latin-1", "ignore").decode("utf-8", "ignore")
    except Exception:
        return s

def video_detail(vid):
    """説明欄と目次を取る"""
    html = get("https://www.youtube.com/watch?v=" + vid).decode("utf-8", "ignore")
    m = re.search(r'"shortDescription":"(.*?)","isCrawlable"', html, re.S)
    desc = unesc(m.group(1)) if m else ""
    chapters = []
    for line in desc.split("\n"):
        mm = re.match(r"^\s*\(?(\d{1,2}:\d{2}(?::\d{2})?)\)?\s*[-–—:｜|]?\s*(.+?)\s*$", line)
        if mm and len(mm.group(2)) > 1:
            chapters.append({"t": mm.group(1), "label": mm.group(2)[:70]})
    clean = "\n".join([l for l in desc.split("\n")
                       if not re.match(r"^\s*https?://", l.strip()) and not l.strip().startswith("#")])
    return desc, chapters, re.sub(r"\s+", " ", clean).strip()[:260]

def collect_youtube(chs, cache):
    items, fetched, misses, blocked = [], 0, 0, False
    for c in chs:
        try:
            xml = get("https://www.youtube.com/feeds/videos.xml?channel_id=" + c["id"])
            entries = ET.fromstring(xml).findall(A + "entry")[:VIDEOS_PER_CHANNEL]
        except Exception as e:
            sys.stderr.write("NG  %s %s\n" % (c["name"], str(e)[:40])); continue
        got = 0
        for e in entries:
            vid = e.find(Y + "videoId").text
            url = "https://www.youtube.com/watch?v=" + vid
            title = e.find(A + "title").text or ""
            date = (e.find(A + "published").text or "")[:10]
            old = cache.get(url)
            if old and old.get("summary") is not None:
                chapters, summary = old.get("chapters", []), old.get("summary", "")
            elif fetched < MAX_DESC_FETCH and not blocked:
                try:
                    _, chapters, summary = video_detail(vid)
                    fetched += 1; misses = 0
                    time.sleep(POLITE_WAIT)
                except Exception as ex:
                    chapters, summary = [], None
                    misses += 1
                    if misses >= GIVE_UP_AFTER:
                        blocked = True
                        sys.stderr.write("    ※説明欄の取得を断られたので、今回はここで止めます（%s）\n" % str(ex)[:40])
            else:
                chapters, summary = [], None
            items.append({"kind": "youtube", "title": title, "url": url, "date": date,
                          "thumb": "https://i.ytimg.com/vi/%s/mqdefault.jpg" % vid,
                          "author": c["name"], "pick": c.get("pick", ""),
                          "ai": classify(title + " " + (summary or "") + " " + " ".join([x["label"] for x in chapters])),
                          "chapters": chapters, "summary": summary})
            got += 1
        sys.stderr.write("OK  %-26s %2d本\n" % (c["name"][:26], got))
    sys.stderr.write("    （説明欄を新たに取得: %d本%s）\n" % (fetched, " ／ 途中で断られました" if blocked else ""))
    return items, blocked

def collect_note(feeds):
    items = []
    for f in feeds:
        try:
            xml = get(f["url"])
            for it in ET.fromstring(xml).findall(".//item")[:15]:
                title = (it.findtext("title") or "").strip()
                link = (it.findtext("link") or "").strip()
                raw = it.findtext("pubDate") or ""
                try:
                    date = parsedate_to_datetime(raw).strftime("%Y-%m-%d")
                except Exception:
                    date = raw[:10]
                desc = re.sub(r"<[^>]+>", "", it.findtext("description") or "")
                desc = re.sub(r"\s+", " ", desc).strip()[:260]
                th = (it.findtext(MD + "thumbnail") or it.findtext("thumbnail") or "").strip()
                if not th:
                    nd = it.find(MD + "thumbnail") or it.find("enclosure")
                    if nd is not None: th = (nd.get("url") or "").strip()
                items.append({"kind": "note", "title": title, "url": link, "date": date,
                              "thumb": th,
                              "author": f["name"], "pick": f.get("pick", ""),
                              "ai": classify(title + " " + desc), "chapters": [], "summary": desc})
            sys.stderr.write("OK  %-26s note\n" % f["name"][:26])
        except Exception as e:
            sys.stderr.write("NG  %-26s %s\n" % (f["name"][:26], str(e)[:40]))
    return items

def main():
    src = json.load(io.open(SRC, encoding="utf-8"))
    cache = {}
    if os.path.exists(OUT):
        try:
            for it in json.load(io.open(OUT, encoding="utf-8")).get("items", []):
                cache[it["url"]] = it
        except Exception:
            pass
    yt, blocked = collect_youtube(src["youtube"], cache)
    items = yt + collect_note(src["note"])
    # URLだけでなく「同じ発信者＋同じタイトル」でも重複を除く
    # （同じ内容を別の動画IDで再投稿する発信者がいるため）
    seen_url, seen_title, merged = set(), set(), []
    for it in items:
        key_t = (it.get("author",""), it.get("title","").strip())
        if it["url"] in seen_url or key_t in seen_title:
            continue
        seen_url.add(it["url"]); seen_title.add(key_t); merged.append(it)
    merged.sort(key=lambda x: x.get("date") or "", reverse=True)
    out = {"updated": datetime.now().strftime("%Y-%m-%d %H:%M"),
           "desc_blocked": blocked, "items": merged[:500]}
    io.open(OUT, "w", encoding="utf-8").write(json.dumps(out, ensure_ascii=False, indent=1))
    print("feed.json に %d 件（目次つき %d 件）%s" %
          (len(out["items"]), len([x for x in out["items"] if x["chapters"]]),
           "※説明欄の取得を断られました" if blocked else ""))

if __name__ == "__main__":
    main()
