# -*- coding: utf-8 -*-
"""スマホから送られた「いいね」をGitHubのIssueから読み取って、data/likes.json に反映する。

サイトの「📮 Claudeに送る」ボタンが、GitHubに次の形の投稿を作る:
    L: gpt-001,claude-056
    N: claude-065
    OFF: other-001
    at: 2026-09-23 18:00

使い方:
    python3 read_likes.py          … 新しい投稿を読んで likes.json に反映し、傾向を表示
    python3 read_likes.py --show   … 反映せず、今たまっている投稿を見るだけ
"""
from __future__ import unicode_literals
import json, io, os, re, subprocess, sys, collections

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = "ryuguuu38/ai-kotsu"
LIKES = os.path.join(HERE, "data", "likes.json")
TIPS = os.path.join(HERE, "data", "tips.json")


def gh(args):
    try:
        out = subprocess.check_output(["gh"] + args, stderr=subprocess.STDOUT)
        return out.decode("utf-8", "ignore")
    except subprocess.CalledProcessError as e:
        print("GitHubの読み取りに失敗: %s" % e.output.decode("utf-8", "ignore")[:200])
        return None


def fetch_issues():
    """「likes」ラベルの付いた、まだ閉じていない投稿を新しい順に取る"""
    raw = gh(["issue", "list", "--repo", REPO, "--label", "likes",
              "--state", "open", "--limit", "30",
              "--json", "number,title,body,createdAt"])
    if not raw:
        return []
    try:
        return json.loads(raw)
    except Exception:
        return []


def parse(body):
    """本文から L / N / OFF を取り出す"""
    got = {"L": [], "N": [], "OFF": []}
    for line in (body or "").replace("\r", "").split("\n"):
        m = re.match(r"^\s*(L|N|OFF)\s*[:：]\s*(.*)$", line)
        if m:
            ids = [x.strip() for x in m.group(2).split(",") if x.strip()]
            got[m.group(1)] = ids
    return got


def load_tips():
    """IDから、タイトルや5軸を引けるようにする"""
    d = json.load(io.open(TIPS, encoding="utf-8"))
    by = {}
    for t in d.get("tips", []):
        by[t["id"]] = t
    return by


def main():
    show_only = "--show" in sys.argv
    issues = fetch_issues()
    if not issues:
        print("新しい投稿はありません。")
        print("（スマホのサイトで「📮 Claudeに送る」を押すと、ここに届きます）")
        return 0

    tips = load_tips()
    saved = json.load(io.open(LIKES, encoding="utf-8")) if os.path.exists(LIKES) else {}
    likes = saved.get("likes", {}) or {}
    nopes = saved.get("nopes", {}) or {}

    print("届いている投稿: %d件" % len(issues))
    handled = []
    # 古い順に反映する（新しい操作があとから上書きするように）
    for iss in sorted(issues, key=lambda x: x.get("createdAt", "")):
        g = parse(iss.get("body"))
        print("  #%s %s  → 👍%d 👎%d 外した%d"
              % (iss["number"], iss.get("createdAt", "")[:16].replace("T", " "),
                 len(g["L"]), len(g["N"]), len(g["OFF"])))
        if show_only:
            continue
        for i in g["OFF"]:
            likes.pop(i, None); nopes.pop(i, None)
        for i in g["N"]:
            likes.pop(i, None)
            nopes[i] = {"at": iss.get("createdAt", "")[:10]}
        for i in g["L"]:
            if i in nopes:
                continue
            likes[i] = {"at": iss.get("createdAt", "")[:10]}
        handled.append(iss["number"])

    if show_only:
        return 0

    saved["likes"], saved["nopes"] = likes, nopes
    saved["updated"] = max([i.get("createdAt", "")[:10] for i in issues] or [""])
    io.open(LIKES, "w", encoding="utf-8").write(json.dumps(saved, ensure_ascii=False, indent=1))
    print("\ndata/likes.json に反映しました（👍%d件 / 👎%d件）" % (len(likes), len(nopes)))

    # ---- 傾向を出す ----
    def tally(ids, key):
        c = collections.Counter()
        for i in ids:
            t = tips.get(i)
            if not t:
                continue
            v = (t.get("axes") or {}).get(key) if key in ("scene", "kind", "effect", "effort", "depth") else t.get(key)
            if v:
                c[v] += 1
        return " / ".join("%s%d" % (k, v) for k, v in c.most_common())

    for ids, label in ((list(likes), "👍 いいね"), (list(nopes), "👎 違う")):
        known = [i for i in ids if i in tips]
        if not known:
            continue
        print("\n=== %s の傾向（コツ %d件ぶん）===" % (label, len(known)))
        for key, name in (("scene", "① 場面"), ("kind", "② 種類"), ("effect", "③ 効き方"),
                          ("effort", "④ 手間"), ("depth", "⑤ 具体度"),
                          ("ai", "AI別"), ("level", "レベル"), ("use", "用途")):
            r = tally(known, key)
            if r:
                print("  %-10s %s" % (name, r))
        print("\n  中身:")
        for i in known:
            print("    ・%s" % tips[i]["title"][:52])

    print("\n※ 反映した投稿は、確認後に閉じてください:")
    for n in handled:
        print("    gh issue close %s --repo %s" % (n, REPO))
    return 0


if __name__ == "__main__":
    sys.exit(main())
