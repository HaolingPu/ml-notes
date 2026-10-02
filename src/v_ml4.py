from shell import build
from ml_common import *
Y=118
ops=[("linear1","W₁x + b₁",150),("relu","ReLU",286),("linear2","w₂·h + b₂",424),("sigmoid","σ",560),("bce","−log ŷ",690)]
tens=[("tx","x",60,"(1.0, 0.5)",""),("tz","z",220,"(0.5, 1.0)","(−0.2, 0.4)"),("th","h",354,"(0.5, 1.0)","(−0.2, 0.4)"),
      ("tu","u",494,"0.0","−0.5"),("ty","ŷ",626,"0.5","−2.0"),("tl","L",770,"0.693","1")]
svg=''
# edges along the chain
chain_x=[60,150,220,286,354,424,494,560,626,690,770]
for i in range(len(chain_x)-1):
    svg+=f'<path d="M{chain_x[i]+22},{Y} L{chain_x[i+1]-22},{Y}" stroke="{N_S}" stroke-width="1.6" fill="none" marker-end="url(#fm)"/>'
svg='<defs><marker id="fm" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="5" markerHeight="5" orient="auto"><path d="M0,1 L9,5 L0,9 z" fill="#B9B9C4"/></marker>'+\
    '<marker id="gm" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M0,1 L9,5 L0,9 z" fill="'+GRAD+'"/></marker></defs>'+svg
# reverse arrows (hidden)
for i in range(len(chain_x)-1):
    svg+=f'<path id="rv{i}" class="fd" d="M{chain_x[i+1]-24},{Y+6} L{chain_x[i]+24},{Y+6}" stroke="{GRAD}" stroke-width="2" stroke-dasharray="5 4" fill="none" marker-end="url(#gm)"/>'
# op nodes
for idp,lab,x in ops:
    svg+=f'<g id="{idp}" class="fd"><rect x="{x-40}" y="{Y-20}" width="80" height="40" rx="8" fill="{V_F}" stroke="{V_S}" stroke-width="1.5"/>'
    svg+=f'<text class="tiny mono" x="{x}" y="{Y+4}" text-anchor="middle" font-weight="650">{lab}</text>'
    svg+=f'<text id="{idp}s" class="tiny mono fd" x="{x}" y="{Y-28}" text-anchor="middle" fill="{INK3}"></text></g>'
# tensor nodes
for idp,lab,x,val,grad in tens:
    f=B_F if idp=="tx" else N_F; s=B_S if idp=="tx" else N_S
    svg+=f'<g id="{idp}"><circle cx="{x}" cy="{Y}" r="17" fill="{f}" stroke="{s}" stroke-width="1.5"/>'
    svg+=f'<text class="lbl-b" x="{x}" y="{Y+4}" text-anchor="middle">{lab}</text>'
    svg+=f'<text id="{idp}v" class="tiny mono fd" x="{x}" y="{Y-24}" text-anchor="middle" fill="#2F6FB0" font-weight="650">{val}</text>'
    svg+=f'<text id="{idp}g" class="tiny mono fd" x="{x}" y="{Y+36}" text-anchor="middle" fill="{GRAD}" font-weight="650">{grad}</text></g>'
# parameters feeding ops from below
params=[("pW1","W₁, b₁",150,"[[−0.2, −0.1], [0.4, 0.2]]  (−0.2, 0.4)"),("pw2","w₂, b₂",424,"(−0.25, −0.5)  −0.5"),("py","y = 1",690,"")]
for idp,lab,x,g in params:
    svg+=f'<path d="M{x},{Y+74} L{x},{Y+24}" stroke="{N_S}" stroke-width="1.6" fill="none" marker-end="url(#fm)"/>'
    if idp!="py": svg+=f'<path id="{idp}r" class="fd" d="M{x+6},{Y+24} L{x+6},{Y+72}" stroke="{GRAD}" stroke-width="2" stroke-dasharray="5 4" fill="none" marker-end="url(#gm)"/>'
    svg+=f'<g id="{idp}"><rect x="{x-38}" y="{Y+76}" width="76" height="30" rx="7" fill="{P_F if idp!="py" else N_F}" stroke="{P_S if idp!="py" else N_S}" stroke-width="1.4"/>'
    svg+=f'<text class="tiny mono" x="{x}" y="{Y+95}" text-anchor="middle" font-weight="650">{lab}</text>'
    svg+=f'<text id="{idp}g" class="tiny mono fd" x="{x}" y="{Y+122}" text-anchor="middle" fill="{GRAD}" font-weight="650">{g}</text></g>'
svg+=f'<text id="leafnote" class="tiny fd" x="60" y="{Y+95}" text-anchor="middle" fill="{INK3}">x: no grad needed</text>'
# bottom panels: code (left) and notes (right)
CX,CY,CW,CH=24,262,430,126
svg+=f'<g id="code"><rect x="{CX}" y="{CY}" width="{CW}" height="{CH}" rx="9" fill="#FAFAFB" stroke="{N_S}"/>'
code=["x  = torch.tensor([1.0, 0.5])",
      "W1 = torch.tensor([[0.7,-0.6],[0.3,1.0]], requires_grad=True)",
      "h  = torch.relu(W1 @ x + b1)            # b1, w2, b2 likewise",
      "yhat = torch.sigmoid(w2 @ h + b2)",
      "loss = -torch.log(yhat)                 # y = 1",
      "loss.backward()",
      "W1.grad   # tensor([[-0.2, -0.1], [0.4, 0.2]])"]
for i,l in enumerate(code):
    svg+=f'<text id="cd{i}" class="tiny mono fd" x="{CX+12}" y="{CY+19+i*16}" fill="{INK}" xml:space="preserve" style="white-space:pre">{l.replace("&","&amp;").replace("<","&lt;")}</text>'
svg+='</g>'
NX,NY,NW,NH=470,262,366,126
svg+=f'<g id="note" class="fd"><rect x="{NX}" y="{NY}" width="{NW}" height="{NH}" rx="9" fill="{A_F}" stroke="{A_S}"/>'
svg+=f'<text id="nt" class="tiny" x="{NX+12}" y="{NY+18}" font-weight="650"></text>'
for i in range(5):
    svg+=f'<text id="n{i}" class="tiny mono" x="{NX+12}" y="{NY+38+i*17}" fill="{INK}" xml:space="preserve" style="white-space:pre"></text>'
svg+='</g>'
svg+=f'<rect id="ring" class="fd" x="0" y="0" width="0" height="0" rx="10" fill="none" stroke="{GRAD}" stroke-width="2"/>'

js="""
var TV=['tz','th','tu','ty','tl'],TG=['tz','th','tu','ty','tl'],RV=['rv1','rv2','rv3','rv4','rv5','rv6','rv7','rv8','rv9'];
var OPS=['linear1','relu','linear2','sigmoid','bce'];
function vals(on){TV.forEach(function(k){o(k+'v',on)})}
function grads(ids){TG.forEach(function(k){o(k+'g',ids.indexOf(k)>=0?1:0)})}
function rvs(ids){RV.forEach(function(k){o(k,ids.indexOf(k)>=0?1:0)})}
function saved(on){tx('linear1s',on?'saves x':'');tx('relus',on?'saves z>0':'');tx('linear2s',on?'saves h':'');tx('sigmoids',on?'saves ŷ':'');tx('bces',on?'saves ŷ':'')}
function note(t,a,b,c,d,e){o('note',1);tx('nt',t||'');tx('n0',a||'');tx('n1',b||'');tx('n2',c||'');tx('n3',d||'');tx('n4',e||'')}
function code(n){for(var i=0;i<7;i++)o('cd'+i,i<n?1:0.22)}
function ring(x,y,w,h){var r=$('ring');if(x===null){r.style.opacity=0;return}r.style.opacity=1;r.setAttribute('x',x);r.setAttribute('y',y);r.setAttribute('width',w);r.setAttribute('height',h)}
function pg(on){o('pW1g',on);o('pw2g',on);o('pW1r',on);o('pw2r',on)}
function base(){vals(0);grads([]);rvs([]);o('rv0',0);saved(0);o('note',0);code(5);ring(null);pg(0);o('leafnote',0);
  OPS.forEach(function(k){$(k).firstChild.setAttribute('fill','#EFEAF8')})}
function hot(k){$(k).firstChild.setAttribute('fill','#FBEBD2')}
var S=[
{c:'Write the forward pass as ordinary code and PyTorch builds this graph <b>while the code runs</b>: every operation becomes a node, every tensor an edge between nodes. Nothing was declared ahead of time — define-by-run.',
 a:function(){code(5)}},
{c:'The forward pass computes each value <i>and</i> each node quietly <b>saves what its derivative will need</b>: linear keeps its input, ReLU keeps which entries were positive, sigmoid keeps its own output. These saved tensors are the activation memory.',
 a:function(){vals(1);saved(1);code(5)}},
{c:'<b>No node knows the whole formula.</b> Each knows only its own local derivative. That is the entire trick: a global gradient is assembled from local pieces that never see each other.',
 a:function(){vals(1);saved(1);note('local derivative of each node','linear:   ∂out/∂W = input,   ∂out/∂input = W','relu:     1 where z > 0, else 0','sigmoid:  ŷ (1 − ŷ)','−log:     −1 / ŷ')}},
{c:'<code>loss.backward()</code> seeds the gradient at L with 1 and walks the graph <b>in reverse order</b>. The first node it meets is −log: local derivative −1/ŷ = −2.0. That becomes the gradient at ŷ.',
 a:function(){vals(1);code(6);grads(['tl','ty']);rvs(['rv9','rv8']);hot('bce');ring(650,92,80,52);note('node 1 of 5: −log','incoming grad:  1','local:          −1/ŷ = −1/0.5 = −2.0','outgoing grad:  1 × (−2.0) = −2.0  → ŷ')}},
{c:'Sigmoid node: incoming −2.0 × local ŷ(1−ŷ) = 0.25 gives <b>−0.5 at u</b>. Autodiff did not know the shortcut ŷ − y from the backprop page; it reached the same number by multiplying local pieces.',
 a:function(){vals(1);code(6);grads(['tl','ty','tu']);rvs(['rv9','rv8','rv7','rv6']);hot('sigmoid');ring(520,92,80,52);note('node 2 of 5: sigmoid','incoming grad:  −2.0','local:          ŷ(1−ŷ) = 0.5·0.5 = 0.25','outgoing grad:  −2.0 × 0.25 = −0.5  → u')}},
{c:'The linear node has <b>three inputs</b> — h, w₂ and b₂ — so it emits a gradient for each: ∂L/∂h = −0.5·w₂ = (−0.2, 0.4) continues down the chain; w₂.grad = −0.5·h and b₂.grad = −0.5 land on the leaves. One incoming vector, several outgoing: a vector–Jacobian product.',
 a:function(){vals(1);code(6);grads(['tl','ty','tu','th']);rvs(['rv9','rv8','rv7','rv6','rv5','rv4']);hot('linear2');ring(384,92,80,52);o('pw2g',1);o('pw2r',1);note('node 3 of 5: w₂·h + b₂','incoming grad:  −0.5','→ h:   −0.5 · w₂ = (−0.2, 0.4)     (keeps going)','→ w₂:  −0.5 · h  = (−0.25, −0.5)  (a leaf: stored in .grad)','→ b₂:  −0.5')}},
{c:'ReLU passes the vector through its saved mask (both on), then the first linear node drops <b>W₁.grad</b> and <b>b₁.grad</b> onto their leaves. x never asked for a gradient, so the walk stops. Every <code>.grad</code> matches the hand derivation exactly.',
 a:function(){vals(1);code(7);grads(['tl','ty','tu','th','tz']);rvs(RV);OPS.forEach(hot);pg(1);o('leafnote',1);note('nodes 4–5: relu, then W₁x + b₁','relu:    (−0.2, 0.4) × mask (1, 1) = (−0.2, 0.4)','→ W₁:  outer((−0.2, 0.4), x) = [[−0.2, −0.1], [0.4, 0.2]]','→ b₁:  (−0.2, 0.4)','→ x:   skipped — requires_grad = False')}},
{c:'<b>Why reverse mode.</b> The loss is one number and the parameters are many. One backward sweep from that number fills <i>every</i> .grad. Forward-mode differentiation would need one sweep per parameter — eight here, hundreds of billions in an LLM.',
 a:function(){vals(1);code(7);grads(TG);rvs(RV);pg(1);note('reverse vs forward mode','reverse:  1 sweep from the scalar loss \u2192 all N .grad','forward:  N sweeps, one per parameter','same local rules, opposite order of multiplication','N = 8 here; N \u2248 10\u00b9\u00b9 in a frontier LLM')}},
{c:'<b>The price.</b> Every saved tensor must stay in memory from the forward pass until the backward pass reaches it — batch × sequence × depth of them. That is why training needs several times the memory of inference, and why activation checkpointing recomputes some of them instead of storing them.',
 a:function(){vals(1);saved(1);code(7);note('activation memory','saved here: x, (z>0), h, \u0177 \u2014 five small tensors','in a transformer: every layer\u2019s input, attention probs,','MLP activations \u2014 for every token in the batch','checkpointing: drop them, recompute in backward (~30% more FLOPs)')}},
{c:'The whole training step is three lines. <code>backward()</code> fills the .grad fields; the optimizer reads them to move the weights; <code>zero_grad()</code> clears them — because gradients <b>accumulate</b> into .grad (that is how a tensor used in two places gets the sum of both paths).',
 a:function(){vals(1);code(7);pg(1);note('the training step','loss.backward()        # fill every .grad (this page)','optimizer.step()       # w ← w − η·grad  (next page)','optimizer.zero_grad()  # grads accumulate; reset them')}}
];
"""
build("autodiff.html","Automatic differentiation — what loss.backward() actually does",
      "The same network as a computational graph: local derivatives, walked in reverse, landing on .grad.",svg,js,"0 0 860 400")
print("ok")
