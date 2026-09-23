# -*- coding: utf-8 -*-
"""台本(podcast.json)を VOICEVOX で音声にして1本のmp3にまとめる。
   ※VOICEVOXアプリを起動しておく必要があります（エンジンが 127.0.0.1:50021 で動きます）"""
from __future__ import unicode_literals
import urllib.request, urllib.parse, json, io, os, sys, subprocess, glob, time, re, hashlib

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(HERE, "音声")
TMP = os.path.join(OUT_DIR, "_parts")
# 版ごとに同じセリフ（あいさつ・締め など）が何度も出てくるので、
# 一度作った声は使い回して、作り直す時間を減らす
CACHE = os.path.join(OUT_DIR, "_koe_cache")
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

BGM_DIR = os.path.join(HERE, "bgm")
BGM_VOLUME = 0.10          # 声を邪魔しない音量

def pick_bgm(cast):
    """その日の台本の中身から、合うBGMを選ぶ。
       ※音の性格は事前に測定済み（音圧・明るさ）。bgm/クレジット.txt 参照"""
    lines = cast.get("lines", [])
    text = " ".join(l.get("text", "") for l in lines)
    date = cast.get("date", "")
    # 内容の傾向で選ぶ
    if any(w in text for w in ["節約", "枠", "消費", "上限", "失敗", "事故", "注意", "危険", "崩壊"]):
        pick = "calm"        # 気をつける話が多い日は静かに
    elif any(w in text for w in ["新機能", "登場", "リリース", "神", "すごい", "爆速", "革命"]):
        pick = "bright"      # 新しい話題が多い日は元気に
    elif len(lines) >= 70:
        pick = "quiet"       # 長い回は一番おとなしい曲で疲れさせない
    else:
        pick = "morning"     # 通常は朝向き
    path = os.path.join(BGM_DIR, pick + ".mp3")
    if not os.path.exists(path):
        # 予備：あるものを日替わりで
        cands = sorted(glob.glob(os.path.join(BGM_DIR, "*.mp3")))
        if not cands: return None, None
        try: idx = int(date.replace("-", "")) % len(cands)
        except Exception: idx = 0
        path = cands[idx]; pick = os.path.basename(path)[:-4]
    return path, pick

def check_ffmpeg():
    """音声をまとめる道具があるか先に確かめる"""
    try:
        subprocess.check_output([FFMPEG, "-version"], stderr=subprocess.STDOUT)
        return True
    except Exception as e:
        print("NG: ffmpeg が使えません（%s）: %s" % (FFMPEG, str(e)[:80]))
        return False

def main(edition="all"):
    print("使う ffmpeg: %s" % FFMPEG)
    if not check_ffmpeg():
        return 1
    if not engine_alive():
        print("NG: VOICEVOXのエンジンが動いていません。")
        print("    VOICEVOXアプリを起動してから、もう一度実行してください。")
        return 1
    src = "podcast.json" if edition == "all" else "podcast_%s.json" % edition
    src_path = os.path.join(HERE, "data", src)
    if not os.path.exists(src_path):
        print("  %s の台本がないので飛ばします" % edition)
        return 0
    cast = json.load(io.open(src_path, encoding="utf-8"))
    lines = cast["lines"]
    for d in (OUT_DIR, TMP, CACHE):
        if not os.path.isdir(d): os.makedirs(d)
    for f in glob.glob(os.path.join(TMP, "*")): os.remove(f)

    t0 = time.time()
    parts, reused = [], 0
    for i, l in enumerate(lines):
        sid = SPEAKER.get(l["who"], 3)
        key = hashlib.sha1(("%d|%s" % (sid, l["text"])).encode("utf-8")).hexdigest()[:16]
        wav_path = os.path.join(CACHE, key + ".wav")
        if os.path.exists(wav_path) and os.path.getsize(wav_path) > 1000:
            parts.append(wav_path); reused += 1
            continue
        try:
            q = json.loads(post("/audio_query", params={"text": l["text"], "speaker": sid}))
        except Exception as e:
            print("NG: %d行目の音声化に失敗: %s" % (i, str(e)[:120]))
            print("   セリフ: %s" % l["text"][:60])
            raise
        q["speedScale"] = 1.05
        q["postPhonemeLength"] = 0.15          # セリフ間の間
        wav = post("/synthesis", data=q, params={"speaker": sid})
        io.open(wav_path, "wb").write(wav)
        parts.append(wav_path)
        if (i + 1) % 10 == 0 or i + 1 == len(lines):
            sys.stderr.write("  音声化 %d/%d（%.0f秒経過）\n" % (i + 1, len(lines), time.time() - t0))
    if reused:
        print("  ※ %d行は前の版で作った声を使い回しました" % reused)

    # 全部つなげてmp3に
    listfile = os.path.join(TMP, "list.txt")
    with io.open(listfile, "w", encoding="utf-8") as f:
        for w in parts:
            f.write("file '%s'\n" % w)
    if edition == "all":
        out = os.environ.get("VOICE_OUT") or os.path.join(OUT_DIR, "AIコツ図鑑_%s.mp3" % cast["date"])
    else:
        base = os.environ.get("VOICE_OUT")
        out = (os.path.splitext(base)[0] + "_" + edition + ".mp3") if base \
              else os.path.join(OUT_DIR, "AIコツ図鑑_%s_%s.mp3" % (cast["date"], edition))
    d = os.path.dirname(out)
    if d and not os.path.isdir(d):
        os.makedirs(d)

    bgm, bgm_name = pick_bgm(cast)
    if bgm:
        # 声をつないだものに、BGMを小さく重ねる（ループ＋前後フェード）
        voice_tmp = os.path.join(TMP, "_voice.mp3")
        subprocess.call([FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", listfile,
                         "-codec:a", "libmp3lame", "-b:a", "128k", voice_tmp],
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        # 全体の長さを測って、終わりのフェード開始点を決める
        try:
            r = subprocess.run([FFMPEG, "-i", voice_tmp], capture_output=True, text=True)
            m = re.search(r"Duration: (\d+):(\d+):(\d+)", r.stderr)
            total = int(m.group(1))*3600 + int(m.group(2))*60 + int(m.group(3)) if m else 300
        except Exception:
            total = 300
        fade_out_at = max(total - 6, 1)
        subprocess.call([FFMPEG, "-y", "-i", voice_tmp, "-stream_loop", "-1", "-i", bgm,
                         "-filter_complex",
                         "[1:a]volume=%.2f,afade=t=in:st=0:d=2[bg];"
                         "[0:a][bg]amix=inputs=2:duration=first:dropout_transition=0,"
                         "afade=t=out:st=%d:d=6[out]" % (BGM_VOLUME, fade_out_at),
                         "-map", "[out]", "-codec:a", "libmp3lame", "-b:a", "128k", out],
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("BGM: %s（音量%d%%）" % (bgm_name, int(BGM_VOLUME*100)))
    else:
        subprocess.call([FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", listfile,
                         "-codec:a", "libmp3lame", "-b:a", "128k", out],
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("BGM: なし（bgmフォルダが見つかりません）")
    if not os.path.exists(out):
        print("NG: ffmpeg での結合に失敗しました（生成した部品は %d個）" % len(lines))
    if os.path.exists(out):
        mb = os.path.getsize(out) / 1024.0 / 1024.0
        print("できました: %s（%.1fMB）" % (out, mb))
        for f in glob.glob(os.path.join(TMP, "*")): os.remove(f)   # ※キャッシュは残す
        return 0
    print("NG: mp3の作成に失敗しました")
    return 1

if __name__ == "__main__":
    eds = sys.argv[1:] or ["all"]
    rc = 0
    try:
        for e in eds:
            print("---- %s ----" % e)
            rc = main(e) or rc
    finally:
        # その日のぶんの声は用が済んだので消す（ためこまない）
        for f in glob.glob(os.path.join(CACHE, "*.wav")):
            try: os.remove(f)
            except Exception: pass
    sys.exit(rc)
