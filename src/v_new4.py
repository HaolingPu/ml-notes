from shell import build
B_F,B_S="#E3EDF9","#A9C4E4"; G_F,G_S="#E2EFE3","#A8CBAC"
A_F,A_S="#FBEBD2","#E2BC85"; N_F,N_S="#F1F1F4","#D5D5DC"; R_F,R_S="#F7DADA","#DF9C9C"; P_F,P_S="#F7E4EC","#DFAFC3"

# ---------------- AGENT CHECKPOINTING ----------------
svg=f'''<text x="24" y="32" class="lbl-b">Agent run</text>'''
for k in range(6):
    x=40+k*86
    svg+=f'''<g id="st{k}" class="fd"><rect x="{x}" y="48" width="72" height="34" rx="5" fill="{N_F}" stroke="{N_S}" stroke-width="1.2"/>
<text x="{x+36}" y="69" class="tiny" text-anchor="middle" id="stt{k}">step {k+1}</text></g>'''
svg+=f'''<g id="crash" class="fd"><path d="M{40+5*86+36},40 L{40+5*86+36},90" stroke="{R_S}" stroke-width="2.5"/>
<text x="{40+5*86+36}" y="32" class="tiny" text-anchor="middle" fill="#B36A6A">crash</text></g>
<g id="hist" class="fd"><rect x="570" y="44" width="250" height="42" rx="8" fill="#FAFAFB" stroke="{N_S}" stroke-dasharray="3 3"/>
<text x="695" y="62" class="tiny" text-anchor="middle" font-weight="650">conversation history</text>
<text x="695" y="78" class="tiny" text-anchor="middle" id="ht">the raw trace</text></g>
<g id="ckpt" class="fd"><rect x="40" y="112" width="360" height="150" rx="10" fill="{G_F}" stroke="{G_S}" stroke-width="1.5"/>
<text x="220" y="134" class="tiny" text-anchor="middle" font-weight="650">checkpoint \u2014 structured execution state</text>'''
ITEMS=["goal + plan","steps done / pending","key observations","artifacts touched","pending action + approval","environment refs"]
for i,t in enumerate(ITEMS):
    svg+=f'<text x="{60 if i%2==0 else 230}" y="{160+ (i//2)*26}" class="tiny" id="ck{i}">{t}</text>'
svg+=f'''<text x="220" y="246" class="tiny" text-anchor="middle" id="ckn"></text></g>
<g id="mem" class="fd"><rect x="430" y="112" width="180" height="66" rx="9" fill="{B_F}" stroke="{B_S}" stroke-width="1.3"/>
<text x="520" y="134" class="tiny" text-anchor="middle" font-weight="650">memory</text>
<text x="520" y="152" class="tiny" text-anchor="middle">knowledge worth keeping</text>
<text x="520" y="168" class="tiny" text-anchor="middle">"this repo uses pnpm"</text></g>
<g id="ckres" class="fd"><rect x="430" y="192" width="180" height="70" rx="9" fill="{G_F}" stroke="{G_S}" stroke-width="1.3"/>
<text x="520" y="214" class="tiny" text-anchor="middle" font-weight="650">checkpoint</text>
<text x="520" y="232" class="tiny" text-anchor="middle">where to resume</text>
<text x="520" y="248" class="tiny" text-anchor="middle">"step 7 pending"</text></g>
<g id="sr" class="fd"><rect x="640" y="112" width="180" height="70" rx="9" fill="{A_F}" stroke="{A_S}" stroke-width="1.3"/>
<text x="730" y="134" class="tiny" text-anchor="middle" font-weight="650">snapshot vs replay</text>
<text x="730" y="152" class="tiny" text-anchor="middle">save state directly, or</text>
<text x="730" y="168" class="tiny" text-anchor="middle">rebuild it from an event log</text></g>
<g id="idem" class="fd"><rect x="640" y="192" width="180" height="70" rx="9" fill="{R_F}" stroke="{R_S}" stroke-width="1.4"/>
<text x="730" y="212" class="tiny" text-anchor="middle" font-weight="650">irreversible actions</text>
<text x="730" y="230" class="tiny" text-anchor="middle">charge, email, delete</text>
<text x="730" y="248" class="tiny" text-anchor="middle" id="idt">must not replay</text></g>
<g id="sm" class="fd"><rect x="40" y="282" width="780" height="46" rx="9" fill="#fff" stroke="{N_S}"/>
<text x="430" y="302" class="tiny" text-anchor="middle" font-weight="650" id="s1"></text>
<text x="430" y="320" class="tiny" text-anchor="middle" id="s2"></text></g>'''
js="""
function steps(done,cur){for(var k=0;k<6;k++){
  var e=$('st'+k),f='#F1F1F4',s='#D5D5DC',t='step '+(k+1);
  if(k<done){f='#E2EFE3';s='#A8CBAC';t='\u2713 '+(k+1)}
  else if(k===cur){f='#FBEBD2';s='#E2BC85';t='\u2192 '+(k+1)}
  e.firstChild.setAttribute('fill',f);e.firstChild.setAttribute('stroke',s);tx('stt'+k,t)}}
function base(){steps(0,-1);o('crash',0);o('hist',0);o('ckpt',0);o('mem',0);o('ckres',0);o('sr',0);o('idem',0);
  o('sm',0);tx('s1','');tx('s2','');tx('ckn','');tx('idt','must not replay');tx('ht','the raw trace')}
var S=[
{c:'A long agent run: read a file, run the tests, read the log, edit, re-run. Five steps in, it is holding a lot of hard-won progress.',
 a:function(){steps(5,5)}},
{c:'Then something interrupts it \u2014 a crash, a restart, a context that grew too long, or simply <b>waiting for a human to approve</b> something.',
 a:function(){steps(5,5);o('crash',1)}},
{c:'If the only record is the <b>conversation history</b>, resuming means re-reading the whole transcript and hoping the model reconstructs where it was. And if the history was truncated, that information is simply <b>gone</b>.',
 a:function(){steps(5,5);o('crash',1);o('hist',1);tx('ht','truncated \u2014 the early steps are gone')}},
{c:'<b>So persist structured state instead.</b> Not the transcript \u2014 the <b>execution state</b>: what the goal is, which steps are done, what was observed, what is pending, and what the environment looked like.',
 a:function(){steps(5,5);o('ckpt',1);tx('ckn','written as the run progresses, not at the end')}},
{c:'Now resume is mechanical. Load the latest checkpoint, see that steps 1\u20135 are done and step 6 is pending, and <b>carry on</b> \u2014 no re-derivation, no guessing.',
 a:function(){steps(5,5);o('ckpt',1);tx('ckn','resume = load the checkpoint and continue at step 6')}},
{c:'<b>Three things people merge that are not the same.</b> Memory is knowledge worth keeping. A checkpoint is execution progress. Conversation history is the raw trace \u2014 useful for audit, insufficient for resume.',
 a:function(){steps(5,5);o('mem',1);o('ckres',1);o('hist',1)}},
{c:'Two ways to build it. <b>Snapshot</b> saves the current state directly; <b>replay</b> rebuilds it by re-running a log of past events. Real systems do both \u2014 periodic snapshots so replay never starts from zero.',
 a:function(){steps(5,5);o('ckpt',1);o('sr',1);tx('ckn','snapshot the state, log the events')}},
{c:'<b>And here is the genuinely hard part.</b> Some actions cannot be replayed. If the agent charged a card and crashed before recording it, a naive resume charges it <b>again</b>.',
 a:function(){steps(5,5);o('crash',1);o('idem',1);tx('idt','charged \u2014 but was it recorded?')}},
{c:'So persist an <b>action ID and idempotency key before the call</b>, and reconcile after. Then recovery can ask the provider whether that key already succeeded rather than guessing \u2014 and a state machine distinguishes <i>"never sent"</i> from <i>"sent, outcome unknown"</i>.',
 a:function(){steps(5,5);o('idem',1);tx('idt','idempotency key \u2192 safe to retry');o('sm',1);
   tx('s1','RUNNING \u00b7 WAITING_FOR_TOOL \u00b7 WAITING_FOR_APPROVAL \u00b7 FAILED \u00b7 COMPLETED');
   tx('s2','"we sent it and do not know the outcome" is its own state \u2014 that is the one that matters')}},
{c:'<b>The line to say:</b> make a long-running agent resumable by persisting <b>structured execution state</b>, not conversation history. And for anything with side effects, durable action status and idempotency are what make recovery safe rather than merely possible.',
 a:function(){steps(6,-1);o('ckpt',1);tx('ckn','resumable by construction');o('idem',1);tx('idt','safe to recover')}}
];
"""
build("agent-checkpointing.html","Agent state and checkpointing \u2014 surviving the interruption",
      "Why conversation history is not enough, and what must never be replayed.",svg,js,"0 0 860 342")
print("ok")
