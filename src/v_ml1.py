from shell import build
from ml_common import *
import json
NUM=json.load(open('/tmp/claude-0/-home-claude/1cea3905-d70d-561d-bb7b-617467468669/scratchpad/nums.json'))
traj=NUM['traj']
pos=[(2.0,3.0),(3.0,3.4),(3.4,2.2),(2.6,2.4)]; neg=[(1.0,1.2),(2.0,0.6),(0.6,2.2),(1.4,0.4)]
pts=[(p,1) for p in pos]+[(p,-1) for p in neg]
# plot box
BX0,BY0,BX1,BY1=44,36,364,356; SC=80
def px(x,y): return (BX0+x*SC, BY0+(4-y)*SC)
def clip_half(w,b):
    # polygon of {w.x + b > 0} inside the data box [0,4]^2
    poly=[(0,0),(4,0),(4,4),(0,4)]
    out=[]
    def f(p): return w[0]*p[0]+w[1]*p[1]+b
    for i in range(4):
        a,c=poly[i],poly[(i+1)%4]; fa,fc=f(a),f(c)
        if fa>0: out.append(a)
        if (fa>0)!=(fc>0):
            t=fa/(fa-fc); out.append((a[0]+(c[0]-a[0])*t, a[1]+(c[1]-a[1])*t))
    return out
def line_seg(w,b):
    poly=clip_half(w,b)
    # the boundary points are those on the box edges with f==0 -> compute directly
    cand=[]
    def f(p): return w[0]*p[0]+w[1]*p[1]+b
    corners=[(0,0),(4,0),(4,4),(0,4)]
    for i in range(4):
        a,c=corners[i],corners[(i+1)%4]; fa,fc=f(a),f(c)
        if (fa>0)!=(fc>0) or fa==0:
            t=fa/(fa-fc) if fa!=fc else 0; cand.append((a[0]+(c[0]-a[0])*t, a[1]+(c[1]-a[1])*t))
    return cand[:2]
def mistakes(w,b):
    return [i for i,(p,t) in enumerate(pts) if ((w[0]*p[0]+w[1]*p[1]+b)>0)!=(t==1)]
STATES=[]
for w,b,upd in traj:
    seg=line_seg(w,b); poly=clip_half(w,b)
    STATES.append(dict(w=w,b=b,seg=[px(*s) for s in seg],poly=[px(*p) for p in poly],mis=mistakes(w,b),upd=upd))
svg=''
# plot frame
svg+=f'<rect x="24" y="22" width="364" height="354" rx="10" fill="#FCFCFD" stroke="{N_S}"/>'
svg+=f'<g id="axes"><line x1="{BX0}" y1="{BY1}" x2="{BX1}" y2="{BY1}" stroke="{N_S}"/><line x1="{BX0}" y1="{BY0}" x2="{BX0}" y2="{BY1}" stroke="{N_S}"/>'
svg+=f'<text id="axx" class="tiny" x="{BX1}" y="{BY1+14}" text-anchor="end">x₁</text><text id="axy" class="tiny" x="{BX0-4}" y="{BY0+8}" text-anchor="end">x₂</text></g>'
svg+=f'<polygon id="half" class="fd" points="" fill="{G_F}" opacity=".55"/>'
svg+=f'<path id="dl" class="fd" d="" stroke="{INK}" stroke-width="2" fill="none"/>'
svg+=f'<path id="dl2" class="fd" d="" stroke="{INK2}" stroke-width="1.5" stroke-dasharray="5 4" fill="none"/>'
svg+=f'<path id="dl3" class="fd" d="" stroke="{INK2}" stroke-width="1.5" stroke-dasharray="5 4" fill="none"/>'
svg+='<g id="sep" class="fd">'
for i,(p,t) in enumerate(pts):
    cx,cy=px(*p)
    if t==1: svg+=f'<circle id="pt{i}" cx="{cx}" cy="{cy}" r="7" fill="{G_S}" stroke="#4E9E6E" stroke-width="1.5"/>'
    else: svg+=f'<rect id="pt{i}" x="{cx-6.5}" y="{cy-6.5}" width="13" height="13" rx="2" fill="{R_S}" stroke="#C97F7F" stroke-width="1.5"/>'
    svg+=f'<circle id="mk{i}" class="fd" cx="{cx}" cy="{cy}" r="12" fill="none" stroke="#C2602B" stroke-width="2"/>'
    svg+=f'<circle id="up{i}" class="fd" cx="{cx}" cy="{cy}" r="15" fill="none" stroke="#2F6FB0" stroke-width="2" stroke-dasharray="4 3"/>'
svg+='</g>'
svg+=f'<g id="legend" class="fd"><circle cx="300" cy="50" r="6" fill="{G_S}" stroke="#4E9E6E"/><text class="tiny" x="310" y="54">class +1</text>'
svg+=f'<rect x="294" y="62" width="12" height="12" rx="2" fill="{R_S}" stroke="#C97F7F"/><text class="tiny" x="310" y="72">class −1</text></g>'
# XOR points
XS=200; XO=(104,296)
def qx(a,b): return (XO[0]+a*XS, XO[1]-b*XS)
svg+='<g id="xor" class="fd">'
for i,((a,b),t) in enumerate([((0,0),-1),((1,1),-1),((1,0),1),((0,1),1)]):
    cx,cy=qx(a,b)
    if t==1: svg+=f'<circle cx="{cx}" cy="{cy}" r="8" fill="{G_S}" stroke="#4E9E6E" stroke-width="1.5"/>'
    else: svg+=f'<rect x="{cx-7.5}" y="{cy-7.5}" width="15" height="15" rx="2" fill="{R_S}" stroke="#C97F7F" stroke-width="1.5"/>'
    svg+=f'<text class="tiny mono" x="{cx+14}" y="{cy+(16 if b==0 else -10)}">({a},{b})</text>'
svg+='</g>'
# h-space points
HS=110
def hx(a,b): return (XO[0]+a*HS, XO[1]-b*HS)
svg+='<g id="hsp" class="fd">'
for (a,b),t,lab in [((0,0),-1,"(0,0) ← (0,0)"),((1,0),1,"(1,0) ← (1,0) and (0,1)"),((2,1),-1,"(2,1) ← (1,1)")]:
    cx,cy=hx(a,b)
    if t==1: svg+=f'<circle cx="{cx}" cy="{cy}" r="8" fill="{G_S}" stroke="#4E9E6E" stroke-width="1.5"/>'
    else: svg+=f'<rect x="{cx-7.5}" y="{cy-7.5}" width="15" height="15" rx="2" fill="{R_S}" stroke="#C97F7F" stroke-width="1.5"/>'
    svg+=f'<text class="tiny mono" x="{cx+14}" y="{cy-10 if b==1 else cy+16}">{lab}</text>'
# separating line in h-space: h1 - 2 h2 = 0.5
a1,b1=hx(0.5,0); a2,b2=hx(2.5,1.0)
svg+=f'<path d="M{a1},{b1} L{a2},{b2}" stroke="{INK}" stroke-width="2"/>'
svg+=f'<text class="tiny" x="300" y="284" text-anchor="middle">h₁ − 2h₂ = 0.5</text>'
svg+=f'<line x1="{BX0}" y1="{BY1}" x2="{BX1}" y2="{BY1}" stroke="{N_S}"/><line x1="{BX0}" y1="{BY0}" x2="{BX0}" y2="{BY1}" stroke="{N_S}"/>'
svg+=f'<text class="tiny" x="{BX1}" y="{BY1+14}" text-anchor="end">h₁</text><text class="tiny" x="{BX0-4}" y="{BY0+8}" text-anchor="end">h₂</text>'
svg+='</g>'
# ----- neuron diagram (right, top)
NX=420
svg+='<g id="neuron" class="fd">'
svg+=f'<circle cx="{NX+30}" cy="70" r="20" fill="{B_F}" stroke="{B_S}" stroke-width="1.5"/><text class="lbl-b" x="{NX+30}" y="74" text-anchor="middle">x₁</text>'
svg+=f'<circle cx="{NX+30}" cy="150" r="20" fill="{B_F}" stroke="{B_S}" stroke-width="1.5"/><text class="lbl-b" x="{NX+30}" y="154" text-anchor="middle">x₂</text>'
svg+=f'<path d="M{NX+50},74 L{NX+150},104" stroke="{N_S}" stroke-width="1.8"/><path d="M{NX+50},146 L{NX+150},116" stroke="{N_S}" stroke-width="1.8"/>'
svg+=f'<text id="wl1" class="tiny mono" x="{NX+96}" y="78" text-anchor="middle" font-weight="650">w₁</text>'
svg+=f'<text id="wl2" class="tiny mono" x="{NX+96}" y="146" text-anchor="middle" font-weight="650">w₂</text>'
svg+=f'<circle cx="{NX+170}" cy="110" r="24" fill="{N_F}" stroke="{N_S}" stroke-width="1.5"/><text class="lbl-b" x="{NX+170}" y="115" text-anchor="middle">Σ</text>'
svg+=f'<text id="bl" class="tiny mono" x="{NX+170}" y="150" text-anchor="middle" fill="{INK3}">+ b</text>'
svg+=f'<path d="M{NX+194},110 L{NX+236},110" stroke="{N_S}" stroke-width="1.8"/>'
svg+=f'<rect x="{NX+238}" y="90" width="60" height="40" rx="8" fill="{A_F}" stroke="{A_S}" stroke-width="1.4"/>'
svg+=f'<path d="M{NX+248},120 L{NX+268},120 L{NX+268},100 L{NX+288},100" stroke="{INK}" stroke-width="1.6" fill="none"/>'
svg+=f'<text class="tiny" x="{NX+268}" y="144" text-anchor="middle">step: s &gt; 0 ?</text>'
svg+=f'<path d="M{NX+298},110 L{NX+340},110" stroke="{N_S}" stroke-width="1.8"/>'
svg+=f'<text class="lbl-b" x="{NX+350}" y="114">±1</text>'
svg+=f'<text id="sline" class="tiny mono" x="{NX+30}" y="30" fill="{INK2}">s = w₁x₁ + w₂x₂ + b</text>'
svg+='</g>'
# ----- tiny 2-2-1 net for XOR (right, top) -----
svg+='<g id="net2" class="fd">'
def mini_node(cx,cy,lab,f=N_F,s=N_S):
    return f'<circle cx="{cx}" cy="{cy}" r="17" fill="{f}" stroke="{s}" stroke-width="1.4"/><text class="tiny" x="{cx}" y="{cy+4}" text-anchor="middle" font-weight="650">{lab}</text>'
NN=[(NX+40,70),(NX+40,150)]; HH=[(NX+190,70),(NX+190,150)]; OO=(NX+340,110)
for a in NN:
    for b in HH: svg+=f'<path d="M{a[0]+17},{a[1]} L{b[0]-17},{b[1]}" stroke="{N_S}" stroke-width="1.5"/>'
for b in HH: svg+=f'<path d="M{b[0]+17},{b[1]} L{OO[0]-17},{OO[1]}" stroke="{N_S}" stroke-width="1.5"/>'
svg+=mini_node(*NN[0],"x₁",B_F,B_S)+mini_node(*NN[1],"x₂",B_F,B_S)+mini_node(*HH[0],"h₁",G_F,G_S)+mini_node(*HH[1],"h₂",G_F,G_S)+mini_node(*OO,"out",A_F,A_S)
svg+=f'<text class="tiny mono" x="{HH[0][0]}" y="{HH[0][1]-26}" text-anchor="middle">h₁ = ReLU(x₁ + x₂)</text>'
svg+=f'<text class="tiny mono" x="{HH[1][0]}" y="{HH[1][1]+32}" text-anchor="middle">h₂ = ReLU(x₁ + x₂ − 1)</text>'
svg+=f'<text class="tiny mono" x="{OO[0]}" y="{OO[1]+34}" text-anchor="middle">h₁ − 2h₂ &gt; 0.5 ?</text>'
svg+=f'<text class="tiny mono" x="{NX+30}" y="30" fill="{INK2}">one hidden layer of two neurons</text>'
svg+='</g>'
# ----- text panel (right, bottom)
TX,TY=410,208
svg+=f'<g id="tp"><rect x="{TX}" y="{TY}" width="426" height="168" rx="9" fill="#FAFAFB" stroke="{N_S}"/>'
svg+=f'<text id="tt" class="tiny" x="{TX+12}" y="{TY+20}" font-weight="650"></text>'
for i in range(6):
    svg+=f'<text id="t{i}" class="tiny mono" x="{TX+12}" y="{TY+42+i*20}" fill="{INK}" xml:space="preserve" style="white-space:pre"></text>'
svg+='</g>'
js="""
var ST=%s;
function P(a){return a.map(function(p){return p[0].toFixed(1)+','+p[1].toFixed(1)}).join(' ')}
function state(k,showMis){var s=ST[k];
  $('dl').setAttribute('d','M'+s.seg[0][0].toFixed(1)+','+s.seg[0][1].toFixed(1)+' L'+s.seg[1][0].toFixed(1)+','+s.seg[1][1].toFixed(1));o('dl',1);
  $('half').setAttribute('points',P(s.poly));o('half',1);
  for(var i=0;i<8;i++)o('mk'+i,showMis&&s.mis.indexOf(i)>=0?1:0);
  tx('wl1',s.w[0].toFixed(1));tx('wl2',s.w[1].toFixed(1));tx('bl','b = '+s.b.toFixed(1));}
function panel(t,a,b,c,d,e,f){tx('tt',t||'');tx('t0',a||'');tx('t1',b||'');tx('t2',c||'');tx('t3',d||'');tx('t4',e||'');tx('t5',f||'')}
function base(){o('dl',0);o('dl2',0);o('dl3',0);o('half',0);for(var i=0;i<8;i++){o('mk'+i,0);o('up'+i,0)}
  o('sep',1);o('legend',1);o('xor',0);o('hsp',0);o('neuron',0);o('net2',0);o('axes',1);
  tx('wl1','w₁');tx('wl2','w₂');tx('bl','+ b');panel()}
var S=[
{c:'Eight points, two classes. The task is the oldest one in machine learning: find a rule that says which class a <i>new</i> point belongs to. The simplest rule is a straight line.',
 a:function(){panel('the data','4 points of class +1  (green circles)','4 points of class −1  (red squares)','','a rule = a function  f(x₁, x₂) → {+1, −1}')}},
{c:'A <b>neuron</b> is that rule. It multiplies each input by a weight, adds them, adds a bias, and fires if the sum is positive: <b>s = w₁x₁ + w₂x₂ + b</b>, output = +1 if s &gt; 0 else −1. This is Rosenblatt’s perceptron, 1958.',
 a:function(){o('neuron',1);panel('a perceptron','s = w₁·x₁ + w₂·x₂ + b','output = +1 if s > 0, else −1','','the weights decide how much each input matters;','the bias shifts the threshold')}},
{c:'On the plot, <b>s = 0 is a line</b> and the neuron predicts +1 on one side of it. Start with a guess, w = (0, 1), b = −3: the line x₂ = 3. Three points land on the wrong side (orange rings).',
 a:function(){o('neuron',1);state(0,1);panel('w = (0, 1), b = −3','line:  0·x₁ + 1·x₂ − 3 = 0  →  x₂ = 3','green side: s > 0','','3 mistakes (orange rings): (2,3) sits on the line','(s = 0 is not > 0); (3.4,2.2) and (2.6,2.4) are below it')}},
{c:'<b>The perceptron learning rule.</b> Take one mistake and nudge the line toward it: <b>w ← w + t·x</b>, <b>b ← b + t</b>, where t is the true label. The point (2, 3) should be +1, so its coordinates are <i>added</i> to w. The line rotates to include it.',
 a:function(){o('neuron',1);state(1,1);o('up0',1);panel('update 1: point (2, 3), true label +1  (blue ring)','w ← (0, 1) + (+1)·(2, 3) = (2, 4)','b ← −3 + (+1) = −2','','adding x to w makes w·x larger for that x, so it moves','to the +1 side — overshooting: now 4 −1 points are wrong')}},
{c:'Next mistake: (1, 1.2) is now on the +1 side but should be −1, so its coordinates are <i>subtracted</i>: w = (1, 2.8), b = −3. Each update is one point’s worth of correction — no calculus, no loss function yet.',
 a:function(){o('neuron',1);state(2,1);o('up4',1);panel('update 2: point (1, 1.2), true label −1  (blue ring)','w ← (2, 4) − (1, 1.2) = (1, 2.8)','b ← −2 − 1 = −3','','subtracting x pushes that point back','toward the −1 side')}},
{c:'Four more updates and every point is on the correct side: w = (1.4, 1.4), b = −5. <b>If a separating line exists, this loop is guaranteed to find one</b> (the perceptron convergence theorem). Notice it stops at <i>a</i> line, not the best one.',
 a:function(){o('neuron',1);state(6,1);panel('after 6 updates: w = (1.4, 1.4), b = −5','line: 1.4x₁ + 1.4x₂ = 5','0 mistakes → the loop stops','','guaranteed to converge if the data is linearly','separable — and useless if it is not')}},
{c:'<b>Where it breaks.</b> XOR: (0,0) and (1,1) are one class, (1,0) and (0,1) the other. Try any line — it always strands one point on the wrong side. One neuron cannot learn XOR, and that fact stalled the field for over a decade (Minsky &amp; Papert, 1969).',
 a:function(){o('sep',0);o('legend',0);o('xor',1);o('neuron',1);tx('wl1','?');tx('wl2','?');tx('bl','b = ?');
   $('dl2').setAttribute('d','M54,146 L254,346');o('dl2',1);$('dl3').setAttribute('d','M154,46 L354,246');o('dl3',1);
   panel('XOR: no line works','(0,0) → −1    (1,1) → −1','(1,0) → +1    (0,1) → +1','','the +1 points sit on opposite corners;','any line that separates them cuts the −1 pair too')}},
{c:'<b>The fix is a hidden layer.</b> Two neurons first, each drawing its own line, then one more neuron on top of <i>their</i> outputs. h₁ = ReLU(x₁ + x₂) and h₂ = ReLU(x₁ + x₂ − 1); output = h₁ − 2h₂.',
 a:function(){o('sep',0);o('legend',0);o('xor',1);o('net2',1);panel('the hidden layer, point by point','x         h₁ = ReLU(x₁+x₂)   h₂ = ReLU(x₁+x₂−1)   h₁−2h₂','(0,0)     0                   0                    0  → −1','(1,0)     1                   0                    1  → +1','(0,1)     1                   0                    1  → +1','(1,1)     2                   1                    0  → −1')}},
{c:'Look at where the hidden layer <b>moved the points</b>. In (h₁, h₂) space the two +1 inputs land on the same spot, and the four points are now separable by one line — which is exactly what the output neuron draws. A layer does not draw a better line; it <b>bends the space</b> so the next line works.',
 a:function(){o('sep',0);o('legend',0);o('xor',0);o('axes',0);o('hsp',1);o('net2',1);panel('in hidden space','(0,0) → (0,0)','(1,0) → (1,0)     (0,1) → (1,0)   ← same point!','(1,1) → (2,1)','','now a single line separates them: h₁ − 2h₂ = 0.5')}},
{c:'<b>That is the whole idea of a neural network.</b> One neuron draws a line. A layer of neurons bends the space. Stacked layers bend it repeatedly until the classes come apart. The next page runs the numbers through such a stack — the forward pass.',
 a:function(){o('sep',0);o('legend',0);o('axes',0);o('hsp',1);o('net2',1);panel('from here','neuron        = weighted sum + bend','layer         = many neurons, one matrix multiply','network       = layers stacked','learning      = adjust every weight from mistakes','              (the perceptron rule, generalised: gradients)')}}
];
"""%json.dumps(STATES)
build("perceptron.html","The perceptron — a neuron is a weighted vote, and a vote is a line",
      "One neuron learns a line from its mistakes; XOR shows why you need a hidden layer.",svg,js,"0 0 860 400")
print("ok")
