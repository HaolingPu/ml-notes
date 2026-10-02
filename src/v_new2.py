from shell import build
B_F,B_S="#E3EDF9","#A9C4E4"; G_F,G_S="#E2EFE3","#A8CBAC"
A_F,A_S="#FBEBD2","#E2BC85"; N_F,N_S="#F1F1F4","#D5D5DC"; R_F,R_S="#F7DADA","#DF9C9C"; P_F,P_S="#F7E4EC","#DFAFC3"

# ---------------- PD DISAGGREGATION ----------------
svg=f'''<text x="24" y="32" class="lbl-b" id="mode">Shared pool — prefill and decode on the same GPUs</text>
<g id="pool" class="fd"><rect x="24" y="46" width="420" height="120" rx="10" fill="#FAFAFB" stroke="{N_S}" stroke-dasharray="4 3"/>
<text x="38" y="66" class="tiny" font-weight="650">GPU pool</text></g>
<g id="bigpf" class="mv fd"><rect width="250" height="30" rx="5" fill="{B_F}" stroke="{B_S}" stroke-width="1.4"/>
<text x="125" y="20" class="tiny" text-anchor="middle">20K-token prefill</text></g>'''
for k in range(4):
    svg+=f'''<g id="ds{k}" class="fd"><rect x="{44+k*44}" y="126" width="36" height="24" rx="4" fill="{A_F}" stroke="{A_S}" stroke-width="1.2"/></g>'''
svg+=f'''<g id="stall" class="fd"><rect x="224" y="126" width="200" height="24" rx="4" fill="{R_F}" stroke="{R_S}" stroke-width="1.2"/>
<text x="324" y="142" class="tiny" text-anchor="middle" fill="#B36A6A">other users' tokens paused</text></g>
<text x="34" y="120" class="tiny" id="dlab">decode steps</text>
<g id="split" class="fd">
<rect x="470" y="46" width="160" height="120" rx="10" fill="{B_F}" stroke="{B_S}" stroke-width="1.3"/>
<text x="550" y="70" class="tiny" text-anchor="middle" font-weight="650">prefill pool</text>
<text x="550" y="88" class="tiny" text-anchor="middle">big GEMMs</text>
<text x="550" y="104" class="tiny" text-anchor="middle">compute-bound</text>
<text x="550" y="128" class="tiny" text-anchor="middle" id="pfn">scale for long prompts</text>
<rect x="672" y="46" width="160" height="120" rx="10" fill="{A_F}" stroke="{A_S}" stroke-width="1.3"/>
<text x="752" y="70" class="tiny" text-anchor="middle" font-weight="650">decode pool</text>
<text x="752" y="88" class="tiny" text-anchor="middle">one token per step</text>
<text x="752" y="104" class="tiny" text-anchor="middle">bandwidth-bound</text>
<text x="752" y="128" class="tiny" text-anchor="middle" id="dcn">scale for long answers</text></g>
<g id="kvmove" class="mv fd"><rect width="46" height="26" rx="4" fill="{G_F}" stroke="{G_S}" stroke-width="1.4"/>
<text x="23" y="17" class="tiny" text-anchor="middle">KV</text></g>
<g id="wire" class="fd"><path d="M573,193 L729,193" stroke="{G_S}" stroke-width="1.4" stroke-dasharray="3 3"/>
<text x="651" y="212" class="tiny" text-anchor="middle" id="wt"></text></g>
<g id="cmp" class="fd"><text x="24" y="248" class="lbl-b">Where the interference goes</text>
<text x="150" y="280" class="tiny" text-anchor="end">chunked prefill</text>
<rect x="160" y="268" width="300" height="15" rx="7" fill="#F1F1F4"/>
<g id="c1" transform="translate(160,268) scale(.45,1)"><rect width="300" height="15" rx="7" fill="{A_S}"/></g>
<text x="472" y="280" class="tiny">same pool, prefill sliced and interleaved — no KV moves</text>
<text x="150" y="312" class="tiny" text-anchor="end">disaggregation</text>
<rect x="160" y="300" width="300" height="15" rx="7" fill="#F1F1F4"/>
<g id="c2" transform="translate(160,300) scale(.08,1)"><rect width="300" height="15" rx="7" fill="{G_S}"/></g>
<text x="472" y="312" class="tiny">separate pools — but the KV cache crosses the network</text></g>
<g id="msg" class="fd"><text x="420" y="348" class="lbl-b" text-anchor="middle" id="mt"></text></g>'''
js="""
function sc(id,x,y,s){$(id).setAttribute('transform','translate('+x+','+y+') scale('+s+',1)')}
function ds(n){for(var k=0;k<4;k++)o('ds'+k,k<n?1:0)}
function base(){o('pool',0);o('bigpf',0);ds(0);o('stall',0);o('split',0);o('kvmove',0);o('wire',0);
  o('cmp',0);o('msg',0);tx('mt','');tx('wt','');o('dlab',0);
  mv('bigpf',44,76);mv('kvmove',527,180);
  tx('mode','Shared pool — prefill and decode on the same GPUs')}
var S=[
{c:'One request: a <b>20K-token prompt</b> that will generate 500 tokens. On a shared pool, both phases run on the same GPUs.',
 a:function(){o('pool',1);o('bigpf',1);ds(4);o('dlab',1)}},
{c:'The prefill is one enormous piece of work. While it runs it <b>occupies the GPU</b> — and every other user who was mid-answer stops receiving tokens.',
 a:function(){o('pool',1);o('bigpf',1);o('dlab',1);ds(1);o('stall',1)}},
{c:'That is the real complaint: not that anything is slow on average, but that someone\\'s stream visibly <b>stutters</b> whenever a long prompt arrives behind them.',
 a:function(){o('pool',1);o('bigpf',1);o('dlab',1);ds(1);o('stall',1);
   o('msg',1);tx('mt','the two phases want opposite things, and they are fighting for the same GPU')}},
{c:'<b>Disaggregation stops them competing.</b> Prefill gets its own pool, decode gets its own. Each can now be sized and tuned for its own bottleneck — compute on one side, memory bandwidth on the other.',
 a:function(){tx('mode','Disaggregated — each phase on its own pool');o('split',1)}},
{c:'A request enters the <b>prefill pool</b>, which reads the prompt and builds the KV cache.',
 a:function(){tx('mode','Disaggregated — each phase on its own pool');o('split',1);o('kvmove',1);mv('kvmove',527,180)}},
{c:'Then the KV cache is <b>transferred across the interconnect</b> to a decode worker, which streams the 500 tokens out. Watch what just moved — that is the whole cost of this design.',
 a:function(){tx('mode','Disaggregated — each phase on its own pool');o('split',1);o('kvmove',1);mv('kvmove',729,180);o('wire',1);
   tx('wt','a 20K-token KV cache, crossing the network on every request')}},
{c:'The payoff is <b>independent scaling</b>. Traffic full of long documents? Add prefill workers. Traffic full of long answers? Add decode workers. On a shared pool you could only add both.',
 a:function(){tx('mode','Disaggregated — each phase on its own pool');o('split',1);o('wire',1);tx('pfn','add workers for long prompts');tx('dcn','add workers for long answers');
   o('msg',1);tx('mt','each pool scales to its own bottleneck')}},
{c:'<b>The comparison to have ready:</b> chunked prefill keeps one pool but slices prefill into chunks interleaved with decode — less interference, and nothing has to move. Disaggregation removes interference entirely but pays a transfer on every request.',
 a:function(){tx('mode','Disaggregated — each phase on its own pool');o('split',1);o('cmp',1)}},
{c:'<b>The line to say:</b> which one wins is an <b>interconnect question</b>. On fast links the transfer is cheap and disaggregation pays; on slow ones it can cost more than the interference it removed. Name the tradeoff, do not just name the technique.',
 a:function(){tx('mode','Disaggregated — each phase on its own pool');o('split',1);o('cmp',1);o('msg',1);tx('mt','fast interconnect → disaggregate · slow interconnect → chunk instead')}}
];
"""
build("pd-disaggregation.html","Prefill–decode disaggregation — stopping the two phases from fighting",
      "Separate pools, and the KV transfer you pay for them.",svg,js,"0 0 840 366")

# ---------------- TP / PP / EP ----------------
svg=f'<text x="24" y="32" class="lbl-b" id="ttl">Tensor Parallelism</text>\n<text x="24" y="50" class="tiny" id="sub2">split the matrices inside one layer</text>\n'
for k in range(4):
    svg+=f'''<g id="g{k}" class="fd"><rect x="{40+k*196}" y="70" width="168" height="118" rx="9" fill="#FAFAFB" stroke="{N_S}" stroke-width="1.2"/>
<text x="{124+k*196}" y="90" class="tiny" text-anchor="middle" font-weight="650">GPU {k+1}</text>
<rect x="{58+k*196}" y="100" width="132" height="30" rx="5" fill="{B_F}" stroke="{B_S}" stroke-width="1.2" id="gb{k}"/>
<text x="{124+k*196}" y="120" class="tiny" text-anchor="middle" id="gt{k}">shard</text>
<text x="{124+k*196}" y="152" class="tiny" text-anchor="middle" id="gs{k}"></text>
<text x="{124+k*196}" y="170" class="tiny" text-anchor="middle" id="gs2{k}"></text></g>'''
svg+=f'''<g id="comm" class="fd">'''
for k in range(3):
    svg+=f'<path id="cw{k}" d="M{208+k*196},129 L{236+k*196},129" stroke="{A_S}" stroke-width="2"/>'
svg+=f'''<text x="424" y="214" class="tiny" text-anchor="middle" id="ctxt"></text></g>
<g id="topo" class="fd"><rect x="40" y="232" width="760" height="56" rx="9" fill="#fff" stroke="{N_S}"/>
<text x="420" y="254" class="tiny" text-anchor="middle" font-weight="650" id="tp1"></text>
<text x="420" y="274" class="tiny" text-anchor="middle" id="tp2"></text></g>'''
js="""
function cells(t){for(var k=0;k<4;k++){tx('gt'+k,t[k]||'');}}
function notes(a,b){for(var k=0;k<4;k++){tx('gs'+k,a?a[k]||'':'');tx('gs2'+k,b?b[k]||'':'')}}
function fills(c){var F={b:['#E3EDF9','#A9C4E4'],g:['#E2EFE3','#A8CBAC'],a:['#FBEBD2','#E2BC85'],p:['#F7E4EC','#DFAFC3']};
  for(var k=0;k<4;k++){var f=F[c[k]]||F.b;$('gb'+k).setAttribute('fill',f[0]);$('gb'+k).setAttribute('stroke',f[1])}}
function comm(n,t){o('comm',n>0?1:0);for(var k=0;k<3;k++)o('cw'+k,k<n?1:0);tx('ctxt',t||'')}
function base(){comm(0,'');o('topo',0);tx('tp1','');tx('tp2','');
  cells(['','','','']);notes(null,null);fills(['b','b','b','b']);
  tx('ttl','Tensor Parallelism');tx('sub2','split the matrices inside one layer')}
var S=[
{c:'The model no longer fits on one GPU, so it has to be cut. There are three places to cut it — and each one creates a <b>different communication pattern</b>. That pattern is what actually decides which to use.',
 a:function(){cells(['?','?','?','?'])}},
{c:'<b>Tensor parallelism</b> cuts <i>inside</i> a layer. All four GPUs hold a slice of the same weight matrices and work on the <b>same layer at the same time</b>.',
 a:function(){cells(['layer slice','layer slice','layer slice','layer slice']);fills(['b','b','b','b'])}},
{c:'But a slice of a matrix multiply is only a <b>partial result</b>. Before the layer can finish, all four must combine what they computed — and that happens at <b>every layer</b>, many times per forward pass.',
 a:function(){cells(['partial','partial','partial','partial']);comm(3,'combine partial results — every layer, every pass')}},
{c:'Which is why TP lives <b>inside a node</b>, on NVLink. Stretch those four GPUs across a slower network and communication dominates — four GPUs can end up slower than one would have been if the model had fit.',
 a:function(){cells(['partial','partial','partial','partial']);comm(3,'constant, latency-sensitive traffic');
   o('topo',1);tx('tp1','TP → keep it on the fast links inside one node');tx('tp2','NVLink / NVSwitch')}},
{c:'<b>Pipeline parallelism</b> cuts somewhere else entirely: each GPU gets a <b>different block of layers</b>. Nobody shares a layer, so nobody shares a partial result.',
 a:function(){tx('ttl','Pipeline Parallelism');tx('sub2','split different groups of layers across stages');
   cells(['layers 1–20','layers 21–40','layers 41–60','layers 61–80']);fills(['g','g','g','g'])}},
{c:'Data now crosses only at the <b>three stage boundaries</b> — rarely, and in one direction. That tolerates a slower link, which is why the standard layout is <b>TP inside a node, PP across nodes</b>.',
 a:function(){tx('ttl','Pipeline Parallelism');tx('sub2','split different groups of layers across stages');
   cells(['layers 1–20','layers 21–40','layers 41–60','layers 61–80']);fills(['g','g','g','g']);
   comm(3,'activations cross only at stage boundaries');
   o('topo',1);tx('tp1','PP → tolerates the slower network between nodes');tx('tp2','communication only at the seams')}},
{c:'But PP buys that with a new problem: stage 2 cannot start until stage 1 hands something over. <b>Most of the pipeline sits idle</b> — the bubble, which micro-batching exists to fill.',
 a:function(){tx('ttl','Pipeline Parallelism');tx('sub2','and the bubble it creates');
   cells(['working','waiting','waiting','waiting']);fills(['g','p','p','p']);
   o('topo',1);tx('tp1','the cost of cutting by layer: stages wait on each other');tx('tp2','see: pipeline bubbles and micro-batching')}},
{c:'<b>Expert parallelism</b> is for MoE models. Each GPU hosts <b>different experts</b>, and a router sends each token only to the experts it selected — so each token touches a couple of GPUs, not all of them.',
 a:function(){tx('ttl','Expert Parallelism');tx('sub2','split the MoE experts across GPUs');
   cells(['experts 1–2','experts 3–4','experts 5–6','experts 7–8']);fills(['a','a','a','a'])}},
{c:'The traffic pattern is different again: every GPU sends <b>different tokens to different destinations</b>. That is an <b>All-to-All</b>, and it happens twice — once to scatter the tokens, once to bring the results home.',
 a:function(){tx('ttl','Expert Parallelism');tx('sub2','split the MoE experts across GPUs');
   cells(['experts 1–2','experts 3–4','experts 5–6','experts 7–8']);fills(['a','a','a','a']);
   comm(3,'All-to-All — tokens scatter to their experts, results come back');
   o('topo',1);tx('tp1','EP → routing is data-dependent, so expert load can be uneven');tx('tp2','a popular expert becomes a straggler everyone waits for')}},
{c:'<b>The line to say:</b> TP splits tensors, PP splits layers, EP splits experts — and the choice follows the <b>hardware topology</b>, not preference. Real systems combine them: TP within a node, PP across nodes, EP where the model is MoE.',
 a:function(){tx('ttl','TP · PP · EP');tx('sub2','three cuts, three communication patterns');
   cells(['tensors','layers','experts','—']);fills(['b','g','a','b']);
   o('topo',1);tx('tp1','every split turns compute into communication');tx('tp2','the question is which communication your hardware can afford')}}
];
"""
build("model-parallelism.html","TP, PP and EP — three ways to cut a model",
      "Each cut creates a different communication pattern, and that decides everything.",svg,js,"0 0 840 300")
print("ok")
