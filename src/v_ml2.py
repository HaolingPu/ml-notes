from shell import build
from ml_common import *
import math
svg=net_svg()
svg+=ledger()
# activation curve panel
PX,PY,PW,PH=600,296,236,92
svg+=f'<g id="curves" class="fd"><rect x="{PX}" y="{PY}" width="{PW}" height="{PH}" rx="9" fill="#FAFAFB" stroke="{N_S}"/>'
def mini(x0,title,fn,lo,hi,ylo,yhi,dots,idp):
    w,h=92,56; ox,oy=x0,PY+74
    sx=w/(hi-lo); sy=h/(yhi-ylo)
    pts=[]
    for i in range(41):
        v=lo+(hi-lo)*i/40; pts.append(f"{ox+(v-lo)*sx:.1f},{oy-(fn(v)-ylo)*sy:.1f}")
    s=f'<text class="tiny" x="{ox}" y="{PY+16}" font-weight="650">{title}</text>'
    s+=f'<line x1="{ox}" y1="{oy-(0-ylo)*sy:.1f}" x2="{ox+w}" y2="{oy-(0-ylo)*sy:.1f}" stroke="{N_S}"/>'
    s+=f'<line x1="{ox+(0-lo)*sx:.1f}" y1="{oy-h}" x2="{ox+(0-lo)*sx:.1f}" y2="{oy}" stroke="{N_S}"/>'
    s+=f'<polyline points="{" ".join(pts)}" fill="none" stroke="{INK2}" stroke-width="1.6"/>'
    for k,(v,lab) in enumerate(dots):
        s+=f'<g id="{idp}{k}" class="fd"><circle cx="{ox+(v-lo)*sx:.1f}" cy="{oy-(fn(v)-ylo)*sy:.1f}" r="4" fill="{A_F}" stroke="{A_S}" stroke-width="1.5"/>'
        s+=f'<text class="tiny mono" x="{ox+(v-lo)*sx+8:.1f}" y="{oy-(fn(v)-ylo)*sy+10:.1f}">{lab}</text></g>'
    return s
svg+=mini(PX+14,"ReLU(z) = max(0, z)",lambda v:max(0,v),-1.5,1.5,-0.2,1.5,[(0.5,"0.5"),(1.0,"1.0")],"rd")
svg+=mini(PX+130,"σ(u) = 1/(1+e⁻ᵘ)",lambda v:1/(1+math.exp(-v)),-4,4,-0.1,1.1,[(0.0,"0.5")],"sd")
svg+='</g>'
# "collapse" formula panel (shown once)
svg+=f'<g id="lin" class="fd"><rect x="{PX}" y="{PY}" width="{PW}" height="{PH}" rx="9" fill="{R_F}" stroke="{R_S}"/>'
svg+=f'<text class="tiny" x="{PX+14}" y="{PY+20}" font-weight="650">without the bend</text>'
svg+=f'<text class="lbl mono" x="{PX+14}" y="{PY+44}">W₂(W₁x + b₁) + b₂</text>'
svg+=f'<text class="lbl mono" x="{PX+14}" y="{PY+66}">= (W₂W₁) x + b′</text>'
svg+=f'<text class="tiny" x="{PX+14}" y="{PY+84}">one linear map — depth bought nothing</text></g>'
# shapes panel (zoom out)
svg+=f'<g id="shapes" class="fd"><rect x="24" y="300" width="560" height="86" rx="9" fill="{V_F}" stroke="{V_S}"/>'
svg+=f'<text class="tiny" x="38" y="320" font-weight="650">the same two lines at real scale</text>'
svg+=f'<text class="lbl mono" x="38" y="344">H = ReLU(X W₁ + b₁)    X: [batch × d_in]   W₁: [d_in × d_hidden]</text>'
svg+=f'<text class="lbl mono" x="38" y="368">ŷ = σ(H w₂ + b₂)        e.g. batch 4096, d 4096 → one big matmul per layer</text></g>'
# highlight ring
svg+=f'<circle id="ring" class="fd" cx="0" cy="0" r="{R+5}" fill="none" stroke="#8A6D3B" stroke-width="2"/>'

js="""
var HID=['e11','e12','e21','e22','eo1','eo2'];
function led(a,b,c){tx('led0',a||'');tx('led1',b||'');tx('led2',c||'')}
function edges(ids,on){HID.forEach(function(k){var e=$(k);e.setAttribute('stroke',ids.indexOf(k)>=0?'#8A6D3B':'#D5D5DC');e.setAttribute('stroke-width',ids.indexOf(k)>=0?2.6:1.6);
  $(k+'l').setAttribute('fill',ids.indexOf(k)>=0?'#8A6D3B':'#6B6B76')})}
function ring(x,y){var r=$('ring');if(x===null){r.style.opacity=0;return}r.style.opacity=1;r.setAttribute('cx',x);r.setAttribute('cy',y)}
function nv(id,v,f,s){tx(id+'v',v);var c=$(id).firstChild;c.setAttribute('fill',f);c.setAttribute('stroke',s)}
function base(){edges([],0);ring(null);o('nlring',0);o('led',0);led();o('curves',0);o('lin',0);o('shapes',0);
  o('rd0',0);o('rd1',0);o('sd0',0);
  nv('nh1','','#F1F1F4','#D5D5DC');nv('nh2','','#F1F1F4','#D5D5DC');nv('no','','#F1F1F4','#D5D5DC');
  tx('nh1a','');tx('nh2a','');tx('noa','');tx('nlv','');
  var l=$('nl').firstChild;l.setAttribute('fill','#F1F1F4');l.setAttribute('stroke','#D5D5DC')}
function h1(){nv('nh1','0.5','#E2EFE3','#A8CBAC');tx('nh1a','z₁ = 0.5')}
function h2(){nv('nh2','1.0','#E2EFE3','#A8CBAC');tx('nh2a','z₂ = 1.0')}
function out(){nv('no','0.5','#E2EFE3','#A8CBAC');tx('noa','u = 0.0')}
function loss(){tx('nlv','0.693');var l=$('nl').firstChild;l.setAttribute('fill','#FBEBD2');l.setAttribute('stroke','#E2BC85')}
var S=[
{c:'A tiny network: two inputs, two hidden neurons, one output. Every number on an edge is a <b>weight</b>, every <span class="q">b</span> is a <b>bias</b> — all learned. The input <b>x = (1.0, 0.5)</b> is the only thing that comes from outside.',
 a:function(){}},
{c:'A neuron does one thing: multiply each input by its weight, add them up, add the bias. Hidden neuron 1: <b>z₁ = 0.7·1.0 + (−0.6)·0.5 + 0.1 = 0.5</b>.',
 a:function(){edges(['e11','e21'],1);ring(318,96);o('led',1);led('z₁ = w₁₁·x₁ + w₁₂·x₂ + b₁','   = 0.7·1.0 + (−0.6)·0.5 + 0.1','   = 0.7 − 0.3 + 0.1 = 0.5');tx('nh1a','z₁ = 0.5')}},
{c:'Hidden neuron 2 does the same with its own weights: <b>z₂ = 0.3·1.0 + 1.0·0.5 + 0.2 = 1.0</b>. Both neurons together are <b>one matrix multiply</b>: z = W₁x + b₁.',
 a:function(){edges(['e12','e22'],1);ring(318,228);o('led',1);led('z = W₁ x + b₁','[0.7  −0.6] [1.0]   [0.1]   [0.5]','[0.3   1.0] [0.5] + [0.2] = [1.0]');tx('nh1a','z₁ = 0.5');tx('nh2a','z₂ = 1.0')}},
{c:'Then the <b>bend</b>: an activation function. ReLU keeps positive values and zeroes negative ones. Both z are positive, so <b>h = ReLU(z) = (0.5, 1.0)</b> passes through unchanged.',
 a:function(){h1();h2();o('curves',1);o('rd0',1);o('rd1',1);o('led',1);led('h = ReLU(z) = max(0, z)','h₁ = max(0, 0.5) = 0.5','h₂ = max(0, 1.0) = 1.0')}},
{c:'<b>Why the bend is not optional.</b> Without it, the next layer would multiply a linear map by another linear map — which is just one linear map. A hundred linear layers draw one straight line. The nonlinearity is what lets depth build curves.',
 a:function(){h1();h2();o('lin',1);o('led',1);led('with ReLU in between, the two layers do not merge:','ŷ = σ( w₂ · ReLU(W₁ x + b₁) + b₂ )','the bend is where the model stops being a line')}},
{c:'The output neuron reads the hidden layer the same way: <b>u = 0.4·0.5 + (−0.8)·1.0 + 0.6 = 0.0</b>. Same operation, one layer deeper.',
 a:function(){h1();h2();edges(['eo1','eo2'],1);ring(548,162);o('led',1);led('u = w₂ · h + b₂','  = 0.4·0.5 + (−0.8)·1.0 + 0.6','  = 0.2 − 0.8 + 0.6 = 0.0');tx('noa','u = 0.0')}},
{c:'The output bend is a <b>sigmoid</b>, which squashes any number into (0, 1) so it can be read as a probability. <b>ŷ = σ(0) = 0.5</b> — the network is exactly undecided.',
 a:function(){h1();h2();out();o('curves',1);o('sd0',1);o('led',1);led('ŷ = σ(u) = 1 / (1 + e⁻ᵘ)','  = 1 / (1 + e⁰) = 1 / 2 = 0.5','a probability: P(class = 1 | x)')}},
{c:'The true label is <b>y = 1</b>. The <b>loss</b> turns “how wrong” into one number. For a probability, cross-entropy: <b>L = −log ŷ = −log 0.5 = 0.693</b>. Everything in training exists to push this number down.',
 a:function(){h1();h2();out();loss();o('nlring',1);o('led',1);led('L = −[ y·log ŷ + (1−y)·log(1−ŷ) ]','  = −log 0.5 = 0.693','(for a regression you would use (ŷ − y)² instead)')}},
{c:'Zoom out. A real layer does exactly these two lines, but <b>X</b> is a whole batch and <b>W</b> is thousands wide. The forward pass is matmul, bend, matmul, bend — which is why GPUs, built for matmul, are the whole story of the infrastructure notes.',
 a:function(){h1();h2();out();loss();o('shapes',1)}},
{c:'<b>Keep every intermediate.</b> z, h, u and ŷ are all stored — the backward pass is about to need each one. That storage is why training needs far more memory than inference.',
 a:function(){h1();h2();out();loss();o('led',1);led('stored for backprop:  x = (1.0, 0.5)   z = (0.5, 1.0)   h = (0.5, 1.0)','                      u = 0.0   ŷ = 0.5   y = 1   L = 0.693','next: which way should each weight move?')}}
];
"""
build("forward-pass.html","The forward pass — weighted sums and bends, layer by layer",
      "Every number computed by hand on a 2-2-1 network: z = Wx + b, h = ReLU(z), ŷ = σ(u), L = −log ŷ.",svg,js,"0 0 860 400")
print("ok")
