# -*- coding: utf-8 -*-
"""その日の新着から「今日の10分」の台本を作る。
   四国めたん（解説役）× ずんだもん（聞き役）の掛け合い形式。
   Python標準ライブラリのみ。"""
from __future__ import unicode_literals
import json, io, os, re, random
from datetime import datetime, date

HERE = os.path.dirname(os.path.abspath(__file__))
M, Z = "metan", "zunda"        # 四国めたん / ずんだもん

def load(name, key):
    p = os.path.join(HERE, "data", name)
    if not os.path.exists(p): return []
    try: return json.load(io.open(p, encoding="utf-8")).get(key, [])
    except Exception: return []

def days_ago(d):
    try:
        y, m, dd = [int(x) for x in str(d).split("-")[:3]]
        return (date.today() - date(y, m, dd)).days
    except Exception:
        return 999

PROMO = ["こちら", "購入", "キャンペーン", "ハッシュタグ", "割引", "OFF", "特典", "登録",
         "チャンネル", "概要欄", "メンバーシップ", "公式LINE", "無料配布",
         "プレゼント", "クーポン", "申し込", "提供"]

def is_promo(t):
    t = t or ""
    return sum(1 for w in PROMO if w in t) >= 2 or len(t) < 25

def clean(s):
    s = re.sub(r"https?://\S+", "", s or "")
    s = re.sub(r"[【】『』「」\[\]（）()#＃*_|｜/\\~＝=+•·▼▲■□◆◇★☆→←↑↓]", " ", s)
    s = re.sub(r"[\U0001F000-\U0001FAFF☀-➿]", "", s)
    return re.sub(r"\s+", " ", s).strip()

def speak_name(n):
    n = (n or "").replace("&", "").replace("｜", " ").replace("|", " ")
    n = n.replace("（note）", "さんのノート").replace("(note)", "さんのノート")
    n = re.sub(r"\s*ch\s*$", "", n).replace("AI WEB", "").strip()
    return n + ("" if "さん" in n else "さん")

# ずんだもんの相づち（日替わりで変わるように複数用意）
ASK   = ["どんな内容なのだ？", "それ、何がすごいのだ？", "中身を教えてほしいのだ！",
         "詳しく聞きたいのだ！", "へえ、それで？", "気になるのだ！"]
REACT = ["なるほどなのだ！", "それは知らなかったのだ…", "さっそく試すのだ！",
         "頭に入れておくのだ！", "地味に効きそうなのだ！", "うわ、損してたのだ…",
         "それ早く言ってほしかったのだ！", "メモしておくのだ！"]
WHY   = ["なんで効くのだ？", "どうしてそうなるのだ？", "理由が知りたいのだ！"]
HOW   = ["やり方も教えてほしいのだ！", "具体的にはどうするのだ？", "手順を頼むのだ！"]

class Deck(object):
    """同じ相づちが続かないように順に配る"""
    def __init__(self, items, seed):
        self.items = list(items)
        random.Random(seed).shuffle(self.items)
        self.i = 0
    def next(self):
        v = self.items[self.i % len(self.items)]
        self.i += 1
        return v

def build():
    feed = load("feed.json", "items")
    news = load("news.json", "news")
    tips = load("tips.json", "tips")
    today = datetime.now()
    wd = "月火水木金土日"[today.weekday()]
    seed = today.timetuple().tm_yday
    ask, react, why, how = Deck(ASK, seed), Deck(REACT, seed+1), Deck(WHY, seed+2), Deck(HOW, seed+3)

    fresh = [f for f in feed if days_ago(f.get("date")) <= 1]
    if len(fresh) < 3:
        fresh = [f for f in feed if days_ago(f.get("date")) <= 3]
    star = [f for f in fresh if f.get("pick") == "オーナー指定"]
    others = [f for f in fresh if f.get("pick") != "オーナー指定"]
    picks = (star[:5] + others)[:8]
    todays_news = [n for n in news if days_ago(n.get("date")) <= 1][:6]
    todays_tips = []
    if tips:
        base = seed * 3
        todays_tips = [tips[(base + k) % len(tips)] for k in range(3)]

    L = []
    def say(who, text):
        t = clean(text)
        if t: L.append({"who": who, "text": t})

    # ---- オープニング ----
    say(M, "おはよう。AIコツ図鑑、%d月%d日、%s曜日の回よ。" % (today.month, today.day, wd))
    say(Z, "今日はどんな話があるのだ？")
    say(M, "追いかけている人の新着が%d本、ニュースが%d本入っているわ。"
           "その中から、知っておくと得をするものだけ話すわね。" % (len(fresh), len(todays_news)))
    say(Z, "全部読むのは無理だから助かるのだ！")

    # ---- 新着 ----
    if picks:
        say(M, "まずは新着から。")
        for i, f in enumerate(picks, 1):
            who = speak_name(clean(f.get("author", "")))
            kind = "の動画" if f.get("kind") == "youtube" else "の記事"
            say(M, "%d本目は、%s%s。%s。" % (i, who, kind, clean(f.get("title", ""))))
            chaps = f.get("chapters") or []
            labels = [clean(c.get("label", "")) for c in chaps[1:8] if clean(c.get("label", ""))]
            if labels:
                say(Z, ask.next())
                say(M, "扱っているのは、%s、といったところね。" % "、".join(labels))
                say(Z, react.next())
            elif f.get("summary") and not is_promo(f["summary"]):
                say(Z, ask.next())
                say(M, clean(f["summary"])[:200] + "。")
    else:
        say(M, "今日は新着がなかったわ。")
        say(Z, "そういう日もあるのだ。")

    # ---- ニュース ----
    if todays_news:
        say(M, "次に、今日のニュースの見出しだけ流すわね。")
        for n in todays_news:
            say(M, "%s から、%s。" % (clean(n.get("source", "")), clean(n.get("title", ""))))
        say(Z, "気になるのがあったら、あとでサイトから開けばいいのだ。")

    # ---- コツ（本編） ----
    if todays_tips:
        say(M, "ここからが本題。今日のコツを3つ話すわ。")
        for k, tip in enumerate(todays_tips, 1):
            say(M, "%dつ目。%s の話で、%s。" % (k, tip.get("ai", ""), clean(tip.get("title", ""))))
            say(Z, ask.next())
            say(M, clean(tip.get("summary", "")))
            if tip.get("why"):
                say(Z, why.next())
                say(M, clean(tip["why"]))
            steps = tip.get("steps") or []
            if steps:
                say(Z, how.next())
                say(M, "%d段階よ。" % len(steps))
                for i, st in enumerate(steps[:6], 1):
                    say(M, "%d、%s。" % (i, clean(st)))
            say(Z, react.next())
            src = (tip.get("source") or {}).get("title")
            if src:
                say(M, "出どころは、%s ね。" % clean(src)[:55])

    # ---- クロージング ----
    say(M, "以上よ。詳しくはサイトのカードから、元の動画や記事に飛べるわ。")
    say(Z, "今日もいい一日にするのだ！")
    say(M, "音声は ボイスボックス。ずんだもんと四国めたんで作っているわ。")

    chars = sum(len(re.sub(r"\s", "", x["text"])) for x in L)
    minutes = round(chars / 370.0, 1)
    out = {
        "date": today.strftime("%Y-%m-%d"),
        "built": today.strftime("%Y-%m-%d %H:%M"),
        "minutes": minutes, "chars": chars,
        "lines": L,
        "credit": "VOICEVOX:ずんだもん / 四国めたん",
        "tip_ids": [t.get("id") for t in todays_tips],
    }
    io.open(os.path.join(HERE, "data", "podcast.json"), "w", encoding="utf-8").write(
        json.dumps(out, ensure_ascii=False, indent=1))
    print("台本ができました：約%s分（%d字・%dセリフ）" % (minutes, chars, len(L)))
    return out

if __name__ == "__main__":
    o = build()
    print("---- 冒頭 ----")
    for x in o["lines"][:10]:
        print(("  めたん： " if x["who"] == "metan" else "  ずんだ： ") + x["text"][:70])
