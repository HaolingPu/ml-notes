from shell import build
from ml_common import *
import math
sig=lambda z:1/(1+math.exp(-z)); tanh=math.tanh; relu=lambda z:max(0.0,z)
leaky=lambda z: z if z>0 else 0.01*z
gelu=lambda z:0.5*z*(1+math.erf(z/math.sqrt(2)))
def d(f,z,h=1e-4): return (f(z+h)-f(z-h))/(2*h)
# main plot
X0,SCX,Y0,SCY=255,65,270,65
def px(z,y): return (X0+z*SCX, Y0-y*SCY)
svg=f'<rect x="24" y="22" width="446" height="354" rx="10" fill="#FCFCFD" stroke="{N_S}"/>'
svg+=f'<line x1="{px(-3,0)[0]}" y1="{Y0}" x2="{px(3,0)[0]}" y2="{Y0}" stroke="{N_S}"/><line x1="{X0}" y1="{px(0,3.1)[1]}" x2="{X0}" y2="{px(0,-1.3)[1]}" stroke="{N_S}"/>'
for z in (-2,-1,1,2): svg+=f'<text class="tiny" x="{px(z,0)[0]}" y="{Y0+13}" text-anchor="middle" fill="{INK3}">{z}</text>'
for y in (1,2,3,-1): svg+=f'<text class="tiny" x="{X0-6}" y="{px(0,y)[1]+4}" text-anchor="end" fill="{INK3}">{y}</text>'
svg+=f'<text class="tiny" x="{px(3,0)[0]}" y="{Y0+28}" text-anchor="end">z (the weighted sum)</text><text class="tiny" x="{X0+6}" y="{px(0,3.1)[1]+4}">a = f(z)</text>'
COL={"step":INK2,"sig":"#2F6FB0","tanh":"#2E8B73","relu":"#C2602B","leaky":"#C2602B","gelu":"#6B4FA8"}
def curve(idp,f,col,dash="",lo=-3,hi=3,clip=3.0):
    pts=[]
    for i in range(121):
        z=lo+(hi-lo)*i/120; y=max(-1.3,min(clip,f(z))); pts.append(f"{px(z,y)[0]:.1f},{px(z,y)[1]:.1f}")
    da=(' stroke-dasharray="%s"'%dash) if dash else ""
    return f'<polyline id="{idp}" class="fd" points="{" ".join(pts)}" fill="none" stroke="{col}" stroke-width="2.2"{da}/>'
svg+=f'<g id="cstep" class="fd"><path d="M{px(-3,0)[0]},{Y0} L{X0},{Y0} M{X0},{px(0,1)[1]} L{px(3,1)[0]},{px(3,1)[1]}" fill="none" stroke="{INK2}" stroke-width="2.2"/><circle cx="{X0}" cy="{px(0,1)[1]}" r="3" fill="{INK2}"/></g>'
svg+=curve("csig",sig,COL["sig"])+curve("ctanh",tanh,COL["tanh"])+curve("crelu",relu,COL["relu"])+curve("cleaky",leaky,COL["leaky"],"5 4")+curve("cgelu",gelu,COL["gelu"])
# curve labels
labs=[("lstep","step",2.4,1.15,COL["step"]),("lsig","sigmoid",2.2,0.78,COL["sig"]),("ltanh","tanh",-2.2,-0.78,COL["tanh"]),("lrelu","ReLU",2.35,2.6,COL["relu"]),("lleaky","leaky ReLU",-2.3,0.25,COL["leaky"]),("lgelu","GELU",1.3,1.65,COL["gelu"])]
for idp,t,z,y,c in labs:
    svg+=f'<text id="{idp}" class="tiny fd" x="{px(z,y)[0]}" y="{px(z,y)[1]}" fill="{c}" font-weight="650" text-anchor="middle">{t}</text>'
# slope panel (top right)
SX,SY,SW,SH=490,22,346,170
svg+=f'<g id="slope" class="fd"><rect x="{SX}" y="{SY}" width="{SW}" height="{SH}" rx="9" fill="#FAFAFB" stroke="{N_S}"/>'
svg+=f'<text id="slt" class="tiny" x="{SX+12}" y="{SY+18}" font-weight="650">the slope f′(z) — what backprop multiplies by</text>'
sx0,ssx,sy0,ssy=SX+173,45,SY+SH-30,95
def spx(z,y): return (sx0+z*ssx,sy0-y*ssy)
svg+=f'<line x1="{spx(-3,0)[0]}" y1="{sy0}" x2="{spx(3,0)[0]}" y2="{sy0}" stroke="{N_S}"/>'
for y,t in ((0.25,"0.25"),(1,"1")):
    svg+=f'<line x1="{spx(-3,y)[0]}" y1="{spx(0,y)[1]}" x2="{spx(3,y)[0]}" y2="{spx(0,y)[1]}" stroke="{N_S}" stroke-dasharray="2 3"/><text class="tiny" x="{spx(-3,y)[0]-4}" y="{spx(0,y)[1]+4}" text-anchor="end" fill="{INK3}">{t}</text>'
def dcurve(idp,f,col):
    pts=[]
    for i in range(121):
        z=-3+6*i/120; y=max(-0.2,min(1.15,d(f,z))); pts.append(f"{spx(z,y)[0]:.1f},{spx(z,y)[1]:.1f}")
    return f'<polyline id="{idp}" class="fd" points="{" ".join(pts)}" fill="none" stroke="{col}" stroke-width="2"/>'
svg+=dcurve("dsig",sig,COL["sig"])+dcurve("dtanh",tanh,COL["tanh"])+dcurve("drelu",relu,COL["relu"])+dcurve("dgelu",gelu,COL["gelu"])
svg+=f'<text id="dstep" class="tiny fd" x="{sx0}" y="{sy0-50}" text-anchor="middle" fill="{INK2}">slope 0 everywhere (and undefined at 0)</text>'
svg+='</g>'
# notes panel (bottom right)
NX,NY,NW,NH=490,206,346,170
svg+=f'<g id="notes"><rect x="{NX}" y="{NY}" width="{NW}" height="{NH}" rx="9" fill="{A_F}" stroke="{A_S}"/>'
svg+=f'<text id="nt" class="tiny" x="{NX+12}" y="{NY+18}" font-weight="650"></text>'
for i in range(7):
    svg+=f'<text id="n{i}" class="tiny mono" x="{NX+12}" y="{NY+38+i*19}" fill="{INK}" xml:space="preserve" style="white-space:pre"></text>'
svg+='</g>'
# chain panel: signal through 10 layers (overlays the slope panel)
svg+=f'<g id="chain" class="fd"><rect x="{SX}" y="{SY}" width="{SW}" height="{SH}" rx="9" fill="{R_F}" stroke="{R_S}"/>'
svg+=f'<text class="tiny" x="{SX+12}" y="{SY+18}" font-weight="650">a gradient crossing 10 layers at typical |z| ≈ 1</text>'
rows=[("sigmoid","0.20","× 0.20 × … × 0.20","≈ 1e−7"),("tanh","0.42","× 0.42 × … × 0.42","≈ 2e−4"),("ReLU (on)","1.00","× 1 × … × 1","= 1"),("ReLU (off)","0","× 0","= 0")]
for i,(a,b,c,e) in enumerate(rows):
    y=SY+44+i*26
    svg+=f'<text class="tiny mono" x="{SX+12}" y="{y}" fill="{INK}">{a}</text><text class="tiny mono" x="{SX+92}" y="{y}" fill="{INK}">slope {b}</text><text class="tiny mono" x="{SX+176}" y="{y}" fill="{INK2}">{c}</text><text class="tiny mono" x="{SX+SW-12}" y="{y}" text-anchor="end" fill="{INK}" font-weight="650">{e}</text>'
svg+=f'<text class="tiny" x="{SX+12}" y="{SY+SH-12}" fill="{INK2}">the first layers of a deep sigmoid network receive almost no signal</text></g>'
# softmax panel (overlays the main plot)
svg+=f'<g id="smx" class="fd"><rect x="24" y="22" width="446" height="354" rx="10" fill="#FCFCFD" stroke="{N_S}"/>'
svg+=f'<text class="tiny" x="40" y="46" font-weight="650">softmax: an activation for a whole vector of outputs</text>'
zs=[("cat",2.0,7.389,0.659),("dog",1.0,2.718,0.242),("bird",0.1,1.105,0.099)]
svg+=f'<text class="tiny mono" x="40" y="76" fill="{INK3}" xml:space="preserve" style="white-space:pre">class     logit z    e^z        p = e^z / Σ</text>'
for i,(n,z,e,p) in enumerate(zs):
    y=100+i*26
    svg+=f'<text class="tiny mono" x="40" y="{y}" fill="{INK}" xml:space="preserve" style="white-space:pre">{n:<9} {z:<10} {e:<10} {p}</text>'
    svg+=f'<rect x="300" y="{y-11}" width="{p*150:.0f}" height="14" rx="3" fill="{B_F}" stroke="{B_S}"/>'
svg+=f'<text class="tiny mono" x="40" y="186" fill="{INK}" xml:space="preserve" style="white-space:pre">Σ e^z = 7.389 + 2.718 + 1.105 = 11.212     Σ p = 1.000</text>'
svg+=f'<text class="tiny" x="40" y="222" fill="{INK2}">exponentiate (so every value is positive), then divide by the total:</text>'
svg+=f'<text class="tiny" x="40" y="240" fill="{INK2}">a probability distribution over classes. The biggest logit wins,</text>'
svg+=f'<text class="tiny" x="40" y="258" fill="{INK2}">but not absolutely — “soft” max. Sigmoid is the two-class special case.</text>'
svg+=f'<text class="tiny" x="40" y="296" fill="{INK2}">paired with cross-entropy, the gradient at the logits is p − onehot(y):</text>'
svg+=f'<text class="tiny mono" x="40" y="316" fill="{INK}">y = cat:  (0.659−1, 0.242, 0.099) = (−0.341, 0.242, 0.099)</text>'
svg+=f'<text class="tiny" x="40" y="346" fill="{INK2}">every LLM ends in exactly this: softmax over the vocabulary.</text></g>'
# usage table panel (overlays the main plot)
svg+=f'<g id="use" class="fd"><rect x="24" y="22" width="446" height="354" rx="10" fill="#FCFCFD" stroke="{N_S}"/>'
svg+=f'<text class="tiny" x="40" y="46" font-weight="650">which bend, where</text>'
use=[("hidden layers, MLPs / CNNs","ReLU","cheap, slope 1, no saturation"),("transformer MLP blocks","GELU / SiLU (SwiGLU)","smooth ReLU; GPT, BERT: GELU; Llama: SiLU"),("output, binary classification","sigmoid","one probability"),("output, many classes","softmax","a distribution over classes"),("output, regression","none (identity)","any real number"),("gates in LSTMs / GRUs","sigmoid, tanh","bounded, 0–1 for gates")]
svg+=f'<text class="tiny mono" x="40" y="76" fill="{INK3}" xml:space="preserve" style="white-space:pre">where                          activation</text>'
for i,(a,b,c) in enumerate(use):
    y=100+i*30
    svg+=f'<text class="tiny mono" x="40" y="{y}" fill="{INK}">{a}</text><text class="tiny mono" x="226" y="{y}" fill="{INK}" font-weight="650">{b}</text><text class="tiny" x="40" y="{y+14}" fill="{INK2}">{c}</text>'
svg+=f'<text class="tiny" x="40" y="300" fill="{INK2}">the rule: hidden layers want a slope that stays near 1 so gradients survive;</text>'
svg+=f'<text class="tiny" x="40" y="318" fill="{INK2}">the output layer wants whatever shape the loss expects.</text></g>'

js="""
var C=['cstep','csig','ctanh','crelu','cleaky','cgelu'],L=['lstep','lsig','ltanh','lrelu','lleaky','lgelu'],D=['dsig','dtanh','drelu','dgelu'];
function cv(ids,dim){C.forEach(function(k){var e=$(k);var on=ids.indexOf(k)>=0;e.style.opacity=on?1:(dim&&dim.indexOf(k)>=0?0.22:0)});
  L.forEach(function(k){var on=ids.indexOf('c'+k.slice(1))>=0;$(k).style.opacity=on?1:0})}
function dv(ids){D.forEach(function(k){o(k,ids.indexOf(k)>=0?1:0)})}
function note(t){var a=Array.prototype.slice.call(arguments,1);tx('nt',t||'');for(var i=0;i<7;i++)tx('n'+i,a[i]||'')}
function base(){cv([]);dv([]);o('dstep',0);o('chain',0);o('smx',0);o('use',0);o('slope',1);note()}
var S=[
{c:'Recall why the bend exists: without a nonlinearity between layers, a deep network is one linear map. The perceptron’s bend was a <b>step</b> — but its slope is 0 everywhere, so the chain rule has nothing to multiply. A step cannot be trained by gradients.',
 a:function(){cv(['cstep']);o('dstep',1);note('the two jobs of an activation','1. bend the space (so depth means something)','2. have a slope backprop can use','','the step does job 1 and fails job 2','every function below is a trade-off between','how it bends and how its slope behaves')}},
{c:'<b>Sigmoid</b>, σ(z) = 1/(1+e⁻ᵡ), squashes any number into (0, 1) — a probability, which is why the output layer used it. Its slope is σ(1−σ): at most <b>0.25</b>, and near zero once |z| is large. That saturation is the problem.',
 a:function(){cv(['csig']);dv(['dsig']);note('sigmoid','σ(z) = 1 / (1 + e⁻ᵡ)        range (0, 1)','σ′(z) = σ(z)(1 − σ(z))     at most 0.25','','good:  a probability; smooth','bad:   slope ≤ 0.25, and ≈ 0 for |z| > 4','       outputs are never negative (not centred)')}},
{c:'<b>tanh</b> is a rescaled sigmoid: range (−1, 1), centred on zero, slope up to 1 at the origin. Better signal than sigmoid, but it saturates just the same once |z| grows.',
 a:function(){cv(['ctanh'],['csig']);dv(['dtanh','dsig']);note('tanh','tanh(z) = 2σ(2z) − 1          range (−1, 1)','tanh′(z) = 1 − tanh²(z)       at most 1','','good:  zero-centred, slope up to 1','bad:   still saturates — slope ≈ 0 for |z| > 3','used:  RNN / LSTM gates, older MLPs')}},
{c:'<b>Why saturation kills deep networks.</b> Backprop multiplies one slope per layer. Ten sigmoid layers at typical |z| ≈ 1 multiply the gradient by 0.2 ten times — about 10⁻⁷. The early layers receive nothing and never learn. This is the <b>vanishing gradient</b>, and it is why deep nets did not work before 2010.',
 a:function(){cv(['csig','ctanh']);o('chain',1);note('vanishing gradients','∂L/∂W₁ = (…) · f′(z₁₀) · … · f′(z₁)','','ten factors each < 1 → a product near 0','','the fix is a slope that stays near 1:','ReLU — and later residual connections','and normalisation, which attack the same product')}},
{c:'<b>ReLU</b>, max(0, z): keep positives, zero negatives. Slope exactly 1 wherever the unit is on, so the signal passes through untouched — no saturation, no matter how large z gets — and it costs one comparison. The default for a decade.',
 a:function(){cv(['crelu']);dv(['drelu']);note('ReLU','ReLU(z) = max(0, z)','ReLU′(z) = 1 if z > 0 else 0','','good:  slope 1 — gradients survive depth','       cheap; sparse (half the units are 0)','bad:   not centred; slope 0 when off','used:  almost everywhere, 2012 – 2018')}},
{c:'<b>Dead ReLUs.</b> A unit whose z is negative for every input outputs 0 and has slope 0 — so its weights get no gradient and it can never recover. A big learning-rate step can kill units permanently. <b>Leaky ReLU</b> gives the negative side a small slope (0.01) so there is always a way back.',
 a:function(){cv(['crelu','cleaky']);dv(['drelu']);note('dead units and the leaky fix','a unit is dead when z < 0 for all inputs:','  output 0, slope 0, gradient 0 → stuck','','leaky ReLU(z) = z if z > 0 else 0.01 z','  slope 0.01 on the negative side','','also: PReLU (learned slope), ELU')}},
{c:'<b>GELU</b> is the smooth version transformers use: z·Φ(z), where Φ is the Gaussian CDF. It behaves like ReLU for large |z| but curves gently through zero, with a slight dip below it. GPT and BERT use GELU; Llama uses the close cousin SiLU = z·σ(z), gated as SwiGLU.',
 a:function(){cv(['cgelu'],['crelu']);dv(['dgelu','drelu']);note('GELU and SiLU','GELU(z) = z · Φ(z)      Φ = Gaussian CDF','SiLU(z) = z · σ(z)      (“swish”)','','smooth everywhere → slope never exactly 0','no dead units; slightly better accuracy','in transformers at the same cost','used:  GPT-2/3, BERT (GELU); Llama (SwiGLU)')}},
{c:'All of them side by side. The hidden layers of modern networks use ReLU or GELU because their slope stays near 1; sigmoid and tanh survive only where a <b>bounded</b> output is the point — gates, and probabilities.',
 a:function(){cv(['csig','ctanh','crelu','cgelu']);dv(['dsig','dtanh','drelu','dgelu']);note('reading the slope panel','ReLU / GELU:  slope ≈ 1 for z > 0','sigmoid:      slope ≤ 0.25 everywhere','tanh:         1 at the origin, 0 far out','','pick the hidden activation for its slope,','the output activation for its range')}},
{c:'The output layer is different: it has to produce what the loss expects. Binary → sigmoid. Many classes → <b>softmax</b>, which turns a vector of logits into a distribution: exponentiate, then divide by the sum. Paired with cross-entropy, its gradient at the logits is simply p − onehot(y).',
 a:function(){o('smx',1);o('slope',0);note('softmax','pᵢ = e^{zᵢ} / Σⱼ e^{zⱼ}','','every pᵢ > 0 and they sum to 1','subtract max(z) first for numerical safety','','with cross-entropy: ∂L/∂z = p − onehot(y)','the same “gradient = error” as the sigmoid case')}},
{c:'<b>Which bend, where.</b> Hidden layers: ReLU, or GELU/SiLU in transformers. Output: sigmoid for one probability, softmax for a distribution, nothing for a regression. Gates inside recurrent units: sigmoid and tanh, because bounded is the point there.',
 a:function(){o('use',1);o('slope',0);note('the one-line version','hidden: a slope near 1 (ReLU, GELU, SiLU)','output: the shape the loss expects','','sigmoid for P(yes), softmax for P(class),','identity for a number','','every LLM: GELU/SiLU inside, softmax at the end')}}
];
"""
build("activation-functions.html","Activation functions — the bend, and the slope backprop multiplies by",
      "Step, sigmoid, tanh, ReLU, GELU and softmax: what each one does to the signal going forward and to the gradient going back.",svg,js,"0 0 860 400")
print("ok")
