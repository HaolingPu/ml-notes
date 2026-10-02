from shell import build
from ml_common import *
import json, math
J=json.load(open('/tmp/claude-0/-home-claude/1cea3905-d70d-561d-bb7b-617467468669/scratchpad/sgd.json'))
data,mu,sd,gd,sgd,batch=J['data'],J['mu'],J['sd'],J['gd'],J['sgd'],J['batch']
N=len(data); B=32; lr=0.3
def loss(w): return 0.5*((w-mu)**2+sd**2)
# ---------- left panel A: the dataset strip
LX0,LX1=50,450; U=(LX1-LX0)/6.0
def dx(v): return LX0+v*U
svg=f'<g id="dataset" class="fd"><rect x="24" y="22" width="446" height="354" rx="10" fill="#FCFCFD" stroke="{N_S}"/>'
svg+=f'<text class="tiny" x="40" y="46" font-weight="650">N = 1,000 examples xᵢ — fit one number w to minimise the average ½(w − xᵢ)²</text>'
bins=[0]*24
for v in data:
    k=int(v/0.25)
    if 0<=k<24: bins[k]+=1
mx=max(bins); BASE=230
for k,c in enumerate(bins):
    h=c/mx*110
    svg+=f'<rect x="{dx(k*0.25)+1:.1f}" y="{BASE-h:.1f}" width="{U*0.25-2:.1f}" height="{h:.1f}" fill="{B_F}" stroke="{B_S}" stroke-width="1"/>'
svg+=f'<line x1="{LX0}" y1="{BASE}" x2="{LX1}" y2="{BASE}" stroke="{N_S}"/>'
for v in range(7): svg+=f'<text class="tiny" x="{dx(v)}" y="{BASE+14}" text-anchor="middle" fill="{INK3}">{v}</text>'
svg+=f'<text class="tiny" x="{LX1}" y="{BASE+30}" text-anchor="end">x</text>'
# batch points
svg+='<g id="batch" class="fd">'
for i,v in enumerate(batch):
    svg+=f'<circle cx="{dx(v):.1f}" cy="{BASE-8-(i%4)*7}" r="3.2" fill="{A_F}" stroke="#C2602B" stroke-width="1.3"/>'
svg+=f'<text class="tiny" x="{dx(4.6)}" y="{BASE-128}" fill="#C2602B" font-weight="650">a random mini-batch, B = 32</text></g>'
# markers
svg+=f'<g id="mum" class="fd"><line x1="{dx(mu):.1f}" y1="{BASE-140}" x2="{dx(mu):.1f}" y2="{BASE}" stroke="{INK}" stroke-width="1.6" stroke-dasharray="4 3"/><text class="tiny mono" x="{dx(mu)+5:.1f}" y="{BASE-146}" fill="{INK}">μ = 3.03 (the answer)</text></g>'
svg+=f'<g id="wm" class="fd"><line x1="{dx(0):.1f}" y1="{BASE-100}" x2="{dx(0):.1f}" y2="{BASE}" stroke="#2F6FB0" stroke-width="2"/><text class="tiny mono" x="{dx(0)+5:.1f}" y="{BASE-106}" fill="#2F6FB0" font-weight="650">w = 0.0</text></g>'
# arrows: full-batch step and mini-batch step
svg+=f'<g id="gfull" class="fd"><path d="M{dx(0)},{BASE+40} L{dx(lr*mu)-3:.1f},{BASE+40}" stroke="#2F6FB0" stroke-width="2.4" marker-end="url(#ab)"/><text class="tiny mono" x="{dx(0)}" y="{BASE+58}" fill="#2F6FB0">full gradient: w − μ = −3.03 → step η·3.03 = 0.91</text></g>'
bm=sum(batch)/B
svg+=f'<g id="gbatch" class="fd"><path d="M{dx(0)},{BASE+80} L{dx(lr*bm)-3:.1f},{BASE+80}" stroke="#C2602B" stroke-width="2.4" marker-end="url(#ar)"/><text class="tiny mono" x="{dx(0)}" y="{BASE+98}" fill="#C2602B">batch gradient: w − mean(batch) = −2.94 → step 0.88</text></g>'
svg+=f'<text id="costnote" class="tiny fd" x="{dx(0)}" y="{BASE+124}" fill="{INK2}"></text>'
svg+='</g>'
svg='<defs><marker id="ab" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M0,1 L9,5 L0,9 z" fill="#2F6FB0"/></marker>'+\
    '<marker id="ar" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M0,1 L9,5 L0,9 z" fill="#C2602B"/></marker></defs>'+svg
# ---------- left panel B: loss vs examples processed
CX0,CX1,CY0,CY1=70,440,330,70
def cp(n,l): return (CX0+n/3000*(CX1-CX0), CY0-(l-0.3)/(5.2-0.3)*(CY0-CY1))
svg+=f'<g id="curve" class="fd"><rect x="24" y="22" width="446" height="354" rx="10" fill="#FCFCFD" stroke="{N_S}"/>'
svg+=f'<text class="tiny" x="40" y="46" font-weight="650">loss vs examples processed — the same compute, two walkers</text>'
svg+=f'<line x1="{CX0}" y1="{CY0}" x2="{CX1}" y2="{CY0}" stroke="{N_S}"/><line x1="{CX0}" y1="{CY0}" x2="{CX0}" y2="{CY1}" stroke="{N_S}"/>'
for n,t in ((0,"0"),(1000,"1 epoch"),(2000,"2"),(3000,"3")):
    svg+=f'<text class="tiny" x="{cp(n,0)[0]:.0f}" y="{CY0+14}" text-anchor="middle" fill="{INK3}">{t}</text>'
for l in (1,2,3,4,5): svg+=f'<text class="tiny" x="{CX0-6}" y="{cp(0,l)[1]+4:.0f}" text-anchor="end" fill="{INK3}">{l}</text>'
minl=0.5*sd*sd
svg+=f'<line x1="{CX0}" y1="{cp(0,minl)[1]:.1f}" x2="{CX1}" y2="{cp(0,minl)[1]:.1f}" stroke="{N_S}" stroke-dasharray="3 3"/><text class="tiny" x="{CX0+8}" y="{cp(0,minl)[1]-4:.1f}" text-anchor="start" fill="{INK3}">best possible: ½σ² = 0.49</text>'
sp=" ".join(f"{cp(n,loss(w))[0]:.1f},{cp(n,loss(w))[1]:.1f}" for n,w in sgd)
svg+=f'<g id="csgd" class="fd"><polyline points="{sp}" fill="none" stroke="#C2602B" stroke-width="1.8"/><text class="tiny" x="{cp(700,0.8)[0]:.0f}" y="{cp(0,0.95)[1]:.0f}" fill="#C2602B" font-weight="650">SGD, B = 32: 31 steps per epoch</text></g>'
gp=" ".join(f"{cp(n,loss(w))[0]:.1f},{cp(n,loss(w))[1]:.1f}" for n,w in gd)
svg+=f'<g id="cgd" class="fd"><polyline points="{gp}" fill="none" stroke="#2F6FB0" stroke-width="1.8"/>'
for n,w in gd: svg+=f'<circle cx="{cp(n,loss(w))[0]:.1f}" cy="{cp(n,loss(w))[1]:.1f}" r="4" fill="#fff" stroke="#2F6FB0" stroke-width="1.6"/>'
svg+=f'<text class="tiny" x="{cp(1500,0)[0]:.0f}" y="{cp(0,2.6)[1]:.0f}" fill="#2F6FB0" font-weight="650">full-batch GD: 1 step per epoch</text></g>'
# zoom box on the tail
svg+=f'<g id="tail" class="fd"><rect x="{cp(2000,0)[0]:.0f}" y="{cp(0,0.75)[1]:.0f}" width="{cp(3000,0)[0]-cp(2000,0)[0]:.0f}" height="{cp(0,0.38)[1]-cp(0,0.75)[1]:.0f}" rx="4" fill="none" stroke="#C2602B" stroke-dasharray="3 3"/><text class="tiny" x="{cp(2500,0)[0]:.0f}" y="{cp(0,0.95)[1]:.0f}" text-anchor="middle" fill="#C2602B">never settles: jitter ≈ ησ/√B</text></g>'
svg+='</g>'
# ---------- left panel C: sharp vs flat minima
svg+=f'<g id="flat" class="fd"><rect x="24" y="22" width="446" height="354" rx="10" fill="#FCFCFD" stroke="{N_S}"/>'
svg+=f'<text class="tiny" x="40" y="46" font-weight="650">why a little noise can help: sharp vs flat minima</text>'
def fl(x): return 1.6-1.4*math.exp(-((x-1.3)/0.18)**2)-1.0*math.exp(-((x-3.6)/0.9)**2)
pts=[]
for i in range(201):
    x=0.2+4.6*i/200; pts.append(f"{dx(x):.1f},{300-fl(x)*120:.1f}")
svg+=f'<polyline points="{" ".join(pts)}" fill="none" stroke="{INK2}" stroke-width="2"/>'
svg+=f'<text class="tiny" x="40" y="{300-fl(1.3)*120+28:.0f}" fill="{INK}">sharp: lower, but one noisy step away from the wall</text>'
svg+=f'<text class="tiny" x="{dx(2.3)}" y="{300-fl(3.6)*120+40:.0f}" fill="{INK}">flat: a little higher, and noise cannot push you out</text>'
svg+=f'<path d="M{dx(1.3)},{300-fl(1.3)*120-18:.0f} l 14,-30 l 14,22 l 16,-34" stroke="#C2602B" stroke-width="2" fill="none" marker-end="url(#ar)"/>'
svg+=f'<text class="tiny" x="40" y="346" fill="{INK2}">a widely held view with real evidence behind it, not a theorem — phrase it carefully in an interview</text></g>'
# ---------- right top: noise vs B chart
RX,RY,RW,RH=490,22,346,170
svg+=f'<g id="noisechart" class="fd"><rect x="{RX}" y="{RY}" width="{RW}" height="{RH}" rx="9" fill="#FAFAFB" stroke="{N_S}"/>'
svg+=f'<text class="tiny" x="{RX+12}" y="{RY+18}" font-weight="650">gradient noise ∝ 1/√B (σ = 1.0 here)</text>'
Bs=[(1,0.99),(8,0.35),(32,0.18),(128,0.09),(1000,0.03)]
for i,(b,sdev) in enumerate(Bs):
    x=RX+34+i*62; h=sdev*96
    svg+=f'<rect x="{x}" y="{RY+RH-28-h:.1f}" width="40" height="{h:.1f}" rx="3" fill="{A_F}" stroke="{A_S}"/>'
    svg+=f'<text class="tiny mono" x="{x+20}" y="{RY+RH-32-h:.1f}" text-anchor="middle">{sdev:.2f}</text><text class="tiny mono" x="{x+20}" y="{RY+RH-12}" text-anchor="middle" fill="{INK3}">B={b}</text>'
svg+='</g>'
# ---------- right top alt: the loop / definitions panel (text)
svg+=f'<g id="rtxt" class="fd"><rect x="{RX}" y="{RY}" width="{RW}" height="{RH}" rx="9" fill="#FAFAFB" stroke="{N_S}"/>'
svg+=f'<text id="rtt" class="tiny" x="{RX+12}" y="{RY+18}" font-weight="650"></text>'
for i in range(7):
    svg+=f'<text id="rt{i}" class="tiny mono" x="{RX+12}" y="{RY+38+i*19}" fill="{INK}" xml:space="preserve" style="white-space:pre"></text>'
svg+='</g>'
# ---------- right bottom: notes
NX,NY,NW,NH=490,206,346,170
svg+=f'<g id="notes"><rect x="{NX}" y="{NY}" width="{NW}" height="{NH}" rx="9" fill="{A_F}" stroke="{A_S}"/>'
svg+=f'<text id="nt" class="tiny" x="{NX+12}" y="{NY+18}" font-weight="650"></text>'
for i in range(7):
    svg+=f'<text id="n{i}" class="tiny mono" x="{NX+12}" y="{NY+38+i*19}" fill="{INK}" xml:space="preserve" style="white-space:pre"></text>'
svg+='</g>'

js="""
function note(t){var a=Array.prototype.slice.call(arguments,1);tx('nt',t||'');for(var i=0;i<7;i++)tx('n'+i,a[i]||'')}
function rtx(t){var a=Array.prototype.slice.call(arguments,1);o('rtxt',1);tx('rtt',t||'');for(var i=0;i<7;i++)tx('rt'+i,a[i]||'')}
function left(k){['dataset','curve','flat'].forEach(function(x){o(x,x===k?1:0)})}
function base(){left('dataset');o('batch',0);o('wm',0);o('mum',0);o('gfull',0);o('gbatch',0);tx('costnote','');o('csgd',0);o('cgd',0);o('tail',0);o('noisechart',0);o('rtxt',0);note()}
var S=[
{c:'A loss is an <b>average over the dataset</b>: L(w) = (1/N) Σᵢ ℓ(w, xᵢ). The simplest possible case — 1,000 numbers, one parameter w, ℓ = ½(w − xᵢ)² — has everything SGD is about. The answer is the mean, μ = 3.03; w starts at 0.',
 a:function(){o('mum',1);o('wm',1);note('the setup','L(w) = (1/N) Σᵢ ½(w − xᵢ)²','∇L(w) = (1/N) Σᵢ (w − xᵢ) = w − μ','','so the gradient is an average too —','and an average over 1,000 terms costs','1,000 evaluations')}},
{c:'<b>Full-batch gradient descent</b> computes that average exactly: touch all 1,000 examples, get w − μ = −3.03, step η = 0.3 of the way. Exact direction, but one step costs a whole pass over the data — on a real dataset, hours per step.',
 a:function(){o('mum',1);o('wm',1);o('gfull',1);tx('costnote','cost of this one step: 1,000 examples');note('full-batch GD','g = w − μ = 0 − 3.03 = −3.03','w ← 0 − 0.3·(−3.03) = 0.91','','exact, but one step = one epoch','a real dataset: billions of tokens per step','→ far too slow to be used as is')}},
{c:'<b>A mini-batch estimate.</b> Pick 32 examples at random. Their mean is 2.94, so the batch gradient is −2.94 and the step is 0.88 instead of 0.91 — nearly the same direction, at <b>1/31 of the cost</b>. It is an unbiased estimate: on average over batches it equals the true gradient.',
 a:function(){o('mum',1);o('wm',1);o('batch',1);o('gfull',1);o('gbatch',1);tx('costnote','cost of this one step: 32 examples');note('stochastic (mini-batch) gradient','ĝ = (1/B) Σ over the batch of (w − xᵢ)','  = w − mean(batch) = −2.94','','E[ĝ] = ∇L   (unbiased)','cost: B = 32 examples instead of 1,000','error this time: 0.09 — the noise')}},
{c:'<b>How noisy?</b> The batch mean has standard deviation σ/√B. With σ = 1: B = 1 gives ±1.0, B = 32 gives ±0.18, B = 1000 (the full set) gives ±0.03. Four times the batch halves the noise — diminishing returns, which is why batches are not simply made as big as possible.',
 a:function(){o('mum',1);o('wm',1);o('batch',1);o('gbatch',1);o('noisechart',1);note('noise vs batch size','std(ĝ) = σ / √B','','B = 1:     1.00     (pure SGD)','B = 32:    0.18','B = 128:   0.09','B = 1000:  0.03     (the full gradient)','4× the batch → half the noise')}},
{c:'<b>Same compute, many more steps.</b> One pass over the data buys full-batch GD one step; it buys SGD with B = 32 thirty-one steps. By the time GD has moved from 0 to 0.91, SGD is already at the minimum. Noisy steps that come 31× as often win by a mile.',
 a:function(){left('curve');o('cgd',1);o('csgd',1);note('one epoch of compute','GD:   1 step   → w = 0.91,  L = 2.74','SGD:  31 steps → w ≈ 3.0,   L ≈ 0.50','','after 3 epochs GD is at L = 1.03;','SGD got there in a tenth of an epoch','','steps per epoch = N / B')}},
{c:'<b>The price of noise.</b> SGD never settles exactly: near the minimum each step still carries a random error of about ησ/√B, so w jitters around μ (±0.07 here). To converge you have to shrink the noise — decay η over time, or grow the batch. That is what learning-rate schedules are for.',
 a:function(){left('curve');o('cgd',1);o('csgd',1);o('tail',1);note('the jitter near the minimum','step noise ≈ η · σ / √B','  = 0.3 · 1.0 / √32 ≈ 0.05 per step','  → w wanders ±0.07 around μ','','to settle: smaller η (a schedule),','bigger B (a batch-size ramp), or both')}},
{c:'<b>Batch size and learning rate move together.</b> A bigger batch means a more accurate gradient, so a larger η is safe — roughly proportionally, up to a point (the linear scaling rule). The hardware agrees: a bigger batch is a bigger matmul, which GPUs run more efficiently. Past a critical size the gradient stops improving and the extra examples are wasted.',
 a:function(){left('dataset');o('mum',1);o('wm',1);o('batch',1);rtx('batch size \u2194 learning rate','noise \u221d \u03b7 / \u221aB','','B \u00d7 k \u2192 \u03b7 \u00d7 k keeps the per-epoch progress','about the same (the linear scaling rule)','','above the critical batch size the gradient','is already accurate: more B, no more progress');note('why big batches anyway','GPU utilisation: a 4096-token batch is','one big matmul; 32 tokens is idle silicon','','so training uses the largest B that still','learns, and scales η up with it — with','a warm-up because early steps are fragile')}},
{c:'<b>The vocabulary.</b> One <b>epoch</b> is one pass over the data. A <b>step</b> (iteration) is one update, on one batch; there are N/B of them per epoch. The data is <b>shuffled</b> every epoch so batches differ — without that the noise is not random and the estimate is biased.',
 a:function(){left('dataset');o('mum',1);o('wm',1);o('batch',1);rtx('definitions','epoch      one pass over all N examples','step       one update on one batch of B','           N/B steps per epoch','batch      the B examples in one step','shuffle    reorder the data each epoch','','1,000 / 32 → 31 steps per epoch here');note('for LLMs','there is rarely more than ~1 epoch:','the data is larger than the compute,','so every token is seen about once','','“steps” and “tokens processed” are','the units people quote, not epochs')}},
{c:'<b>Why the noise may even help.</b> A sharp minimum fits the training set a little better but is one noisy step away from a wall; SGD’s jitter tends to bounce out of it and settle in flat basins, which generalise better to new data. Widely believed, well supported, not a theorem — say it that way.',
 a:function(){left('flat');note('noise as regulariser','small-batch SGD prefers flat minima','(Keskar et al. 2017, and much since)','','flat minimum: nearby weights all work','  → small changes in data do not hurt','sharp minimum: fits the training set,','  → brittle on anything new')}},
{c:'<b>The one-line version.</b> SGD is gradient descent with a cheap, noisy gradient. The batch size sets the noise (∝ 1/√B) and the cost per step; the learning rate scales with it; the noise is why schedules exist and may be why the result generalises. The optimizers page builds on exactly this gradient.',
 a:function(){left('curve');o('cgd',1);o('csgd',1);note('SGD, summarised','gradient:  on B examples, not N','noise:     σ/√B, unbiased','cost:      B per step → N/B steps per epoch','η:         scales with B, up to a point','settle:    decay η or grow B','bonus:     flatter minima')}}
];
"""
build("sgd.html","SGD and mini-batches — the gradient you can afford",
      "One parameter, 1,000 examples: why a noisy gradient on 32 of them beats the exact gradient on all of them.",svg,js,"0 0 860 400")
print("ok")
