from shell import build
from ml_common import *
svg=net_svg()
# gradient labels on edges (opposite side of the weight label)
def gl(idp,a,b,t,dy,txt):
    import math
    dx,dy_=b[0]-a[0],b[1]-a[1]; d=math.hypot(dx,dy_); ux,uy=dx/d,dy_/d
    a2=(a[0]+ux*R,a[1]+uy*R); b2=(b[0]-ux*R,b[1]-uy*R)
    p=(a2[0]+(b2[0]-a2[0])*t, a2[1]+(b2[1]-a2[1])*t)
    return f'<text id="{idp}" class="tiny mono fd" x="{p[0]:.1f}" y="{p[1]+dy:.1f}" text-anchor="middle" font-weight="650" fill="{GRAD}">{txt}</text>'
svg+=gl("g11",X1,H1,0.42,13,"∂w: −0.2")
svg+=gl("g12",X1,H2,0.5,16,"∂w: 0.4")
svg+=gl("g21",X2,H1,0.5,-14,"∂w: −0.1")
svg+=gl("g22",X2,H2,0.42,-6,"∂w: 0.2")
svg+=gl("go1",H1,OUT,0.5,13,"∂w: −0.25")
svg+=gl("go2",H2,OUT,0.5,-6,"∂w: −0.5")
# reverse-flow arrows (amber dashed) along each edge
import math
def rev(idp,a,b):
    dx,dy_=b[0]-a[0],b[1]-a[1]; d=math.hypot(dx,dy_); ux,uy=dx/d,dy_/d
    a2=(a[0]+ux*(R+3),a[1]+uy*(R+3)); b2=(b[0]-ux*(R+3),b[1]-uy*(R+3))
    return f'<path id="{idp}" class="fd" d="M{b2[0]:.1f},{b2[1]:.1f} L{a2[0]:.1f},{a2[1]:.1f}" stroke="{GRAD}" stroke-width="2.2" stroke-dasharray="5 4" fill="none" marker-end="url(#gm)"/>'
svg='<defs><marker id="gm" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M0,1 L9,5 L0,9 z" fill="'+GRAD+'"/></marker></defs>'+svg
for idp,a,b in (("r11",X1,H1),("r12",X1,H2),("r21",X2,H1),("r22",X2,H2),("ro1",H1,OUT),("ro2",H2,OUT),("rol",OUT,LOSS)):
    svg+=rev(idp,a,b)
svg+=ledger()
# chain panel
PX,PY,PW,PH=24,300,812,86
svg+=f'<g id="chain" class="fd"><rect x="{PX}" y="{PY}" width="{PW}" height="{PH}" rx="9" fill="{A_F}" stroke="{A_S}"/>'
svg+=f'<text id="cht" class="tiny" x="{PX+12}" y="{PY+18}" font-weight="650">the chain rule, one path</text>'
for i in range(3):
    svg+=f'<text id="ch{i}" class="tiny mono" x="{PX+12}" y="{PY+40+i*18}" fill="{INK}" xml:space="preserve" style="white-space:pre"></text>'
svg+='</g>'
svg+=f'<circle id="ring" class="fd" cx="0" cy="0" r="{R+5}" fill="none" stroke="{GRAD}" stroke-width="2"/>'

js="""
var GL=['g11','g12','g21','g22','go1','go2'], RV=['r11','r12','r21','r22','ro1','ro2','rol'];
function led(a,b,c){tx('led0',a||'');tx('led1',b||'');tx('led2',c||'')}
function chain(a,b,c,t){o('chain',1);tx('ch0',a||'');tx('ch1',b||'');tx('ch2',c||'');tx('cht',t||'the chain rule, one path')}
function ring(x,y){var r=$('ring');if(x===null){r.style.opacity=0;return}r.style.opacity=1;r.setAttribute('cx',x);r.setAttribute('cy',y)}
function nv(id,v,f,s){tx(id+'v',v);var c=$(id).firstChild;c.setAttribute('fill',f);c.setAttribute('stroke',s)}
function fwd(){nv('nh1','0.5','#E2EFE3','#A8CBAC');nv('nh2','1.0','#E2EFE3','#A8CBAC');nv('no','0.5','#E2EFE3','#A8CBAC');
  tx('nlv','0.693');var l=$('nl').firstChild;l.setAttribute('fill','#FBEBD2');l.setAttribute('stroke','#E2BC85')}
function ab(id,t,c){var e=$(id+'a');e.textContent=t;e.setAttribute('fill',c||'#6B6B76')}
function base(){fwd();ring(null);o('led',0);led();o('chain',0);o('nlring',0);
  GL.forEach(function(k){o(k,0)});RV.forEach(function(k){o(k,0)});
  ab('nh1','z₁ = 0.5');ab('nh2','z₂ = 1.0');ab('no','u = 0.0')}
function sig(){ab('no','∂L/∂u = −0.5','#C2602B');o('rol',1)}
function hid(){ab('nh1','∂L/∂h₁ = −0.2','#C2602B');ab('nh2','∂L/∂h₂ = 0.4','#C2602B');o('ro1',1);o('ro2',1)}
var S=[
{c:'The forward pass left every value in place: h = (0.5, 1.0), ŷ = 0.5, L = 0.693. The label was y = 1, so the network is wrong by half. The question now: <b>for each weight, which way should it move to lower L?</b>',
 a:function(){o('nlring',1)}},
{c:'That question is a derivative, <b>∂L/∂w</b>, and the network is a chain of simple functions. The <b>chain rule</b> says: multiply the local derivatives along the path from w to L. Backprop is just doing that for every weight at once, starting from the end.',
 a:function(){chain('∂L/∂w₁₁ = ∂L/∂u · ∂u/∂h₁ · ∂h₁/∂z₁ · ∂z₁/∂w₁₁','          ?        ?         ?          ?','each factor is local to one node')}},
{c:'<b>First link: how L changes with the logit u.</b> Sigmoid followed by cross-entropy collapses to something memorable: <b>∂L/∂u = ŷ − y = 0.5 − 1 = −0.5</b>. The gradient at the output is simply the error.',
 a:function(){sig();ring(548,162);o('led',1);led('∂L/∂ŷ = −1/ŷ = −2      ∂ŷ/∂u = ŷ(1−ŷ) = 0.25','∂L/∂u = (−2)(0.25) = −0.5  =  ŷ − y','negative: pushing u up would lower the loss')}},
{c:'<b>Output weights.</b> u = w₂·h + b₂, so ∂u/∂w₂ is just h. Gradient of a weight = <b>upstream signal × the input that weight multiplies</b>: ∂L/∂w₂ = −0.5 · (0.5, 1.0) = (−0.25, −0.5). For the bias the input is 1, so ∂L/∂b₂ = −0.5.',
 a:function(){sig();o('go1',1);o('go2',1);o('led',1);led('∂L/∂w₂₁ = ∂L/∂u · h₁ = (−0.5)(0.5) = −0.25','∂L/∂w₂₂ = ∂L/∂u · h₂ = (−0.5)(1.0) = −0.5','∂L/∂b₂  = ∂L/∂u · 1  = −0.5')}},
{c:'<b>Now send the signal backwards through the weights.</b> ∂u/∂h is w₂, so ∂L/∂h = −0.5 · (0.4, −0.8) = (−0.2, +0.4). Going forward you multiply by the weight; going backward you multiply by the same weight.',
 a:function(){sig();o('go1',1);o('go2',1);hid();o('led',1);led('∂L/∂h₁ = ∂L/∂u · w₂₁ = (−0.5)(0.4)  = −0.2','∂L/∂h₂ = ∂L/∂u · w₂₂ = (−0.5)(−0.8) = +0.4','h₂ should go down, h₁ should go up')}},
{c:'<b>Through the ReLU.</b> Its derivative is 1 where z was positive and 0 where it was not. Both were positive, so the signal passes untouched: ∂L/∂z = (−0.2, 0.4). <b>A neuron that was off would pass 0</b> — the gradient stops there, and its weights do not learn from this example.',
 a:function(){sig();hid();ab('nh1','∂L/∂z₁ = −0.2 · 1','#C2602B');ab('nh2','∂L/∂z₂ = 0.4 · 1','#C2602B');o('led',1);led('ReLU′(z) = 1 if z > 0 else 0','∂L/∂z₁ = (−0.2)(1) = −0.2     ∂L/∂z₂ = (0.4)(1) = 0.4','(this is where stored forward values are needed: was z > 0?)')}},
{c:'<b>First-layer weights</b>, same rule: upstream signal × the input. Row 1: −0.2 · (1.0, 0.5) = (−0.2, −0.1). Row 2: 0.4 · (1.0, 0.5) = (0.4, 0.2). Biases get the signal itself: (−0.2, 0.4). Every weight now has a gradient.',
 a:function(){sig();hid();GL.forEach(function(k){o(k,1)});RV.forEach(function(k){o(k,1)});o('led',1);led('∂L/∂W₁ = ∂L/∂z ⊗ x :  [−0.2·1.0  −0.2·0.5]   [−0.2  −0.1]','                      [ 0.4·1.0   0.4·0.5] = [ 0.4   0.2]','∂L/∂b₁ = (−0.2, 0.4)')}},
{c:'Read the whole chain for one weight and it is exactly the chain rule from step 2 — four local factors multiplied: <b>(−0.5)(0.4)(1)(1.0) = −0.2</b>. Backprop never computed a global formula; it reused each factor across every path that shares it.',
 a:function(){sig();hid();GL.forEach(function(k){o(k,1)});o('r11',1);o('ro1',1);o('rol',1);chain('∂L/∂w₁₁ = ∂L/∂u · ∂u/∂h₁ · ∂h₁/∂z₁ · ∂z₁/∂w₁₁','       = (−0.5) · (0.4) · (1) · (1.0)','       = −0.2')}},
{c:'<b>Reading the signs.</b> A negative gradient means raising that weight lowers the loss. The largest is ∂L/∂w₂₂ = −0.5: w₂₂ = −0.8 is dragging the output down the hardest, so it is the weight to move most. The optimizer page does exactly that.',
 a:function(){sig();hid();GL.forEach(function(k){o(k,1)});o('led',1);led('update rule (next page):  w ← w − η · ∂L/∂w','w₂₂: −0.8 − 0.1·(−0.5) = −0.75     w₂₁: 0.4 + 0.025 = 0.425','all eight parameters move at once, each by its own gradient')}},
{c:'<b>What it cost.</b> One sweep backwards, visiting each node once, reusing the stored forward values — roughly twice the work of the forward pass. That ratio (training ≈ 3× forward FLOPs) and the memory for stored activations are the two facts about backprop that matter for infrastructure.',
 a:function(){sig();hid();GL.forEach(function(k){o(k,1)});RV.forEach(function(k){o(k,1)});chain('forward:  1 unit of work, and store z, h, u, ŷ for later','backward: ~2 units — one matmul for ∂L/∂W, one for ∂L/∂h, per layer','you never do this by hand — autodiff does, next page','what it cost')}}
];
"""
build("backprop.html","Backpropagation — the chain rule, run backwards",
      "The same 2-2-1 network; every gradient derived by hand from ∂L/∂u = ŷ − y.",svg,js,"0 0 860 400")
print("ok")
