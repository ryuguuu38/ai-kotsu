# -*- coding: utf-8 -*-
"""サイトの自己点検（再発防止用）。
   今日みつけた種類の不具合を、次回から自動で捕まえるための道具。
   使い方:  python3 check_site.py          … データとHTMLの静的チェック
            python3 check_site.py --links  … 出典リンクが生きているかも確認（時間かかる）
"""
from __future__ import unicode_literals
import json, io, os, re, sys, collections

HERE = os.path.dirname(os.path.abspath(__file__))
def load(name, key=None):
    p = os.path.join(HERE, "data", name)
    if not os.path.exists(p): return None
    d = json.load(io.open(p, encoding="utf-8"))
    return d.get(key) if key else d

NG, WARN = [], []
def ng(m): NG.append(m)
def warn(m): WARN.append(m)

# ---------- 1. コツのデータ ----------
tips = load("tips.json", "tips") or []
ids = [t.get("id") for t in tips]
for i, c in collections.Counter(ids).items():
    if c > 1: ng("コツのIDが重複: %s (%d件)" % (i, c))
for t in tips:
    for k in ("id", "ai", "title", "summary", "level", "tags", "source", "use"):
        if not t.get(k): ng("コツ %s: %s が空" % (t.get("id"), k))
    s = t.get("source") or {}
    if s and not s.get("url") and not s.get("title"):
        ng("コツ %s: 出典が空" % t.get("id"))
    if len(t.get("title","")) > 46: warn("コツ %s: タイトルが長い(%d字)" % (t["id"], len(t["title"])))

# ---------- 2. 動画・note ----------
feed = load("feed.json", "items") or []
seen_u, seen_t = set(), set()
for it in feed:
    if it["url"] in seen_u: ng("動画/noteのURL重複: %s" % it["url"])
    key = (it.get("author",""), it.get("title","").strip())
    if key in seen_t: ng("同じ発信者の同じタイトルが重複: %s / %s" % (key[0], key[1][:34]))
    seen_u.add(it["url"]); seen_t.add(key)
no_thumb = len([x for x in feed if not x.get("thumb")])
if feed and no_thumb * 100 // len(feed) > 20:
    warn("動画・noteのサムネ欠け %d/%d件" % (no_thumb, len(feed)))

# ---------- 3. ニュース ----------
news = load("news.json", "news") or []
if len(set(n["url"] for n in news)) != len(news): ng("ニュースのURLが重複している")

# ---------- 4. 台本と音声 ----------
cast = load("podcast.json") or {}
if cast:
    if not cast.get("lines"): ng("台本が空")
    vb = ""
    vp = os.path.join(HERE, "data", "voice_built.txt")
    if os.path.exists(vp): vb = io.open(vp, encoding="utf-8").read().strip()[:10]
    if vb and cast.get("date") and vb < cast["date"]:
        warn("音声(%s)が台本(%s)より古い ＝ 次の自動更新で揃う" % (vb, cast["date"]))

# ---------- 5. できあがったHTML ----------
site = os.path.join(HERE, "サイト", "index.html")
if os.path.exists(site):
    h = io.open(site, encoding="utf-8").read()
    # 消したはずの機能が残っていないか
    for word in ("speechSynthesis", "stopCast", "端末の声"):
        if word in h: ng("HTMLに削除済みのはずの %s が残っている" % word)
    # 壊れた色指定・未定義の変数呼び出しの兆候
    if re.search(r'[а-яА-Яáčďěňřšťůž\uac00-\ud7a3\u0370-\u03ff]', h):
        ng("HTMLに不審な外国語文字が混入")
    for need in ("favicon.svg", "apple-touch-icon", "noindex", "robots"):
        if need not in h: warn("HTMLに %s が見当たらない" % need)
    # 主要なタブが全部あるか
    for tab in ("今日", "今日の10分", "コツ", "動画・note", "ニュース"):
        if 'data-view' in h and tab not in h: ng("タブ「%s」が見当たらない" % tab)

# ---------- 6. 出典リンク（--links のときだけ） ----------
if "--links" in sys.argv:
    import urllib.request, time
    UA = {"User-Agent": "Mozilla/5.0 (Macintosh) AppleWebKit/537.36 Chrome/125"}
    urls = sorted({(t.get("source") or {}).get("url") for t in tips if (t.get("source") or {}).get("url")})
    print("出典リンクを %d件 確認中..." % len(urls))
    for u in urls:
        try:
            code = urllib.request.urlopen(urllib.request.Request(u, headers=UA, method="HEAD"), timeout=12).getcode()
        except Exception as e:
            code = getattr(e, "code", 0) or 0
        if code not in (200, 301, 302, 403):   # 403はbot避け。切れとは限らない
            ng("出典リンクが切れている可能性 HTTP %s : %s" % (code, u))
        time.sleep(0.2)


# ---------- 6. 公開してはいけない言葉が紛れていないか ----------
# 一度やらかしている（会社メールでコミットして会社アカウントが公開表示された）ので、自動で見張る。
# このリポジトリは公開なので、個人・会社が特定できる語と、身内向けの言い回しを弾く。
# ※「オーナー指定」は画面に出す正常なラベルなので対象外。
#   ここに入れるのは「個人・勤め先が特定できる語」と「手元のパソコンの情報」だけ。
PRIVATE_WORDS = ["apol.co.jp", "@apol", "アポロ株式会社", "山\u5c4e", "yamasaki", "ryuichi.yamasaki",
                 "/Users/", "あなたの社内ルール", "弊社は研修会社"]
for _name, _rows in (("コツ", tips), ("動画・note", feed), ("ニュース", news)):
    for _x in _rows:
        _s = json.dumps(_x, ensure_ascii=False)
        for _w in PRIVATE_WORDS:
            if _w in _s:
                ng("公開してはいけない言葉「%s」が %s に入っている（%s）"
                   % (_w, _name, (_x.get("id") or _x.get("url", ""))[:44]))
                break
for _f in ("build.py", "build_podcast.py", "collect_sources.py", "collect_news.py",
           "make_voice.py", "update_all.py", "README.md"):
    _p = os.path.join(HERE, _f)
    if not os.path.exists(_p):
        continue
    _t = io.open(_p, encoding="utf-8").read()
    for _w in PRIVATE_WORDS:
        if _w in _t and not (_w == "/Users/" and _f == "make_voice.py"):
            ng("公開してはいけない言葉「%s」が %s に入っている" % (_w, _f))
            break


# ---------- 7. 書き間違いで外国語が混ざっていないか ----------
# Claudeが日本語を書いているときに、キリル文字・ハングル・ギリシャ文字などが
# 紛れ込むことが実際に何度かあった。どの項目かまで言えるようにしておく。
FOREIGN = re.compile(r'[а-яА-Яáčďěňřšťůž\uac00-\ud7a3\u0370-\u03ff]')
for _name, _rows in (("コツ", tips),):
    for _x in _rows:
        for _k, _v in _x.items():
            vals = _v if isinstance(_v, list) else [_v]
            for _vv in vals:
                if isinstance(_vv, str):
                    m = FOREIGN.search(_vv)
                    if m:
                        ng("%s %s の %s に外国語文字「%s」が混入" % (_name, _x.get("id"), _k, m.group(0)))

# ---------- 結果 ----------
print("=" * 58)
print("コツ %d件 / 動画・note %d件 / ニュース %d件" % (len(tips), len(feed), len(news)))
print("=" * 58)
if NG:
    print("❌ 直すべき問題 %d件" % len(NG))
    for m in NG: print("   ・" + m)
else:
    print("✅ 直すべき問題はありません")
if WARN:
    print("⚠️  気になる点 %d件" % len(WARN))
    for m in WARN: print("   ・" + m)
sys.exit(1 if NG else 0)
