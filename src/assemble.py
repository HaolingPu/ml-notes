import json
from _figs import FIG_CSS
P = json.load(open("_parts.json"))

CSS = P["vcss"] + FIG_CSS + """
:root{
  color-scheme: light;
  --paper:#F5F5F7; --card:#FFFFFF; --ink:#1D1D22; --ink2:#5E5E68; --ink3:#8B8B95;
  --rule:#E5E5EA; --rule2:#D2D2DA; --accent:#2F6FB0;
}
*{box-sizing:border-box}
html,body{margin:0;padding:0;background:var(--paper);color:var(--ink);
  font-family:"Source Sans 3",-apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif;
  -webkit-font-smoothing:antialiased;font-size:15px;line-height:1.6}
text{font-family:"Source Sans 3",-apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif}
.capnum,.eyebrow,.navsub,kbd,.vizhead span{font-family:"IBM Plex Mono",ui-monospace,SFMono-Regular,Menlo,monospace}
h1,h2,h3,.navtitle,.card b{font-family:"Newsreader",Georgia,"Times New Roman",serif;font-weight:600;letter-spacing:-.012em}
a{color:inherit}
:focus-visible{outline:2px solid var(--accent);outline-offset:3px;border-radius:6px}

.shell{display:grid;grid-template-columns:268px minmax(0,1fr);gap:0;min-height:100vh}
.shell>*{min-width:0}
.side{position:sticky;top:0;height:100vh;overflow-y:auto;background:var(--card);
  border-right:1px solid var(--rule);padding:24px 18px 40px}
.brand{display:block;width:100%;text-align:left;background:none;border:0;padding:0;cursor:pointer;margin:0 0 6px}
.brand h1{font-size:19px;margin:0;line-height:1.2}
.brand p{font-size:11px;color:var(--ink3);margin:4px 0 0;font-family:"IBM Plex Mono",monospace}
.areas{display:grid;grid-template-columns:1fr 1fr;gap:5px;margin:16px 0 4px}
.area{padding:7px 7px;border-radius:9px;border:1px solid var(--rule2);background:var(--card);
  font:inherit;cursor:pointer;text-align:left;transition:.15s}
.area b{display:block;font-size:11.5px;font-weight:600}
.area span{display:block;font-size:9px;color:var(--ink3);line-height:1.3;margin-top:1px;
  font-family:"IBM Plex Mono",monospace}
.area:hover{background:#F0F0F4}
.area.on{background:var(--ink);color:#fff;border-color:var(--ink)}
.area.on span{color:#B9B9C2}
.homebtn{width:100%;margin:14px 0 20px;padding:8px 12px;border-radius:9px;border:1px solid var(--rule2);
  background:var(--card);font:inherit;font-size:12.5px;font-weight:600;cursor:pointer;text-align:left;transition:.15s}
.homebtn:hover{background:#F0F0F4}
.homebtn.on{background:var(--ink);color:#fff;border-color:var(--ink)}
.navgroup{margin-bottom:18px}
.navtitle{font-size:12.5px;font-weight:700;margin-bottom:1px}
.navsub{font-size:9.5px;color:var(--ink3);margin-bottom:7px;letter-spacing:-.1px}
.nav{display:block;width:100%;text-align:left;margin:0 0 3px;padding:6px 10px;border-radius:8px;
  border:1px solid transparent;background:transparent;cursor:pointer;font:inherit;transition:.14s}
.nav b{display:block;font-size:12.5px;font-weight:600}
.nav span{display:block;font-size:10px;color:var(--ink3);line-height:1.35;margin-top:1px}
.nav:hover{background:#F1F1F5}
.nav.on{background:var(--card);border-color:var(--rule2);box-shadow:0 1px 3px rgba(0,0,0,.05)}
.nav.on b{color:var(--ac)}
.nav.on::before{content:"";position:absolute;margin-left:-14px;width:3px;height:15px;border-radius:2px;background:var(--ac)}

main{padding:34px 40px 80px;max-width:1180px}
.pane{background:var(--card);border:1px solid var(--rule);border-radius:16px;padding:30px 34px 32px;
  box-shadow:0 1px 3px rgba(0,0,0,.04)}
.phead{border-left:4px solid var(--ac);padding-left:16px;margin-bottom:18px}
.eyebrow{font-size:10px;letter-spacing:.09em;text-transform:uppercase;color:var(--ac);font-weight:600}
.phead h1{font-size:30px;margin:4px 0 2px;line-height:1.15;text-wrap:balance}
.tagline{margin:0;color:var(--ink2);font-size:14.5px}
.lede{font-size:16.5px;line-height:1.62;color:var(--ink);max-width:68ch;margin:0 0 22px}
.pq{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-bottom:26px}
.pqcard{background:#FAFAFB;border:1px solid var(--rule);border-radius:11px;padding:16px 18px}
.pqcard.solve{background:#F5FAF7;border-color:#D3E7DC}
.pqcard h3{margin:0 0 6px;font-size:13px;color:var(--ink2);font-family:"IBM Plex Mono",monospace;
  font-weight:500;letter-spacing:.02em;text-transform:uppercase;font-size:10.5px}
.pqcard p{margin:0;font-size:14.5px;line-height:1.55}
.sec{font-size:19px;margin:0 0 10px}
.method{font-size:15px;max-width:74ch;margin:0 0 18px;color:#2B2B32}
.vizwrap{border:1px solid var(--rule);border-radius:13px;overflow:hidden;background:#FCFCFD;margin-bottom:24px}
.vizhead{padding:12px 16px 10px;border-bottom:1px solid var(--rule);background:var(--card)}
.vizhead b{font-size:13.5px;display:block}
.vizhead span{font-size:10.5px;color:var(--ink3)}
.vizwrap .stage{border:0;border-radius:0;background:#FCFCFD;padding:10px 14px}
.vizwrap .cap{margin:4px 16px 0}
.vizwrap .ctl{margin:10px 16px 14px}
.says{border-left:4px solid #E0A33A;background:#FDF7EC;border-radius:0 11px 11px 0;padding:14px 18px;margin-bottom:26px}
.says span{font-size:10px;letter-spacing:.09em;text-transform:uppercase;color:#9A6B12;font-weight:700;
  font-family:"IBM Plex Mono",monospace}
.says p{margin:4px 0 0;font-size:15.5px;line-height:1.55}
.ddgrp{margin-bottom:26px}
.dd{border:1px solid var(--rule);border-radius:11px;background:#FAFAFB;margin-bottom:8px;overflow:hidden}
.dd+.dd{margin-top:0}
.dd>summary{cursor:pointer;padding:11px 16px;font-size:13.5px;font-weight:600;list-style:none;
  display:flex;gap:10px;align-items:baseline;transition:background .14s}
.dd>summary::-webkit-details-marker{display:none}
.dd>summary::before{content:"";width:0;height:0;flex:none;display:inline-block;position:relative;top:1px;
  border-left:6px solid var(--ac);border-top:4.5px solid transparent;border-bottom:4.5px solid transparent;
  transition:transform .18s;transform-origin:30% 50%}
.dd[open]>summary::before{transform:rotate(90deg)}
.dd>summary:hover{background:#F1F1F5}
.dd.ex{background:#FCFAF5;border-color:#EADFC8}
.dd.ex>summary:hover{background:#F8F3E8}
.ddb{padding:0 18px 15px 40px;font-size:14px;line-height:1.6;color:#2B2B32}
.ddb p{margin:0 0 9px}
.ddb p:last-child{margin:0}
.ddb code{font-family:"IBM Plex Mono",monospace;font-size:12.5px;background:#EDEDF1;
  padding:1px 5px;border-radius:4px}
.ddb sub{font-size:9px}
.two{display:grid;grid-template-columns:1fr 1fr;gap:30px}
.rels,.trades{list-style:none;margin:0;padding:0}
.rels li{margin-bottom:7px}
.rel{display:flex;align-items:baseline;gap:8px;text-decoration:none;padding:8px 11px;border-radius:9px;
  border:1px solid var(--rule);background:#FAFAFB;transition:.14s;flex-wrap:wrap}
.rel:hover{background:var(--card);border-color:var(--rule2);transform:translateX(2px)}
.reldot{width:7px;height:7px;border-radius:50%;flex:none;align-self:center}
.rel b{font-size:13.5px}
.rel span{font-size:12.5px;color:var(--ink2)}
.trades li{padding:8px 0 8px 16px;border-left:2px solid #E8C7C7;margin-bottom:8px}
.trades b{display:block;font-size:13.5px}
.trades span{font-size:12.5px;color:var(--ink2)}

/* ---- home ---- */
.hero{margin-bottom:22px}
.hero h1{font-size:38px;margin:0 0 6px;line-height:1.1;text-wrap:balance}
.hero p{margin:0;font-size:16.5px;color:var(--ink2);max-width:74ch}
.mapcard{background:var(--card);border:1px solid var(--rule);border-radius:16px;padding:18px 20px 14px;
  box-shadow:0 1px 3px rgba(0,0,0,.04);margin-bottom:26px}
.maphint{font-size:11.5px;color:var(--ink3);margin:0 0 10px;font-family:"IBM Plex Mono",monospace}
.mapsvg{width:100%;height:auto;display:block}
.node{cursor:pointer}
.node .nbox{transition:filter .18s, transform .18s}
.node:hover .nbox{filter:brightness(.97) drop-shadow(0 3px 7px rgba(0,0,0,.13))}
.node:hover .nt{text-decoration:underline;text-underline-offset:2px}
.mapsvg.dim .node:not(.hot) .nbox{opacity:.42}
.mapsvg.dim .node:not(.hot) text{opacity:.5}
.edge{transition:stroke .2s;stroke-dasharray:6 6;animation:flow 1.6s linear infinite}
.edge.back{stroke-dasharray:5 5;animation:flow 2.1s linear infinite}
@keyframes flow{to{stroke-dashoffset:-12}}
.mapsvg.dim .edge{opacity:.3}
.cardgroup{margin-bottom:20px}
.cardgroup h3{font-size:15px;margin:0 0 9px}
.cardrow{display:grid;grid-template-columns:repeat(auto-fill,minmax(215px,1fr));gap:10px}
.card{display:block;text-decoration:none;background:var(--card);border:1px solid var(--rule);
  border-left:3px solid var(--ac);border-radius:10px;padding:11px 14px;transition:.15s}
.card:hover{background:var(--tint);transform:translateY(-1px);box-shadow:0 3px 9px rgba(0,0,0,.07)}
.card b{display:block;font-size:14.5px}
.card span{display:block;font-size:11.5px;color:var(--ink3);line-height:1.35;margin-top:1px}
/* ---- roadmap ---- */
.roadmap{margin-top:10px;background:var(--card);border:1px solid var(--rule);border-radius:16px;padding:18px 22px 10px;box-shadow:0 1px 3px rgba(0,0,0,.04)}
.roadmap .sec{margin-top:0}
.rmlede{margin:-4px 0 14px;color:var(--ink2);font-size:14px;max-width:70ch}
.rmgroup{margin-bottom:14px;border-left:3px solid var(--ac);padding-left:14px}
.rmgroup h3{font-size:15px;margin:0 0 6px;color:var(--ac)}
.rmgroup ol{margin:0;padding-left:18px}
.rmgroup li{margin:0 0 5px;font-size:13.5px}
.rmgroup li b{font-weight:600}
.rmgroup li span{color:var(--ink2);font-size:12.5px;margin-left:6px}

@media (prefers-reduced-motion:reduce){
  .mv,.fd,.nav,.card,.rel,button,.dot,.node .nbox,.dd>summary,.dd>summary::before{transition:none !important}
  .edge{animation:none !important;stroke-dasharray:none !important}
}
@media (max-width:900px){
  .shell{grid-template-columns:minmax(0,1fr)}
  .side{position:static;height:auto;border-right:0;border-bottom:1px solid var(--rule);padding:18px 16px 12px}
  .navgroup{margin-bottom:12px}
  .nav{display:inline-block;width:auto;margin:0 4px 4px 0}
  .nav span{display:none}
  .nav.on::before{display:none}
  main{padding:20px 16px 60px}
  .pane{padding:20px 18px 24px;border-radius:13px}
  .phead h1{font-size:24px}
  .pq,.two{grid-template-columns:1fr;gap:12px}
  .hero h1{font-size:27px}
  .mapcard{padding:12px 12px 10px;overflow-x:auto}
  .mapsvg{min-width:820px}
  .areas{grid-template-columns:1fr 1fr 1fr 1fr}
}
"""

BODY = f"""<div class="shell">
<aside class="side">
  <button class="brand" data-home><h1>Brian's ML Notes</h1><p>ml &amp; infra, one mechanism at a time</p></button>
  <div class="areas">
    <button class="area" data-area="0"><b>Infrastructure</b><span>prompt → token</span></button>
    <button class="area" data-area="1"><b>Agents</b><span>the loop</span></button>
    <button class="area" data-area="2"><b>Blackwell</b><span>one kernel</span></button>
    <button class="area" data-area="3"><b>Foundations</b><span>neuron → update</span></button>
  </div>
  <button class="homebtn" id="homebtn" data-home>◆&nbsp; <span id="homelabel">The map</span></button>
  <div id="nav0">{P["nav"][0]}</div>
  <div id="nav1" hidden>{P["nav"][1]}</div>
  <div id="nav2" hidden>{P["nav"][2]}</div>
  <div id="nav3" hidden>{P["nav"][3]}</div>
</aside>
<main>
<section class="pane" id="pane-home" hidden>
  <div class="hero">
    <h1>Everything that happens between a prompt and a token</h1>
    <p>Fifteen mechanisms from the serving stack, each one a step-through walkthrough rather than a wall of text. Start anywhere on the map — every box opens its own page.</p>
  </div>
  <div class="mapcard">
    <p class="maphint">click any box to open it · flowing edges show which way work moves</p>
    {P["home"]}
  </div>
  {P["cards"][0]}
</section>
<section class="pane" id="pane-agents" hidden>
  <div class="hero">
    <h1>The loop that wraps the model</h1>
    <p>An agent is not one model call. Six pieces: the loop itself, one real instance of it, and the four problems the loop creates — context, state, reach, and what gets to enter the context.</p>
  </div>
  <div class="mapcard">
    <p class="maphint">click any box to open it · flowing edges show one turn of the loop</p>
    {P["agents"]}
  </div>
  {P["cards"][1]}
</section>
<section class="pane" id="pane-blackwell" hidden>
  <div class="hero">
    <h1>One CUDA kernel, 600 microseconds to 57</h1>
    <p>NVIDIA MLSys 2026 \u2014 sparse attention on a B200. Seven mechanisms, in the order the bottleneck moved: what the kernel is handed, the machine it lands on, and the four versions that each answered a different limit.</p>
  </div>
  <div class="mapcard">
    <p class="maphint">click any box to open it \u00b7 the bar chart is measured latency, lower is better</p>
    {P["blackwell"]}
  </div>
  {P["cards"][2]}
</section>
<section class="pane" id="pane-foundations" hidden>
  <div class="hero">
    <h1>From one neuron to a trained network</h1>
    <p>The foundations, with real numbers: one 2-2-1 network carried from the perceptron through the forward pass, the activation functions, backprop, autodiff, mini-batch SGD and the optimizer \u2014 every value checkable by hand. Dashed boxes are the roadmap still to write.</p>
  </div>
  <div class="mapcard">
    <p class="maphint">click a solid box to open it \u00b7 dashed boxes are still to do</p>
    {P["foundations"]}
  </div>
  {P["cards"][3]}
  {P["roadmap"]}
</section>
{P["panes"]}
</main>
</div>
<script>
var VIZ={{}},INST={{}},IDS={json.dumps(P["ids"])},TAREA={json.dumps(P["topicarea"])};
var HUB=["home","agents","blackwell","foundations"],AREA=0;
{P["scripts"]}
function setArea(a){{
  AREA=a;
  for(var n=0;n<4;n++) document.getElementById('nav'+n).hidden = (n!==a);
  document.getElementById('homelabel').textContent =
    a===0 ? 'The map \u2014 how it all connects'
  : a===1 ? 'The loop \u2014 how it all connects'
  : a===2 ? 'The kernel \u2014 how it all connects'
  :         'The path \u2014 and the roadmap';
  Array.prototype.forEach.call(document.querySelectorAll('.area'),function(b){{
    b.classList.toggle('on', +b.getAttribute('data-area')===a);
  }});
}}
function show(id){{
  var hub = HUB.indexOf(id);
  if(hub>=0) setArea(hub); else if(TAREA[id]!==undefined) setArea(TAREA[id]);
  HUB.forEach(function(h){{ document.getElementById('pane-'+h).hidden = (h!==id); }});
  IDS.forEach(function(k){{
    var p=document.getElementById('pane-'+k); if(p) p.hidden = (k!==id);
    var b=document.querySelector('.nav[data-v="'+k+'"]'); if(b) b.classList.toggle('on',k===id);
  }});
  document.getElementById('homebtn').classList.toggle('on',hub>=0);
  for(var k in INST){{ if(k!==id) INST[k].stop(); }}
  if(hub<0){{
    if(!INST[id]) INST[id]=VIZ[id](document.getElementById('pane-'+id));
    else INST[id].go(0);
  }}
  window.scrollTo(0,0);
}}
function route(){{
  var h=location.hash.replace(/^#\\/?/,'');
  show(IDS.indexOf(h)>=0 || HUB.indexOf(h)>=0 ? h : 'home');
}}
Array.prototype.forEach.call(document.querySelectorAll('.nav'),function(b){{
  b.onclick=function(){{ location.hash='#/'+b.getAttribute('data-v'); }};
}});
Array.prototype.forEach.call(document.querySelectorAll('[data-home]'),function(b){{
  b.onclick=function(){{ location.hash = '#/'+(AREA===1?'agents':AREA===2?'blackwell':AREA===3?'foundations':''); }};
}});
Array.prototype.forEach.call(document.querySelectorAll('.area'),function(b){{
  b.onclick=function(){{ var a=+b.getAttribute('data-area'); location.hash = '#/'+(a===1?'agents':a===2?'blackwell':a===3?'foundations':''); }};
}});
Array.prototype.forEach.call(document.querySelectorAll('.node'),function(n){{
  var t=n.getAttribute('data-go');
  n.onclick=function(){{ location.hash='#/'+t; }};
  n.setAttribute('tabindex','0'); n.setAttribute('role','link');
  n.onkeydown=function(e){{ if(e.key==='Enter'||e.key===' '){{e.preventDefault();location.hash='#/'+t;}} }};
  n.onmouseenter=function(){{
    var svg=n.closest('.mapsvg'); if(!svg)return; svg.classList.add('dim');
    Array.prototype.forEach.call(svg.querySelectorAll('.node'),function(m){{
      m.classList.toggle('hot', m.getAttribute('data-go')===t);
    }});
  }};
  n.onmouseleave=function(){{
    var svg=n.closest('.mapsvg'); if(!svg)return; svg.classList.remove('dim');
    Array.prototype.forEach.call(svg.querySelectorAll('.node'),function(m){{m.classList.remove('hot');}});
  }};
}});

window.addEventListener('hashchange',route);
route();
</script>"""

HEAD_LINKS = ('<link rel="preconnect" href="https://fonts.googleapis.com">'
  '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
  '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?'
  'family=Newsreader:opsz,wght@6..72,500;6..72,600&family=Source+Sans+3:wght@400;600&'
  'family=IBM+Plex+Mono:wght@400;500&display=swap">')

# artifact form (no doctype/head/body wrapper)
open("artifact.html","w").write(f"<title>Brian's ML Notes</title>{HEAD_LINKS}<style>{CSS}</style>{BODY}")
# standalone form for GitHub Pages
import os
os.makedirs("dist", exist_ok=True)
open("dist/index.html","w").write(
 f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Brian's ML Notes</title>
<meta name="description" content="Interactive step-through notes on machine learning and AI infrastructure — from the perceptron and backprop to attention, KV cache, serving, parallelism, agents and a CUDA kernel.">
{HEAD_LINKS}<style>{CSS}</style></head><body>{BODY}</body></html>""")
print("artifact.html", os.path.getsize("artifact.html"), "| dist/index.html", os.path.getsize("dist/index.html"))
