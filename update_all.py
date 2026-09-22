# -*- coding: utf-8 -*-
"""これ1本で全部更新する。1) 指定の発信者を巡回 2) ニュース収集 3) サイトを作り直す"""
from __future__ import unicode_literals
import subprocess, sys, os, io, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "更新ログ.txt")

def run(name, script):
    print("▶ %s ..." % name)
    p = subprocess.Popen([sys.executable, os.path.join(HERE, script)],
                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    out = p.communicate()[0].decode("utf-8", "ignore")
    tail = [l for l in out.strip().split("\n") if l.strip()][-1:] 
    print("  " + (tail[0] if tail else "(出力なし)"))
    return (tail[0] if tail else ""), p.returncode

if __name__ == "__main__":
    stamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = ["[%s] 更新開始" % stamp]
    for name, script in [("発信者の巡回（YouTube・note）", "collect_sources.py"),
                         ("ニュース収集", "collect_news.py"),
                         ("今日の10分の台本づくり", "build_podcast.py"),
                         ("サイトの組み立て", "build.py")]:
        msg, code = run(name, script)
        lines.append("  %s: %s%s" % (name, msg, "" if code == 0 else " ←失敗"))
    lines.append("[%s] 完了" % datetime.datetime.now().strftime("%H:%M"))
    with io.open(LOG, "a", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines[-1:]))
