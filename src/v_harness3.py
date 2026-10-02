from shell import build
B_F,B_S="#E3EDF9","#A9C4E4"; G_F,G_S="#E2EFE3","#A8CBAC"
A_F,A_S="#FBEBD2","#E2BC85"; N_F,N_S="#F1F1F4","#D5D5DC"; R_F,R_S="#F7DADA","#DF9C9C"; P_F,P_S="#F7E4EC","#DFAFC3"

svg=f'''<text x="24" y="30" class="lbl-b" id="lt">One tool call per round trip</text>
<g id="rt" class="fd">'''
for k in range(7):
    y=44+k*40
    svg+=f'''<g id="r{k}" class="fd"><rect x="28" y="{y}" width="92" height="30" rx="5" fill="{B_F}" stroke="{B_S}" stroke-width="1.2"/>
<text x="74" y="{y+19}" class="tiny" text-anchor="middle">model</text>
<path d="M120,{y+15} L152,{y+15}" stroke="{N_S}" stroke-width="1.2" marker-end="url(#pa)"/>
<rect x="156" y="{y}" width="112" height="30" rx="5" fill="{A_F}" stroke="{A_S}" stroke-width="1.2"/>
<text x="212" y="{y+19}" class="tiny" text-anchor="middle" id="rc{k}">simulate_move</text>
<path d="M268,{y+15} L300,{y+15}" stroke="{N_S}" stroke-width="1.2" marker-end="url(#pa)"/>
<rect x="304" y="{y}" width="92" height="30" rx="5" fill="{G_F}" stroke="{G_S}" stroke-width="1.2"/>
<text x="350" y="{y+19}" class="tiny" text-anchor="middle">result</text>
<path d="M396,{y+15} C420,{y+15} 420,{y+55} 74,{y+55} L74,{y+40}" stroke="{N_S}" stroke-width="1" fill="none" stroke-dasharray="3 3"/></g>'''
svg+=f'''</g>
<g id="ell" class="fd"><text x="212" y="330" class="tiny" text-anchor="middle" id="et"></text></g>
<g id="cost" class="fd"><text x="28" y="356" class="tiny">whole prompt resent</text>
<rect x="152" y="344" width="244" height="14" rx="7" fill="#F1F1F4"/>
<g id="cb" transform="translate(152,344) scale(0,1)"><rect width="244" height="14" rx="7" fill="{R_S}"/></g>
<text x="406" y="356" class="tiny" id="ct"></text></g>
<g id="code" class="fd"><rect x="440" y="44" width="390" height="196" rx="9" fill="#fff" stroke="{B_S}" stroke-width="1.4"/>
<text x="458" y="66" class="tiny" font-weight="650">one step · run_python</text>'''
CODE=["best = None","for mv in board.legal_moves():","    after = simulate_move(mv)","    for reply in after.legal_moves():",
      "        score = evaluate(simulate_move(reply))","        … keep the worst case for this mv …",
      "    if better(mv): best = mv","play_move(best)"]
for i,l in enumerate(CODE):
    svg+=f'<text x="458" y="{88+i*18}" class="tiny mono" fill="{"#4E7A57" if i==7 else "#2B2B30"}">{l}</text>'
svg+=f'''<text x="635" y="232" class="tiny" text-anchor="middle" id="cn"></text></g>
<g id="win" class="fd"><rect x="440" y="256" width="390" height="46" rx="9" fill="{G_F}" stroke="{G_S}" stroke-width="1.3"/>
<text x="635" y="276" class="tiny" text-anchor="middle" font-weight="650">21 round trips → 1 step</text>
<text x="635" y="293" class="tiny" text-anchor="middle">the tools ran 21 times; the model was called once</text></g>
<g id="risk" class="fd"><rect x="440" y="314" width="390" height="60" rx="9" fill="{R_F}" stroke="{R_S}" stroke-width="1.3"/>
<text x="635" y="334" class="tiny" text-anchor="middle" font-weight="650" fill="#B36A6A">you are now running model-written code</text>
<text x="635" y="352" class="tiny" text-anchor="middle">it belongs in the sandbox, beside the tools —</text>
<text x="635" y="368" class="tiny" text-anchor="middle">never in the agent process</text></g>
<defs><marker id="pa" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0,1 L9,5 L0,9 z" fill="{N_S}"/></marker></defs>'''
js="""
function trips(n){o('rt',n>0?1:0);for(var k=0;k<7;k++)o('r'+k,k<n?1:0)}
function cost(s,t){o('cost',1);$('cb').setAttribute('transform','translate(152,344) scale('+s+',1)');tx('ct',t)}
function base(){trips(0);o('ell',0);tx('et','');o('cost',0);o('code',0);o('win',0);o('risk',0);
  tx('cn','');tx('lt','One tool call per round trip');
  $('cb').setAttribute('transform','translate(152,344) scale(0,1)')}
var S=[
{c:'The default contract is one tool call per model response. The model asks, the harness executes, the observation comes back, and the next step begins.',
 a:function(){trips(2)}},
{c:'Now give it something that needs <b>search</b>. A two-ply look-ahead over twenty candidate moves means twenty <code>simulate_move</code> calls and then one <code>play_move</code>.',
 a:function(){trips(7);o('ell',1);tx('et','… and so on, twenty times …')}},
{c:'That is <b>21 round trips</b>, and each one is a full model call that resends the entire transcript. The thinking is trivial; the transport is the whole bill.',
 a:function(){trips(7);o('ell',1);tx('et','… 21 round trips …');cost(1,'21 times')}},
{c:'Worse, it caps what the agent can attempt. A procedure too long to spell out as individual calls simply cannot be run — the <b>unit of work is the call</b>, and that is the ceiling.',
 a:function(){trips(7);o('ell',1);tx('et','… and a deeper search is simply out of reach …');cost(1,'21 times')}},
{c:'<b>So let the model write code instead.</b> Inside a sandbox beside the tools, they are ordinary functions — so a snippet can call them in a loop, branch on results, and commit only the final choice.',
 a:function(){o('code',1);tx('lt','The model writes code that composes the tools')}},
{c:'One step. The snippet ran <code>simulate_move</code> twenty times, evaluated the replies, and called <code>play_move</code> exactly once as its last statement. <b>The tools ran 21 times; the model was called once.</b>',
 a:function(){o('code',1);o('win',1);cost(.05,'once');tx('lt','The model writes code that composes the tools')}},
{c:'What changed is the <b>unit of work</b>: from a call to a procedure. Loops, branching and search stop costing a round trip each, which makes depths of search that were previously unreachable simply routine.',
 a:function(){tx('lt','The model writes code that composes the tools');o('code',1);o('win',1);tx('cn','the unit of work is now a procedure, not a call')}},
{c:'<b>The cost is real, though.</b> You are executing code the model wrote, against live state. It belongs in the sandbox next to the tools, never in the agent process — and the harness must <b>re-read the world afterwards</b>, because the snippet may already have changed it.',
 a:function(){tx('lt','The model writes code that composes the tools');o('code',1);o('risk',1)}},
{c:'<b>The line to say:</b> programmatic tool calling changes the unit of work from a call to a procedure. It is the difference between an agent that can take twenty actions and one that can run an algorithm — paid for with a sandbox and a re-read.',
 a:function(){tx('lt','The model writes code that composes the tools');o('code',1);o('win',1);o('risk',1)}}
];
"""
build("programmatic-tools.html","Programmatic tool calling",
      "When the model writes code that calls the tools, the unit of work stops being a round trip.",svg,js,"0 0 850 388")
print("ok")
