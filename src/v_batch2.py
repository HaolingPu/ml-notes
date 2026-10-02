from shell import build
B_F,B_S="#E3EDF9","#A9C4E4"; G_F,G_S="#E2EFE3","#A8CBAC"
A_F,A_S="#FBEBD2","#E2BC85"; N_F,N_S="#F1F1F4","#D5D5DC"; R_F,R_S="#F7DADA","#DF9C9C"; P_F,P_S="#F7E4EC","#DFAFC3"

# ---------------- PAGED ATTENTION ----------------
CW,CH,GAP=46,26,6
svg=f'<text x="24" y="34" class="lbl-b">GPU memory for KV</text>\n'
for r in range(4):
    for c in range(12):
        x,y=24+c*(CW+GAP),46+r*(CH+GAP)
        svg+=f'<g id="m{r}_{c}" class="fd"><rect x="{x}" y="{y}" width="{CW}" height="{CH}" rx="4" fill="{N_F}" stroke="{N_S}" stroke-width="1"/></g>'
svg+=f'''<g id="legend" class="fd">
<rect x="678" y="46" width="14" height="14" rx="3" fill="{B_F}" stroke="{B_S}"/><text x="700" y="58" class="tiny">request A</text>
<rect x="678" y="70" width="14" height="14" rx="3" fill="{G_F}" stroke="{G_S}"/><text x="700" y="82" class="tiny">request B</text>
<rect x="678" y="94" width="14" height="14" rx="3" fill="{A_F}" stroke="{A_S}"/><text x="700" y="106" class="tiny">request C</text>
<rect x="678" y="118" width="14" height="14" rx="3" fill="{R_F}" stroke="{R_S}"/><text x="700" y="130" class="tiny">reserved, unused</text></g>
<text x="24" y="212" class="lbl-b">Memory actually put to work</text>
<rect x="24" y="224" width="500" height="18" rx="6" fill="#F1F1F4"/>
<g id="ub" transform="translate(24,224) scale(0,1)"><rect width="500" height="18" rx="6" fill="{G_S}"/></g>
<text x="536" y="238" class="tiny" id="ut"></text>
<g id="msg" class="fd"><text x="330" y="274" class="lbl-b" text-anchor="middle" id="mtxt"></text>
<text x="330" y="294" class="tiny" text-anchor="middle" id="mtxt2"></text></g>'''
js="""
var F={n:['#F1F1F4','#D5D5DC'],a:['#E3EDF9','#A9C4E4'],b:['#E2EFE3','#A8CBAC'],
       c:['#FBEBD2','#E2BC85'],r:['#F7DADA','#DF9C9C']};
function cell(r,c,k){var e=$('m'+r+'_'+c);if(!e)return;
  e.firstChild.setAttribute('fill',F[k][0]);e.firstChild.setAttribute('stroke',F[k][1])}
function row(r,spec){for(var c=0;c<12;c++)cell(r,c,spec[c]||'n')}
function fillu(s,t){$('ub').setAttribute('transform','translate(24,224) scale('+s+',1)');tx('ut',t)}
function base(){for(var r=0;r<4;r++)for(var c=0;c<12;c++)cell(r,c,'n');
  o('legend',0);o('msg',0);tx('mtxt','');tx('mtxt2','');fillu(0,'')}
var aa='a',bb='b',cc='c',rr='r',nn='n';
var S=[
{c:'Three requests arrive. Here is the problem in one sentence: <b>nobody knows how long any of them will be.</b> One might answer in ten tokens, another might write for four thousand.',
 a:function(){o('legend',1)}},
{c:'The old approach reserves a <b>contiguous worst-case block</b> for each request, because attention wants its keys and values laid out in one run of memory.',
 a:function(){o('legend',1);row(0,[aa,aa,aa,rr,rr,rr,rr,rr,rr,rr,rr,rr]);row(1,[bb,bb,rr,rr,rr,rr,rr,rr,rr,rr,rr,rr]);row(2,[cc,cc,cc,cc,cc,rr,rr,rr,rr,rr,rr,rr]);
   fillu(.28,'most of it reserved for nothing');o('msg',1);tx('mtxt','reserved for a worst case that rarely arrives');tx('mtxt2','the red space cannot be given to anyone else')}},
{c:'Worse, when a request finishes it leaves a <b>hole</b>. A new request needing a long run may not fit in any single gap, even though plenty of memory is free. This is classic <b>fragmentation</b>.',
 a:function(){o('legend',1);row(0,[aa,aa,aa,rr,rr,rr,rr,rr,rr,rr,rr,rr]);row(1,[nn,nn,nn,nn,nn,nn,nn,nn,nn,nn,nn,nn]);row(2,[cc,cc,cc,cc,cc,rr,rr,rr,rr,rr,rr,rr]);
   fillu(.22,'free, but unusable');o('msg',1);tx('mtxt','free memory that nothing can use');tx('mtxt2','the gap is the wrong shape')}},
{c:'<b>PagedAttention borrows the idea of virtual memory.</b> Chop KV storage into small fixed-size <b>blocks</b>, and give each request a block table that says where its blocks are. They no longer have to sit next to each other.',
 a:function(){o('legend',1);row(0,[aa,bb,cc,aa,bb,cc,aa,cc,nn,nn,nn,nn]);row(1,[cc,aa,bb,cc,nn,nn,nn,nn,nn,nn,nn,nn]);
   fillu(.52,'no reservation, no waste');o('msg',1);tx('mtxt','a request claims one more block only when it needs one');tx('mtxt2','scattered in memory, contiguous to the kernel')}},
{c:'Nothing is reserved in advance, so almost <b>all</b> of the memory does real work. In practice this is what lets a server hold far more conversations on the same card.',
 a:function(){o('legend',1);row(0,[aa,bb,cc,aa,bb,cc,aa,cc,bb,aa,cc,bb]);row(1,[cc,aa,bb,cc,aa,bb,cc,aa,bb,cc,nn,nn]);row(2,[aa,bb,cc,aa,nn,nn,nn,nn,nn,nn,nn,nn]);
   fillu(.88,'nearly all of it in use');o('msg',1);tx('mtxt','far more requests fit on the same GPU');tx('mtxt2','the win came from removing waste, not adding speed')}},
{c:'And there is a bonus that matters for agents. Two requests that begin with the <b>same prompt</b> can point their block tables at the <b>same blocks</b> instead of each keeping a copy — which is what makes prefix sharing cheap.',
 a:function(){o('legend',1);row(0,[aa,aa,aa,nn,nn,nn,nn,nn,nn,nn,nn,nn]);row(1,[aa,aa,aa,nn,nn,nn,nn,nn,nn,nn,nn,nn]);
   fillu(.5,'one copy, two readers');o('msg',1);tx('mtxt','shared blocks — both requests read the same memory');tx('mtxt2','this is the foundation prefix caching is built on')}},
{c:'<b>The line to say:</b> PagedAttention is about <i>where KV lives</i>, not how attention is computed. It costs an extra indirection and a custom kernel, and it buys back the memory that reservation and fragmentation were wasting.',
 a:function(){o('legend',1);row(0,[aa,bb,cc,aa,bb,cc,aa,cc,bb,aa,cc,bb]);row(1,[cc,aa,bb,cc,aa,bb,cc,aa,bb,cc,nn,nn]);
   fillu(.88,'');o('msg',1);tx('mtxt','capacity is the product, indirection is the price');tx('mtxt2','')}}
];
"""
build("paged-attention.html","PagedAttention — why KV memory is stored in blocks",
      "Reservation and fragmentation waste more memory than anything else in serving.",svg,js,"0 0 840 310")

# ---------------- CONTINUOUS BATCHING ----------------
SW,SH=88,26
svg=f'<text x="24" y="34" class="lbl-b" id="mode">Static batching</text>\n<text x="24" y="52" class="tiny" id="modesub">the batch runs until its slowest member finishes</text>\n'
for k in range(8):
    y=68+k*30
    svg+=f'<text x="24" y="{y+18}" class="tiny">slot {k+1}</text>'
    svg+=f'<rect x="72" y="{y}" width="520" height="{SH}" rx="5" fill="#FAFAFB" stroke="{N_S}" stroke-width="1" stroke-dasharray="3 3"/>'
    svg+=f'<g id="s{k}" class="mv fd"><rect width="{SW}" height="{SH}" rx="5" fill="{B_F}" stroke="{B_S}" stroke-width="1.2"/><text x="{SW/2}" y="17" class="tiny" text-anchor="middle" id="st{k}">req</text></g>'
svg+=f'''<g id="idle" class="fd"><text x="332" y="326" class="tiny" text-anchor="middle" fill="#B36A6A" id="itxt"></text></g>
<text x="628" y="86" class="lbl-b">GPU work being done</text>
<rect x="628" y="98" width="190" height="16" rx="8" fill="#F1F1F4"/>
<g id="gb" transform="translate(628,98) scale(0,1)"><rect width="190" height="16" rx="8" fill="{G_S}"/></g>
<text x="628" y="132" class="tiny" id="gt"></text>
<g id="q" class="fd"><text x="628" y="176" class="lbl-b">Waiting queue</text>'''
for k in range(4):
    svg+=f'<g id="qq{k}" class="fd"><rect x="628" y="{188+k*30}" width="80" height="24" rx="4" fill="{A_F}" stroke="{A_S}" stroke-width="1.2"/><text x="668" y="204" class="tiny" text-anchor="middle">queued</text></g>'
svg+='</g>'
js="""
var SW=88;
function put(k,x,w,f,s,lab){var g=$('s'+k);o('s'+k,1);mv('s'+k,72+x,68+k*30);
  g.firstChild.setAttribute('width',w);g.firstChild.setAttribute('fill',f);g.firstChild.setAttribute('stroke',s);
  var t=$('st'+k);t.setAttribute('x',w/2);t.textContent=lab||''}
function hide(k){o('s'+k,0)}
function gpu(s,t){$('gb').setAttribute('transform','translate(628,98) scale('+s+',1)');tx('gt',t)}
function queue(n){o('q',1);for(var k=0;k<4;k++)o('qq'+k,k<n?1:0)}
function base(){for(var k=0;k<8;k++)hide(k);o('idle',0);tx('itxt','');gpu(0,'');
  o('q',0);for(var k=0;k<4;k++)o('qq'+k,0);
  tx('mode','Static batching');tx('modesub','the batch runs until its slowest member finishes')}
var B_F='#E3EDF9',B_S='#A9C4E4',G_F='#E2EFE3',G_S='#A8CBAC',A_F='#FBEBD2',A_S='#E2BC85';
var S=[
{c:'Eight requests start together in one batch. They all look the same on arrival — <b>none of them knows how long its answer will be.</b>',
 a:function(){for(var k=0;k<8;k++)put(k,0,60,B_F,B_S,'req '+(k+1));gpu(1,'fully busy');queue(4)}},
{c:'They finish at wildly different times. Seven are short. One is writing a long document and keeps going.',
 a:function(){for(var k=0;k<7;k++)put(k,0,60+k*6,B_F,B_S,'req '+(k+1));put(7,0,420,B_F,B_S,'req 8 — long');gpu(1,'fully busy');queue(4)}},
{c:'With a <b>static</b> batch, a finished slot just goes empty. It cannot take new work until the whole batch is done, so seven eighths of the hardware sits idle waiting on one request.',
 a:function(){for(var k=0;k<7;k++)hide(k);put(7,0,420,B_F,B_S,'req 8 — still going');gpu(.14,'one request in flight');
   o('idle',1);tx('itxt','seven empty slots, and a queue that cannot move');queue(4)}},
{c:'Meanwhile requests are <b>queued and waiting</b>, right next to hardware that is doing nothing. This is the waste — not slow computation, just poor scheduling.',
 a:function(){put(7,0,420,B_F,B_S,'req 8');gpu(.14,'one request in flight');o('idle',1);
   tx('itxt','the queue is stuck behind the slowest member');queue(4)}},
{c:'<b>Continuous batching changes when the decision is made.</b> Instead of choosing the batch once, the scheduler reconsiders membership at <b>every decode step</b>.',
 a:function(){tx('mode','Continuous batching');tx('modesub','membership is reconsidered every decode step');
   for(var k=0;k<7;k++)put(k,0,60,G_F,G_S,'new');put(7,0,420,B_F,B_S,'req 8');gpu(1,'refilled immediately');queue(1)}},
{c:'So the moment a request finishes, its slot is handed to whoever is waiting. The long request keeps running in its own slot and <b>stops being everyone else\\'s problem</b>.',
 a:function(){tx('mode','Continuous batching');tx('modesub','membership is reconsidered every decode step');
   for(var k=0;k<7;k++)put(k,20+k*8,70,G_F,G_S,'new');put(7,0,420,B_F,B_S,'req 8');gpu(1,'stays busy');queue(0)}},
{c:'The GPU stays saturated across the whole run. Note what this did <b>not</b> change: no request got faster on its own. Throughput went up because the hardware stopped waiting.',
 a:function(){tx('mode','Continuous batching');tx('modesub','membership is reconsidered every decode step');
   for(var k=0;k<7;k++)put(k,40+k*14,70,G_F,G_S,'');put(7,0,420,B_F,B_S,'req 8');gpu(1,'saturated');queue(0)}},
{c:'<b>The line to say:</b> it is <i>iteration-level</i> scheduling rather than request-level. Contrast with dynamic batching, which only picks the moment to launch and then lets the batch run to completion. The cost is a more complex scheduler — and a request\\'s latency now depends on what else is running.',
 a:function(){tx('mode','Continuous batching');tx('modesub','iteration-level scheduling');
   for(var k=0;k<8;k++)put(k,10+k*16,80,G_F,G_S,'');gpu(1,'saturated');queue(0)}}
];
"""
build("continuous-batching.html","Continuous batching — why one long request used to stall seven short ones",
      "The same hardware, rescheduled every decode step.",svg,js,"0 0 840 340")
print("ok")
