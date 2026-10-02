from shell import build
B_F,B_S="#E3EDF9","#A9C4E4"; G_F,G_S="#E2EFE3","#A8CBAC"
A_F,A_S="#FBEBD2","#E2BC85"; N_F,N_S="#F1F1F4","#D5D5DC"; R_F,R_S="#F7DADA","#DF9C9C"; P_F,P_S="#F7E4EC","#DFAFC3"

# ---------------- PREFILL vs DECODE ----------------
svg=f'''<text x="24" y="34" class="lbl-b">Prefill — the whole prompt at once</text>
<g id="pf" class="fd">'''
for k in range(10):
    svg+=f'<rect x="{24+k*40}" y="46" width="34" height="26" rx="4" fill="{B_F}" stroke="{B_S}" stroke-width="1.2"/>'
svg+=f'''</g>
<g id="pfsweep" class="mv fd"><rect x="0" y="42" width="8" height="34" rx="4" fill="{A_S}" opacity=".55"/></g>
<g id="pfarrow" class="fd"><path d="M276,80 L276,104" stroke="{N_S}" stroke-width="1.4" marker-end="url(#a2)"/></g>
<g id="kvb" class="fd"><rect x="152" y="106" width="250" height="28" rx="6" fill="{G_F}" stroke="{G_S}" stroke-width="1.4"/>
<text x="277" y="124" class="tiny" text-anchor="middle" font-weight="650">KV cache built</text></g>
<text x="24" y="176" class="lbl-b">Decode — one token at a time</text>
<g id="dc" class="fd">'''
for k in range(8):
    svg+=f'<g id="d{k}" class="fd"><rect x="{24+k*58}" y="188" width="46" height="26" rx="4" fill="{A_F}" stroke="{A_S}" stroke-width="1.2"/><text x="{47+k*58}" y="205" class="tiny" text-anchor="middle">t{k+1}</text></g>'
svg+=f'''</g>
<g id="dread" class="fd"><path d="M380,134 L380,184" stroke="{G_S}" stroke-width="1.2" fill="none" stroke-dasharray="3 3" marker-end="url(#a3)"/>
<text x="396" y="164" class="tiny" fill="#5F7F63">every step re-reads the cache</text></g>
<g id="util" class="fd"><text x="520" y="34" class="lbl-b">GPU doing useful work</text>
<text x="520" y="60" class="tiny">prefill</text><rect x="580" y="48" width="230" height="14" rx="7" fill="#F1F1F4"/>
<g id="ub1" transform="translate(580,48) scale(0,1)"><rect width="230" height="14" rx="7" fill="{B_S}"/></g>
<text x="520" y="88" class="tiny">decode</text><rect x="580" y="76" width="230" height="14" rx="7" fill="#F1F1F4"/>
<g id="ub2" transform="translate(580,76) scale(0,1)"><rect width="230" height="14" rx="7" fill="{A_S}"/></g></g>
<g id="bound" class="fd"><text x="666" y="192" class="lbl-b" text-anchor="middle" id="btxt"></text>
<text x="666" y="212" class="tiny" text-anchor="middle" id="btxt2"></text></g>
<g id="clk" class="fd"><text x="24" y="258" class="lbl-b">What the user feels</text>
<rect x="24" y="270" width="380" height="26" rx="6" fill="#FAFAFB" stroke="{N_S}"/>
<text x="36" y="287" class="tiny" id="c1">—</text>
<rect x="420" y="270" width="390" height="26" rx="6" fill="#FAFAFB" stroke="{N_S}"/>
<text x="432" y="287" class="tiny" id="c2">—</text></g>
<defs><marker id="a2" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0,1 L9,5 L0,9 z" fill="{N_S}"/></marker>
<marker id="a3" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0,1 L9,5 L0,9 z" fill="{G_S}"/></marker></defs>'''
js="""
function sc(id,x,y,s){$(id).setAttribute('transform','translate('+x+','+y+') scale('+s+',1)')}
function dsteps(n){for(var k=0;k<8;k++)o('d'+k,k<n?1:0)}
function base(){o('pf',0);o('pfsweep',0);o('pfarrow',0);o('kvb',0);dsteps(0);o('dread',0);
  o('util',0);o('bound',0);o('clk',0);tx('btxt','');tx('btxt2','');tx('c1','—');tx('c2','—');
  sc('ub1',580,48,0);sc('ub2',580,76,0);mv('pfsweep',16,0)}
var S=[
{c:'A prompt arrives. Every token of it is available <b>right now</b> — nothing has to be generated yet, so nothing has to wait.',
 a:function(){o('pf',1)}},
{c:'So prefill reads all of it in <b>one pass</b>. Watch the sweep: this is a single large matrix multiply, the shape of work a GPU is built for.',
 a:function(){o('pf',1);o('pfsweep',1);mv('pfsweep',400,0);o('util',1);sc('ub1',580,48,.94)}},
{c:'The output of that pass is the <b>KV cache</b> for the whole prompt — the model\\'s notes on everything it has read.',
 a:function(){o('pf',1);o('pfarrow',1);o('kvb',1);o('util',1);sc('ub1',580,48,.94)}},
{c:'Now generation begins, and the shape of the work flips completely. One token comes out per step, and each step depends on the one before it. <b>Nothing can be parallelised away.</b>',
 a:function(){o('kvb',1);dsteps(3);o('dread',1);o('util',1);sc('ub1',580,48,.94);sc('ub2',580,76,.12)}},
{c:'Each step does <b>almost no arithmetic</b> — but it must re-read the model weights and the whole KV cache to produce a single token. The hardware sits mostly idle waiting on memory.',
 a:function(){o('kvb',1);dsteps(6);o('dread',1);o('util',1);sc('ub1',580,48,.94);sc('ub2',580,76,.12);
   o('bound',1);tx('btxt','compute-bound vs bandwidth-bound');tx('btxt2','same request, two different machines')}},
{c:'That is why the two phases feel different. Prefill sets the <b>wait before the first word</b>; decode sets the <b>speed the words appear</b>.',
 a:function(){o('kvb',1);dsteps(8);o('util',1);sc('ub1',580,48,.94);sc('ub2',580,76,.12);o('clk',1);
   tx('c1','prefill → time to first token');tx('c2','decode → time per output token')}},
{c:'And the balance moves with the workload. Summarising a long report is <b>nearly all prefill</b>; answering a one-line question with a long essay is <b>nearly all decode</b>. One server tuning can be fast for one and slow for the other.',
 a:function(){o('pf',1);o('kvb',1);dsteps(8);o('clk',1);tx('c1','long prompt, short answer → prefill dominates');tx('c2','short prompt, long answer → decode dominates')}},
{c:'<b>The line to say:</b> name the phase before naming the fix. Prefix caching and chunked prefill attack prefill; GQA, KV quantisation and bigger batches attack decode.',
 a:function(){o('kvb',1);dsteps(8);o('bound',1);tx('btxt','name the phase, then the fix');tx('btxt2','it is the cleanest way to structure the answer')}}
];
"""
build("prefill-vs-decode.html","Prefill vs decode — one request, two different machines",
      "Why the first word is slow for a different reason than the rest.",svg,js,"0 0 840 316")

# ---------------- GQA ----------------
svg=f'''<text x="24" y="34" class="lbl-b" id="ttl">Multi-Head Attention</text>
<text x="24" y="52" class="tiny" id="sub2">every query head keeps its own keys and values</text>'''
for k in range(8):
    svg+=f'<g id="q{k}" class="fd"><rect x="{24+k*72}" y="70" width="60" height="28" rx="5" fill="{B_F}" stroke="{B_S}" stroke-width="1.2"/><text x="{54+k*72}" y="88" class="tiny" text-anchor="middle">Q{k+1}</text></g>'
for k in range(8):
    svg+=f'<g id="kv{k}" class="mv fd"><rect width="60" height="28" rx="5" fill="{G_F}" stroke="{G_S}" stroke-width="1.2"/><text x="30" y="18" class="tiny" text-anchor="middle">KV</text></g>'
for k in range(8):
    svg+=f'<g id="w{k}" class="fd"><path id="wp{k}" d="" stroke="#C2C2CB" stroke-width="1.2" fill="none"/></g>'
svg+=f'''<text x="24" y="230" class="lbl-b">KV cache size</text>
<rect x="24" y="242" width="480" height="20" rx="6" fill="#F1F1F4"/>
<g id="mb" transform="translate(24,242) scale(1,1)"><rect width="480" height="20" rx="6" fill="{B_S}"/></g>
<text x="516" y="257" class="tiny" id="mt">8 KV heads</text>
<text x="24" y="292" class="lbl-b">Concurrent users on the same GPU</text>
<rect x="24" y="304" width="480" height="20" rx="6" fill="#F1F1F4"/>
<g id="ub" transform="translate(24,304) scale(.25,1)"><rect width="480" height="20" rx="6" fill="{G_S}"/></g>
<text x="516" y="319" class="tiny" id="ut">baseline</text>
<g id="warn" class="fd"><text x="620" y="120" class="lbl-b" text-anchor="middle" fill="#B36A6A" id="wtxt"></text>
<text x="620" y="140" class="tiny" text-anchor="middle" id="wtxt2"></text></g>'''
js="""
var QX=[];for(var k=0;k<8;k++)QX.push(24+k*72+30);
function conf(nkv,label,t,st){
  if(t)tx('ttl',t); if(st)tx('sub2',st);
  var slotW=480/nkv;
  for(var k=0;k<8;k++){
    var grp=Math.floor(k/(8/nkv));
    var cx=24+grp*slotW+slotW/2;
    if(k<nkv){o('kv'+k,1);mv('kv'+k,24+k*slotW+slotW/2-30,166)}else{o('kv'+k,0)}
    o('w'+k,1);
    $('wp'+k).setAttribute('d','M'+QX[k]+',98 L'+cx+',166');
  }
  $('mb').setAttribute('transform','translate(24,242) scale('+(nkv/8)+',1)');
  tx('mt',label);
}
function base(){for(var k=0;k<8;k++){o('kv'+k,0);o('w'+k,0)}o('warn',0);tx('wtxt','');tx('wtxt2','');
  $('ub').setAttribute('transform','translate(24,304) scale(.25,1)');tx('ut','baseline');
  tx('ttl','Multi-Head Attention');tx('sub2','every query head keeps its own keys and values')}
var S=[
{c:'Start with <b>multi-head attention</b>. Eight query heads, and each one carries its own set of keys and values. Maximum freedom — every head can attend completely independently.',
 a:function(){conf(8,'8 KV heads — largest cache','Multi-Head Attention','every query head keeps its own keys and values')}},
{c:'The trouble is what that costs at decode time. Every one of those KV heads has to be <b>read from memory for every token generated</b>, and decode is already limited by memory speed, not arithmetic.',
 a:function(){conf(8,'8 KV heads — largest cache','Multi-Head Attention','every query head keeps its own keys and values');o('warn',1);tx('wtxt','the cache is read every single step');tx('wtxt2','so its size sets the pace of generation')}},
{c:'<b>MQA takes the extreme option:</b> throw away all but one KV head and let all eight queries share it. Watch the cache collapse.',
 a:function(){conf(1,'1 KV head — smallest cache','Multi-Query Attention','all eight query heads share one set of keys and values');
   $('ub').setAttribute('transform','translate(24,304) scale(1,1)');tx('ut','many more users');
   o('warn',1);tx('wtxt','but all eight heads now agree on what to look at');tx('wtxt2','expressiveness is genuinely lost')}},
{c:'<b>GQA is the compromise.</b> Group the query heads and give each group its own keys and values — here two groups. Heads inside a group share; heads across groups stay independent.',
 a:function(){conf(2,'2 KV heads','Grouped-Query Attention','heads share inside a group, stay independent across groups');$('ub').setAttribute('transform','translate(24,304) scale(.85,1)');tx('ut','most of the MQA win')}},
{c:'In a real model the numbers are bigger but the shape is the same: 32 query heads with <b>8</b> KV groups. A quarter of MHA\\'s cache — which is roughly four times the users, or four times the context, on the same GPU.',
 a:function(){conf(4,'8 of 32 KV heads — a quarter of MHA','Grouped-Query Attention','the arrangement real models actually ship');$('ub').setAttribute('transform','translate(24,304) scale(.9,1)');tx('ut','≈4× the concurrency')}},
{c:'<b>The line to say:</b> GQA sits at the knee of the curve — nearly MHA\\'s quality at nearly MQA\\'s memory. It is a <i>serving</i> decision that got made inside the architecture, which is why every recent open model ships with it.',
 a:function(){conf(4,'the modern default','Grouped-Query Attention','the modern default');$('ub').setAttribute('transform','translate(24,304) scale(.9,1)');tx('ut','≈4× the concurrency');
   o('warn',1);tx('wtxt','fewer KV heads → smaller cache → faster decode');tx('wtxt2','the tradeoff is expressiveness')}}
];
"""
build("mha-gqa-mqa.html","MHA → GQA → MQA — shrinking what decode has to read",
      "The only thing that changes is how many query heads share a set of keys and values.",svg,js,"0 0 840 340")
print("ok")
