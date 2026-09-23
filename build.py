# -*- coding: utf-8 -*-
"""data/*.json から サイト/index.html を作る（Python標準ライブラリのみ）"""
from __future__ import unicode_literals
import json, io, os
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
# 出力先：GitHub上（.githubフォルダがある）ならリポジトリ直下、手元なら「サイト」フォルダ
OUTDIR = HERE if os.path.isdir(os.path.join(HERE, ".github")) else os.path.join(HERE, "サイト")
OUT = os.path.join(OUTDIR, "index.html")

def load_obj(name):
    p = os.path.join(HERE, "data", name)
    if not os.path.exists(p):
        return {}
    try:
        return json.load(io.open(p, encoding="utf-8"))
    except Exception:
        return {}

def load(name, key):
    p = os.path.join(HERE, "data", name)
    if not os.path.exists(p):
        return []
    try:
        return json.load(io.open(p, encoding="utf-8")).get(key, [])
    except Exception:
        return []

TEMPLATE = r"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow, noarchive, nosnippet">
<meta name="googlebot" content="noindex, nofollow">
<title>AIコツ図鑑</title>
<link rel="icon" type="image/svg+xml" href="favicon.svg?v=2">
<link rel="icon" type="image/png" sizes="32x32" href="favicon-32.png?v=2">
<link rel="shortcut icon" href="favicon.ico?v=2">
<link rel="apple-touch-icon" href="apple-touch-icon.png?v=2">
<link rel="manifest" href="site.webmanifest">
<meta name="theme-color" content="#c2512a">
<style>
:root{
  --bg:#f7f7f5; --panel:#ffffff; --ink:#1c1c1a; --muted:#6b6b63; --line:#e3e3dd;
  --accent:#c2512a; --accent-soft:#fdf0e9; --shadow:0 1px 2px rgba(0,0,0,.05),0 8px 24px rgba(0,0,0,.05);
  --chatgpt:#10a37f; --claude:#c2512a; --gemini:#3d7de8; --copilot:#7a4fd6; --other:#7a7a70;
}
:root:not([data-theme="light"]){ }
@media (prefers-color-scheme: dark){
  :root:not([data-theme="light"]){
    --bg:#16161a; --panel:#1f1f24; --ink:#ecece8; --muted:#9a9a93; --line:#32323a;
    --accent:#e8794a; --accent-soft:#2a1e18; --shadow:0 1px 2px rgba(0,0,0,.4),0 8px 24px rgba(0,0,0,.35);
  }
}
:root[data-theme="dark"]{
  --bg:#16161a; --panel:#1f1f24; --ink:#ecece8; --muted:#9a9a93; --line:#32323a;
  --accent:#e8794a; --accent-soft:#2a1e18; --shadow:0 1px 2px rgba(0,0,0,.4),0 8px 24px rgba(0,0,0,.35);
}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);
  font-family:"Hiragino Sans","Hiragino Kaku Gothic ProN","Meiryo",system-ui,sans-serif;
  line-height:1.7;-webkit-font-smoothing:antialiased}
a{color:inherit}
header{position:sticky;top:0;z-index:20;background:var(--bg);border-bottom:1px solid var(--line)}
.wrap{max-width:1080px;margin:0 auto;padding:0 16px}
.top{display:flex;align-items:baseline;gap:12px;flex-wrap:wrap;padding:14px 0 10px}
h1{font-size:19px;margin:0;letter-spacing:.02em}
h1 span{color:var(--accent)}
.sub{font-size:12px;color:var(--muted)}
.themebtn{margin-left:8px;border:1px solid var(--line);background:var(--panel);color:var(--muted);
  border-radius:999px;padding:5px 12px;font-size:12px;cursor:pointer}
.tabs{display:flex;gap:4px;padding-bottom:0}
.tab{border:0;background:none;color:var(--muted);font-size:14px;font-weight:600;padding:9px 14px;
  cursor:pointer;border-bottom:2px solid transparent;font-family:inherit}
.tab.on{color:var(--ink);border-bottom-color:var(--accent)}
.toolbar{display:flex;gap:8px;flex-wrap:wrap;align-items:center;padding:14px 0 6px}
input[type=search]{flex:1;min-width:200px;padding:9px 13px;border:1px solid var(--line);border-radius:9px;
  background:var(--panel);color:var(--ink);font-size:14px;font-family:inherit}
.pills{display:flex;gap:6px;flex-wrap:wrap;padding:8px 0 16px}
.pill{border:1px solid var(--line);background:var(--panel);color:var(--muted);border-radius:999px;
  padding:5px 12px;font-size:13px;cursor:pointer;font-family:inherit}
.pill.on{background:var(--ink);color:var(--bg);border-color:var(--ink)}
.pill b{font-weight:600;opacity:.6;margin-left:5px;font-size:11px}
main{padding:0 0 80px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(320px,1fr));gap:14px}
@media(min-width:1180px){ .grid{grid-template-columns:repeat(3,1fr)} }
.card{background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:18px;
  box-shadow:var(--shadow);display:flex;flex-direction:column;gap:10px}
.badges{display:flex;gap:6px;align-items:center;flex-wrap:wrap;font-size:11px}
.ai{padding:2px 9px;border-radius:999px;color:#fff;font-weight:700;letter-spacing:.03em}
.ai.ChatGPT{background:var(--chatgpt)} .ai.Claude{background:var(--claude)}
.ai.Gemini{background:var(--gemini)} .ai.Copilot{background:var(--copilot)}
.ai\.その他,.ai.other{background:var(--other)}
.org{border-radius:5px;padding:1px 7px;font-weight:700;letter-spacing:.02em}
.org.X{background:#111;color:#fff} .org.YouTube{background:#e03b2f;color:#fff}
.org.note{background:#2cb696;color:#fff} .org.Claude{background:var(--accent-soft);color:var(--accent);border:1px solid var(--accent)}
.lv{color:var(--muted);border:1px solid var(--line);border-radius:999px;padding:2px 8px}
.card h3{margin:0;font-size:16px;line-height:1.5}
.sum{margin:0;font-size:13.5px;color:var(--ink)}
.why{margin:0;font-size:12.5px;color:var(--muted);border-left:2px solid var(--line);padding-left:10px}
ol.steps{margin:0;padding-left:20px;font-size:13px;color:var(--ink)}
ol.steps li{margin:3px 0}
.promptbox{position:relative;background:var(--accent-soft);border:1px solid var(--line);border-radius:10px;
  padding:12px 12px 10px;font-size:12.5px;white-space:pre-wrap;word-break:break-word;
  font-family:ui-monospace,"SF Mono",Menlo,monospace;max-height:210px;overflow:auto}
.fav{border:1px solid var(--line);background:var(--panel);color:var(--muted);border-radius:7px;
  padding:2px 9px;font-size:12px;cursor:pointer;font-family:inherit;margin-left:auto}
.fav.on{background:#f5b301;color:#2a2200;border-color:#f5b301;font-weight:700}
.copy{position:absolute;top:8px;right:8px;border:1px solid var(--line);background:var(--panel);
  color:var(--muted);border-radius:7px;padding:3px 9px;font-size:11px;cursor:pointer;font-family:inherit}
.copy.done{background:var(--accent);color:#fff;border-color:var(--accent)}
.foot{display:flex;gap:8px;flex-wrap:wrap;align-items:center;font-size:11.5px;color:var(--muted);
  border-top:1px solid var(--line);padding-top:9px;margin-top:auto}
.tag{background:var(--bg);border:1px solid var(--line);border-radius:6px;padding:1px 7px}
.src{margin-left:auto;text-decoration:none;color:var(--accent);font-weight:600}
.unverified{color:#a8783a}
.newsrow{display:flex;gap:10px;align-items:baseline;padding:10px 4px;border-bottom:1px solid var(--line);font-size:14px}
.newsrow .d{color:var(--muted);font-size:11.5px;white-space:nowrap;width:74px;flex:none}
.newsrow a{text-decoration:none}
.newsrow a:hover{color:var(--accent)}
.newsrow .s{color:var(--muted);font-size:11.5px;white-space:nowrap}
.thumb{flex:none;width:120px;height:68px;border-radius:9px;object-fit:cover;background:var(--bg);
  border:1px solid var(--line)}
.thumbx{flex:none;width:120px;height:68px;border-radius:9px;display:flex;align-items:center;justify-content:center;
  font-weight:800;font-size:19px;color:#fff;letter-spacing:.02em;border:1px solid var(--line)}
.fbody{flex:1;min-width:0}
.frow{display:flex;gap:12px;align-items:flex-start}
.nthumb{flex:none;width:56px;height:38px;border-radius:6px;object-fit:cover;border:1px solid var(--line);background:var(--bg)}
.nthumbx{flex:none;width:56px;height:38px;border-radius:6px;display:flex;align-items:center;justify-content:center;
  font-weight:800;font-size:12px;color:#fff;border:1px solid var(--line)}
@media(max-width:600px){ .thumb,.thumbx{width:96px;height:56px} .nthumb,.nthumbx{width:44px;height:30px} }
.fcard{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:14px 16px;
  margin-bottom:10px;box-shadow:var(--shadow)}
.fhead{display:flex;gap:8px;align-items:center;flex-wrap:wrap;font-size:11.5px;color:var(--muted);margin-bottom:6px}
.who{font-weight:700;color:var(--ink)}
.kind{border:1px solid var(--line);border-radius:5px;padding:1px 6px}
.ftitle{font-size:15px;font-weight:600;text-decoration:none;line-height:1.5;display:block;margin-bottom:5px}
.ftitle:hover{color:var(--accent)}
.fsum{font-size:12.5px;color:var(--muted);margin:0 0 6px}
details.chap{font-size:12.5px}
details.chap summary{cursor:pointer;color:var(--accent);font-weight:600;font-size:12px;outline:none}
details.chap ul{margin:7px 0 0;padding-left:18px;color:var(--ink)}
details.chap li{margin:2px 0}
details.chap .t{color:var(--muted);font-family:ui-monospace,Menlo,monospace;font-size:11px;margin-right:6px}
.sec{margin:6px 0 26px}
.sec h2{font-size:14px;margin:0 0 10px;letter-spacing:.04em;color:var(--muted);
  display:flex;align-items:center;gap:8px}
.sec h2 em{font-style:normal;background:var(--accent);color:#fff;border-radius:999px;
  padding:1px 8px;font-size:11px}
.sec h2 a{margin-left:auto;font-size:11.5px;color:var(--accent);text-decoration:none;font-weight:600}
.big{background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:16px 18px;
  box-shadow:var(--shadow);margin-bottom:12px}
.big h3{margin:0 0 6px;font-size:15.5px;line-height:1.5}
.big h3 a{text-decoration:none}
.big h3 a:hover{color:var(--accent)}
.zero{color:var(--muted);font-size:13px;padding:10px 0}
.when{color:var(--muted);font-size:11.5px;white-space:nowrap}
.when.today{color:var(--accent);font-weight:700}
.lang{border:1px solid var(--line);border-radius:4px;padding:0 5px;font-size:10px;color:var(--muted)}
.more{display:block;width:100%;margin:18px 0 0;padding:11px;border:1px solid var(--line);
  background:var(--panel);color:var(--ink);border-radius:10px;font-size:13.5px;cursor:pointer;font-family:inherit}
.more:hover{border-color:var(--accent);color:var(--accent)}
.totop{position:fixed;right:16px;bottom:16px;z-index:30;border:1px solid var(--line);background:var(--panel);
  color:var(--muted);border-radius:999px;width:42px;height:42px;cursor:pointer;font-size:16px;
  box-shadow:var(--shadow);display:none}
.totop.show{display:block}
mark{background:#ffe58a;color:#231c00;border-radius:3px;padding:0 1px}
:root[data-theme="dark"] mark{background:#6b5a1a;color:#fff}
a:visited .ftitle,.newsrow a:visited{opacity:.62}
.edrow{display:flex;gap:6px;overflow-x:auto;padding:0 0 10px;-webkit-overflow-scrolling:touch}
.edpill{flex:0 0 auto;border:1px solid var(--line);background:var(--panel);color:var(--fg);
  border-radius:999px;padding:7px 13px;font-size:12.5px;font-weight:700;cursor:pointer;white-space:nowrap}
.edpill b{font-weight:600;color:var(--muted);margin-left:5px;font-size:11px}
.edpill.on{background:var(--accent);color:#fff;border-color:var(--accent)}
.edpill.on b{color:rgba(255,255,255,.8)}
.edtag{margin-left:7px;font-size:11px;font-weight:700;background:var(--accent);color:#fff;
  border-radius:999px;padding:2px 8px;vertical-align:middle}
.castbar{position:sticky;top:96px;z-index:15;background:var(--panel);border:1px solid var(--line);
  border-radius:12px;padding:12px 14px;margin-bottom:16px;box-shadow:var(--shadow);
  display:flex;gap:10px;align-items:center;flex-wrap:wrap}
.castmeta{font-size:12px;color:var(--muted);margin-left:auto}
.line{display:flex;gap:10px;margin-bottom:12px;align-items:flex-start}
.line .who{flex:none;width:58px;font-size:11px;font-weight:700;text-align:center;
  border-radius:8px;padding:5px 0;line-height:1.3}
.line.metan .who{background:#f0e2f5;color:#6b2d80}
.line.zunda .who{background:#dff3dc;color:#2a6b28}
:root[data-theme="dark"] .line.metan .who{background:#3a2440;color:#e9c9f5}
:root[data-theme="dark"] .line.zunda .who{background:#25381f;color:#c5edbe}
.line .txt{flex:1;font-size:15px;line-height:1.8;padding:6px 12px;border-radius:12px;
  background:var(--panel);border:1px solid var(--line);transition:background .2s}
.line.now .txt{background:var(--accent-soft);border-color:var(--accent)}
.audiobox{background:var(--accent-soft);border:2px solid var(--accent);border-radius:12px;
  padding:14px;margin-bottom:14px;box-shadow:var(--shadow)}
.audiobox h3{margin:0 0 4px;font-size:14px}
.audiobox audio{width:100%;margin-top:8px}
.audiobox .note{font-size:11.5px;color:var(--muted);margin:4px 0 0}
.audiobox a{color:var(--accent);font-weight:600;text-decoration:none;font-size:12px}
.credit{font-size:11.5px;color:var(--muted);margin-top:18px;text-align:right}
.empty{color:var(--muted);padding:40px 0;text-align:center;font-size:14px}
.hint{font-size:12px;color:var(--muted);padding:2px 0 14px}
/* 空の絞り込み行が余白を作らないように */
.pills:empty{display:none;padding:0;margin:0}
.fwrap{display:none}
.fwrap.open{display:block}
.fhead{display:flex;gap:8px;align-items:center;padding:6px 0 2px;flex-wrap:wrap}
.fbtn{border:1px solid var(--line);background:var(--panel);color:var(--ink);border-radius:999px;
  padding:6px 13px;font-size:12.5px;cursor:pointer;font-family:inherit;font-weight:600}
.fbtn.act{background:var(--accent);color:#fff;border-color:var(--accent)}
.fsum2{font-size:12px;color:var(--muted)}
/* 動画・noteの説明文は3行まで（長すぎると一覧が読めない） */
.fsum{display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden}
@media(max-width:600px){
  .grid{grid-template-columns:1fr} h1{font-size:17px} .newsrow{flex-wrap:wrap}
  /* タブは折り返さず横スクロールにする（縦書きになるのを防ぐ） */
  .tabs{flex-wrap:nowrap;overflow-x:auto;-webkit-overflow-scrolling:touch;scrollbar-width:none}
  .tabs::-webkit-scrollbar{display:none}
  .tab{white-space:nowrap;flex:0 0 auto;font-size:13px;padding:9px 10px}
  .top{padding-bottom:6px}
  .themebtn{font-size:11px;padding:4px 9px}
  .toolbar{padding:10px 0 4px}
  .pills{padding:6px 0 10px}
  .big h3{font-size:14.5px}
  .fsum{-webkit-line-clamp:2}
}
</style>
</head>
<body>
<header>
 <div class="wrap">
  <div class="top">
    <h1>AI<span>コツ</span>図鑑</h1>
    <div class="sub" id="stamp"></div>
    <button class="themebtn" id="likeExport" style="margin-left:auto" title="いいねした一覧をコピーします">👍 好みをClaudeに渡す</button>
    <button class="themebtn" id="theme">◐ 表示</button>
  </div>
  <div class="tabs">
    <button class="tab on" data-view="home">🏠 今日</button>
    <button class="tab" data-view="cast">🎧 今日の10分</button>
    <button class="tab" data-view="tips">💡 コツ</button>
    <button class="tab" data-view="feed">🎥 動画・note</button>
    <button class="tab" data-view="news">📰 ニュース</button>
  </div>
 </div>
</header>
<button class="totop" id="totop" title="上に戻る">↑</button>
<main class="wrap">
  <div class="toolbar">
    <input type="search" id="q" placeholder="キーワードで探す（例：Excel、提案書、要約）">
  </div>
  <div class="pills" id="aipills"></div>
  <div id="filterhead"></div>
  <div id="filterwrap" class="fwrap">
  <div class="pills" id="filterpills"></div>
  <div class="pills" id="tagpills"></div>
  <div class="pills" id="authorpills"></div>
  </div>
  <div class="hint" id="hint"></div>
  <div id="body"></div>
</main>
<script>
const DATA = __DATA__;
let view="home", ai="すべて", tag="すべて", author="すべて", q="", onlyNew=false, onlyChap=false;
let onlyLiked=false;
let level="すべて", onlyPrompt=false, sortBy="新着順", showAllTags=false, useFor="すべて";
const FAV_KEY="aikotsu_like";
function favs(){ try{ return JSON.parse(localStorage.getItem(FAV_KEY)||"[]"); }catch(e){ return []; } }
function likeMeta(){ try{ return JSON.parse(localStorage.getItem(FAV_KEY+"_meta")||"{}"); }catch(e){ return {}; } }
function toggleFav(id, info){
  const f=favs(); const i=f.indexOf(id);
  const meta=likeMeta();
  if(i<0){ f.push(id); meta[id]=Object.assign({at:new Date().toISOString().slice(0,10)}, info||{}); }
  else { f.splice(i,1); delete meta[id]; }
  try{ localStorage.setItem(FAV_KEY, JSON.stringify(f));
       localStorage.setItem(FAV_KEY+"_meta", JSON.stringify(meta)); }catch(e){}
  render();
}
/* いいねの一覧を、Claudeに渡せる形で書き出す */
function exportLikes(){
  const meta=likeMeta(); const ids=favs();
  const rows=ids.map(id=>{
    const m=meta[id]||{};
    return {id:id, kind:m.kind||"", title:m.title||"", ai:m.ai||"", tags:m.tags||[],
            level:m.level||"", author:m.author||"", at:m.at||""};
  });
  const out=JSON.stringify({exported:new Date().toISOString().slice(0,16), count:rows.length, likes:rows}, null, 1);
  navigator.clipboard.writeText(out).then(()=>{
    alert("いいね "+rows.length+"件をコピーしました。\nClaudeのチャットに貼り付けてください。");
  }).catch(()=>{
    const b=new Blob([out],{type:"application/json"});
    const a=document.createElement("a"); a.href=URL.createObjectURL(b);
    a.download="私のいいね.json"; a.click();
  });
}

const el=(s)=>document.querySelector(s);
const PAGE=40; let shown=PAGE;
function whenLabel(d){
  if(!d) return "";
  const n=daysAgo(d);
  if(n===0) return "今日";
  if(n===1) return "昨日";
  if(n<7) return n+"日前";
  return d;
}
function hl(s){
  if(!q) return s;
  try{ return s.replace(new RegExp("("+q.replace(/[.*+?^${}()|[\]\\]/g,"\\$&")+")","gi"),"<mark>$1</mark>"); }
  catch(e){ return s; }
}
const esc=(s)=>(s||"").replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;");
function hue(str){ let h=0; for(const c of (str||"")) h=(h*31+c.charCodeAt(0))%360; return h; }
function thumbHtml(item, small){
  const cls = small ? "nthumb" : "thumb";
  const clsx = small ? "nthumbx" : "thumbx";
  const label = (item.author || item.source || "?").replace(/[【】（）\(\)]/g,"").trim().slice(0, small?1:2);
  if(item.thumb){
    return `<img class="${cls}" src="${esc(item.thumb)}" alt="" loading="lazy" referrerpolicy="no-referrer"
      onerror="this.outerHTML='<span class=\'${clsx}\' style=\'background:hsl(${hue(item.author||item.source)},42%,52%)\'>${esc(label)}</span>'">`;
  }
  return `<span class="${clsx}" style="background:hsl(${hue(item.author||item.source)},42%,52%)">${esc(label)}</span>`;
}
const aiClass=(a)=>({"ChatGPT":"ChatGPT","Claude":"Claude","Gemini":"Gemini","Copilot":"Copilot"}[a]||"other");

el("#stamp").textContent = "コツ "+DATA.tips.length+"件 ／ 動画・note "+DATA.feed.length+"件 ／ ニュース "+DATA.news.length+"件 ・ 更新 "+DATA.updated;

/* 表示の切り替え（明るい／暗い） */
const saved=(()=>{try{return localStorage.getItem("theme")}catch(e){return null}})();
if(saved) document.documentElement.setAttribute("data-theme",saved);
el("#likeExport").onclick=exportLikes;
el("#theme").onclick=()=>{
  const now=document.documentElement.getAttribute("data-theme")==="dark"?"light":"dark";
  document.documentElement.setAttribute("data-theme",now);
  try{localStorage.setItem("theme",now)}catch(e){}
};

document.querySelectorAll(".tab").forEach(t=>t.onclick=()=>{
  document.querySelectorAll(".tab").forEach(x=>x.classList.remove("on"));
  t.classList.add("on"); view=t.dataset.view; onlyLiked=false; ai="すべて"; tag="すべて"; author="すべて"; onlyNew=false; onlyChap=false; level="すべて"; onlyPrompt=false; useFor="すべて"; shown=PAGE; render();
});
el("#q").oninput=(e)=>{q=e.target.value.trim().toLowerCase(); shown=PAGE; render();};

function likeBar(){
  const n = items().filter(x=>favs().includes(x.id||x.url)).length;
  return `<button class="pill ${onlyLiked?"on":""}" id="fLiked">👍 いいねしたもの<b>${n}</b></button>`;
}
function items(){ return view==="tips"?DATA.tips:(view==="feed"?DATA.feed:DATA.news); }

/* ===== 今日の10分 ===== */
const ED_KEY="aikotsu_edition";
let castEd=(function(){ try{ return localStorage.getItem(ED_KEY)||"all"; }catch(e){ return "all"; } })();
function edList(){ return Object.keys(DATA.casts||{}); }
function edSwitch(){
  const ks=edList();
  if(ks.length<2) return "";
  if(ks.indexOf(castEd)<0) castEd=ks[0];
  const emoji={all:"🎁",claude:"🟠",gemini:"🔵",chatgpt:"🟢",news:"📰"};
  return `<div class="edrow" id="edrow">`+ks.map(k=>{
    const c=DATA.casts[k];
    return `<button class="edpill ${k===castEd?"on":""}" data-ed="${k}">`+
           `${emoji[k]||"🎧"} ${esc(c.label||k)}<b>${c.minutes}分</b></button>`;
  }).join("")+`</div>`;
}
function castView(){
  const all=DATA.casts||{};
  const c=(all[castEd])||DATA.cast||{};
  const ls=c.lines||[];
  if(!ls.length) return edSwitch()+`<p class="empty">今日の台本はまだ作られていません。</p>`;
  const body=ls.map((l,i)=>
    `<div class="line ${l.who==="zunda"?"zunda":"metan"}" data-i="${i}">
       <span class="who">${l.who==="zunda"?"ずんだもん":"四国めたん"}</span>
       <span class="txt">${esc(l.text)}</span></div>`).join("")
    + `<p class="credit">${esc(c.credit||"")}</p>`;
  const mp3="https://github.com/ryuguuu38/ai-kotsu/releases/download/audio/today"
            +(castEd&&castEd!=="all"?"_"+castEd:"")+".mp3";
  const player=`<div class="audiobox">
      <h3>🔊 ずんだもん × 四国めたん<span class="edtag">${esc(c.label||"全部")}</span></h3>
      <audio controls preload="none" src="${mp3}"></audio>
      <p class="note" id="vnote">毎朝7時すぎに自動で更新されます。
        <a href="${mp3}" download>ダウンロード ↓</a></p>
    </div>`;
  // 台本より音声が古い場合は警告を出す
  const vb = (c.voice_built||"").slice(0,10);
  const stale = vb && c.date && vb < c.date;
  const warn = stale
    ? `<p class="note" style="color:#b4531f"><b>⚠️ この音声は ${esc(vb)} 版です。</b>下の台本（${esc(c.date)}版）とは内容が違います。次の自動更新（毎朝7時）で揃います。</p>`
    : (vb ? `<p class="note">音声も台本も ${esc(vb)} 版です ✅</p>` : "");
  return edSwitch() + player.replace("</div>", warn + "</div>") + `<div class="castbar">
      <span class="castmeta" style="margin-left:0">台本（約${c.minutes}分・${c.date}版）／ セリフを押すとその場所を目立たせます</span>
    </div>
    <div class="script">${body}</div>`;
}

function match(it){
  if(onlyLiked){
    const key = it.id || it.url;
    if(!favs().includes(key)) return false;
  }
  if(ai!=="すべて" && it.ai!==ai) return false;
  if(view==="tips"){
    if(level!=="すべて" && it.level!==level) return false;
    if(onlyPrompt && !it.prompt) return false;
    if(useFor!=="すべて" && it.use!==useFor && it.use!=="両方") return false;
  }
  if(view==="tips" && tag!=="すべて"){
    if(tag==="★お気に入り"){ if(!favs().includes(it.id)) return false; }
    else if(tag.indexOf("出どころ:")===0){ if((it.origin||"Claude")!==tag.slice(5)) return false; }
    else if(!(it.tags||[]).includes(tag)) return false;
  }
  if(view==="feed"){
    if(author!=="すべて" && it.author!==author) return false;
    if(onlyNew && daysAgo(it.date)>2) return false;
    if(onlyChap && !(it.chapters||[]).length) return false;
  }
  if(!q) return true;
  return JSON.stringify(it).toLowerCase().indexOf(q)>=0;
}

function pills(){
  const order=["すべて","ChatGPT","Claude","Gemini","Copilot","その他"];
  const base=items().filter(it=>!q||JSON.stringify(it).toLowerCase().indexOf(q)>=0);
  el("#aipills").innerHTML=order.map(a=>{
    const n=a==="すべて"?base.length:base.filter(x=>x.ai===a).length;
    return `<button class="pill ${a===ai?"on":""}" data-ai="${a}">${a}<b>${n}</b></button>`;
  }).join("");
  document.querySelectorAll("[data-ai]").forEach(b=>b.onclick=()=>{ai=b.dataset.ai;shown=PAGE;render();});

  if(view==="tips"){
    const base=DATA.tips.filter(t=>(ai==="すべて"||t.ai===ai));
    const lv=(L)=>base.filter(t=>t.level===L).length;
    const un=(U)=>DATA.tips.filter(t=>t.use===U||t.use==="両方").length;
    el("#filterpills").innerHTML = likeBar() +
      `<button class="pill ${useFor==="自分用"?"on":""}" data-use="自分用">🙋 自分用<b>${un("自分用")}</b></button>`+
      `<button class="pill ${useFor==="提案用"?"on":""}" data-use="提案用">💼 提案・研修用<b>${un("提案用")}</b></button>`+
      `<span style="width:10px"></span>`+
      ["初級","中級","上級"].map(L=>
        `<button class="pill ${level===L?"on":""}" data-lv="${L}">${L}<b>${lv(L)}</b></button>`).join("")
      + `<button class="pill ${onlyPrompt?"on":""}" id="fPrompt">📋 コピーできる<b>${base.filter(t=>t.prompt).length}</b></button>`
      + `<button class="pill" id="fSort">↕ ${sortBy}</button>`
      + (level!=="すべて"||onlyPrompt||useFor!=="すべて" ? `<button class="pill" id="fClear">✕ 絞り込み解除</button>` : "");
    document.querySelectorAll("[data-use]").forEach(b=>b.onclick=()=>{
      useFor = (useFor===b.dataset.use) ? "すべて" : b.dataset.use; shown=PAGE; render();});
    document.querySelectorAll("[data-lv]").forEach(b=>b.onclick=()=>{
      level = (level===b.dataset.lv) ? "すべて" : b.dataset.lv; shown=PAGE; render();});
    el("#fPrompt").onclick=()=>{onlyPrompt=!onlyPrompt;shown=PAGE;render();};
    el("#fSort").onclick=()=>{sortBy = sortBy==="新着順"?"AI順":"新着順"; render();};
    const fc=el("#fClear"); if(fc) fc.onclick=()=>{level="すべて";onlyPrompt=false;useFor="すべて";shown=PAGE;render();};

    const origins=[...new Set(DATA.tips.map(t=>t.origin||"Claude"))].map(o=>"出どころ:"+o);
    const all=["すべて"].concat(favs().length?["★お気に入り"]:[]).concat(origins)
              .concat([...new Set(DATA.tips.flatMap(t=>t.tags||[]))]);
    const shownTags = showAllTags ? all : all.slice(0, 9);
    el("#tagpills").innerHTML=shownTags.map(t=>
      `<button class="pill ${t===tag?"on":""}" data-tag="${t}">${t}</button>`).join("")
      + (all.length>9 ? `<button class="pill" id="moreTags">${showAllTags?"タグを閉じる":"タグをもっと見る（+"+(all.length-9)+"）"}</button>` : "");
    document.querySelectorAll("[data-tag]").forEach(b=>b.onclick=()=>{tag=b.dataset.tag;shown=PAGE;render();});
    const mt=el("#moreTags"); if(mt) mt.onclick=()=>{showAllTags=!showAllTags;render();};
  } else if(view==="news"){
    el("#tagpills").innerHTML = likeBar();
    const lb2=el("#fLiked"); if(lb2) lb2.onclick=()=>{onlyLiked=!onlyLiked;shown=PAGE;render();};
    el("#filterpills").innerHTML=""; el("#authorpills").innerHTML="";
  } else { el("#tagpills").innerHTML=""; el("#filterpills").innerHTML=""; }

  if(view==="feed"){
    const nNew=DATA.feed.filter(f=>daysAgo(f.date)<=2).length;
    const nChap=DATA.feed.filter(f=>(f.chapters||[]).length).length;
    el("#tagpills").innerHTML = likeBar() +
      (view==="feed" ? `<button class="pill ${onlyNew?"on":""}" id="fNew">🆕 直近2日<b>${nNew}</b></button>` : "")+
      (view==="feed" ? `<button class="pill ${onlyChap?"on":""}" id="fChap">📑 目次あり<b>${nChap}</b></button>` : "");
    if(el("#fNew")) el("#fNew").onclick=()=>{onlyNew=!onlyNew;shown=PAGE;render();};
    if(el("#fChap")) el("#fChap").onclick=()=>{onlyChap=!onlyChap;shown=PAGE;render();};
    const names=["すべて"].concat([...new Set(DATA.feed.map(f=>f.author))]);
    el("#authorpills").innerHTML=names.map(a=>{
      const n=a==="すべて"?DATA.feed.length:DATA.feed.filter(x=>x.author===a).length;
      const mark=a!=="すべて"&&(DATA.feed.find(x=>x.author===a)||{}).pick==="オーナー指定"?"★":"";
      const fresh=a==="すべて"?DATA.feed.filter(x=>daysAgo(x.date)<=2).length
                              :DATA.feed.filter(x=>x.author===a&&daysAgo(x.date)<=2).length;
      return `<button class="pill ${a===author?"on":""}" data-au="${a}">${mark}${a}<b>${fresh?"🆕"+fresh+" / ":""}${n}</b></button>`;
    }).join("");
    document.querySelectorAll("[data-au]").forEach(b=>b.onclick=()=>{author=b.dataset.au;shown=PAGE;render();});
  } else el("#authorpills").innerHTML="";
}

function feedCard(f){
  const chap=(f.chapters||[]).length? `<details class="chap"><summary>この回の内容（目次 ${f.chapters.length}項目）</summary><ul>`
      + f.chapters.map(c=>`<li><span class="t">${esc(c.t)}</span>${esc(c.label)}</li>`).join("") + `</ul></details>` : "";
  return `<article class="fcard"><div class="frow">${thumbHtml(f,false)}<div class="fbody">
    <div class="fhead"><span class="who">${f.pick==="オーナー指定"?"★ ":""}${esc(f.author)}</span>
      <span class="kind">${f.kind==="youtube"?"YouTube":"note"}</span>
      <span class="ai ${aiClass(f.ai)}" style="font-size:10px">${esc(f.ai)}</span>
      <span class="${daysAgo(f.date)<=1?"when today":"when"}">${esc(whenLabel(f.date))}</span></div>
    <button class="fav ${favs().includes(f.url)?"on":""}" data-fav="${esc(f.url)}" style="float:right;margin:0 0 4px 8px"
      data-info='${esc(JSON.stringify({kind:f.kind,title:f.title,ai:f.ai,author:f.author}))}'
      >${favs().includes(f.url)?"👍":"👍 いいね"}</button>
    <a class="ftitle" href="${esc(f.url)}" target="_blank" rel="noopener">${hl(esc(f.title))}</a>
    ${f.summary?`<p class="fsum">${esc(f.summary)}</p>`:""}
    ${chap}
  </div></div></article>`;
}

function tipCard(t){
  const st=(t.steps||[]);
  const steps = st.length<=5
    ? st.map(s=>`<li>${esc(s)}</li>`).join("")
    : st.slice(0,4).map(s=>`<li>${esc(s)}</li>`).join("")
      + `</ol><details class="chap"><summary>残り${st.length-4}手順を見る</summary><ol class="steps" start="5">`
      + st.slice(4).map(s=>`<li>${esc(s)}</li>`).join("") + `</ol></details><ol class="steps" style="display:none">`;
  const prompt=t.prompt?`<div class="promptbox"><button class="copy">コピー</button>${esc(t.prompt)}</div>`:"";
  const src = (t.source && t.source.url)
    ? `<a class="src" href="${esc(t.source.url)}" target="_blank" rel="noopener">出典 ↗</a>`
    : (t.source ? `<span class="src" style="color:var(--muted);font-weight:600" title="${esc(t.source.title||"")}">出典: 配布教材</span>`
                : `<span class="src unverified">出典なし</span>`);
  return `<article class="card">
    <div class="badges"><span class="ai ${aiClass(t.ai)}">${esc(t.ai)}</span>
      <span class="lv">${esc(t.level||"")}</span>
      <span class="org ${esc(t.origin||"Claude")}">${t.origin==="Claude"?"Claude独自":esc(t.origin||"Claude")}</span>
      <button class="fav ${favs().includes(t.id)?"on":""}" data-fav="${esc(t.id)}"
        data-info='${esc(JSON.stringify({kind:"tip",title:t.title,ai:t.ai,tags:t.tags||[],level:t.level}))}'
        >${favs().includes(t.id)?"👍 いいね済":"👍 いいね"}</button></div>
    <h3>${esc(t.title)}</h3>
    <p class="sum">${esc(t.summary)}</p>
    ${t.why?`<p class="why">${esc(t.why)}</p>`:""}
    ${steps?`<ol class="steps">${steps}</ol>`:""}
    ${prompt}
    <div class="foot">${(t.tags||[]).map(x=>`<span class="tag">${esc(x)}</span>`).join("")}${src}</div>
  </article>`;
}

function newsRow(n){
  const w=whenLabel(n.date);
  return `<div class="newsrow">${thumbHtml(n,true)}<span class="d ${daysAgo(n.date)===0?"when today":"when"}">${esc(w)}</span>
    <span class="ai ${aiClass(n.ai)}" style="font-size:10px">${esc(n.ai)}</span>
    <a href="${esc(n.url)}" target="_blank" rel="noopener">${hl(esc(n.title))}</a>
    <span class="s">${esc(n.source)}</span>
    ${n.lang==="en"?`<span class="lang">英語</span>`:""}
    <button class="fav ${favs().includes(n.url)?"on":""}" data-fav="${esc(n.url)}" style="margin-left:auto;padding:1px 7px;font-size:11px"
      data-info='${esc(JSON.stringify({kind:"news",title:n.title,ai:n.ai,author:n.source}))}'
      >${favs().includes(n.url)?"👍":"👍"}</button></div>`;
}

function daysAgo(d){
  if(!d) return 999;
  const p=String(d).split("-");
  if(p.length<3) return 999;
  const t=new Date();
  const today=Date.UTC(t.getFullYear(), t.getMonth(), t.getDate());
  const x=Date.UTC(+p[0], +p[1]-1, +p[2]);
  const n=Math.round((today-x)/86400000);
  return n<0 ? 0 : n;   // 時差で未来日付になった分は「今日」扱い
}

function homeView(){
  const fresh = DATA.feed.filter(f=>daysAgo(f.date)<=2).slice(0,5);
  const news  = DATA.news.filter(n=>daysAgo(n.date)<=1).slice(0,6);
  const recentTips = [...DATA.tips].reverse().slice(0,3);
  const box = (f)=>`<div class="big"><div class="frow">${thumbHtml(f,false)}<div class="fbody">
      <div class="fhead"><span class="who">${f.pick==="オーナー指定"?"★ ":""}${esc(f.author)}</span>
        <span class="kind">${f.kind==="youtube"?"YouTube":"note"}</span>
        <span class="ai ${aiClass(f.ai)}" style="font-size:10px">${esc(f.ai)}</span>
        <span class="${daysAgo(f.date)<=1?"when today":"when"}">${esc(whenLabel(f.date))}</span></div>
      <h3><a href="${esc(f.url)}" target="_blank" rel="noopener">${esc(f.title)}</a></h3>
      ${f.summary?`<p class="fsum">${esc(f.summary)}</p>`:""}
      ${(f.chapters||[]).length?`<details class="chap"><summary>この回の内容（目次 ${f.chapters.length}項目）</summary><ul>`
        +f.chapters.map(c=>`<li><span class="t">${esc(c.t)}</span>${esc(c.label)}</li>`).join("")+`</ul></details>`:""}
    </div></div></div>`;
  return `
  <div class="sec"><h2>追いかけている人の新着 <em>${fresh.length}</em>
     <a href="#" data-goto="feed">すべて見る →</a></h2>
    ${fresh.length?fresh.map(box).join(""):`<p class="zero">直近2日の新着はありません。「動画・note」タブに過去の分があります。</p>`}</div>

  <div class="sec"><h2>今日のニュース <em>${news.length}</em>
     <a href="#" data-goto="news">すべて見る →</a></h2>
    ${news.length?news.map(newsRow).join(""):`<p class="zero">今日のニュースはまだありません。</p>`}</div>

  <div class="sec"><h2>最近ふえたコツ <a href="#" data-goto="tips">すべて見る →</a></h2>
    <div class="grid">${recentTips.map(tipCard).join("")}</div></div>`;
}

let filterOpen=false;
function activeFilters(){
  const a=[];
  if(onlyLiked) a.push("👍いいね");
  if(view==="tips"){
    if(ai!=="すべて") a.push(ai);
    if(useFor!=="すべて") a.push(useFor);
    if(level!=="すべて") a.push(level);
    if(onlyPrompt) a.push("コピーできる");
    if(tag!=="すべて") a.push(tag);
  }
  if(view==="feed"){
    if(ai!=="すべて") a.push(ai);
    if(author!=="すべて") a.push(author);
    if(onlyNew) a.push("直近2日");
    if(onlyChap) a.push("目次あり");
  }
  if(view==="news" && ai!=="すべて") a.push(ai);
  return a;
}
function renderFilterHead(n){
  const act=activeFilters();
  el("#filterhead").innerHTML = `<div class="fhead">
    <button class="fbtn ${act.length?"act":""}" id="fToggle">⚙ 絞り込み${act.length?"（"+act.length+"）":""} ${filterOpen?"▲":"▼"}</button>
    ${act.length?`<span class="fsum2">${act.map(esc).join(" / ")}</span><button class="fbtn" id="fReset">✕ 解除</button>`:""}
    <span class="fsum2" style="margin-left:auto">${n}件</span></div>`;
  el("#filterwrap").classList.toggle("open", filterOpen);
  el("#fToggle").onclick=()=>{filterOpen=!filterOpen;render();};
  const fr=el("#fReset");
  if(fr) fr.onclick=()=>{ ai="すべて"; tag="すべて"; author="すべて"; level="すべて";
    useFor="すべて"; onlyPrompt=false; onlyNew=false; onlyChap=false; onlyLiked=false;
    shown=PAGE; render(); };
}
function render(){
  let list=items().filter(match);
  renderFilterHead(list.length);
  if(view==="tips"){
    if(sortBy==="新着順") list=[...list].reverse();
    else list=[...list].sort((a,b)=>(a.ai+a.level).localeCompare(b.ai+b.level));
  }
  pills();
  if(view==="cast"){
    el("#filterhead").innerHTML=""; el("#filterwrap").classList.remove("open");
    el("#aipills").innerHTML=""; el("#tagpills").innerHTML=""; el("#authorpills").innerHTML="";
    el("#hint").textContent="上の🔊がずんだもん＆四国めたんの音声です。下は同じ内容の台本なので、読み物としてどうぞ。";
    el("#body").innerHTML=castView();
    const edrow=el("#edrow");
    if(edrow){ edrow.querySelectorAll(".edpill").forEach(b=>{ b.onclick=()=>{
      castEd=b.dataset.ed;
      try{ localStorage.setItem(ED_KEY,castEd); }catch(e){}
      render();
    };}); }
    document.querySelectorAll(".line").forEach(p=>p.onclick=()=>{
      document.querySelectorAll(".line").forEach(x=>x.classList.remove("now"));
      p.classList.add("now");
    });
    return;
  }
  if(view==="home"){
    el("#filterhead").innerHTML=""; el("#filterwrap").classList.remove("open");
    el("#aipills").innerHTML=""; el("#tagpills").innerHTML=""; el("#authorpills").innerHTML="";
    el("#hint").textContent="毎朝ここだけ見れば足ります。★はあなたが指定した発信者です。";
    el("#body").innerHTML=homeView();
    document.querySelectorAll(".copy").forEach(b=>b.onclick=()=>{
      const txt=b.parentElement.textContent.replace(/^コピー/,"");
      navigator.clipboard.writeText(txt).then(()=>{b.textContent="コピーしました";b.classList.add("done");
        setTimeout(()=>{b.textContent="コピー";b.classList.remove("done")},1400);});
    });
    const lb=el("#fLiked"); if(lb) lb.onclick=()=>{onlyLiked=!onlyLiked;shown=PAGE;render();};
  document.querySelectorAll("[data-fav]").forEach(b=>b.onclick=(e)=>{
      e.preventDefault(); e.stopPropagation();
      let info={}; try{ info=JSON.parse(b.dataset.info||"{}"); }catch(_){}
      toggleFav(b.dataset.fav, info);
    });
    document.querySelectorAll("[data-goto]").forEach(a=>a.onclick=(e)=>{
      e.preventDefault();
      const v=a.dataset.goto;
      document.querySelectorAll(".tab").forEach(x=>x.classList.toggle("on",x.dataset.view===v));
      view=v; ai="すべて"; tag="すべて"; author="すべて"; render();
      window.scrollTo(0,0);
    });
    return;
  }
  const hints={tips:"プロンプトはそのままコピーできます。黒い X バッジ＝Xで話題の投稿、オレンジ＝Claude独自の知見です。",
    feed:"★はあなたが指定した発信者。「この回の内容」を開くと、動画のどこで何を話しているかが分かります。",
    news:"自動収集（1日1回）。見出しと出典だけの速報です。"};
  el("#hint").textContent = hints[view];
  const page=list.slice(0,shown);
  const moreBtn = list.length>shown
    ? `<button class="more" id="more">もっと見る（残り ${list.length-shown} 件）</button>` : "";
  el("#body").innerHTML = list.length===0 ? `<p class="empty">該当なし</p>`
    : (view==="tips" ? `<div class="grid">${page.map(tipCard).join("")}</div>${moreBtn}`
       : view==="feed" ? `<div>${page.map(feedCard).join("")}</div>${moreBtn}`
                     : `<div>${page.map(newsRow).join("")}</div>${moreBtn}`);
  const mb=el("#more"); if(mb) mb.onclick=()=>{ shown+=PAGE; render(); };
  document.querySelectorAll(".copy").forEach(b=>b.onclick=()=>{
    const txt=b.parentElement.textContent.replace(/^コピー/,"");
    navigator.clipboard.writeText(txt).then(()=>{b.textContent="コピーしました";b.classList.add("done");
      setTimeout(()=>{b.textContent="コピー";b.classList.remove("done")},1400);});
  });
    const lb=el("#fLiked"); if(lb) lb.onclick=()=>{onlyLiked=!onlyLiked;shown=PAGE;render();};
  document.querySelectorAll("[data-fav]").forEach(b=>b.onclick=(e)=>{
      e.preventDefault(); e.stopPropagation();
      let info={}; try{ info=JSON.parse(b.dataset.info||"{}"); }catch(_){}
      toggleFav(b.dataset.fav, info);
    });
}
window.addEventListener("scroll",()=>{
  el("#totop").classList.toggle("show", window.scrollY>600);
});
el("#totop").onclick=()=>window.scrollTo({top:0,behavior:"smooth"});
document.addEventListener("keydown",(e)=>{
  if(e.key==="/" && document.activeElement!==el("#q")){ e.preventDefault(); el("#q").focus(); }
  if(e.key==="Escape"){ el("#q").value=""; q=""; shown=PAGE; render(); el("#q").blur(); }
});
render();
</script>
</body>
</html>
"""

def main():
    tips = load("tips.json", "tips")
    news = load("news.json", "news")
    feed = load("feed.json", "items")
    cast = load_obj("podcast.json")
    # テーマ別の版（Claudeだけ／Geminiだけ…）も読み込む
    EDITION_LABELS = [("all", "全部"), ("claude", "Claude"), ("gemini", "Gemini"),
                      ("chatgpt", "ChatGPT"), ("news", "ニュース")]
    casts = {}
    for key, label in EDITION_LABELS:
        obj = cast if key == "all" else load_obj("podcast_%s.json" % key)
        if obj and obj.get("lines"):
            obj["label"] = label
            casts[key] = obj
    # 音声が作られた時刻（GitHubの自動実行が書き残す）
    vstamp = ""
    vp = os.path.join(HERE, "data", "voice_built.txt")
    if os.path.exists(vp):
        try: vstamp = io.open(vp, encoding="utf-8").read().strip()
        except Exception: pass
    cast["voice_built"] = vstamp
    for c in casts.values():
        c["voice_built"] = vstamp
    data = {"updated": datetime.now().strftime("%Y-%m-%d %H:%M"), "tips": tips, "feed": feed, "news": news, "cast": cast, "casts": casts}
    html = TEMPLATE.replace("__DATA__", json.dumps(data, ensure_ascii=False))
    if not os.path.isdir(OUTDIR):
        os.makedirs(OUTDIR)
    io.open(OUT, "w", encoding="utf-8").write(html)
    # スマホのホーム画面に追加したときの表示設定
    io.open(os.path.join(OUTDIR, "site.webmanifest"), "w", encoding="utf-8").write(json.dumps({
        "name": "AIコツ図鑑", "short_name": "AIコツ",
        "icons": [{"src": "icon-192.png", "sizes": "192x192", "type": "image/png"},
                  {"src": "apple-touch-icon.png", "sizes": "180x180", "type": "image/png"}],
        "theme_color": "#c2512a", "background_color": "#f7f7f5",
        "display": "standalone", "start_url": "./"
    }, ensure_ascii=False, indent=1))
    # 検索エンジンに拾わせないための指示ファイル
    io.open(os.path.join(OUTDIR, "robots.txt"), "w", encoding="utf-8").write(
        "User-agent: *\nDisallow: /\n")
    print("できました: %s（コツ %d件 / 動画・note %d件 / ニュース %d件）" % (OUT, len(tips), len(feed), len(news)))

if __name__ == "__main__":
    main()
