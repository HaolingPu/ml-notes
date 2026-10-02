# Shared shell for every interactive visualisation embedded in Notion.
CSS = """
*{box-sizing:border-box}
html,body{margin:0;padding:0;background:#fff;color:#2B2B30;
  font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Inter,Helvetica,Arial,sans-serif}
.wrap{max-width:900px;margin:0 auto;padding:14px 16px 16px}
h1{font-size:15px;margin:0 0 2px;font-weight:650;letter-spacing:-.01em}
.sub{font-size:12px;color:#6B6B76;margin:0 0 10px}
.stage{width:100%;background:#FCFCFD;border:1px solid #EAEAEE;border-radius:10px;padding:6px}
svg{width:100%;height:auto;display:block}
.cap{display:flex;gap:10px;align-items:flex-start;margin:11px 2px 0;min-height:44px}
.capnum{flex:none;font-size:10.5px;font-weight:650;color:#6B6B76;background:#F1F1F4;
  border-radius:20px;padding:3px 9px;margin-top:1px;font-variant-numeric:tabular-nums}
.captxt{font-size:12.5px;line-height:1.5;color:#2B2B30}
.captxt b{font-weight:650}
.captxt .q{color:#8A6D3B}
.ctl{display:flex;align-items:center;gap:8px;margin-top:10px;flex-wrap:wrap}
button{font:inherit;font-size:12px;font-weight:550;color:#2B2B30;background:#fff;
  border:1px solid #D8D8DE;border-radius:7px;padding:5px 11px;cursor:pointer;transition:.15s}
button:hover{background:#F4F4F6;border-color:#BFBFC8}
button:disabled{opacity:.38;cursor:default;background:#fff}
button.pri{background:#2B2B30;color:#fff;border-color:#2B2B30}
button.pri:hover{background:#3E3E45}
.dots{display:flex;gap:5px;margin-left:auto}
.dot{width:7px;height:7px;border-radius:50%;background:#DCDCE2;cursor:pointer;transition:.2s}
.dot.on{background:#2B2B30;transform:scale(1.18)}
.dot.past{background:#A9A9B4}
/* animation */
.mv{transition:transform .6s cubic-bezier(.45,.05,.2,1),opacity .35s ease}
.fd{transition:opacity .35s ease,fill .35s ease,stroke .35s ease}
text{font-family:inherit}
.lbl{font-size:11px;fill:#6B6B76}
.lbl-b{font-size:11.5px;fill:#2B2B30;font-weight:650}
.tiny{font-size:9.5px;fill:#6B6B76}
text.mono{font-family:"IBM Plex Mono",ui-monospace,SFMono-Regular,Menlo,monospace}
.panel{fill:none;stroke:#DCDCE2;stroke-width:1;stroke-dasharray:4 3}
.hot{stroke:#E2BC85;stroke-width:2}
@media (max-width:560px){.sub{display:none}.captxt{font-size:12px}}
"""

ENGINE = """
var _C=document.getElementById('cap'),_N=document.getElementById('num'),
    _D=document.getElementById('dots'),_i=0,_T=null;
function $(x){return document.getElementById(x)}
function o(id,v){var e=$(id);if(e)e.style.opacity=v}
function mv(id,x,y){var e=$(id);if(e)e.setAttribute('transform','translate('+x+','+y+')')}
function cl(id,c,on){var e=$(id);if(e)e.classList[on?'add':'remove'](c)}
function tx(id,t){var e=$(id);if(e)e.textContent=t}
function fill(id,c){var e=$(id);if(e)e.setAttribute('fill',c)}
function stroke(id,c){var e=$(id);if(e)e.setAttribute('stroke',c)}
for(var _k=0;_k<S.length;_k++){(function(k){var d=document.createElement('div');
  d.className='dot';d.onclick=function(){stop();go(k)};_D.appendChild(d)})(_k)}
function go(n){
  _i=(n%S.length+S.length)%S.length;
  base(); S[_i].a();
  _C.innerHTML=S[_i].c; _N.textContent=(_i+1)+' / '+S.length;
  var ds=_D.children;
  for(var k=0;k<ds.length;k++){ds[k].className='dot'+(k===_i?' on':(k<_i?' past':''))}
  $('prev').disabled=false;$('next').disabled=false;
}
function stop(){if(_T){clearInterval(_T);_T=null;$('play').textContent='▶ Play';$('play').classList.remove('pri')}}
function play(){
  if(_T){stop();return}
  if(_i>=S.length-1)go(0);
  $('play').textContent='❚❚ Pause';$('play').classList.add('pri');
  _T=setInterval(function(){ if(_i>=S.length-1){stop();return} go(_i+1) },2600);
}
$('prev').onclick=function(){stop();go(_i-1)};
$('next').onclick=function(){stop();go(_i+1)};
$('play').onclick=play;
document.addEventListener('keydown',function(e){
  if(e.key==='ArrowRight'){stop();go(_i+1)}
  else if(e.key==='ArrowLeft'){stop();go(_i-1)}
  else if(e.key===' '){e.preventDefault();play()}
});
go(0);
"""

import json as _json, os as _os
def build(path, title, sub, svg, steps_js, vb="0 0 860 360"):
    _os.makedirs("mods", exist_ok=True)
    _json.dump({"id":_os.path.basename(path).replace(".html",""),"title":title,"sub":sub,
                "svg":svg,"js":steps_js,"vb":vb}, open("mods/"+_os.path.basename(path)+".json","w"))
    html = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title><style>{CSS}</style></head>
<body><div class="wrap">
<h1>{title}</h1><p class="sub">{sub}</p>
<div class="stage"><svg viewBox="{vb}" xmlns="http://www.w3.org/2000/svg">{svg}</svg></div>
<div class="cap"><span class="capnum" id="num">1 / 1</span><span class="captxt" id="cap"></span></div>
<div class="ctl">
<button id="prev">←&nbsp; Back</button><button id="play">▶ Play</button><button id="next">Next &nbsp;→</button>
<div class="dots" id="dots"></div></div>
</div>
<script>{steps_js}
{ENGINE}</script></body></html>"""
    open(path, "w").write(html)
    return path
