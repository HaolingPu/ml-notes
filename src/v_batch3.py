from shell import build
B_F,B_S="#E3EDF9","#A9C4E4"; G_F,G_S="#E2EFE3","#A8CBAC"
A_F,A_S="#FBEBD2","#E2BC85"; N_F,N_S="#F1F1F4","#D5D5DC"; R_F,R_S="#F7DADA","#DF9C9C"

# ---------------- PREFIX CACHING ----------------
svg=f'''<text x="24" y="34" class="lbl-b">The prompt an agent sends on every single step</text>
<g id="p0" class="fd"><rect x="24" y="48" width="180" height="30" rx="5" fill="{G_F}" stroke="{G_S}" stroke-width="1.2"/><text x="114" y="68" class="tiny" text-anchor="middle">system prompt</text></g>
<g id="p1" class="fd"><rect x="208" y="48" width="160" height="30" rx="5" fill="{G_F}" stroke="{G_S}" stroke-width="1.2"/><text x="288" y="68" class="tiny" text-anchor="middle">tool definitions</text></g>
<g id="p2" class="fd"><rect x="372" y="48" width="180" height="30" rx="5" fill="{G_F}" stroke="{G_S}" stroke-width="1.2"/><text x="462" y="68" class="tiny" text-anchor="middle">repository context</text></g>
<g id="p3" class="fd"><rect x="556" y="48" width="130" height="30" rx="5" fill="{A_F}" stroke="{A_S}" stroke-width="1.4"/><text x="621" y="68" class="tiny" text-anchor="middle" font-weight="650">step 20</text></g>
<g id="shared" class="fd"><path d="M24,86 L552,86" stroke="{G_S}" stroke-width="2"/><text x="288" y="104" class="tiny" text-anchor="middle" fill="#5F7F63">identical on every one of the 20 calls</text></g>
<g id="newp" class="fd"><path d="M556,86 L686,86" stroke="{A_S}" stroke-width="2"/><text x="621" y="104" class="tiny" text-anchor="middle" fill="#8A6D3B">the only new part</text></g>
<text x="24" y="146" class="lbl-b">Prefill work per step</text>
<g id="w1" class="fd"><text x="24" y="176" class="tiny">without caching</text>
<rect x="150" y="164" width="420" height="15" rx="7" fill="#F1F1F4"/>
<g id="wb1" transform="translate(150,164) scale(0,1)"><rect width="420" height="15" rx="7" fill="{R_S}"/></g>
<text x="584" y="176" class="tiny" id="wt1"></text></g>
<g id="w2" class="fd"><text x="24" y="204" class="tiny">with caching</text>
<rect x="150" y="192" width="420" height="15" rx="7" fill="#F1F1F4"/>
<g id="wb2" transform="translate(150,192) scale(0,1)"><rect width="420" height="15" rx="7" fill="{G_S}"/></g>
<text x="584" y="204" class="tiny" id="wt2"></text></g>
<g id="tree" class="fd"><text x="24" y="248" class="lbl-b">Cached prefixes, indexed as a tree</text>
<rect x="24" y="260" width="120" height="26" rx="5" fill="{G_F}" stroke="{G_S}" stroke-width="1.2"/><text x="84" y="277" class="tiny" text-anchor="middle">system</text>
<path d="M144,273 L176,273" stroke="{N_S}" stroke-width="1.2"/>
<rect x="176" y="260" width="120" height="26" rx="5" fill="{G_F}" stroke="{G_S}" stroke-width="1.2"/><text x="236" y="277" class="tiny" text-anchor="middle">+ tools</text>
<path d="M296,273 L328,273" stroke="{N_S}" stroke-width="1.2"/>
<rect x="328" y="260" width="120" height="26" rx="5" fill="{G_F}" stroke="{G_S}" stroke-width="1.2"/><text x="388" y="277" class="tiny" text-anchor="middle">+ repo</text>
<g id="match" class="fd"><rect x="20" y="256" width="432" height="34" rx="8" fill="none" stroke="{G_S}" stroke-width="2"/>
<text x="236" y="308" class="tiny" fill="#5F7F63">longest prefix already computed — reuse it as-is</text></g>
<g id="branch" class="fd"><path d="M448,273 L480,273" stroke="{A_S}" stroke-width="1.2"/>
<rect x="480" y="260" width="120" height="26" rx="5" fill="{A_F}" stroke="{A_S}" stroke-width="1.2"/><text x="540" y="277" class="tiny" text-anchor="middle">prefill this only</text></g></g>
<g id="brk" class="fd"><path d="M120,40 L120,96" stroke="{R_S}" stroke-width="2.5"/>
<text x="128" y="128" class="tiny" fill="#B36A6A" id="brkt"></text></g>
<g id="msg" class="fd"><text x="355" y="326" class="lbl-b" text-anchor="middle" id="mtxt"></text></g>'''
js="""
function bar(id,y,s,t,lab){$(id).setAttribute('transform','translate(150,'+y+') scale('+s+',1)');tx(t,lab)}
function base(){o('p0',1);o('p1',1);o('p2',1);o('p3',0);o('shared',0);o('newp',0);
  o('w1',0);o('w2',0);o('tree',0);o('match',0);o('branch',0);o('brk',0);o('msg',0);
  tx('mtxt','');tx('brkt','');bar('wb1',164,0,'wt1','');bar('wb2',192,0,'wt2','')}
var S=[
{c:'Look at what an agent actually sends. A long, <b>identical</b> preamble — system prompt, tool definitions, repository context — followed by a short new bit.',
 a:function(){o('p3',1)}},
{c:'And it sends that same preamble <b>every single step</b>. By step 20 the model has read it twenty times. Only the highlighted tail has ever changed.',
 a:function(){o('p3',1);o('shared',1);o('newp',1)}},
{c:'Without caching, all of it gets prefilled again on every call. That is the bill: almost all of the prefill work is <b>re-reading text the model has already read</b>.',
 a:function(){o('p3',1);o('shared',1);o('newp',1);o('w1',1);bar('wb1',164,1,'wt1','the whole prompt, every step')}},
{c:'The key fact that makes a fix possible: a token\\'s keys and values depend <b>only on the tokens before it</b>. So an identical prefix always produces identical KV — no matter which request it belongs to.',
 a:function(){o('p3',1);o('shared',1);o('w1',1);bar('wb1',164,1,'wt1','')}},
{c:'So cache it. Prefixes are stored in a <b>tree</b>, and a new request walks down it to find the <b>longest prefix already computed</b>.',
 a:function(){o('p3',1);o('tree',1);o('match',1)}},
{c:'That match is reused as-is, and only the unmatched tail gets prefilled. The work per step collapses to the size of what is genuinely new.',
 a:function(){o('p3',1);o('tree',1);o('match',1);o('branch',1);o('w1',1);o('w2',1);
   bar('wb1',164,1,'wt1','');bar('wb2',192,.08,'wt2','only the new tail')}},
{c:'<b>But it is brittle, and this is the practical part.</b> Put a timestamp at the top of the system prompt, or reorder the tool list, and the shared prefix ends right there — everything after it has to be prefilled again.',
 a:function(){o('p3',1);o('shared',1);o('brk',1);tx('brkt','one changed token here invalidates everything after it');
   o('w1',1);o('w2',1);bar('wb1',164,1,'wt1','');bar('wb2',192,.9,'wt2','almost no reuse left')}},
{c:'Which gives you a real engineering rule: keep the <b>volatile parts of a prompt at the end</b>. Stable instructions first, changing context last.',
 a:function(){o('p3',1);o('shared',1);o('newp',1);o('w2',1);bar('wb2',192,.08,'wt2','reuse restored');
   o('msg',1);tx('mtxt','stable content first, volatile content last')}},
{c:'<b>One distinction to keep straight:</b> the cached tokens are still <b>fully attended to</b>. Nothing is being ignored — only their <i>recomputation</i> is skipped. The win shows up as prefill cost and time to first token.',
 a:function(){o('p3',1);o('tree',1);o('match',1);o('branch',1);o('msg',1);
   tx('mtxt','skipped recomputation — not skipped attention')}}
];
"""
build("prefix-caching.html","Prefix caching — why an agent stops re-reading its own preamble",
      "Reuse across requests, and the one-character change that destroys it.",svg,js,"0 0 740 344")

# ---------------- FULL vs LINEAR ATTENTION ----------------
svg=f'''<text x="24" y="34" class="lbl-b">Full attention</text>
<text x="24" y="52" class="tiny">keeps every past key and value</text>
<g id="fullset" class="fd">'''
for k in range(10):
    svg+=f'<g id="f{k}" class="fd"><rect x="{24+k*52}" y="66" width="44" height="26" rx="4" fill="{G_F}" stroke="{G_S}" stroke-width="1.2"/></g>'
svg+=f'''</g>
<g id="fq" class="fd"><rect x="230" y="150" width="90" height="28" rx="5" fill="{B_F}" stroke="{B_S}" stroke-width="1.3"/><text x="275" y="169" class="tiny" text-anchor="middle">query</text></g>
<g id="flines" class="fd">'''
for k in range(10):
    svg+=f'<path id="fp{k}" d="M{46+k*52},92 L275,148" stroke="#CFCFD8" stroke-width="1"/>'
svg+=f'''</g>
<g id="fmem" class="fd"><text x="24" y="208" class="tiny">memory</text>
<rect x="90" y="196" width="440" height="14" rx="7" fill="#F1F1F4"/>
<g id="fb" transform="translate(90,196) scale(0,1)"><rect width="440" height="14" rx="7" fill="{B_S}"/></g>
<text x="542" y="208" class="tiny" id="ft"></text></g>
<line x1="24" y1="240" x2="816" y2="240" stroke="#E6E6EB" stroke-dasharray="4 4"/>
<text x="24" y="272" class="lbl-b">Linear attention</text>
<text x="24" y="290" class="tiny">folds the past into one fixed-size state</text>
<g id="lstate" class="fd"><rect x="180" y="304" width="180" height="44" rx="7" fill="{A_F}" stroke="{A_S}" stroke-width="1.5"/>
<text x="270" y="323" class="tiny" text-anchor="middle" font-weight="650">recurrent state</text>
<text x="270" y="338" class="tiny" text-anchor="middle" id="lsz">size never changes</text></g>
<g id="lin" class="mv fd"><rect width="44" height="26" rx="4" fill="{G_F}" stroke="{G_S}" stroke-width="1.2"/><text x="22" y="17" class="tiny" text-anchor="middle">K,V</text></g>
<g id="lq" class="fd"><rect x="430" y="312" width="90" height="28" rx="5" fill="{B_F}" stroke="{B_S}" stroke-width="1.3"/><text x="475" y="331" class="tiny" text-anchor="middle">query</text>
<path d="M428,326 L366,326" stroke="#CFCFD8" stroke-width="1.4" marker-end="url(#a4)"/></g>
<g id="lmem" class="fd"><text x="560" y="290" class="tiny">memory</text>
<rect x="560" y="298" width="240" height="14" rx="7" fill="#F1F1F4"/>
<g id="lb" transform="translate(560,298) scale(.12,1)"><rect width="240" height="14" rx="7" fill="{A_S}"/></g>
<text x="560" y="332" class="tiny" id="lt"></text></g>
<g id="ask" class="fd"><rect x="560" y="60" width="256" height="60" rx="8" fill="#fff" stroke="{N_S}"/>
<text x="688" y="84" class="tiny" text-anchor="middle" id="q1"></text>
<text x="688" y="104" class="tiny" text-anchor="middle" id="q2"></text></g>
<defs><marker id="a4" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0,1 L9,5 L0,9 z" fill="#CFCFD8"/></marker></defs>'''
js="""
function fset(n){for(var k=0;k<10;k++)o('f'+k,k<n?1:0);for(var k=0;k<10;k++)o('fp'+k,0)}
function flines(n){for(var k=0;k<10;k++)o('fp'+k,k<n?1:0)}
function base(){fset(0);o('fq',0);o('fmem',0);o('lstate',0);o('lin',0);o('lq',0);o('lmem',0);o('ask',0);
  tx('ft','');tx('lt','');tx('q1','');tx('q2','');tx('lsz','size never changes');
  $('fb').setAttribute('transform','translate(90,196) scale(0,1)');
  $('lb').setAttribute('transform','translate(560,298) scale(.12,1)');
  mv('lin',24,312)}
var S=[
{c:'Both designs answer the same question — what should this token attend to? — but they <b>store the past completely differently</b>.',
 a:function(){fset(4);o('lstate',1)}},
{c:'<b>Full attention keeps everything.</b> Every past token leaves a key and a value behind, and they are all still there, individually, however far back they go.',
 a:function(){fset(10);o('fmem',1);$('fb').setAttribute('transform','translate(90,196) scale(.85,1)');tx('ft','grows with every token')}},
{c:'So a query can reach any one of them directly. It is a <b>lookup</b>: exact, addressable, and it costs a comparison against every stored key.',
 a:function(){fset(10);flines(10);o('fq',1);o('fmem',1);$('fb').setAttribute('transform','translate(90,196) scale(.85,1)');tx('ft','and every one gets compared')}},
{c:'<b>Linear attention refuses to keep them.</b> Each new key and value is <b>folded into a single fixed-size state</b> and then let go.',
 a:function(){o('lstate',1);o('lin',1);mv('lin',126,312);o('lmem',1);tx('lt','flat, no matter the length')}},
{c:'Token after token, the state absorbs each one and never grows. Memory is <b>flat</b> and the work per step is <b>constant</b> — the long-sequence problem simply stops existing.',
 a:function(){o('lstate',1);o('lin',0);mv('lin',250,314);o('lmem',1);tx('lt','constant');tx('lsz','one summary of everything seen')}},
{c:'A query then reads <b>from the state</b>, not from the tokens. There is nothing else left to read.',
 a:function(){o('lstate',1);o('lq',1);o('lmem',1);tx('lt','constant')}},
{c:'Which is exactly where the difference shows up. Ask something <b>specific</b> — and full attention has the token, while the state has only a blend that the name was mixed into.',
 a:function(){fset(10);flines(10);o('fq',1);o('lstate',1);o('lq',1);o('ask',1);
   tx('q1','"what was the variable on line 200?"');tx('q2','exact lookup  vs  plausible guess')}},
{c:'Ask something <b>broad</b> and the picture flips — a compressed summary answers that perfectly well, at constant cost, however long the document is.',
 a:function(){o('lstate',1);o('lq',1);o('ask',1);o('lmem',1);tx('lt','constant');
   tx('q1','"what is this document about?"');tx('q2','a summary is all you needed')}},
{c:'<b>The line to say:</b> it is a compression-versus-recall trade. Full attention is lossless lookup at quadratic cost; linear attention is lossy lookup at constant cost. That is also why hybrids exist — mostly linear layers, with a few full-attention layers kept for exact recall.',
 a:function(){fset(10);o('lstate',1);o('ask',1);tx('q1','lossless and expensive  vs  lossy and cheap');tx('q2','hybrids keep a few full layers for the lookups that matter')}}
];
"""
build("full-vs-linear-attention.html","Full vs linear attention — keep every token, or keep a summary",
      "A compression-versus-recall trade, seen directly.",svg,js,"0 0 840 366")
print("ok")
