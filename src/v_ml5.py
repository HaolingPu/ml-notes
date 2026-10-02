from shell import build
from ml_common import *
import json, math
TR=json.load(open('/tmp/claude-0/-home-claude/1cea3905-d70d-561d-bb7b-617467468669/scratchpad/opt.json'))
# ---------- plot geometry
PX0,PX1,PY0,PY1=44,504,56,356
def mp(w1,w2): return (PX0+(w1+10)*23, PY0+(3-w2)*50)
svg=''
svg+=f'<g id="valley" class="fd"><rect x="24" y="22" width="500" height="354" rx="10" fill="#FCFCFD" stroke="{N_S}"/>'
for c in (0.5,2,5,10,20,35):
    a=math.sqrt(2*c); b=a/math.sqrt(10)
    cx,cy=mp(0,0)
    svg+=f'<ellipse cx="{cx}" cy="{cy}" rx="{a*23:.1f}" ry="{b*50:.1f}" fill="none" stroke="{N_S}" stroke-width="1.1"/>'
svg+=f'<text class="tiny" x="{mp(0,0)[0]}" y="{mp(0,0)[1]+18}" fill="{INK3}" text-anchor="middle">minimum</text>'
svg+=f'<circle cx="{mp(0,0)[0]}" cy="{mp(0,0)[1]}" r="3" fill="{INK3}"/>'
svg+=f'<text class="tiny" x="{PX1}" y="{PY1+14}" text-anchor="end">w₁  (shallow: ∂f/∂w₁ = w₁)</text>'
svg+=f'<text class="tiny" x="{PX0}" y="{PY0-8}">w₂  (steep: ∂f/∂w₂ = 10 w₂)</text>'
sx,sy=mp(*TR['gd'][0])
svg+=f'<circle cx="{sx}" cy="{sy}" r="5" fill="{INK}"/><text class="tiny" x="{sx+8}" y="{sy-8}">start (−9, 1.4)</text>'
svg+='</g>'
COL={"gd":"#2F6FB0","gd_big":"#C2602B","gd_small":"#8B8B95","sgd":"#2F6FB0","mom":"#2E8B73","adam":"#6B4FA8"}
def traj(idp,key,dash=""):
    pts=TR[key]; col=COL[key]
    d=" ".join(f"{mp(*p)[0]:.1f},{mp(*p)[1]:.1f}" for p in pts)
    da=(' stroke-dasharray="%s"'%dash) if dash else ""
    s=f'<g id="{idp}" class="fd"><polyline points="{d}" fill="none" stroke="{col}" stroke-width="1.8"{da}/>'
    for p in pts[1:]:
        x,y=mp(*p); s+=f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3" fill="#fff" stroke="{col}" stroke-width="1.6"/>'
    x,y=mp(*pts[-1]); s+=f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4.5" fill="{col}"/>'
    return s+'</g>'
svg+=traj("tgd","gd")+traj("tbig","gd_big","4 3")+traj("tsmall","gd_small","2 3")+traj("tsgd","sgd")+traj("tmom","mom")+traj("tadam","adam")
# gradient arrow at the start (for step 3)
gx,gy=mp(-9,1.4); g=(-9,14); L=math.hypot(*g); ux,uy=-g[0]/L,-g[1]/L
svg+=f'<g id="garrow" class="fd"><path d="M{gx},{gy} L{gx+ux*60:.1f},{gy-uy*60*50/23:.1f}" stroke="{GRAD}" stroke-width="2.2" marker-end="url(#om)"/>'
svg+=f'<text class="tiny" x="{gx+ux*60+6:.1f}" y="{gy-uy*60*50/23+4:.1f}" fill="{GRAD}">−∇f: mostly down the steep wall</text></g>'
svg='<defs><marker id="om" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M0,1 L9,5 L0,9 z" fill="'+GRAD+'"/></marker></defs>'+svg
# ---------- table for steps 1-2 (same position as the valley)
svg+=f'<g id="tbl" class="fd"><rect x="24" y="22" width="500" height="354" rx="10" fill="#FCFCFD" stroke="{N_S}"/>'
svg+=f'<text class="tiny" x="40" y="46" font-weight="650">one step of gradient descent on the 2-2-1 network, η = 0.1</text>'
rows=[("parameter","value","gradient","−η·gradient","new value"),
      ("w₁₁","0.7","−0.2","+0.02","0.72"),("w₁₂","−0.6","−0.1","+0.01","−0.59"),
      ("w₂₁","0.3","0.4","−0.04","0.26"),("w₂₂","1.0","0.2","−0.02","0.98"),
      ("b₁","(0.1, 0.2)","(−0.2, 0.4)","(+0.02, −0.04)","(0.12, 0.16)"),
      ("w₂ (out)","(0.4, −0.8)","(−0.25, −0.5)","(+0.025, +0.05)","(0.425, −0.75)"),
      ("b₂","0.6","−0.5","+0.05","0.65")]
cols=[40,130,220,320,430]
for r,row in enumerate(rows):
    y=72+r*24
    for c,t in enumerate(row):
        fw=' font-weight="650"' if (c==4 and r) else ""
        svg+=f'<text class="tiny mono" x="{cols[c]}" y="{y}" fill="{INK if r else INK3}"{fw}>{t}</text>'
    if r==0: svg+=f'<line x1="36" y1="{y+8}" x2="512" y2="{y+8}" stroke="{N_S}"/>'
svg+=f'<text id="tbln" class="tiny" x="40" y="300" fill="{INK2}" xml:space="preserve" style="white-space:pre"></text>'
svg+=f'<text id="tbln2" class="tiny" x="40" y="318" fill="{INK2}" xml:space="preserve" style="white-space:pre"></text>'
# loss curve (8 steps)
hist=[0.693,0.599,0.526,0.468,0.421,0.382,0.349,0.32]
LX,LY,LW,LH=300,250,210,110
svg+=f'<g id="lcurve" class="fd"><rect x="{LX}" y="{LY}" width="{LW}" height="{LH}" rx="8" fill="#fff" stroke="{N_S}"/>'
pts=[]
for i,v in enumerate(hist):
    x=LX+16+i*26; y=LY+LH-12-(v-0.3)/0.45*(LH-34); pts.append((x,y))
svg+=f'<polyline points="{" ".join(f"{x:.1f},{y:.1f}" for x,y in pts)}" fill="none" stroke="#2F6FB0" stroke-width="1.8"/>'
for i,(x,y) in enumerate(pts): svg+=f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3" fill="#fff" stroke="#2F6FB0" stroke-width="1.5"/>'
svg+=f'<text class="tiny mono" x="{pts[0][0]-2}" y="{pts[0][1]-7}">0.693</text><text class="tiny mono" x="{pts[-1][0]-14}" y="{pts[-1][1]-7}">0.320</text>'
svg+=f'<text class="tiny" x="{LX+8}" y="{LY+14}" fill="{INK2}">loss over 8 steps on this example</text></g>'
svg+='</g>'
# ---------- right panel
RX,RY,RW,RH=540,22,296,354
svg+=f'<rect x="{RX}" y="{RY}" width="{RW}" height="{RH}" rx="10" fill="#FAFAFB" stroke="{N_S}"/>'
svg+=f'<text id="rt" class="tiny" x="{RX+14}" y="{RY+24}" font-weight="650"></text>'
for i in range(12):
    svg+=f'<text id="r{i}" class="tiny mono" x="{RX+14}" y="{RY+48+i*22}" fill="{INK}" xml:space="preserve" style="white-space:pre"></text>'
# legend swatches: drawn at the origin, positioned by JS
def sw(idp,col,lab,dash=""):
    da=(' stroke-dasharray="%s"'%dash) if dash else ""
    return (f'<g id="{idp}" class="fd"><line x1="0" y1="0" x2="22" y2="0" stroke="{col}" stroke-width="2.4"{da}/>'
            f'<text class="tiny" x="28" y="4">{lab}</text></g>')
LEG=[("lgd",COL["gd"],"GD, \u03b7 = 0.15"),("lbig",COL["gd_big"],"\u03b7 = 0.21: diverges","4 3"),("lsmall",COL["gd_small"],"\u03b7 = 0.03: crawls","2 3"),
     ("lsgd",COL["sgd"],"SGD (noisy)"),("lmom",COL["mom"],"momentum, \u03b2 = 0.8"),("ladam",COL["adam"],"Adam, \u03b7 = 0.8")]
svg+=f'<rect id="legbg" class="fd" x="380" y="288" width="136" height="58" rx="7" fill="#FFFFFF" opacity=".92" stroke="{N_S}"/>'
for l in LEG:
    svg+=sw(l[0],l[1],l[2],l[3] if len(l)>3 else "")
# lr schedule mini chart
SX,SY,SW_,SH=RX+14,RY+150,268,110
svg+=f'<g id="sched" class="fd"><rect x="{SX}" y="{SY}" width="{SW_}" height="{SH}" rx="8" fill="#fff" stroke="{N_S}"/>'
pp=[]
for i in range(61):
    t=i/60; lr=(t/0.1) if t<0.1 else 0.5*(1+math.cos(math.pi*(t-0.1)/0.9))
    pp.append(f"{SX+12+t*(SW_-24):.1f},{SY+SH-14-lr*(SH-40):.1f}")
svg+=f'<polyline points="{" ".join(pp)}" fill="none" stroke="{COL["adam"]}" stroke-width="1.8"/>'
svg+=f'<text class="tiny" x="{SX+10}" y="{SY+16}" fill="{INK2}">learning rate over training</text>'
svg+=f'<text class="tiny" x="{SX+34}" y="{SY+SH-2}" fill="{INK3}">warm-up</text><text class="tiny" x="{SX+SW_-70}" y="{SY+SH-2}" fill="{INK3}">cosine decay</text></g>'

js="""
var TJ=['tgd','tbig','tsmall','tsgd','tmom','tadam'],LG=['lgd','lbig','lsmall','lsgd','lmom','ladam'];
function rp(t){var a=Array.prototype.slice.call(arguments,1);tx('rt',t||'');for(var i=0;i<12;i++)tx('r'+i,a[i]||'')}
function show(ids){TJ.forEach(function(k){o(k,ids.indexOf(k)>=0?1:0)});
  var n=0;LG.forEach(function(k){var on=ids.indexOf('t'+k.slice(1))>=0;o(k,on?1:0);if(on){mv(k,392,346-8-(ids.length-1-n)*17-4);n++}else mv(k,-500,-500)});
  var bg=$('legbg');bg.style.opacity=ids.length?1:0;bg.setAttribute('height',ids.length*17+12);bg.setAttribute('y',346-(ids.length*17+12))}
function base(){o('tbl',0);o('lcurve',0);tx('tbln','');tx('tbln2','');o('valley',1);o('garrow',0);show([]);o('sched',0);rp()}
var S=[
{c:'Backprop handed us a gradient for every parameter. The <b>update rule</b> is one line: move each parameter a small step <i>against</i> its gradient, <b>w ← w − η·∂L/∂w</b>. With η = 0.1, w₂₂ goes from −0.8 to −0.75 and every other parameter nudges likewise.',
 a:function(){o('valley',0);o('tbl',1);tx('tbln','η (eta) is the learning rate: how far to step along the gradient');tx('tbln2','every parameter moves at once, each by its own gradient');rp('the rule','w ← w − η · ∂L/∂w','','negative gradient → weight goes up','positive gradient → weight goes down','','the gradient says which way is uphill;','η says how far to walk the other way')}},
{c:'Run the forward pass again with the new weights: ŷ rises from 0.50 to 0.55 and the loss falls from 0.693 to 0.599. Repeat eight times and it is 0.32. <b>That loop — forward, backward, update — is training.</b>',
 a:function(){o('valley',0);o('tbl',1);o('lcurve',1);tx('tbln','after one step: ŷ 0.50 → 0.55');tx('tbln2','L 0.693 → 0.599; after 8 steps 0.320');rp('the training loop','repeat:','  ŷ = forward(x)        # compute','  L = loss(ŷ, y)        # how wrong','  grads = backward(L)    # which way','  w ← w − η·grads       # step','','one pass over the data = one epoch')}},
{c:'Now zoom out. The loss is a <b>surface over all the weights</b> and training is walking downhill on it. Real surfaces are rarely round bowls — they are valleys, steep in some directions and nearly flat in others. This one is 10× steeper in w₂ than in w₁.',
 a:function(){o('garrow',1);rp('the landscape','f(w) = ½ (w₁² + 10 w₂²)','','∂f/∂w₁ = w₁       (shallow)','∂f/∂w₂ = 10 w₂    (steep)','','the gradient points mostly across the','valley, not along it — that is the problem','every optimizer below is solving')}},
{c:'<b>Plain gradient descent</b>, η = 0.15. Each step overshoots the steep wall and bounces to the other side, while progress along the shallow floor is a slow crawl. The zigzag is not a bug in the code — it is what following the raw gradient does in a valley.',
 a:function(){show(['tgd']);rp('gradient descent','w ← w − η ∇f','','steep direction: step = 0.15 × 10 w₂ = 1.5 w₂','  → overshoots, flips sign each step','shallow direction: step = 0.15 w₁','  → shrinks w₁ by only 15% per step','','after 12 steps: w₁ is still at −1.3')}},
{c:'<b>The learning rate is the most important knob.</b> Raise it to 0.21 and the steep direction overshoots by more than it came — the loss explodes. Lower it to 0.03 and nothing diverges, but after 12 steps you have barely moved. One η has to serve both directions.',
 a:function(){show(['tgd','tbig','tsmall']);rp('too big, too small','η = 0.21:  step = 2.1 w₂','  |1 − 2.1| = 1.1 > 1  → grows every step','  f goes 1 → 39 in 7 steps','','η = 0.03:  stable, but w₁ shrinks 3%','  per step — 4× slower than η = 0.15','','in practice: too big → loss spikes / NaN,','too small → nothing happens for hours')}},
{c:'<b>SGD.</b> The true gradient needs the whole dataset; a mini-batch gives a noisy estimate of it for a fraction of the cost. The path jitters, but it still heads downhill — and far more steps fit in the same compute. Every large model is trained this way.',
 a:function(){show(['tsgd']);rp('stochastic gradient descent','ĝ = ∇f on a mini-batch of B examples','','E[ĝ] = ∇f     noise ∝ 1/√B','','cost per step: B examples, not N','so for the same compute: N/B steps','instead of 1','','the noise also helps escape sharp,','narrow minima that generalise badly')}},
{c:'<b>Momentum</b> keeps a running velocity: v ← βv + g, w ← w − ηv. The zigzag components point opposite ways on alternate steps and cancel; the consistent along-the-valley component adds up. Same gradients, smoother and faster path.',
 a:function(){show(['tgd','tmom']);rp('momentum','v ← β v + ∇f','w ← w − η v','','steep direction: +, −, +, − … cancels','shallow direction: −, −, − … accumulates','  up to 1/(1−β) = 5× the raw step','','a heavy ball rolling down the valley','instead of a hiker re-reading the slope')}},
{c:'<b>Adam</b> goes further: a running mean of the gradient (momentum) <i>and</i> a running mean of its square, per parameter. The step is m/√v — so every parameter moves about η regardless of how steep its own direction is. The 10× scale difference stops mattering.',
 a:function(){show(['tgd','tadam']);rp('Adam','m ← β₁ m + (1−β₁) g       mean of g','v ← β₂ v + (1−β₂) g²      mean of g²','w ← w − η · m̂ / (√v̂ + ε)','','g/√g² ≈ ±1: each coordinate steps ~η','so w₁ (gradient 9) and w₂ (gradient 14)','move the same distance per step','','β₁ = 0.9, β₂ = 0.999; m̂, v̂ are bias-','corrected for the first few steps')}},
{c:'What actually trains a transformer: <b>AdamW</b> (Adam with weight decay applied directly to the weights, not through the gradient) under a <b>schedule</b> — warm up η from zero so early noisy steps cannot wreck the initialisation, then decay it so the walk settles into the minimum.',
 a:function(){show(['tadam']);o('sched',1);rp('AdamW + a schedule','AdamW: w ← w − η (m̂/√v̂ + λ w)','  decay pulls weights toward 0 as a','  separate term — regularisation','','warm-up: Adam’s v̂ is unreliable at first')}},
{c:'<b>The ladder.</b> Gradient descent is the idea. SGD is what you can afford. Momentum fixes the zigzag. Adam fixes the scale mismatch between parameters. AdamW with warm-up and cosine decay is the default for every large model today — and η is still the knob you tune first.',
 a:function(){show(['tgd','tmom','tadam']);rp('which one, when','GD        the idea; never used as is','SGD+mom   vision models, CNNs','Adam      transformers, RL, anything','          with mixed gradient scales','AdamW     the default for LLM training','','tune first: η (and its warm-up)','tune second: batch size, β₂, weight decay')}}
];
"""
build("optimizers.html","Optimizers — from a gradient to an update, and why plain descent is not enough",
      "One step on the tiny network, then the same valley walked by GD, SGD, momentum and Adam.",svg,js,"0 0 860 400")
print("ok")
