from shell import build
B_F,B_S="#E3EDF9","#A9C4E4"; G_F,G_S="#E2EFE3","#A8CBAC"
A_F,A_S="#FBEBD2","#E2BC85"; N_F,N_S="#F1F1F4","#D5D5DC"; R_F,R_S="#F7DADA","#DF9C9C"
CW,CG,CX,CY=52,6,40,96
svg=f'''<text x="24" y="36" class="lbl-b">KV cache — keys and values already computed</text>
<rect x="24" y="52" width="640" height="76" rx="9" fill="#FAFAFB" stroke="#DCDCE2"/>'''
for k in range(10):
    x=CX+k*(CW+CG)
    svg+=f'''<g id="c{k}" class="fd"><rect x="{x}" y="{CY-30}" width="{CW}" height="26" rx="4" fill="{G_F}" stroke="{G_S}" stroke-width="1.2"/>
<text x="{x+CW/2}" y="{CY-13}" class="tiny" text-anchor="middle">K,V</text></g>'''
svg+=f'''<g id="promptlab" class="fd"><text x="{CX+2*(CW+CG)}" y="148" class="tiny" text-anchor="middle">prompt tokens</text></g>
<g id="genlab" class="fd"><text x="{CX+7*(CW+CG)}" y="148" class="tiny" text-anchor="middle">generated so far</text></g>
<g id="newtok" class="mv fd"><rect width="{CW}" height="26" rx="4" fill="{A_F}" stroke="{A_S}" stroke-width="1.4"/>
<text x="{CW/2}" y="17" class="tiny" text-anchor="middle" font-weight="650">new</text></g>
<text x="24" y="192" class="lbl-b">Work per decode step</text>
<g id="wo" class="fd"><text x="24" y="222" class="tiny">without cache</text>
<rect x="140" y="210" width="300" height="14" rx="7" fill="#F1F1F4"/>
<g id="wob" transform="translate(140,210) scale(0,1)"><rect width="300" height="14" rx="7" fill="{R_S}"/></g>
<text x="452" y="222" class="tiny" id="wot"></text></g>
<g id="wi" class="fd"><text x="24" y="250" class="tiny">with cache</text>
<rect x="140" y="238" width="300" height="14" rx="7" fill="#F1F1F4"/>
<g id="wib" transform="translate(140,238) scale(0,1)"><rect width="300" height="14" rx="7" fill="{G_S}"/></g>
<text x="452" y="250" class="tiny" id="wit"></text></g>
<g id="mem" class="fd"><text x="24" y="300" class="lbl-b">GPU memory held by the cache</text>
<rect x="24" y="312" width="520" height="20" rx="6" fill="#F1F1F4"/>
<g id="memb" transform="translate(24,312) scale(0,1)"><rect width="520" height="20" rx="6" fill="{B_S}"/></g>
<text x="556" y="327" class="tiny" id="memt" ></text>
<g id="gcap" class="fd"><path d="M544,306 L544,338" stroke="{R_S}" stroke-width="2"/><text x="552" y="348" class="tiny" fill="#B36A6A">GPU limit</text></g></g>
<g id="qnote" class="fd"><rect x="676" y="52" width="150" height="76" rx="8" fill="#fff" stroke="{N_S}" stroke-dasharray="3 3"/>
<text x="751" y="76" class="tiny" text-anchor="middle" font-weight="650">old queries</text>
<text x="751" y="94" class="tiny" text-anchor="middle">never reused</text>
<text x="751" y="112" class="tiny" text-anchor="middle" fill="#B36A6A">so Q is not cached</text></g>
<g id="msg" class="fd"><text x="415" y="374" class="lbl-b" text-anchor="middle" id="mtxt"></text></g>'''
js="""
var CX=%d,CW=%d,CG=%d;
function cells(n){for(var k=0;k<10;k++)o('c'+k,k<n?1:0)}
function bar(id,s,t,lab){$(id).setAttribute('transform','translate('+(id==='wob'?140:(id==='wib'?140:24))+','+(id==='wob'?210:(id==='wib'?238:312))+') scale('+s+',1)');if(lab)tx(t,lab)}
function base(){cells(0);o('newtok',0);o('wo',0);o('wi',0);o('mem',0);o('gcap',0);o('qnote',0);o('msg',0);
  o('promptlab',0);o('genlab',0);tx('mtxt','');tx('wot','');tx('wit','');tx('memt','');
  bar('wob',0,'wot','');bar('wib',0,'wit','');bar('memb',0,'memt','');
  mv('newtok',CX+5*(CW+CG),66)}
var S=[
{c:'The prompt has been read and its <b>keys and values</b> are sitting in memory. Generation is about to begin.',
 a:function(){cells(5);o('promptlab',1)}},
{c:'A new token is produced. To attend, it needs the keys and values of everything before it — and those have <b>not changed</b> since last step. Recomputing them would be pure waste.',
 a:function(){cells(5);o('promptlab',1);o('newtok',1)}},
{c:'So the model computes <b>only the new token\\'s</b> Q, K and V, appends its K,V to the cache, and attends across everything stored. One token of work instead of the whole prefix.',
 a:function(){cells(6);o('promptlab',1);o('newtok',1);mv('newtok',CX+6*(CW+CG),66)}},
{c:'Step after step, the cache grows by exactly one entry. Watch the two work bars: <b>without</b> a cache the cost per step climbs with the length of the text; <b>with</b> one it stays flat.',
 a:function(){cells(8);o('promptlab',1);o('genlab',1);o('wo',1);o('wi',1);bar('wob',.55,'wot','grows every step');bar('wib',.1,'wit','flat')}},
{c:'By the five-hundredth token the gap is enormous. Without the cache you would push 499 tokens through every layer again just to rebuild values identical to last time.',
 a:function(){cells(10);o('genlab',1);o('wo',1);o('wi',1);bar('wob',1,'wot','enormous');bar('wib',.1,'wit','still flat')}},
{c:'<b>Why not cache Q as well?</b> Because a query is used once, by the token that issued it, and never again. Keys and values are read by <i>every</i> future token. That asymmetry is the whole reason it is a K,V cache.',
 a:function(){cells(10);o('genlab',1);o('qnote',1)}},
{c:'But the cache is not free — it is <b>GPU memory</b>, and it grows with the length of the conversation.',
 a:function(){cells(10);o('genlab',1);o('mem',1);bar('memb',.3,'memt','one long conversation')}},
{c:'Now serve many users at once. The cache scales with <b>length × concurrency</b>, and it can end up larger than the model weights themselves.',
 a:function(){cells(10);o('mem',1);o('gcap',1);bar('memb',.8,'memt','many conversations')}},
{c:'When it fills, the server cannot simply slow down — it has to <b>queue or evict</b>. So the symptom users actually see is not sluggishness, it is <b>rejected requests</b>. This is why serving is a memory problem.',
 a:function(){cells(10);o('mem',1);o('gcap',1);bar('memb',1,'memt','at the limit');o('msg',1);tx('mtxt','capacity, not compute, is what runs out')}},
{c:'Everything downstream follows from this one bar: <b>GQA and MQA</b> shrink it by sharing KV heads, <b>quantisation</b> stores it in fewer bits, <b>PagedAttention</b> stops it fragmenting, and <b>compaction</b> shortens what has to be kept at all.',
 a:function(){cells(10);o('mem',1);o('gcap',1);bar('memb',.45,'memt','after GQA + quantisation');o('msg',1);tx('mtxt','every KV technique is aimed at this bar')}}
];
"""%(CX,CW,CG)
build("kv-cache.html","The KV cache — what it saves, and what it costs",
      "Why decoding reuses keys and values, and why memory is the thing that runs out.",svg,js,"0 0 840 390")
print("ok")
