from shell import build
B_F,B_S="#E3EDF9","#A9C4E4"; G_F,G_S="#E2EFE3","#A8CBAC"
A_F,A_S="#FBEBD2","#E2BC85"; N_F,N_S="#F1F1F4","#D5D5DC"; R_F,R_S="#F7DADA","#DF9C9C"; P_F,P_S="#F7E4EC","#DFAFC3"
SYS,USR,AST,TOOL="#8A6410","#2F5F7E","#256A4A","#7A3468"
SYS_F,USR_F,AST_F,TOOL_F="#FBF2DE","#E6EFF5","#E4F0EA","#F6E6F1"

# ---------------- THE MESSAGE PROTOCOL ----------------
MSG=[("system","standing instructions",SYS_F,SYS),
     ("user","the task",USR_F,USR),
     ("assistant","call_1 · execute(ls)",AST_F,AST),
     ("tool","call_1 · listing",TOOL_F,TOOL),
     ("assistant","call_2 · execute(sed)",AST_F,AST),
     ("tool","call_2 · 10k of source",TOOL_F,TOOL),
     ("assistant","call_3 · execute(pytest)",AST_F,AST),
     ("tool","call_3 · test output",TOOL_F,TOOL)]
svg=f'<text x="24" y="30" class="lbl-b">The message list, rebuilt and resent every step</text>\n'
for i,(r,d,f,s) in enumerate(MSG):
    y=44+i*38
    svg+=f'''<g id="m{i}" class="fd"><rect x="28" y="{y}" width="392" height="30" rx="5" fill="{f}" stroke="{s}" stroke-width="1.2"/>
<text x="42" y="{y+19}" class="tiny" font-weight="650" fill="{s}">{r}</text>
<text x="128" y="{y+19}" class="tiny">{d}</text></g>'''
svg+=f'''<g id="link" class="fd">
<path d="M420,139 C448,139 448,177 420,177" stroke="{TOOL}" stroke-width="1.6" fill="none"/>
<text x="458" y="163" class="tiny" fill="{TOOL}">tool_call_id ties them together</text></g>
<g id="rules" class="fd"><rect x="470" y="44" width="352" height="126" rx="9" fill="#fff" stroke="{N_S}"/>
<text x="646" y="66" class="tiny" text-anchor="middle" font-weight="650">the rules the API enforces</text>'''
for i,t in enumerate(["exactly one system message, first",
                      "user poses the task before any assistant turn",
                      "every assistant tool call must be answered",
                      "each tool message carries the id it answers"]):
    svg+=f'<text x="490" y="{90+i*20}" class="tiny">· {t}</text>'
svg+=f'''</g>
<g id="badcut" class="fd"><path d="M24,158 L424,158" stroke="{R_S}" stroke-width="2" stroke-dasharray="6 4"/>
<text x="430" y="154" class="tiny" fill="#B36A6A" font-weight="650">cut here</text>
<rect x="470" y="196" width="352" height="82" rx="9" fill="{R_F}" stroke="{R_S}" stroke-width="1.3"/>
<text x="646" y="218" class="tiny" text-anchor="middle" font-weight="650" fill="#B36A6A">400 — request rejected</text>
<text x="646" y="238" class="tiny" text-anchor="middle">call_1 was answered, but its assistant</text>
<text x="646" y="256" class="tiny" text-anchor="middle">message is gone — the tool reply is an orphan</text></g>
<g id="goodcut" class="fd"><path d="M24,196 L424,196" stroke="{G_S}" stroke-width="2" stroke-dasharray="6 4"/>
<text x="430" y="192" class="tiny" fill="#4E7A57" font-weight="650">cut here</text>
<rect x="470" y="196" width="352" height="82" rx="9" fill="{G_F}" stroke="{G_S}" stroke-width="1.3"/>
<text x="646" y="218" class="tiny" text-anchor="middle" font-weight="650" fill="#4E7A57">valid</text>
<text x="646" y="238" class="tiny" text-anchor="middle">the cut lands on an assistant boundary, so</text>
<text x="646" y="256" class="tiny" text-anchor="middle">no call is separated from its observation</text></g>
<g id="stateless" class="fd"><rect x="470" y="196" width="352" height="82" rx="9" fill="#fff" stroke="{N_S}" stroke-dasharray="3 3"/>
<text x="646" y="220" class="tiny" text-anchor="middle" font-weight="650">the model remembers nothing</text>
<text x="646" y="240" class="tiny" text-anchor="middle">everything it knows at step 40 is in the list</text>
<text x="646" y="258" class="tiny" text-anchor="middle">you hand it at step 40</text></g>
<g id="cost" class="fd"><rect x="470" y="196" width="352" height="82" rx="9" fill="{A_F}" stroke="{A_S}" stroke-width="1.3"/>
<text x="646" y="220" class="tiny" text-anchor="middle" font-weight="650">one measured run</text>
<text x="646" y="240" class="tiny" text-anchor="middle">463,000 prompt tokens · 13,000 completion</text>
<text x="646" y="258" class="tiny" text-anchor="middle">the bill is for re-reading, not for thinking</text></g>'''
js="""
function msgs(n){for(var k=0;k<8;k++)o('m'+k,k<n?1:0)}
function base(){msgs(0);o('link',0);o('rules',0);o('badcut',0);o('goodcut',0);o('stateless',0);o('cost',0)}
var S=[
{c:'A chat completion is <b>stateless</b>: text in, text out. It cannot remember the last step, and it has no access to anything that happened before.',
 a:function(){msgs(2);o('stateless',1)}},
{c:'So the harness rebuilds the <b>entire message list</b> and resends it every single step. That one fact drives almost every design decision that follows.',
 a:function(){msgs(4);o('stateless',1)}},
{c:'Four roles, in a sequence the API enforces. <b>system</b> carries standing instructions, <b>user</b> poses the task, <b>assistant</b> carries the model\\'s text and its tool calls, and <b>tool</b> carries exactly one observation.',
 a:function(){msgs(8);o('rules',1)}},
{c:'The detail that matters more than it looks: each <b>tool</b> message carries the <code>tool_call_id</code> of the call it answers. It is not bookkeeping — it is structural.',
 a:function(){msgs(8);o('link',1);o('rules',1)}},
{c:'Two consequences. <b>Every tool call must be answered</b>, even a malformed one — otherwise the next request is invalid. This is why a broken call returns an error string rather than raising.',
 a:function(){msgs(8);o('link',1);o('rules',1)}},
{c:'And you <b>cannot cut the history at an arbitrary index</b>. Slice between an assistant message and its tool reply and the observation is orphaned — the API rejects the whole request.',
 a:function(){msgs(8);o('badcut',1)}},
{c:'The cut has to land on an <b>assistant boundary</b>, keeping every call paired with its observation. That constraint is what shapes how context compaction can work at all.',
 a:function(){msgs(8);o('goodcut',1)}},
{c:'And because every step resends everything, cost is the <b>area under a rising curve</b> — quadratic in run length, not linear. In one measured coding run: 463k prompt tokens against 13k of completion.',
 a:function(){msgs(8);o('cost',1)}},
{c:'<b>The line to say:</b> the prompt <i>is</i> the state, and the state is a budget. Memory, persistence and continuity are all properties of the list you rebuild — none of them live in the model.',
 a:function(){msgs(8);o('link',1);o('cost',1)}}
];
"""
build("message-protocol.html","The prompt is the state",
      "Four roles, one structural rule, and why you cannot cut history anywhere you like.",svg,js,"0 0 850 372")

# ---------------- ERROR POLICY ----------------
svg=f'''<text x="24" y="30" class="lbl-b">Two classes of failure, and only two</text>
<g id="c1" class="fd"><rect x="28" y="44" width="380" height="104" rx="10" fill="{G_F}" stroke="{G_S}" stroke-width="1.4"/>
<text x="218" y="68" class="tiny" text-anchor="middle" font-weight="650">the model can fix this</text>
<text x="218" y="90" class="tiny" text-anchor="middle">bad arguments · malformed JSON · unknown tool</text>
<text x="218" y="108" class="tiny" text-anchor="middle">illegal move · failing test · non-zero exit</text>
<text x="218" y="132" class="tiny" text-anchor="middle" font-weight="650" fill="#4E7A57">→ return it as an observation</text></g>
<g id="c2" class="fd"><rect x="440" y="44" width="380" height="104" rx="10" fill="{R_F}" stroke="{R_S}" stroke-width="1.4"/>
<text x="630" y="68" class="tiny" text-anchor="middle" font-weight="650">nothing can fix this</text>
<text x="630" y="90" class="tiny" text-anchor="middle">the sandbox is gone · credentials revoked</text>
<text x="630" y="108" class="tiny" text-anchor="middle">the environment no longer exists</text>
<text x="630" y="132" class="tiny" text-anchor="middle" font-weight="650" fill="#B36A6A">→ terminate with a clear message</text></g>
<text x="24" y="188" class="lbl-b" id="scen">A recoverable failure, handled correctly</text>'''
for k in range(8):
    x=32+k*98
    svg+=f'''<g id="s{k}" class="fd"><rect x="{x}" y="204" width="86" height="34" rx="5" fill="{N_F}" stroke="{N_S}" stroke-width="1.2"/>
<text x="{x+43}" y="219" class="tiny" text-anchor="middle" id="st{k}"></text>
<text x="{x+43}" y="232" class="tiny" text-anchor="middle" id="su{k}"></text></g>'''
svg+=f'''<g id="dots" class="fd"><text x="440" y="260" class="tiny" text-anchor="middle" id="dt"></text></g>
<g id="meter" class="fd"><text x="24" y="300" class="tiny">tokens burned</text>
<rect x="128" y="288" width="480" height="16" rx="8" fill="#F1F1F4"/>
<g id="mb" transform="translate(128,288) scale(0,1)"><rect width="480" height="16" rx="8" fill="{R_S}"/></g>
<text x="622" y="301" class="tiny" id="mt"></text></g>
<g id="code" class="fd"><rect x="24" y="324" width="800" height="58" rx="8" fill="#fff" stroke="{N_S}"/>
<text x="40" y="344" class="tiny" font-weight="650" id="k1"></text>
<text x="40" y="364" class="tiny" id="k2"></text></g>'''
js="""
function steps(arr,col){for(var k=0;k<8;k++){
  var on=k<arr.length;o('s'+k,on?1:0);
  if(on){var e=$('s'+k);var c=arr[k][2]||'n';
    var F={n:['#F1F1F4','#D5D5DC'],g:['#E2EFE3','#A8CBAC'],r:['#F7DADA','#DF9C9C'],a:['#FBEBD2','#E2BC85']}[c];
    e.firstChild.setAttribute('fill',F[0]);e.firstChild.setAttribute('stroke',F[1]);
    tx('st'+k,arr[k][0]);tx('su'+k,arr[k][1])}}}
function meter(s,t){o('meter',1);$('mb').setAttribute('transform','translate(128,288) scale('+s+',1)');tx('mt',t)}
function base(){o('c1',0);o('c2',0);steps([]);o('dots',0);tx('dt','');o('meter',0);o('code',0);
  tx('k1','');tx('k2','');tx('scen','A recoverable failure, handled correctly');
  $('mb').setAttribute('transform','translate(128,288) scale(0,1)')}
var S=[
{c:'Every failure an agent hits falls into one of two classes, and the entire error policy follows from which one you are looking at.',
 a:function(){o('c1',1)}},
{c:'<b>Failures the model can fix</b> must come back as <b>observations</b>, not exceptions. Bad arguments, an illegal move, a failing test — the model reads the error and corrects itself on the next step.',
 a:function(){o('c1',1);o('code',1);
   tx('k1','every failure path returns a string, never raises');
   tx('k2','except json.JSONDecodeError as exc:  return format_tool_output({"error": f"not valid JSON ({exc})"})')}},
{c:'In practice that looks like this: an illegal move comes back tagged, the model sees why, and it plays a legal one. Two steps, problem solved.',
 a:function(){o('c1',1);steps([['e4','played','g'],['Qh9','illegal','r'],['reads','the error','a'],['Nf3','played','g']])}},
{c:'<b>But the other class exists too</b>, and forgetting it is expensive. Some failures no amount of model cleverness can repair.',
 a:function(){o('c1',1);o('c2',1)}},
{c:'Here is what happened when they were not distinguished. A sandbox hit its 30-minute lifetime and was reclaimed mid-game. Every subsequent tool call returned a transport error — correctly formatted as a <i>recoverable</i> observation.',
 a:function(){o('c2',1);tx('scen','The same policy applied to a failure nothing can fix');
   steps([['move','ok','g'],['sandbox','dies','r'],['error','observed','a'],['retry','fails','r']])}},
{c:'So the model dutifully tried again. And again. <b>165 steps</b> of retrying, each one resending a 100,000-token prompt, until the step limit finally stopped it.',
 a:function(){tx('scen','The same policy applied to a failure nothing can fix');
   steps([['retry','fails','r'],['retry','fails','r'],['retry','fails','r'],['retry','fails','r'],
          ['retry','fails','r'],['retry','fails','r'],['retry','fails','r'],['retry','fails','r']]);
   o('dots',1);tx('dt','… 165 steps, 22 moves actually played …');
   meter(1,'17.1M tokens burned')}},
{c:'<b>The fix is a termination condition.</b> On a transport failure, ask the environment whether it is still alive — and if it is not, abort with a clear message instead of handing the model something it cannot act on.',
 a:function(){o('c2',1);tx('scen','With a termination condition');
   steps([['move','ok','g'],['sandbox','dies','r'],['health','check','a'],['abort','1 step','g']]);
   meter(.04,'the same failure now costs one step');o('code',1);
   tx('k1','on transport failure: probe the environment before returning it as recoverable');
   tx('k2','plus a consecutive-failure backstop — and a success resets the counter')}},
{c:'Note the backstop matters as much as the probe: five consecutive failures should abort even if the health check itself lies. And <b>recoverable failures must never count toward it</b> — an illegal move is not evidence the world is broken.',
 a:function(){o('c1',1);o('c2',1);o('code',1);
   tx('k1','illegal moves never increment the counter · any success resets it');
   tx('k2','otherwise a merely clumsy agent gets killed for being clumsy')}},
{c:'<b>The line to say:</b> graceful degradation <i>without</i> a termination condition is an expensive infinite loop. Every retry policy needs to separate “the model can fix this” from “nothing can fix this” — and cost per retry is what makes it urgent rather than tidy.',
 a:function(){o('c1',1);o('c2',1);meter(.04,'one step instead of 165')}}
];
"""
build("error-policy.html","Error policy — recoverable, or terminal",
      "The two classes of failure, and the 17-million-token lesson in confusing them.",svg,js,"0 0 850 396")
print("ok")
