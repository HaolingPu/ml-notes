from shell import build
B_F,B_S="#E3EDF9","#A9C4E4"; G_F,G_S="#E2EFE3","#A8CBAC"
A_F,A_S="#FBEBD2","#E2BC85"; N_F,N_S="#F1F1F4","#D5D5DC"; R_F,R_S="#F7DADA","#DF9C9C"; P_F,P_S="#F7E4EC","#DFAFC3"

# ---------------- SERVICE MESH ----------------
svg=f'''<g id="user" class="fd"><rect x="24" y="130" width="96" height="34" rx="6" fill="{N_F}" stroke="{N_S}" stroke-width="1.2"/>
<text x="72" y="152" class="tiny" text-anchor="middle" font-weight="650">client</text></g>
<g id="gw" class="fd"><rect x="164" y="130" width="104" height="34" rx="6" fill="{B_F}" stroke="{B_S}" stroke-width="1.2"/>
<text x="216" y="152" class="tiny" text-anchor="middle">API gateway</text></g>
<g id="mesh" class="fd"><rect x="312" y="122" width="120" height="50" rx="8" fill="{A_F}" stroke="{A_S}" stroke-width="1.5"/>
<text x="372" y="142" class="tiny" text-anchor="middle" font-weight="650">service mesh</text>
<text x="372" y="158" class="tiny" text-anchor="middle">Envoy proxy</text></g>
<g id="ctl" class="fd"><rect x="312" y="42" width="120" height="42" rx="8" fill="#fff" stroke="{A_S}" stroke-width="1.2" stroke-dasharray="4 3"/>
<text x="372" y="60" class="tiny" text-anchor="middle" font-weight="650">control plane</text>
<text x="372" y="75" class="tiny" text-anchor="middle">Istio</text>
<path d="M372,84 L372,120" stroke="{A_S}" stroke-width="1.2" stroke-dasharray="3 3"/>
<text x="300" y="70" class="tiny" text-anchor="end" fill="#8A6D3B">configures every proxy</text></g>'''
for k in range(3):
    y=62+k*76
    svg+=f'''<g id="r{k}" class="fd"><rect x="524" y="{y}" width="150" height="56" rx="8" fill="{G_F}" stroke="{G_S}" stroke-width="1.2"/>
<text x="599" y="{y+22}" class="tiny" text-anchor="middle" font-weight="650">inference replica {k+1}</text>
<text x="599" y="{y+40}" class="tiny" text-anchor="middle" id="rs{k}">healthy</text></g>
<g id="e{k}" class="fd"><path d="M432,147 C478,147 478,{y+28} 524,{y+28}" stroke="{N_S}" stroke-width="1.2" fill="none"/></g>'''
svg+=f'''<g id="a1" class="fd"><path d="M120,147 L164,147" stroke="{N_S}" stroke-width="1.4" marker-end="url(#am)"/></g>
<g id="a2" class="fd"><path d="M268,147 L312,147" stroke="{N_S}" stroke-width="1.4" marker-end="url(#am)"/></g>
<g id="pkt" class="mv fd"><circle r="7" fill="{A_S}"/></g>
<g id="sched" class="fd"><rect x="524" y="286" width="290" height="62" rx="8" fill="#fff" stroke="{B_S}" stroke-width="1.3"/>
<text x="669" y="306" class="tiny" text-anchor="middle" font-weight="650">inside one replica: the engine scheduler</text>
<text x="669" y="324" class="tiny" text-anchor="middle">which requests share the next decode step,</text>
<text x="669" y="339" class="tiny" text-anchor="middle">which KV blocks to allocate</text>
<path d="M599,270 L599,286" stroke="{B_S}" stroke-width="1.2" stroke-dasharray="3 3"/></g>
<g id="msg" class="fd"><text x="250" y="306" class="lbl-b" text-anchor="middle" id="mt"></text>
<text x="250" y="326" class="tiny" text-anchor="middle" id="mt2"></text></g>
<defs><marker id="am" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0,1 L9,5 L0,9 z" fill="{N_S}"/></marker></defs>'''
js="""
function reps(n){for(var k=0;k<3;k++)o('r'+k,k<n?1:0)}
function edges(n){for(var k=0;k<3;k++)o('e'+k,k<n?1:0)}
function base(){o('user',1);o('gw',0);o('mesh',0);o('ctl',0);reps(0);edges(0);
  o('a1',0);o('a2',0);o('pkt',0);o('sched',0);o('msg',0);tx('mt','');tx('mt2','');
  for(var k=0;k<3;k++)tx('rs'+k,'healthy');
  mv('pkt',72,147)}
var S=[
{c:'A platform does not run one copy of a model. It runs many replicas of many services — and every one of them needs retries, timeouts, health checks, TLS and routing.',
 a:function(){reps(3)}},
{c:'Writing all of that <b>inside every application</b> means the same logic duplicated everywhere, implemented slightly differently each time, and impossible to change centrally.',
 a:function(){reps(3);o('msg',1);tx('mt','the naive answer: every service does its own networking');tx('mt2','duplicated, inconsistent, unchangeable')}},
{c:'A <b>service mesh</b> pulls that logic out of the applications and into infrastructure. A proxy — usually <b>Envoy</b> — sits beside each service and handles the traffic. This is the <b>data plane</b>.',
 a:function(){o('gw',1);o('mesh',1);reps(3);o('a1',1);o('a2',1)}},
{c:'A <b>control plane</b> — usually <b>Istio</b> — configures all those proxies from one place. Change a routing rule once and every proxy picks it up. The applications just make ordinary calls.',
 a:function(){o('gw',1);o('mesh',1);o('ctl',1);reps(3);o('a1',1);o('a2',1)}},
{c:'Now a request arrives. The gateway hands it to the mesh, which picks a <b>healthy replica</b> and forwards it. Health checking, retry and failover all happen here, not in your code.',
 a:function(){o('gw',1);o('mesh',1);o('ctl',1);reps(3);edges(3);o('a1',1);o('a2',1);
   o('pkt',1);mv('pkt',372,147)}},
{c:'If a replica goes unhealthy the mesh simply stops sending to it. No application had to know.',
 a:function(){o('mesh',1);o('ctl',1);reps(3);edges(3);o('pkt',1);mv('pkt',599,90);
   tx('rs1','unhealthy — skipped');o('msg',1);tx('mt','failover without touching application code');tx('mt2','')}},
{c:'<b>And here is where the mesh stops.</b> Once the request is inside a replica, an entirely different scheduler takes over — deciding which requests share the next decode iteration and which KV blocks to allocate. The mesh has no idea any of that exists.',
 a:function(){o('mesh',1);reps(3);edges(3);o('sched',1);o('pkt',1);mv('pkt',599,90)}},
{c:'<b>The line to say:</b> a service mesh routes <i>between services</i>; the inference scheduler decides execution <i>inside one replica</i>. Different granularities — requests versus tokens. The mesh also knows nothing about what makes an LLM request expensive, which is exactly why LLM-aware routing has to be added on top.',
 a:function(){o('mesh',1);reps(3);o('sched',1);o('msg',1);
   tx('mt','requests between services  vs  tokens inside one');tx('mt2','the mesh is necessary, but not LLM-aware')}}
];
"""
build("service-mesh.html","Service mesh — routing between services",
      "Where the network layer stops and the inference engine begins.",svg,js,"0 0 840 366")

# ---------------- LLM-AWARE LOAD BALANCING ----------------
svg=f'''<g id="req" class="mv fd"><rect width="150" height="46" rx="7" fill="{A_F}" stroke="{A_S}" stroke-width="1.5"/>
<text x="75" y="20" class="tiny" text-anchor="middle" font-weight="650">new request</text>
<text x="75" y="36" class="tiny" text-anchor="middle">15K shared prefix + 100 new</text></g>
<g id="lb" class="fd"><rect x="252" y="120" width="130" height="52" rx="8" fill="{B_F}" stroke="{B_S}" stroke-width="1.5"/>
<text x="317" y="142" class="tiny" text-anchor="middle" font-weight="650">load balancer</text>
<text x="317" y="158" class="tiny" text-anchor="middle" id="lbmode">least connections</text></g>'''
SV=[("A",56,"5 active · 70% used","holds the 15K prefix",G_F,G_S),("B",196,"2 active · 40% used","no useful cache",N_F,N_S)]
for i,(nm,y,l1,l2,f,s) in enumerate(SV):
    svg+=f'''<g id="sv{i}" class="fd"><rect x="470" y="{y}" width="200" height="80" rx="9" fill="{f}" stroke="{s}" stroke-width="1.4"/>
<text x="570" y="{y+24}" class="tiny" text-anchor="middle" font-weight="650">replica {nm}</text>
<text x="570" y="{y+44}" class="tiny" text-anchor="middle">{l1}</text>
<text x="570" y="{y+62}" class="tiny" text-anchor="middle" id="sc{i}">{l2}</text></g>
<g id="pa{i}" class="fd"><path d="M382,146 C426,146 426,{y+40} 470,{y+40}" stroke="{N_S}" stroke-width="1.6" fill="none" marker-end="url(#am2)"/></g>'''
svg+=f'''<g id="sig" class="fd"><text x="150" y="228" class="lbl-b">Signals a router can actually see</text>'''
SIG=["queue depth / active requests","GPU + KV-cache pressure","prompt length → prefill cost","estimated output length","prefix-cache affinity"]
for i,t in enumerate(SIG):
    svg+=f'<g id="sg{i}" class="fd"><rect x="24" y="{242+i*26}" width="250" height="20" rx="5" fill="#fff" stroke="{N_S}" stroke-width="1"/><text x="34" y="{256+i*26}" class="tiny">{t}</text></g>'
svg+='</g>'
svg+=f'''<g id="cost" class="fd"><text x="340" y="318" class="lbl-b">Expected cost of serving it here</text>
<text x="330" y="344" class="tiny" text-anchor="end">replica A</text>
<rect x="340" y="332" width="300" height="15" rx="7" fill="#F1F1F4"/>
<g id="cbA" transform="translate(340,332) scale(0,1)"><rect width="300" height="15" rx="7" fill="{G_S}"/></g>
<text x="652" y="344" class="tiny" id="ctA"></text>
<text x="330" y="374" class="tiny" text-anchor="end">replica B</text>
<rect x="340" y="362" width="300" height="15" rx="7" fill="#F1F1F4"/>
<g id="cbB" transform="translate(340,362) scale(0,1)"><rect width="300" height="15" rx="7" fill="{R_S}"/></g>
<text x="652" y="374" class="tiny" id="ctB"></text></g>
<g id="hot" class="fd"><text x="420" y="404" class="lbl-b" text-anchor="middle" fill="#B36A6A" id="ht"></text></g>
<defs><marker id="am2" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0,1 L9,5 L0,9 z" fill="{N_S}"/></marker></defs>'''
js="""
function bar(id,y,s,t,lab){$(id).setAttribute('transform','translate(340,'+y+') scale('+s+',1)');tx(t,lab)}
function sigs(n){o('sig',n>0?1:0);for(var k=0;k<5;k++)o('sg'+k,k<n?1:0)}
function base(){o('req',1);mv('req',24,124);o('lb',0);o('sv0',0);o('sv1',0);o('pa0',0);o('pa1',0);
  sigs(0);o('cost',0);o('hot',0);tx('ht','');tx('lbmode','least connections');
  tx('sc0','holds the 15K prefix');tx('sc1','no useful cache');
  bar('cbA',332,0,'ctA','');bar('cbB',362,0,'ctB','')}
var S=[
{c:'Two replicas, one incoming request. An ordinary load balancer has to choose — and it assumes, as web balancers always have, that <b>requests cost about the same</b>.',
 a:function(){o('lb',1);o('sv0',1);o('sv1',1)}},
{c:'For LLMs that assumption is badly wrong. Prompt length, output length, prefill versus decode cost, KV pressure and cache locality all vary enormously between two requests that look <b>identical on arrival</b>.',
 a:function(){o('lb',1);o('sv0',1);o('sv1',1);o('sig',1);sigs(0)}},
{c:'By connection count the answer is obvious: <b>replica B</b> is half as busy. That is what least-connections picks.',
 a:function(){o('lb',1);o('sv0',1);o('sv1',1);o('pa1',1);mv('req',24,124)}},
{c:'But look at what the request actually is — a <b>15K-token prefix</b> plus 100 new tokens. And replica A already holds that prefix in its KV cache.',
 a:function(){o('lb',1);o('sv0',1);o('sv1',1);tx('sc0','✓ already holds this exact prefix');tx('sc1','✗ would prefill all 15K')}},
{c:'Now compare <b>expected cost</b> rather than load. On A the prefix is reused and only 100 tokens are prefilled. On B all 15,100 tokens must be processed from scratch. The busier replica is dramatically cheaper.',
 a:function(){o('lb',1);o('sv0',1);o('sv1',1);o('cost',1);
   bar('cbA',332,.12,'ctA','reuse the cache');bar('cbB',362,1,'ctB','full 15K prefill');
   tx('sc0','✓ already holds this exact prefix');tx('sc1','✗ would prefill all 15K')}},
{c:'So an <b>LLM-aware</b> router scores replicas on signals a web balancer never needed — above all <b>prefix-cache affinity</b>: does this replica already hold KV this request can reuse?',
 a:function(){o('lb',1);tx('lbmode','expected serving cost');o('sv0',1);o('sv1',1);sigs(5)}},
{c:'And it routes to <b>A</b> — the busier one.',
 a:function(){o('lb',1);tx('lbmode','expected serving cost');o('sv0',1);o('sv1',1);o('pa0',1);sigs(5);
   o('cost',1);bar('cbA',332,.12,'ctA','chosen');bar('cbB',362,1,'ctB','')}},
{c:'<b>The honest caveat.</b> If every request with that prefix routes to A, A becomes a hotspot while B idles. Cache affinity <i>fights</i> plain load balancing, so real routers blend the two and fall back once a replica saturates.',
 a:function(){o('lb',1);o('sv0',1);o('sv1',1);o('pa0',1);tx('sc0','⚠ now saturating');
   o('hot',1);tx('ht','affinity concentrates load — blend it with pressure, or you build a hotspot')}},
{c:'<b>The line to say:</b> the least-busy server is not always the cheapest server. Route on <b>estimated total serving cost</b>, not request count — and cache locality is often the single largest term in that estimate.',
 a:function(){o('lb',1);tx('lbmode','expected serving cost');o('sv0',1);o('sv1',1);sigs(5);
   o('cost',1);bar('cbA',332,.12,'ctA','');bar('cbB',362,1,'ctB','')}}
];
"""
build("load-balancing.html","LLM-aware load balancing — why the busiest replica can be the cheapest",
      "Routing on expected serving cost instead of connection count.",svg,js,"0 0 840 420")
print("ok")
