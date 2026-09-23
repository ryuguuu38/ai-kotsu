# -*- coding: utf-8 -*-
"""その日の新着から「今日の10分」の台本を作る。
   四国めたん（解説役）× ずんだもん（聞き役）の掛け合い形式。
   Python標準ライブラリのみ。"""
from __future__ import unicode_literals
import json, io, os, re, random
from datetime import datetime, date

HERE = os.path.dirname(os.path.abspath(__file__))
M, Z = "metan", "zunda"        # 四国めたん / ずんだもん

# 版（テーマ別）の定義：キー → (表示名, 対象AI, コツの本数, 新着の本数, ニュースの本数)
EDITIONS = {
    "all":     ("全部入り",   None,       3, 5, 4),
    "claude":  ("Claude編",   "Claude",   3, 4, 3),
    "gemini":  ("Gemini編",   "Gemini",   3, 4, 3),
    "chatgpt": ("ChatGPT編",  "ChatGPT",  3, 4, 3),
    "news":    ("ニュース編", None,       0, 0, 10),
}

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

def gist(text, limit=95, title=""):
    """記事の説明文から、聞いて分かる1〜2文だけ抜く。
       ・見出しの言い直しは落とす（同じことを2回読まない）
       ・宣伝や定型文は落とす
       ・文の途中で切らない（切れた尻尾は捨てる）"""
    t = clean(text)
    if not t:
        return ""
    t = re.sub(r"^(はじめに|概要|要約|この記事(は|では)|本記事(は|では))[はでに、]*", "", t)
    tt = re.sub(r"\s+", "", clean(title))
    NG = ("この記事は", "動画はこちら", "チャンネル", "概要欄", "登録", "登場する", "はこちら")
    out, total = [], 0
    for sent in re.split(r"(?<=[。！？])", t):
        sent = sent.strip()
        if len(sent) < 15 or not sent.endswith(("。", "！", "？")):
            continue                              # 文になっていないもの（尻尾）は捨てる
        if "…" in sent or "..." in sent:
            continue
        if any(w in sent for w in NG):
            continue
        core = re.sub(r"\s+", "", sent)[:22]      # 見出しの言い直しかを見る
        if tt and core and core[:10] in tt:
            continue
        out.append(sent); total += len(sent)
        if total >= limit:
            break
    if not out:
        return ""
    g = "".join(out)
    if len(g) > limit + 80:                       # 1文が長すぎるときだけ、読点で区切る
        cut = g[:limit + 60].rfind("、")
        g = (g[:cut] + "。") if cut > 40 else g[:limit + 60] + "。"
    return g

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

def build(edition="all"):
    label, only_ai, n_tips, n_picks, n_news = EDITIONS.get(edition, EDITIONS["all"])
    feed = load("feed.json", "items")
    news = load("news.json", "news")
    tips = load("tips.json", "tips")
    if only_ai:
        feed = [f for f in feed if f.get("ai") == only_ai]
        news = [n for n in news if n.get("ai") == only_ai]
        tips = [t for t in tips if t.get("ai") == only_ai]
    today = datetime.now()
    wd = "月火水木金土日"[today.weekday()]
    seed = today.timetuple().tm_yday
    ask, react, why, how = Deck(ASK, seed), Deck(REACT, seed+1), Deck(WHY, seed+2), Deck(HOW, seed+3)

    fresh = [f for f in feed if days_ago(f.get("date")) <= 1]
    if len(fresh) < 3:
        fresh = [f for f in feed if days_ago(f.get("date")) <= 3]
    star = [f for f in fresh if f.get("pick") == "オーナー指定"]
    others = [f for f in fresh if f.get("pick") != "オーナー指定"]
    picks = (star[:4] + others)[:n_picks]
    todays_news = [n for n in news if days_ago(n.get("date")) <= 1][:max(n_news*3, 12)]
    todays_tips = []
    if tips and n_tips:
        base = seed * 3
        todays_tips = [tips[(base + k) % len(tips)] for k in range(min(n_tips, len(tips)))]

    L = []
    def say(who, text):
        t = clean(text)
        if t: L.append({"who": who, "text": t})

    # ---- 版ごとの入り ----
    ED_HOOK = {
        "claude":  "Claudeだけ聞きたい人向けなのだ！",
        "gemini":  "Geminiだけ聞きたい人向けなのだ！",
        "chatgpt": "ChatGPTだけ聞きたい人向けなのだ！",
        "news":    "ニュースだけ知りたい人向けなのだ！",
    }
    if edition != "all":
        say(M, "今日は%sよ。" % label)
        say(Z, ED_HOOK.get(edition, "さっそく聞きたいのだ！"))
    # ---- 本題：今日のコツ ----
    if todays_tips:
        say(M, "今日のコツを%dつ話すわ。" % len(todays_tips))
        for k, tip in enumerate(todays_tips, 1):
            # AIを絞った版では毎回「Geminiの話で」と言うとくどいので省く
            if only_ai:
                say(M, "%dつ目。%s。" % (k, clean(tip.get("title", ""))))
            else:
                say(M, "%dつ目。%sの話で、%s。" % (k, tip.get("ai", ""), clean(tip.get("title", ""))))
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

    # ---- 後半：今日の新着 ----
    if picks:
        say(M, "ここからは、今日出たものを軽く流すわ。" if todays_tips else "今日出たものを見ていくわ。")
        for i, f in enumerate(picks, 1):
            who = speak_name(clean(f.get("author", "")))
            kind = "の動画" if f.get("kind") == "youtube" else "の記事"
            say(M, "%d本目は、%s%s。%s。" % (i, who, kind, clean(f.get("title", ""))))
            chaps = f.get("chapters") or []
            labels = [clean(c.get("label", "")) for c in chaps[1:6] if clean(c.get("label", ""))]
            if labels:
                say(Z, ask.next())
                say(M, "扱っているのは、%s、といったところね。" % "、".join(labels))
                say(Z, react.next())
            elif f.get("summary") and not is_promo(f["summary"]):
                say(Z, ask.next())
                say(M, clean(f["summary"])[:200] + "。")
    elif n_picks:
        # 新着を読む予定だったのに0件だった日だけ言う（ニュース編など、はじめから読まない版では言わない）
        say(M, "今日は新着がなかったわ。")
        say(Z, "そういう日もあるのだ。")

    # ---- ニュース ----
    if todays_news:
        if edition == "news":
            say(M, "今日は%d本、まとめて流すわ。" % min(n_news, len(todays_news)))
        else:
            say(M, "最後に、今日のニュースから気になったものだけ。")
        # 日本語記事を優先し、同じ媒体が続かないように散らす
        ordered = sorted(todays_news, key=lambda n: 0 if n.get("lang") == "ja" else 1)
        picked, used_src = [], set()
        for allow_dup in (False, True):        # まず1媒体1本、足りなければ2本目も許す
            for n in ordered:
                if n in picked:
                    continue
                src = n.get("source", "")
                if not allow_dup and src in used_src:
                    continue
                used_src.add(src)
                picked.append(n)
                if len(picked) >= n_news:
                    break
            if len(picked) >= n_news:
                break
        LEADS = ["つぎは", "それから", "お次は", "こんなのも出ていたわ", "さらに", "もうひとつ"]
        for i, n in enumerate(picked):
            title = clean(n.get("title", ""))
            ai = n.get("ai", "その他")
            topic = ("%sの話" % ai) if ai and ai != "その他" else "こんな話"
            if i == 0:
                head = "まず、%s。" % topic
            elif i == len(picked) - 1:
                head = "最後は、%s。" % topic
            else:
                head = "%s、%s。" % (LEADS[(i - 1) % len(LEADS)], topic)
            say(M, head + title + "。")
            # ニュース編は本数が多いので、見出しだけで終わらせず中身にひとこと触れる
            if edition == "news":
                g = gist(n.get("summary"), title=n.get("title", ""))
                if g and not is_promo(g):
                    say(M, g)
                if (i + 1) % 3 == 0 and i + 1 < len(picked):
                    say(Z, react.next())
            elif len(picked) >= 3 and i == len(picked) // 2:
                say(Z, "見出しだけでも、流れは分かるのだ。")
        say(Z, "気になったのがあったら、サイトのニュース欄から開けるのだ。")


    # ---- コツ（本編） ----
    # ---- クロージング ----
    say(M, "以上よ。詳しくはサイトのカードから、元の動画や記事に飛べるわ。")
    say(Z, "今日もいい一日にするのだ！")
    say(M, "音声は ボイスボックス。ずんだもんと四国めたんで作っているわ。")

    chars = sum(len(re.sub(r"\s", "", x["text"])) for x in L)
    minutes = round(chars / 370.0, 1)
    if len(L) <= 4:
        print("%s: 今日は中身が少ないので作りません" % label)
        return None
    out = {
        "edition": edition, "label": label,
        "date": today.strftime("%Y-%m-%d"),
        "built": today.strftime("%Y-%m-%d %H:%M"),
        "minutes": minutes, "chars": chars,
        "lines": L,
        "credit": "VOICEVOX:ずんだもん / 四国めたん",
        "tip_ids": [t.get("id") for t in todays_tips],
    }
    name = "podcast.json" if edition == "all" else "podcast_%s.json" % edition
    io.open(os.path.join(HERE, "data", name), "w", encoding="utf-8").write(
        json.dumps(out, ensure_ascii=False, indent=1))
    print("%-10s 約%s分（%d字・%dセリフ）→ %s" % (label, minutes, chars, len(L), name))
    return out

if __name__ == "__main__":
    import sys
    targets = sys.argv[1:] or list(EDITIONS.keys())
    made = []
    for e in targets:
        if build(e): made.append(e)
    print("作った版: %s" % ", ".join(made))
