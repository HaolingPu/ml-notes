from shell import build
B_F,B_S="#E3EDF9","#A9C4E4"; G_F,G_S="#E2EFE3","#A8CBAC"
A_F,A_S="#FBEBD2","#E2BC85"; N_F,N_S="#F1F1F4","#D5D5DC"; P_F,P_S="#F7E4EC","#DFAFC3"
TOK=["The","cat","that","chased","the","mouse","was","hungry"]
W,GP,X0=88,8,26
X=[X0+i*(W+GP) for i in range(8)]
# weights after softmax (illustrative, not numbers to memorise)
WT=[.04,.55,.03,.11,.02,.13,.04,.08]
svg=''
for i,t in enumerate(TOK):
    hot = (i==7)
    svg+=f'''<g id="tk{i}" class="fd"><rect x="{X[i]}" y="44" width="{W}" height="30" rx="5" fill="{N_F}" stroke="{N_S}" stroke-width="1.2"/>
<text x="{X[i]+W/2}" y="64" class="tiny" text-anchor="middle" font-weight="600">{t}</text></g>'''
svg+=f'<g id="focus" class="fd"><rect x="{X[7]-2}" y="42" width="{W+4}" height="34" rx="6" fill="none" stroke="#8A6D3B" stroke-width="2"/></g>'
svg+=f'''<g id="qbox" class="fd"><rect x="{X[7]}" y="98" width="{W}" height="26" rx="5" fill="{B_F}" stroke="{B_S}" stroke-width="1.3"/>
<text x="{X[7]+W/2}" y="115" class="tiny" text-anchor="middle" font-weight="650">Query</text></g>
<g id="qlab" class="fd"><text x="{X[7]+W/2}" y="140" class="tiny" text-anchor="middle" fill="#8A6D3B">"who is this about?"</text></g>'''
for i in range(8):
    svg+=f'''<g id="k{i}" class="fd"><rect x="{X[i]}" y="98" width="{W}" height="26" rx="5" fill="{P_F}" stroke="{P_S}" stroke-width="1.2"/>
<text x="{X[i]+W/2}" y="115" class="tiny" text-anchor="middle">Key</text></g>'''
    svg+=f'''<g id="v{i}" class="fd"><rect x="{X[i]}" y="292" width="{W}" height="26" rx="5" fill="{G_F}" stroke="{G_S}" stroke-width="1.2"/>
<text x="{X[i]+W/2}" y="309" class="tiny" text-anchor="middle">Value</text></g>'''
    svg+=f'''<g id="ln{i}" class="fd"><path d="M{X[7]+W/2},124 C{X[7]+W/2},160 {X[i]+W/2},150 {X[i]+W/2},170" stroke="{A_S}" stroke-width="1.2" fill="none"/></g>'''
    h=int(72*WT[i]/max(WT))
    svg+=f'''<g id="bw{i}" class="mv fd" transform="translate({X[i]+W/2-16},246) scale(1,0)"><rect x="0" y="-72" width="32" height="72" rx="3" fill="{A_F}" stroke="{A_S}" stroke-width="1.2"/></g>
<g id="pc{i}" class="fd"><text x="{X[i]+W/2}" y="268" class="tiny" text-anchor="middle">{int(round(WT[i]*100))}%</text></g>'''
    svg+=f'''<g id="fl{i}" class="fd"><path d="M{X[i]+W/2},292 C{X[i]+W/2},350 {X[7]+W/2},346 {X[7]+W/2},356" stroke="{G_S}" stroke-width="{max(1,round(WT[i]*14,1))}" fill="none" opacity=".85"/></g>'''
svg+=f'''<g id="out" class="fd"><rect x="{X[7]-14}" y="356" width="{W+28}" height="30" rx="6" fill="{B_F}" stroke="{B_S}" stroke-width="1.6"/>
<text x="{X[7]+W/2}" y="376" class="tiny" text-anchor="middle" font-weight="650">new "hungry"</text></g>
<g id="axl" class="fd"><text x="18" y="250" class="tiny">attention</text><text x="18" y="262" class="tiny">weight</text></g>
<g id="note" class="fd"><text x="415" y="206" class="lbl-b" text-anchor="middle" id="ntxt"></text></g>'''
sc=[]
for i in range(8): sc.append(round(WT[i]/max(WT),3))
js="""
var SC=%s;
function bars(on,scaled){for(var k=0;k<8;k++){
  var s=on?(scaled?SC[k]:SC[k]):0;
  $('bw'+k).setAttribute('transform','translate('+(%s[k]+44-16)+',246) scale(1,'+s+')');
  o('pc'+k, on&&scaled?1:0)}}
function keys(on){for(var k=0;k<8;k++)o('k'+k,on)}
function vals(on){for(var k=0;k<8;k++)o('v'+k,on)}
function lines(on){for(var k=0;k<8;k++)o('ln'+k,on)}
function flows(on){for(var k=0;k<8;k++)o('fl'+k,on)}
function base(){o('focus',0);o('qbox',0);o('qlab',0);keys(0);vals(0);lines(0);flows(0);
  bars(0,0);o('out',0);o('axl',0);o('note',0);tx('ntxt','');
  for(var k=0;k<8;k++){$('tk'+k).firstChild.setAttribute('fill','#F1F1F4')}}
function hot(k,c){$('tk'+k).firstChild.setAttribute('fill',c)}

var S=[
{c:'A sentence the model is reading. To represent the last word <b>hungry</b> properly it has to work out <i>who</i> is hungry — and nothing in that word alone says.',
 a:function(){o('focus',1);hot(7,'#FBEBD2')}},
{c:'So <b>hungry</b> emits a <b>Query</b>: a vector that stands for the question it needs answered. Nobody programmed the question — the model learned what to ask for.',
 a:function(){o('focus',1);hot(7,'#FBEBD2');o('qbox',1);o('qlab',1)}},
{c:'Every token in the sentence also exposes a <b>Key</b> — an advertisement of what it can answer. Query and Key live in the same learned space so they can be compared.',
 a:function(){o('focus',1);hot(7,'#FBEBD2');o('qbox',1);keys(1)}},
{c:'Now compare the query against <b>every key at once</b>. Each comparison is a dot product, and the whole set is one matrix multiply — that is the quadratic part.',
 a:function(){o('focus',1);hot(7,'#FBEBD2');o('qbox',1);keys(1);lines(1);o('axl',1)}},
{c:'The scores come out uneven. <b>cat</b> matches strongly, <b>mouse</b> and <b>chased</b> much less, the rest barely at all. This is the model deciding what is relevant.',
 a:function(){o('focus',1);hot(7,'#FBEBD2');o('qbox',1);keys(1);lines(1);o('axl',1);bars(1,0);hot(1,'#E3EDF9')}},
{c:'<b>Softmax</b> turns those raw scores into weights that sum to one. Now they are a genuine distribution — how much of each token to take.',
 a:function(){o('focus',1);hot(7,'#FBEBD2');hot(1,'#E3EDF9');keys(1);bars(1,1);o('axl',1)}},
{c:'Separately, every token carries a <b>Value</b> — the content it hands over if it gets attended to. Q and K did the <i>deciding</i>; V is the <i>payload</i>.',
 a:function(){o('focus',1);hot(7,'#FBEBD2');hot(1,'#E3EDF9');bars(1,1);vals(1);o('axl',1)}},
{c:'Mix the values in proportion to the weights. Watch the thickness of each stream — <b>cat</b> dominates, so most of what flows into the new representation is cat.',
 a:function(){o('focus',1);hot(7,'#FBEBD2');hot(1,'#E3EDF9');bars(1,1);vals(1);flows(1);o('out',1)}},
{c:'The representation of <b>hungry</b> now carries "the cat" inside it. That is the whole mechanism — no grammar rules, just learned queries meeting learned keys.',
 a:function(){o('focus',1);hot(7,'#FBEBD2');hot(1,'#E3EDF9');vals(1);flows(1);o('out',1);o('note',1);tx('ntxt','attention resolved the reference')}},
{c:'Two consequences worth carrying into an interview. Because Q and K only decide <i>routing</i>, you can cache K and V and reuse them — and RoPE only has to touch Q and K. And because every query meets every key, cost grows with the <b>square</b> of the sequence.',
 a:function(){o('out',1);keys(1);vals(1);o('qbox',1);o('note',1);tx('ntxt','Q,K decide routing · V carries content')}}
];
"""%(sc,[x for x in X])
build("self-attention.html","Self-attention — watching a word find what it refers to",
      "Q and K decide who attends to whom; V is what actually gets carried.",svg,js,"0 0 830 400")
print("ok")
