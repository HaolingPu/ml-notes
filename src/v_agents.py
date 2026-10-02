from shell import build
B_F,B_S="#E3EDF9","#A9C4E4"; G_F,G_S="#E2EFE3","#A8CBAC"
A_F,A_S="#FBEBD2","#E2BC85"; N_F,N_S="#F1F1F4","#D5D5DC"; R_F,R_S="#F7DADA","#DF9C9C"; P_F,P_S="#F7E4EC","#DFAFC3"

# ---------------- THE AGENT LOOP ----------------
CX,CY,R=352,196,108
NODES=[("model","the model","reads context, picks an action",B_F,B_S,-90),
       ("orch","the orchestrator","permissions, approval, sandbox",P_F,P_S,-18),
       ("tool","the tool call","shell, search, API, MCP server",A_F,A_S,54),
       ("obs","the observation","often large — a log, a file",G_F,G_S,126),
       ("state","update state","context grows, checkpoint written",N_F,N_S,198)]
import math
svg=f'''<g id="goal" class="fd"><rect x="24" y="22" width="168" height="42" rx="8" fill="{A_F}" stroke="{A_S}" stroke-width="1.5"/>
<text x="108" y="40" class="tiny" text-anchor="middle" font-weight="650">a goal arrives</text>
<text x="108" y="55" class="tiny" text-anchor="middle">"fix the failing test"</text></g>
<g id="ring" class="fd"><circle cx="{CX}" cy="{CY}" r="{R+34}" fill="none" stroke="{N_S}" stroke-width="1" stroke-dasharray="4 4"/></g>'''
POS={}
for i,(nid,t1,t2,f,s,ang) in enumerate(NODES):
    a=math.radians(ang); x=CX+R*math.cos(a)*1.55; y=CY+R*math.sin(a)*1.0
    POS[nid]=(x,y)
    svg+=f'''<g id="n_{nid}" class="fd"><rect x="{x-84}" y="{y-25}" width="168" height="50" rx="9" fill="{f}" stroke="{s}" stroke-width="1.4"/>
<text x="{x}" y="{y-3}" class="tiny" text-anchor="middle" font-weight="650">{t1}</text>
<text x="{x}" y="{y+13}" class="tiny" text-anchor="middle">{t2}</text></g>'''
order=[n[0] for n in NODES]
for i in range(len(order)):
    a,b=POS[order[i]],POS[order[(i+1)%len(order)]]
    svg+=f'<g id="e_{i}" class="fd"><path d="M{a[0]},{a[1]} Q{CX},{CY} {b[0]},{b[1]}" stroke="{N_S}" stroke-width="1.3" fill="none" opacity=".55"/></g>'
svg+=f'''<g id="ctr" class="fd"><text x="{CX}" y="{CY-6}" class="lbl-b" text-anchor="middle" id="c1">the loop</text>
<text x="{CX}" y="{CY+14}" class="tiny" text-anchor="middle" id="c2">not one model call</text></g>
<g id="pk" class="mv fd"><circle r="8" fill="{A_S}"/></g>
<g id="press" class="fd"><text x="730" y="40" class="lbl-b" text-anchor="middle">What the loop makes hard</text>'''
PR=[("context grows","every call re-reads the history","agent-context-growth",64,A_F,A_S),
    ("state must survive","crash, restart, approval wait","agent-checkpointing",134,G_F,G_S),
    ("it must reach out","tools, data, other systems","mcp",204,B_F,B_S),
    ("what enters context","external knowledge vs past experience","rag-vs-memory",274,P_F,P_S)]
for t1,t2,_,y,f,s in PR:
    svg+=f'''<g class="fd"><rect x="628" y="{y}" width="204" height="56" rx="9" fill="{f}" stroke="{s}" stroke-width="1.3"/>
<text x="730" y="{y+23}" class="tiny" text-anchor="middle" font-weight="650">{t1}</text>
<text x="730" y="{y+40}" class="tiny" text-anchor="middle">{t2}</text></g>'''
svg+='</g>'
svg+=f'''<g id="halt" class="fd"><rect x="24" y="330" width="500" height="40" rx="8" fill="#fff" stroke="{N_S}"/>
<text x="274" y="347" class="tiny" text-anchor="middle" font-weight="650" id="h1"></text>
<text x="274" y="362" class="tiny" text-anchor="middle" id="h2"></text></g>'''
js=("var P=%s;\n" % {k:[round(v[0]),round(v[1])] for k,v in POS.items()}) + """
var ORD=['model','orch','tool','obs','state'];
function nodes(n){for(var k=0;k<5;k++)o('n_'+ORD[k],k<n?1:0)}
function edges(n){for(var k=0;k<5;k++)o('e_'+k,k<n?1:0)}
function at(id){o('pk',1);mv('pk',P[id][0],P[id][1]-40)}
function base(){o('goal',0);o('ring',0);nodes(0);edges(0);o('ctr',0);o('pk',0);o('press',0);o('halt',0);
  tx('c1','the loop');tx('c2','not one model call');tx('h1','');tx('h2','')}
var S=[
{c:'A goal arrives. The thing people miss is that an agent is <b>not one model call</b> — it is a loop, and almost every hard problem in agent systems comes from the loop rather than the model.',
 a:function(){o('goal',1);o('ring',1);o('ctr',1)}},
{c:'<b>The model reads the context and picks an action.</b> That is all it does — it emits a decision about which tool to call and with what arguments. It does not execute anything.',
 a:function(){o('goal',1);o('ring',1);nodes(1);at('model')}},
{c:'<b>The orchestrator stays in charge.</b> It checks permissions, gates anything sensitive behind approval, and runs the tool in a sandbox. This is the layer that makes an agent safe to deploy, and it is code you write, not something the model provides.',
 a:function(){o('goal',1);o('ring',1);nodes(2);edges(1);at('orch')}},
{c:'<b>The tool runs.</b> A shell command, a search, an API call, an MCP server — something happens in the real world, which is the whole point and also the whole risk.',
 a:function(){o('goal',1);nodes(3);edges(2);at('tool')}},
{c:'<b>An observation comes back</b> — and this is where agents differ from chat. It is not a sentence, it is a test log, a file, a browser page. One observation can be larger than everything said so far.',
 a:function(){o('goal',1);nodes(4);edges(3);at('obs')}},
{c:'<b>State updates.</b> The observation is appended to the context, and progress is written down. Then the loop runs again — and again, perhaps thirty times.',
 a:function(){o('goal',1);nodes(5);edges(5);at('state');tx('c1','and repeat');tx('c2','often dozens of times')}},
{c:'Round and round. Notice that <b>nothing here is about the model getting smarter</b> — every remaining problem is about what the loop accumulates, what survives a crash, and what it is allowed to touch.',
 a:function(){o('goal',1);nodes(5);edges(5);at('model');tx('c1','the loop is the system');tx('c2','the model is one step in it')}},
{c:'Which gives the <b>four problems</b> the rest of this section is about: the context keeps growing, the state has to survive interruption, the agent has to reach systems it does not own, and something has to decide what enters the context in the first place.',
 a:function(){nodes(5);edges(5);o('press',1);tx('c1','');tx('c2','')}},
{c:'And one more thing the loop needs: <b>a reason to stop</b>. Done, failed, or waiting for a human. An agent without a clear termination condition either quits too early or spends your budget rediscovering the same dead end.',
 a:function(){nodes(5);edges(5);o('halt',1);
   tx('h1','COMPLETED · FAILED · WAITING_FOR_APPROVAL');
   tx('h2','termination is a design decision, not an emergent property')}},
{c:'<b>The line to say:</b> an agent is a model in a loop with tools, state and a stopping rule. The model reasons, the orchestrator controls, the tools act, and the observations are what make it expensive.',
 a:function(){nodes(5);edges(5);o('ctr',1);tx('c1','model + tools + state + a stopping rule');tx('c2','');o('press',1)}}
];
"""
build("agent-loop.html","The agent loop — what an agent actually is",
      "A model in a loop with tools, state, and a reason to stop.",js=js,svg=svg,vb="0 0 870 386",
      title="The agent loop — what an agent actually is",
      sub="A model in a loop with tools, state, and a reason to stop.") if False else build(
      "agent-loop.html","The agent loop — what an agent actually is",
      "A model in a loop with tools, state, and a reason to stop.",svg,js,"0 0 870 386")
print("ok")

# ---------------- CODING AGENT ARCHITECTURE ----------------
B_F,B_S="#E3EDF9","#A9C4E4"; G_F,G_S="#E2EFE3","#A8CBAC"
A_F,A_S="#FBEBD2","#E2BC85"; N_F,N_S="#F1F1F4","#D5D5DC"; R_F,R_S="#F7DADA","#DF9C9C"; P_F,P_S="#F7E4EC","#DFAFC3"
STAGES=[("understand","read the issue","expected vs observed"),
        ("search","search the repo","grep, symbols, vectors"),
        ("localize","localize","what actually runs"),
        ("hypothesize","hypothesise","root cause first"),
        ("edit","edit","smallest change"),
        ("verify","run tests","find out, don\u2019t guess")]
svg=f'<text x="24" y="30" class="lbl-b">The loop</text>\n'
for i,(sid,t1,t2) in enumerate(STAGES):
    x,y=32+i*128,46
    svg+=f'''<g id="s_{sid}" class="fd"><rect x="{x}" y="{y}" width="112" height="56" rx="8" fill="{N_F}" stroke="{N_S}" stroke-width="1.2"/>
<text x="{x+56}" y="{y+24}" class="tiny" text-anchor="middle" font-weight="650">{t1}</text>
<text x="{x+56}" y="{y+41}" class="tiny" text-anchor="middle">{t2}</text></g>'''
    if i<5: svg+=f'<g id="a_{i}" class="fd"><path d="M{x+112},{y+28} L{x+128},{y+28}" stroke="{N_S}" stroke-width="1.3" marker-end="url(#ca)"/></g>'
svg+=f'''<g id="fail" class="fd"><path d="M{32+5*128+56},102 C{32+5*128+56},150 {32+2*128+56},150 {32+2*128+56},106" stroke="{R_S}" stroke-width="1.6" fill="none" stroke-dasharray="5 4" marker-end="url(#cr)"/>
<text x="{32+3*128+56}" y="146" class="tiny" text-anchor="middle" fill="#B36A6A">tests failed — that is an observation, not a dead end</text></g>
<g id="pass" class="fd"><path d="M{32+5*128+112},74 L{32+5*128+134},74" stroke="{G_S}" stroke-width="1.6" marker-end="url(#cg)"/>
<rect x="{32+5*128+138}" y="46" width="96" height="56" rx="8" fill="{G_F}" stroke="{G_S}" stroke-width="1.3"/>
<text x="{32+5*128+186}" y="70" class="tiny" text-anchor="middle" font-weight="650">patch</text>
<text x="{32+5*128+186}" y="86" class="tiny" text-anchor="middle">diff + evidence</text></g>
<g id="repo" class="fd"><rect x="32" y="182" width="300" height="118" rx="10" fill="#FAFAFB" stroke="{N_S}" stroke-dasharray="4 3"/>
<text x="182" y="204" class="tiny" text-anchor="middle" font-weight="650">the repository</text>
<text x="182" y="222" class="tiny" text-anchor="middle">far larger than any context window</text>'''
for k in range(18):
    svg+=f'<rect x="{50+(k%9)*30}" y="{236+(k//9)*22}" width="24" height="14" rx="3" fill="{N_F}" stroke="{N_S}" stroke-width="1" id="f{k}"/>'
svg+=f'''<text x="182" y="290" class="tiny" text-anchor="middle" id="rnote"></text></g>
<g id="retr" class="fd"><rect x="356" y="206" width="150" height="46" rx="8" fill="{A_F}" stroke="{A_S}" stroke-width="1.3"/>
<text x="431" y="226" class="tiny" text-anchor="middle" font-weight="650">retrieval</text>
<text x="431" y="242" class="tiny" text-anchor="middle" id="rt">keyword + symbol + semantic</text>
<path d="M332,229 L356,229" stroke="{N_S}" stroke-width="1.3" marker-end="url(#ca)"/></g>
<g id="ctx" class="fd"><rect x="530" y="206" width="140" height="46" rx="8" fill="{B_F}" stroke="{B_S}" stroke-width="1.3"/>
<text x="600" y="226" class="tiny" text-anchor="middle" font-weight="650">context</text>
<text x="600" y="242" class="tiny" text-anchor="middle">only what matters</text>
<path d="M506,229 L530,229" stroke="{N_S}" stroke-width="1.3" marker-end="url(#ca)"/></g>
<g id="tools" class="fd"><rect x="694" y="176" width="196" height="132" rx="10" fill="#fff" stroke="{N_S}"/>
<text x="792" y="196" class="tiny" text-anchor="middle" font-weight="650">tools, in a sandbox</text>'''
for i,t in enumerate(["read · grep · symbol search","edit file · apply patch","shell · tests · build · lint","git diff · git status","docs · browser · MCP servers"]):
    svg+=f'<text x="792" y="{216+i*19}" class="tiny" text-anchor="middle">{t}</text>'
svg+=f'''</g>
<g id="cmp" class="fd"><rect x="32" y="322" width="420" height="58" rx="9" fill="#fff" stroke="{N_S}"/>
<text x="242" y="342" class="tiny" text-anchor="middle" font-weight="650" id="k1"></text>
<text x="242" y="360" class="tiny" text-anchor="middle" id="k2"></text></g>
<g id="bench" class="fd"><rect x="470" y="322" width="420" height="58" rx="9" fill="{G_F}" stroke="{G_S}" stroke-width="1.2"/>
<text x="680" y="342" class="tiny" text-anchor="middle" font-weight="650" id="b1"></text>
<text x="680" y="360" class="tiny" text-anchor="middle" id="b2"></text></g>
<defs>
<marker id="ca" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0,1 L9,5 L0,9 z" fill="{N_S}"/></marker>
<marker id="cr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0,1 L9,5 L0,9 z" fill="{R_S}"/></marker>
<marker id="cg" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0,1 L9,5 L0,9 z" fill="{G_S}"/></marker></defs>'''
js="""
var ST=['understand','search','localize','hypothesize','edit','verify'];
function stage(n,col){for(var k=0;k<6;k++){
  var e=$('s_'+ST[k]);o('s_'+ST[k],1);
  var on=k<n, f=on?(col||'#E3EDF9'):'#F1F1F4', s=on?(col?'#E2BC85':'#A9C4E4'):'#D5D5DC';
  e.firstChild.setAttribute('fill',f);e.firstChild.setAttribute('stroke',s)}
  for(var k=0;k<5;k++)o('a_'+k,k<n-1?1:0)}
function files(hot){for(var k=0;k<18;k++){var e=$('f'+k);if(!e)continue;
  var on=hot.indexOf(k)>=0;e.setAttribute('fill',on?'#FBEBD2':'#F1F1F4');
  e.setAttribute('stroke',on?'#E2BC85':'#D5D5DC')}}
function base(){stage(0);o('fail',0);o('pass',0);o('repo',0);o('retr',0);o('ctx',0);o('tools',0);
  o('cmp',0);o('bench',0);files([]);tx('rnote','');tx('k1','');tx('k2','');tx('b1','');tx('b2','');
  tx('rt','keyword + symbol + semantic')}
var S=[
{c:'An issue arrives: <i>"the payments test fails intermittently."</i> A coding agent is a closed loop — search, reason, edit, run, observe, replan — and it keeps going until the change is <b>verified</b>, not until it looks plausible.',
 a:function(){stage(1)}},
{c:'<b>First problem: the repository does not fit.</b> A real codebase is orders of magnitude larger than any context window, so the agent cannot simply read it.',
 a:function(){stage(1);o('repo',1);tx('rnote','you cannot put this in a prompt')}},
{c:'So it <b>retrieves</b> — this is RAG, applied to code. Grep and symbol search for exact names, semantic search for "where is retry logic", plus static-analysis references and dependency paths to follow what actually calls what.',
 a:function(){stage(2);o('repo',1);o('retr',1);o('ctx',1);files([3,4,10,11]);
   tx('rnote','a handful of files, not the whole tree')}},
{c:'<b>Localize.</b> Retrieval gives candidates; localization narrows to the files and functions on the <b>execution path that actually produces the bug</b>. Getting this wrong wastes every step after it.',
 a:function(){stage(3);o('repo',1);o('retr',1);o('ctx',1);files([3,10]);
   tx('rt','narrow to the real execution path');tx('rnote','two files that actually run')}},
{c:'<b>Hypothesise before editing.</b> This is what separates a working agent from one that flails: state a root cause first — <i>"the retry shares a connection pool across threads"</i> — then make a change that <b>tests that specific claim</b>.',
 a:function(){stage(4);o('ctx',1)}},
{c:'<b>The smallest targeted edit.</b> A large speculative rewrite makes failure uninterpretable: when the tests still fail you cannot tell which part was wrong.',
 a:function(){stage(5);o('ctx',1);o('tools',1)}},
{c:'<b>Then run the tests</b> — and this is the defining moment. The agent is not predicting whether the fix works; it is <b>finding out</b>. Targeted tests first, then the wider suite.',
 a:function(){stage(6,'#FBEBD2');o('tools',1)}},
{c:'<b>Failure is not a dead end — it is an observation.</b> The error message is new evidence, so the agent goes back to localization with more information than it had before. Randomly editing after a failure is the classic bad-agent behaviour.',
 a:function(){stage(6,'#FBEBD2');o('fail',1);o('tools',1)}},
{c:'When the targeted tests pass, a <b>regression check</b> follows — because fixing one thing and breaking two is the failure mode nobody notices until later. The deliverable is a <b>patch plus the evidence</b> that it works.',
 a:function(){stage(6);o('pass',1);o('tools',1)}},
{c:'<b>The distinction worth stating:</b> RAG retrieves information and generates an answer. A coding agent retrieves code, <b>acts on the environment</b>, observes what happened, and repeats. The interactive verification loop is the whole difference.',
 a:function(){stage(6);o('pass',1);o('cmp',1);
   tx('k1','RAG:  retrieve → generate');tx('k2','coding agent:  retrieve → act → observe → repeat')}},
{c:'And that is exactly what <b>SWE-bench</b> measures — real repositories, real issues, graded on whether the produced patch passes the evaluation tests without breaking existing behaviour. End to end, not step by step.',
 a:function(){stage(6);o('pass',1);o('bench',1);
   tx('b1','SWE-bench: search → localize → edit → patch that passes');
   tx('b2','graded on the outcome, which is why localization quality dominates')}},
{c:'<b>The line to say:</b> search → localize → hypothesise → edit → test → replan, wrapped by an orchestrator with sandboxed tools, checkpointed state, and version control as the verification surface.',
 a:function(){stage(6);o('pass',1);o('tools',1);o('cmp',1);
   tx('k1','the loop is the architecture');tx('k2','the model is one step inside it')}}
];
"""
build("coding-agent.html","Coding agent architecture — the verification loop",
      "Search, localize, hypothesise, edit, test, replan — until it is proven, not plausible.",svg,js,"0 0 920 396")
print("ok2")
