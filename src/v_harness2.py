from shell import build
B_F,B_S="#E3EDF9","#A9C4E4"; G_F,G_S="#E2EFE3","#A8CBAC"
A_F,A_S="#FBEBD2","#E2BC85"; N_F,N_S="#F1F1F4","#D5D5DC"; R_F,R_S="#F7DADA","#DF9C9C"; P_F,P_S="#F7E4EC","#DFAFC3"

# ---------------- CONTEXT COMPACTION ----------------
svg=f'<text x="24" y="30" class="lbl-b">Prompt size, step by step</text>\n'
for k in range(14):
    x=44+k*40
    svg+=f'<g id="b{k}" class="mv fd" transform="translate({x},186) scale(1,0)"><rect x="0" y="-150" width="30" height="150" rx="3" fill="{B_F}" stroke="{B_S}" stroke-width="1.1"/></g>'
svg+=f'''<path d="M36,186 L620,186" stroke="#C2C2CB" stroke-width="1.2"/>
<path d="M36,186 L36,40" stroke="#C2C2CB" stroke-width="1.2"/>
<g id="thresh" class="fd"><path d="M36,106 L620,106" stroke="{A_S}" stroke-width="1.5" stroke-dasharray="5 4"/>
<text x="628" y="110" class="tiny" fill="#8A6D3B">threshold</text></g>
<text x="330" y="204" class="tiny" text-anchor="middle">ReAct step →</text>
<g id="sum" class="fd"><rect x="648" y="44" width="182" height="120" rx="9" fill="{A_F}" stroke="{A_S}" stroke-width="1.4"/>
<text x="739" y="66" class="tiny" text-anchor="middle" font-weight="650">a separate model call</text>
<text x="739" y="86" class="tiny" text-anchor="middle">own system prompt, no tools</text>
<text x="739" y="104" class="tiny" text-anchor="middle">reads the prefix as text</text>
<text x="739" y="122" class="tiny" text-anchor="middle">writes working memory</text>
<text x="739" y="146" class="tiny" text-anchor="middle" font-weight="650" id="sn"></text></g>
<g id="keep" class="fd"><rect x="24" y="222" width="290" height="96" rx="9" fill="{G_F}" stroke="{G_S}" stroke-width="1.3"/>
<text x="169" y="244" class="tiny" text-anchor="middle" font-weight="650">what the summary must preserve</text>
<text x="169" y="264" class="tiny" text-anchor="middle">objective · constraints · files · commands</text>
<text x="169" y="282" class="tiny" text-anchor="middle">edits · concrete results · blockers · next action</text>
<text x="169" y="304" class="tiny" text-anchor="middle" font-weight="650" fill="#4E7A57">and the approaches that failed</text></g>
<g id="tbl" class="fd"><rect x="336" y="222" width="494" height="96" rx="9" fill="#fff" stroke="{N_S}"/>
<text x="583" y="242" class="tiny" text-anchor="middle" font-weight="650">same model, same task, 200-step budget</text>'''
ROWS=[("total tokens","221,187","475,642"),("peak prompt","5,974","24,463"),("prompt cached","57%","70%")]
svg+=f'<text x="470" y="262" class="tiny" text-anchor="middle" font-weight="650">compacted</text><text x="620" y="262" class="tiny" text-anchor="middle" font-weight="650">full context</text>'
for i,(a,b,c) in enumerate(ROWS):
    y=280+i*16
    svg+=f'<text x="356" y="{y}" class="tiny">{a}</text><text x="470" y="{y}" class="tiny" text-anchor="middle">{b}</text><text x="620" y="{y}" class="tiny" text-anchor="middle">{c}</text>'
svg+=f'<text x="760" y="288" class="tiny" text-anchor="middle" id="tn"></text></g>'
svg+=f'''<g id="msg" class="fd"><text x="424" y="344" class="lbl-b" text-anchor="middle" id="mt"></text>
<text x="424" y="362" class="tiny" text-anchor="middle" id="mt2"></text></g>'''
js="""
function bars(spec){for(var k=0;k<14;k++){
  var h=spec[k]===undefined?0:spec[k];
  $('b'+k).setAttribute('transform','translate('+(44+k*40)+',186) scale(1,'+h+')');
  var c=h>0.54?['#FBEBD2','#E2BC85']:['#E3EDF9','#A9C4E4'];
  $('b'+k).firstChild.setAttribute('fill',c[0]);$('b'+k).firstChild.setAttribute('stroke',c[1])}}
function ramp(n,start,step){var a=[];for(var k=0;k<n;k++)a.push(Math.min(1,start+k*step));return a}
function base(){bars([]);o('thresh',0);o('sum',0);o('keep',0);o('tbl',0);o('msg',0);
  tx('mt','');tx('mt2','');tx('sn','');tx('tn','')}
var S=[
{c:'Every step resends the whole transcript, so the prompt grows with each observation appended — roughly 600 tokens a step in one measured run.',
 a:function(){bars(ramp(6,.12,.09))}},
{c:'It never comes down. Total cost is therefore the <b>area under a rising line</b> — quadratic in run length — and eventually the context window ends the run outright.',
 a:function(){bars(ramp(14,.12,.07))}},
{c:'So set a <b>threshold</b>. When the estimated prompt crosses it, stop and do something about it before the next step.',
 a:function(){bars(ramp(14,.12,.07));o('thresh',1)}},
{c:'What happens then is the part people get wrong: the harness makes a <b>separate model call</b>, with its own system prompt and <b>no tools</b>, whose only job is to write a summary of the transcript so far.',
 a:function(){bars(ramp(7,.12,.07));o('thresh',1);o('sum',1);tx('sn','it costs an extra call — worth it')}},
{c:'That summary replaces the old prefix. The system and task messages stay <b>verbatim</b>, the most recent steps stay <b>verbatim</b>, and everything in between becomes one <code>working_memory</code> message.',
 a:function(){bars([.62,.14,.18,.22,.26,.3,.34].concat(ramp(0)));o('thresh',1);o('sum',1);
   tx('sn','prefix out, summary in')}},
{c:'The prompt drops, then climbs again, then compacts again. Five times across this run — a sawtooth instead of a ramp.',
 a:function(){bars([.2,.26,.32,.4,.48,.56,.64,.2,.28,.36,.44,.52,.6,.24]);o('thresh',1)}},
{c:'<b>What the summary is told to preserve is the whole design.</b> Objective, files, commands, edits, concrete results, blockers, next action — and, crucially, <b>the approaches that already failed</b>. Drop those and the agent cheerfully retries what it ruled out an hour ago.',
 a:function(){bars([.2,.26,.32,.4,.48,.56,.64,.2,.28,.36,.44,.52,.6,.24]);o('keep',1)}},
{c:'Measured on a real SWE-bench instance: <b>half the tokens and a quarter of the peak prompt</b> — while taking five <i>more</i> steps and paying for five extra summariser calls. Both runs produced a patch that resolved the issue.',
 a:function(){bars([.2,.26,.32,.4,.48,.56,.64,.2,.28,.36,.44,.52,.6,.24]);o('tbl',1)}},
{c:'<b>But here is the honest caveat.</b> A prompt that only grows at the tail is a perfect cache workload — every request is a prefix of the next. Rewriting memory near the <b>front</b> invalidates everything after it: cache hits fell from 70% to 57%.',
 a:function(){o('tbl',1);tx('tn','← the tension');o('msg',1);
   tx('mt','compaction fights prompt caching');
   tx('mt2','cached tokens are heavily discounted, so the real saving is smaller than the raw counts suggest')}},
{c:'One more silent failure worth knowing: <b>two of the five summaries were truncated</b> — they hit the summariser\\'s output cap mid-sentence and the tail was simply lost. The run still succeeded, which is exactly what makes it dangerous.',
 a:function(){o('keep',1);o('msg',1);
   tx('mt','check the summariser\\'s finish_reason');tx('mt2','“length” means your working memory was cut off and nobody told you')}},
{c:'<b>The line to say:</b> compaction is lossy by construction, so what the summary is <i>told</i> to keep is the design. And name the caching tension unprompted — it is the difference between having read the docs and having paid the bill.',
 a:function(){bars([.2,.26,.32,.4,.48,.56,.64,.2,.28,.36,.44,.52,.6,.24]);o('thresh',1);o('tbl',1)}}
];
"""
build("context-compaction.html","Context compaction — the sawtooth",
      "Rewriting history to cap the prompt, and the caching bill it quietly creates.",svg,js,"0 0 850 376")

# ---------------- OBSERVATION BUDGET ----------------
svg=f'''<text x="24" y="30" class="lbl-b">Three levers, three different questions</text>
<g id="l1" class="fd"><rect x="24" y="44" width="800" height="92" rx="10" fill="#FAFAFB" stroke="{N_S}"/>
<text x="42" y="66" class="tiny" font-weight="650">1 · one observation is enormous</text>
<text x="42" y="84" class="tiny">a cat of a large file, a full stack trace, a browser page</text>
<rect x="42" y="94" width="470" height="26" rx="4" fill="{R_F}" stroke="{R_S}" stroke-width="1.2" id="big"/>
<text x="277" y="111" class="tiny" text-anchor="middle">120,000 characters in one tool result</text>
<text x="600" y="112" class="tiny" font-weight="650" id="l1f"></text></g>
<g id="trunc" class="fd"><rect x="42" y="94" width="150" height="26" rx="4" fill="{G_F}" stroke="{G_S}" stroke-width="1.2"/>
<text x="117" y="111" class="tiny" text-anchor="middle">first 4,900</text>
<rect x="200" y="94" width="120" height="26" rx="4" fill="{N_F}" stroke="{N_S}" stroke-width="1.2" stroke-dasharray="3 2"/>
<text x="260" y="111" class="tiny" text-anchor="middle">… elided …</text>
<rect x="328" y="94" width="150" height="26" rx="4" fill="{G_F}" stroke="{G_S}" stroke-width="1.2"/>
<text x="403" y="111" class="tiny" text-anchor="middle">last 4,900</text></g>
<g id="l2" class="fd"><rect x="24" y="150" width="800" height="92" rx="10" fill="#FAFAFB" stroke="{N_S}"/>
<text x="42" y="172" class="tiny" font-weight="650">2 · many small observations pile up</text>
<text x="42" y="190" class="tiny">each one is reasonable; forty of them are not</text>'''
for k in range(12):
    svg+=f'<rect x="{42+k*38}" y="200" width="30" height="26" rx="3" fill="{B_F}" stroke="{B_S}" stroke-width="1.1" id="acc{k}"/>'
svg+=f'''<text x="600" y="218" class="tiny" font-weight="650" id="l2f"></text></g>
<g id="l3" class="fd"><rect x="24" y="256" width="800" height="104" rx="10" fill="#FAFAFB" stroke="{N_S}"/>
<text x="42" y="278" class="tiny" font-weight="650">3 · describing what the agent can do is itself expensive</text>
<text x="42" y="296" class="tiny">ten capabilities, each with a page of instructions</text>
<rect x="42" y="306" width="330" height="40" rx="5" fill="{A_F}" stroke="{A_S}" stroke-width="1.2" id="cat"/>
<text x="207" y="322" class="tiny" text-anchor="middle" font-weight="650" id="catt">catalogue — name + one line each</text>
<text x="207" y="338" class="tiny" text-anchor="middle" id="catn">two lines in every prompt</text>
<rect x="400" y="306" width="330" height="40" rx="5" fill="{N_F}" stroke="{N_S}" stroke-width="1.2" stroke-dasharray="3 2" id="body"/>
<text x="565" y="322" class="tiny" text-anchor="middle" font-weight="650" id="bodyt">the full body</text>
<text x="565" y="338" class="tiny" text-anchor="middle" id="bodyn">4,771 characters — loaded only when asked for</text>
<text x="760" y="330" class="tiny" font-weight="650" id="l3f"></text></g>'''
js="""
function acc(n){for(var k=0;k<12;k++){var e=$('acc'+k);if(e)e.style.opacity=k<n?1:0}}
function base(){o('l1',0);o('trunc',0);o('l2',0);o('l3',0);acc(0);
  tx('l1f','');tx('l2f','');tx('l3f','');o('big',1);
  tx('catt','catalogue \\u2014 name + one line each');tx('bodyn','4,771 characters \\u2014 loaded only when asked for')}
var S=[
{c:'Three different things can flood a context window, and each needs its own lever. Reaching for the wrong one is why “just summarise the history” is an incomplete answer.',
 a:function(){o('l1',1)}},
{c:'<b>First: a single observation can be enormous.</b> One <code>cat</code> of a large file or a full stack trace can swamp the whole prompt by itself.',
 a:function(){o('l1',1);tx('l1f','← this alone can end a run')}},
{c:'<b>Lever one: truncation</b> — cap a single result. But keep the <b>head and the tail</b>, not just the head: the end of a stack trace is usually the line that identifies the failure.',
 a:function(){o('l1',1);o('big',0);o('trunc',1);tx('l1f','bounded at 10,000 characters')}},
{c:'<b>Second: even well-behaved observations accumulate.</b> Each one is reasonable on its own; forty of them are the problem. Truncation does nothing about this — it bounds each item, not the pile.',
 a:function(){o('l1',1);o('trunc',1);o('l2',1);acc(12);tx('l2f','← truncation cannot help here')}},
{c:'<b>Lever two: compaction</b> — replace the old prefix with a written summary and keep recent steps verbatim. This is the lever that bounds accumulation.',
 a:function(){o('l2',1);acc(4);tx('l2f','← the prefix becomes one summary')}},
{c:'<b>Third, and the one people forget:</b> describing what the agent <i>can do</i> costs context too. Ten capabilities with a page of instructions each is ten pages in every single request — before any work happens.',
 a:function(){o('l3',1);tx('l3f','')}},
{c:'<b>Lever three: progressive disclosure.</b> Advertise each capability by name and one line; load the full instructions only when the model actually asks for them.',
 a:function(){o('l3',1);tx('l3f','← the split');tx('catt','always in the prompt');
   tx('bodyn','revealed on invoke_skill, and not before')}},
{c:'What that split buys is decisive: <b>capability count becomes independent of prompt size</b>. Ten skills cost ten lines, not ten documents — and the same reasoning applies to tool descriptions and documentation.',
 a:function(){o('l3',1);tx('l3f','← the point')}},
{c:'<b>The line to say:</b> truncation bounds one observation, compaction bounds their accumulation, progressive disclosure bounds what you carry <i>before</i> the work starts. They are complementary, not alternatives — naming all three is what separates a real answer from “summarise the history”.',
 a:function(){o('l1',1);o('trunc',1);o('l2',1);acc(4);o('l3',1)}}
];
"""
build("observation-budget.html","Three levers on the context budget",
      "Truncation, compaction and progressive disclosure answer different questions.",svg,js,"0 0 850 376")
print("ok")
