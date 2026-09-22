# -*- coding: utf-8 -*-
"""台本(podcast.json)を VOICEVOX で音声にして1本のmp3にまとめる。
   ※VOICEVOXアプリを起動しておく必要があります（エンジンが 127.0.0.1:50021 で動きます）"""
from __future__ import unicode_literals
import urllib.request, urllib.parse, json, io, os, sys, subprocess, glob, time

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(HERE, "音声")
TMP = os.path.join(OUT_DIR, "_parts")
ENGINE = "http://127.0.0.1:50021"
# ffmpeg の場所：環境変数 FFMPEG → .ffmpeg_path（手元用・公開しない）→ PATH上の ffmpeg の順で探す
def _find_ffmpeg():
    v = os.environ.get("FFMPEG")
    if v:
        return v
    local = os.path.join(HERE, ".ffmpeg_path")
    if os.path.exists(local):
        try:
            v = io.open(local, encoding="utf-8").read().strip()
            if v and os.path.exists(v):
                return v
        except Exception:
            pass
    return "ffmpeg"

FFMPEG = _find_ffmpeg()
SPEAKER = {"metan": 2, "zunda": 3}      # 四国めたん(ノーマル) / ずんだもん(ノーマル)

def post(path, data=None, params=None):
    url = ENGINE + path + ("?" + urllib.parse.urlencode(params) if params else "")
    body = json.dumps(data).encode() if data is not None else b""
    req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"}, method="POST")
    return urllib.request.urlopen(req, timeout=60).read()

def engine_alive():
    try:
        urllib.request.urlopen(ENGINE + "/version", timeout=3).read()
        return True
    except Exception:
        return False

def check_ffmpeg():
    """音声をまとめる道具があるか先に確かめる"""
    try:
        subprocess.check_output([FFMPEG, "-version"], stderr=subprocess.STDOUT)
        return True
    except Exception as e:
        print("NG: ffmpeg が使えません（%s）: %s" % (FFMPEG, str(e)[:80]))
        return False

def main():
    print("使う ffmpeg: %s" % FFMPEG)
    if not check_ffmpeg():
        return 1
    if not engine_alive():
        print("NG: VOICEVOXのエンジンが動いていません。")
        print("    VOICEVOXアプリを起動してから、もう一度実行してください。")
        return 1
    cast = json.load(io.open(os.path.join(HERE, "data", "podcast.json"), encoding="utf-8"))
    lines = cast["lines"]
    for d in (OUT_DIR, TMP):
        if not os.path.isdir(d): os.makedirs(d)
    for f in glob.glob(os.path.join(TMP, "*.wav")): os.remove(f)

    t0 = time.time()
    for i, l in enumerate(lines):
        sid = SPEAKER.get(l["who"], 3)
        try:
            q = json.loads(post("/audio_query", params={"text": l["text"], "speaker": sid}))
        except Exception as e:
            print("NG: %d行目の音声化に失敗: %s" % (i, str(e)[:120]))
            print("   セリフ: %s" % l["text"][:60])
            raise
        q["speedScale"] = 1.05
        q["postPhonemeLength"] = 0.15          # セリフ間の間
        wav = post("/synthesis", data=q, params={"speaker": sid})
        io.open(os.path.join(TMP, "%03d.wav" % i), "wb").write(wav)
        if (i + 1) % 10 == 0 or i + 1 == len(lines):
            sys.stderr.write("  音声化 %d/%d（%.0f秒経過）\n" % (i + 1, len(lines), time.time() - t0))

    # 全部つなげてmp3に
    listfile = os.path.join(TMP, "list.txt")
    with io.open(listfile, "w", encoding="utf-8") as f:
        for i in range(len(lines)):
            f.write("file '%s'\n" % os.path.join(TMP, "%03d.wav" % i))
    out = os.environ.get("VOICE_OUT") or os.path.join(OUT_DIR, "AIコツ図鑑_%s.mp3" % cast["date"])
    d = os.path.dirname(out)
    if d and not os.path.isdir(d):
        os.makedirs(d)
    subprocess.call([FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", listfile,
                     "-codec:a", "libmp3lame", "-b:a", "128k", out],
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if not os.path.exists(out):
        print("NG: ffmpeg での結合に失敗しました（生成した部品は %d個）" % len(lines))
    if os.path.exists(out):
        mb = os.path.getsize(out) / 1024.0 / 1024.0
        print("できました: %s（%.1fMB）" % (out, mb))
        for f in glob.glob(os.path.join(TMP, "*")): os.remove(f)
        return 0
    print("NG: mp3の作成に失敗しました")
    return 1

if __name__ == "__main__":
    sys.exit(main())
