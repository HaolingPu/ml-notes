from shell import build
B_F,B_S="#E3EDF9","#A9C4E4"; G_F,G_S="#E2EFE3","#A8CBAC"
A_F,A_S="#FBEBD2","#E2BC85"; N_F,N_S="#F1F1F4","#D5D5DC"; R_F,R_S="#F7DADA","#DF9C9C"; P_F,P_S="#F7E4EC","#DFAFC3"

# ---------------- MCP ----------------
svg=f'''<g id="naive" class="fd"><text x="24" y="32" class="lbl-b">Without a standard: N agents × M services</text>'''
AG=[("agent A",58),("agent B",122),("agent C",186)]
SV2=[("GitHub",58),("database",122),("files",186)]
for i,(n,y) in enumerate(AG):
    svg+=f'<rect x="40" y="{y}" width="96" height="34" rx="6" fill="{B_F}" stroke="{B_S}" stroke-width="1.2"/><text x="88" y="{y+22}" class="tiny" text-anchor="middle">{n}</text>'
for i,(n,y) in enumerate(SV2):
    svg+=f'<rect x="290" y="{y}" width="96" height="34" rx="6" fill="{G_F}" stroke="{G_S}" stroke-width="1.2"/><text x="338" y="{y+22}" class="tiny" text-anchor="middle">{n}</text>'
for i in range(3):
    for j in range(3):
        svg+=f'<path d="M136,{AG[i][1]+17} L290,{SV2[j][1]+17}" stroke="{R_S}" stroke-width="1" opacity=".7"/>'
svg+=f'<text x="213" y="242" class="tiny" text-anchor="middle" fill="#B36A6A">9 bespoke integrations — each with its own auth, schema and failures</text></g>'
svg+=f'''<g id="std" class="fd"><text x="440" y="32" class="lbl-b">With MCP: N + M</text>'''
for i,(n,y) in enumerate(AG):
    svg+=f'<rect x="440" y="{y}" width="88" height="34" rx="6" fill="{B_F}" stroke="{B_S}" stroke-width="1.2"/><text x="484" y="{y+22}" class="tiny" text-anchor="middle">{n}</text>'
svg+=f'''<rect x="566" y="100" width="78" height="78" rx="8" fill="{A_F}" stroke="{A_S}" stroke-width="1.5"/>
<text x="605" y="132" class="tiny" text-anchor="middle" font-weight="650">MCP</text>
<text x="605" y="150" class="tiny" text-anchor="middle">standard</text>'''
for i,(n,y) in enumerate(SV2):
    svg+=f'<rect x="684" y="{y}" width="96" height="34" rx="6" fill="{G_F}" stroke="{G_S}" stroke-width="1.2"/><text x="732" y="{y+22}" class="tiny" text-anchor="middle">{n} server</text>'
for i in range(3):
    svg+=f'<path d="M528,{AG[i][1]+17} C548,{AG[i][1]+17} 548,139 566,139" stroke="{N_S}" stroke-width="1.2" fill="none"/>'
    svg+=f'<path d="M644,139 C664,139 664,{SV2[i][1]+17} 684,{SV2[i][1]+17}" stroke="{N_S}" stroke-width="1.2" fill="none"/>'
svg+=f'<text x="610" y="242" class="tiny" text-anchor="middle" fill="#5F7F63">any compliant host can use any compliant server</text></g>'
svg+=f'''<g id="stack" class="fd"><rect x="40" y="58" width="760" height="190" rx="10" fill="#FAFAFB" stroke="{N_S}"/>'''
LAYERS=[("the model","decides which tool and what arguments","function calling",B_F,B_S),
        ("the orchestrator","checks permissions, approval, sandboxing","runtime control",P_F,P_S),
        ("the MCP client → server","discovers and reaches the capability","MCP",A_F,A_S),
        ("the external system","GitHub, a database, a file system","the real API",G_F,G_S)]
for i,(a,b,c,f,s) in enumerate(LAYERS):
    y=74+i*44
    svg+=f'''<rect x="60" y="{y}" width="480" height="36" rx="6" fill="{f}" stroke="{s}" stroke-width="1.2"/>
<text x="76" y="{y+16}" class="tiny" font-weight="650">{a}</text>
<text x="76" y="{y+30}" class="tiny">{b}</text>
<text x="700" y="{y+23}" class="tiny" text-anchor="middle" id="ly{i}">{c}</text>'''
svg+=f'''<g id="flow" class="mv fd"><circle r="8" fill="{A_S}"/></g></g>
<g id="msg" class="fd"><text x="420" y="286" class="lbl-b" text-anchor="middle" id="mt"></text>
<text x="420" y="306" class="tiny" text-anchor="middle" id="mt2"></text></g>'''
js="""
function base(){o('naive',0);o('std',0);o('stack',0);o('flow',0);o('msg',0);tx('mt','');tx('mt2','');
  mv('flow',300,92)}
var S=[
{c:'Every agent that wants to reach GitHub, a database or a file system writes its <b>own bespoke integration</b> — its own auth, its own schema, its own failure modes.',
 a:function(){o('naive',1)}},
{c:'Three agents and three services is already nine integrations. Add a service and every agent has to be updated. This is the <b>N×M problem</b>.',
 a:function(){o('naive',1);o('msg',1);tx('mt','every new service means touching every agent');tx('mt2','')}},
{c:'<b>MCP standardises the boundary</b> between the agent runtime and external capabilities. Each service is wrapped once by a <b>server</b>; each agent speaks the protocol once. Nine becomes six — and at scale, N×M becomes N+M.',
 a:function(){o('std',1)}},
{c:'A server exposes three kinds of thing: <b>Tools</b> (actions like <i>create_issue</i>), <b>Resources</b> (data like a file or a record), and <b>Prompts</b> (reusable templates).',
 a:function(){o('std',1);o('msg',1);tx('mt','Tools = actions · Resources = data · Prompts = templates');
   tx('mt2','a tool does something; a resource is something')}},
{c:'<b>Now the distinction that gets tested.</b> MCP does not replace function calling — they sit at different layers. Follow one request down the stack.',
 a:function(){o('stack',1);o('flow',1);mv('flow',300,92)}},
{c:'<b>The model</b> decides <i>which</i> tool to call and with <i>what</i> arguments. That is <b>function calling</b>, and it happens entirely inside the model\\'s output.',
 a:function(){o('stack',1);o('flow',1);mv('flow',300,92)}},
{c:'<b>The orchestrator</b> receives that decision and stays in charge — permission checks, approval gates, sandboxing. MCP bypasses none of this, which is the safety point worth making unprompted.',
 a:function(){o('stack',1);o('flow',1);mv('flow',300,136)}},
{c:'<b>MCP</b> is how the runtime then <i>discovers and reaches</i> that capability — a standard protocol between client and server, not a decision about what to do.',
 a:function(){o('stack',1);o('flow',1);mv('flow',300,180)}},
{c:'And the <b>server</b> translates it into a real API call. Swap GitHub for Linear and the model\\'s half is unchanged — a different server handles it. That substitutability is the entire point.',
 a:function(){o('stack',1);o('flow',1);mv('flow',300,224);o('msg',1);
   tx('mt','the model reasons · the orchestrator controls · MCP connects · the server provides');tx('mt2','')}},
{c:'<b>The tradeoff:</b> another layer and another process to run, a standard interface can hide capabilities a native API exposes, and widening what an agent can reach is a <b>security surface</b>, not just a convenience.',
 a:function(){o('std',1);o('msg',1);tx('mt','standardisation buys substitutability; it costs a layer and widens reach');
   tx('mt2','which is why permission checks stay with the orchestrator, not the protocol')}}
];
"""
build("mcp.html","MCP — standardising how an agent reaches the outside world",
      "Why it is not function calling, and which layer each one lives at.",svg,js,"0 0 840 320")

# ---------------- RAG vs MEMORY ----------------
svg=f'''<g id="task" class="fd"><rect x="300" y="26" width="240" height="38" rx="7" fill="{A_F}" stroke="{A_S}" stroke-width="1.5"/>
<text x="420" y="50" class="tiny" text-anchor="middle" font-weight="650">"fix the flaky test in payments"</text></g>
<g id="rag" class="fd"><rect x="30" y="98" width="330" height="130" rx="10" fill="{B_F}" stroke="{B_S}" stroke-width="1.4"/>
<text x="195" y="122" class="tiny" text-anchor="middle" font-weight="650">RAG</text>
<text x="195" y="140" class="tiny" text-anchor="middle">what external knowledge is relevant?</text>
<rect x="52" y="152" width="286" height="26" rx="5" fill="#fff" stroke="{B_S}" stroke-width="1"/>
<text x="195" y="169" class="tiny" text-anchor="middle" id="r1">the payments module source</text>
<rect x="52" y="184" width="286" height="26" rx="5" fill="#fff" stroke="{B_S}" stroke-width="1"/>
<text x="195" y="201" class="tiny" text-anchor="middle" id="r2">the test framework docs</text></g>
<g id="mem" class="fd"><rect x="480" y="98" width="330" height="130" rx="10" fill="{G_F}" stroke="{G_S}" stroke-width="1.4"/>
<text x="645" y="122" class="tiny" text-anchor="middle" font-weight="650">Memory</text>
<text x="645" y="140" class="tiny" text-anchor="middle">what from before should persist?</text>
<rect x="502" y="152" width="286" height="26" rx="5" fill="#fff" stroke="{G_S}" stroke-width="1"/>
<text x="645" y="169" class="tiny" text-anchor="middle" id="m1">"we tried the timeout fix — it failed"</text>
<rect x="502" y="184" width="286" height="26" rx="5" fill="#fff" stroke="{G_S}" stroke-width="1"/>
<text x="645" y="201" class="tiny" text-anchor="middle" id="m2">"this user wants root cause, not retries"</text></g>
<g id="src" class="fd"><text x="195" y="90" class="tiny" text-anchor="middle">docs · code · wikis · databases — exists independently of you</text>
<text x="645" y="90" class="tiny" text-anchor="middle">decisions · preferences · failed attempts — exists only because of you</text></g>
<g id="ctx" class="fd"><rect x="300" y="256" width="240" height="44" rx="8" fill="#fff" stroke="{A_S}" stroke-width="1.5"/>
<text x="420" y="274" class="tiny" text-anchor="middle" font-weight="650">working context</text>
<text x="420" y="290" class="tiny" text-anchor="middle">what the model actually sees</text>
<path d="M195,228 C195,246 300,252 300,268" stroke="{B_S}" stroke-width="1.4" fill="none"/>
<path d="M645,228 C645,246 540,252 540,268" stroke="{G_S}" stroke-width="1.4" fill="none"/></g>
<g id="wp" class="fd"><rect x="480" y="240" width="330" height="34" rx="7" fill="{A_F}" stroke="{A_S}" stroke-width="1.2"/>
<text x="645" y="261" class="tiny" text-anchor="middle">memory also needs a <tspan font-weight="650">write policy</tspan> — what was worth keeping?</text></g>
<g id="msg" class="fd"><text x="420" y="330" class="lbl-b" text-anchor="middle" id="mt"></text>
<text x="420" y="348" class="tiny" text-anchor="middle" id="mt2"></text></g>'''
js="""
function base(){o('task',1);o('rag',0);o('mem',0);o('src',0);o('ctx',0);o('wp',0);o('msg',0);
  tx('mt','');tx('mt2','');
  tx('r1','the payments module source');tx('r2','the test framework docs');
  tx('m1','"we tried the timeout fix \u2014 it failed"');tx('m2','"this user wants root cause, not retries"')}
var S=[
{c:'One task, and a working context far too small to hold everything that might help. Two different retrieval jobs compete for that space.',
 a:function(){}},
{c:'<b>RAG</b> answers one question: <i>what external knowledge is relevant to this task?</i> It reaches into documents, code, wikis and databases — things that exist whether or not this agent ever ran.',
 a:function(){o('rag',1);o('src',1)}},
{c:'<b>Memory</b> answers a different question: <i>what from earlier should persist?</i> Prior decisions, user preferences, failed hypotheses — things that exist <b>only because of previous interaction</b>.',
 a:function(){o('rag',1);o('mem',1);o('src',1)}},
{c:'Both feed the same working context, and both may sit on the same vector store. The infrastructure can be identical — what differs is the <b>semantics of what is stored</b>.',
 a:function(){o('rag',1);o('mem',1);o('ctx',1)}},
{c:'Watch what each one contributes here. RAG supplies the <b>code and the docs</b>. Memory supplies <i>"we already tried bumping the timeout and it did not help"</i>.',
 a:function(){o('rag',1);o('mem',1);o('ctx',1);o('src',1)}},
{c:'<b>Remove RAG</b> and the agent has no idea what the code looks like. <b>Remove memory</b> and it cheerfully re-tries the timeout fix it already ruled out last week. They fail in completely different ways.',
 a:function(){o('rag',1);o('mem',1);o('ctx',1);
   tx('r1','✗ without RAG: no idea what the code does');tx('r2','');
   tx('m1','✗ without memory: repeats a ruled-out fix');tx('m2','');
   o('msg',1);tx('mt','different failure modes — which is how you know they are different things');tx('mt2','')}},
{c:'<b>And memory has a problem RAG does not.</b> Documents already exist; nobody had to decide they were worth writing. Memories must be <b>chosen</b> — so memory needs a write policy as well as a retrieval policy.',
 a:function(){o('rag',1);o('mem',1);o('wp',1)}},
{c:'Which brings the real risk: a wrong conclusion written to memory gets <b>retrieved forever</b>. RAG is only as good as its chunking and index; memory can <b>compound its own errors</b>.',
 a:function(){o('rag',1);o('mem',1);o('wp',1);o('msg',1);
   tx('mt','both spend scarce context on things that may not help');tx('mt2','but only memory can keep re-confirming its own mistake')}},
{c:'<b>The line to say:</b> RAG retrieves <b>external knowledge</b> for the current task; memory retrieves <b>persistent experience</b> from prior interaction. Same plumbing, different semantics — and MCP is neither: it is how the retrieval capability gets <i>connected</i>, not what gets retrieved.',
 a:function(){o('rag',1);o('mem',1);o('ctx',1);o('msg',1);
   tx('mt','"what does the world know" vs "what did we learn"');
   tx('mt2','MCP can expose search_docs() — that is integration, not retrieval strategy')}}
];
"""
build("rag-vs-memory.html","RAG vs memory — two retrievals, two questions",
      "Same infrastructure, completely different semantics.",svg,js,"0 0 840 362")
print("ok")
