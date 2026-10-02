from shell import build
B_F,B_S="#E3EDF9","#A9C4E4"; G_F,G_S="#E2EFE3","#A8CBAC"
A_F,A_S="#FBEBD2","#E2BC85"; N_F,N_S="#F1F1F4","#D5D5DC"; R_F,R_S="#F7DADA","#DF9C9C"
BW,BG,BX,BY=52,10,60,214
svg=f'<text x="24" y="34" class="lbl-b">What each call has to read</text>\n'
for k in range(10):
    x=BX+k*(BW+BG)
    svg+=f'''<g id="b{k}" class="mv fd" transform="translate({x},{BY}) scale(1,0)"><rect x="0" y="-160" width="{BW}" height="160" rx="4" fill="{B_F}" stroke="{B_S}" stroke-width="1.2"/></g>
<g id="bl{k}" class="fd"><text x="{x+BW/2}" y="{BY+18}" class="tiny" text-anchor="middle">{k+1}</text></g>'''
svg+=f'''<path d="M{BX-14},{BY} L{BX+10*(BW+BG)},{BY}" stroke="#C2C2CB" stroke-width="1.2"/>
<path d="M{BX-14},{BY} L{BX-14},44" stroke="#C2C2CB" stroke-width="1.2"/>
<text x="{BX-22}" y="130" class="tiny" text-anchor="end">tokens</text>
<text x="{BX-22}" y="144" class="tiny" text-anchor="end">read</text>
<text x="{BX+5*(BW+BG)}" y="{BY+36}" class="tiny" text-anchor="middle">agent step</text>
<g id="obs" class="fd"><rect x="684" y="56" width="150" height="72" rx="8" fill="#fff" stroke="{N_S}"/>
<text x="759" y="76" class="tiny" text-anchor="middle" font-weight="650">what gets appended</text>
<text x="759" y="94" class="tiny" text-anchor="middle">source files, test logs,</text>
<text x="759" y="110" class="tiny" text-anchor="middle">browser pages, API output</text></g>
<g id="two" class="fd">
<rect x="24" y="256" width="370" height="46" rx="8" fill="#FAFAFB" stroke="{N_S}"/>
<text x="40" y="276" class="tiny" font-weight="650">context size</text><text x="40" y="292" class="tiny" id="t1">the height of the last bar</text>
<rect x="410" y="256" width="406" height="46" rx="8" fill="#FAFAFB" stroke="{N_S}"/>
<text x="426" y="276" class="tiny" font-weight="650">cumulative work</text><text x="426" y="292" class="tiny" id="t2">the sum of every bar</text></g>
<g id="tot" class="fd"><text x="24" y="336" class="tiny">total paid over the run</text>
<rect x="180" y="324" width="500" height="16" rx="8" fill="#F1F1F4"/>
<g id="tb" transform="translate(180,324) scale(0,1)"><rect width="500" height="16" rx="8" fill="{R_S}"/></g>
<text x="692" y="336" class="tiny" id="tt"></text></g>
<g id="msg" class="fd"><text x="420" y="362" class="lbl-b" text-anchor="middle" id="mtxt"></text></g>'''
js="""
var BX=%d,BW=%d,BG=%d,BY=%d;
function bars(n,scale,col){for(var k=0;k<10;k++){
  var h=k<n?Math.min(1,(k+1)*scale):0;
  $('b'+k).setAttribute('transform','translate('+(BX+k*(BW+BG))+','+BY+') scale(1,'+h+')');
  o('bl'+k,k<n?1:0);
  if(col)$('b'+k).firstChild.setAttribute('fill',col)}}
function tot(s,t){$('tb').setAttribute('transform','translate(180,324) scale('+s+',1)');tx('tt',t)}
function base(){bars(0,0);o('obs',0);o('two',0);o('tot',0);o('msg',0);tot(0,'');
  tx('t1','the height of the last bar');tx('t2','the sum of every bar');tx('mtxt','');
  for(var k=0;k<10;k++)$('b'+k).firstChild.setAttribute('fill','#E3EDF9')}
var S=[
{c:'An agent runs a loop: think, take an action, read the result, repeat. Each pass appends what it saw to the history — and the next call reads <b>all of it</b>.',
 a:function(){bars(3,.12)}},
{c:'Early on this is cheap. The history is short, so each call reads a little.',
 a:function(){bars(4,.12)}},
{c:'But agents do not append conversation — they append <b>environment output</b>. A single test log or source file can be larger than everything said so far.',
 a:function(){bars(6,.12);o('obs',1)}},
{c:'So the bars climb. By step 10 the model is re-reading the output of steps 1 through 9 just to decide <b>one more action</b> — and most of it is long dead: a file it already fixed, a log it already diagnosed.',
 a:function(){bars(10,.1);o('obs',1)}},
{c:'Now separate the two quantities people constantly merge. <b>Context size</b> is how tall the last bar is. <b>Cumulative work</b> is the area of <i>all</i> of them.',
 a:function(){bars(10,.1);o('two',1)}},
{c:'That distinction is the whole point. The history grows steadily — but because every call re-reads it, the total the run pays for grows <b>far faster</b> than the history itself.',
 a:function(){bars(10,.1);o('two',1);o('tot',1);tot(.95,'much larger than the final context');
   tx('t1','grows steadily');tx('t2','grows far faster')}},
{c:'<b>Two different fixes, and they are not interchangeable.</b> Caching stops you <i>recomputing</i> history that is still there — cost falls, but the bars stay exactly as tall.',
 a:function(){bars(10,.1);o('two',1);o('tot',1);tot(.3,'caching cut the recompute');
   tx('t1','unchanged — the window still fills');tx('t2','much cheaper')}},
{c:'<b>Compaction</b> is the other one: summarise or drop old history so the bars actually come down. It is the only fix when the problem is that the window is <b>full</b> rather than expensive.',
 a:function(){bars(10,.045,'#E2EFE3');o('two',1);o('tot',1);tot(.2,'shorter history, less to read');
   tx('t1','actually reduced');tx('t2','reduced too')}},
{c:'But compaction has a price: <b>drift</b>. Summarising throws something away, and you find out which thing mattered several steps later, when the agent no longer remembers why it ruled an approach out.',
 a:function(){bars(10,.045,'#E2EFE3');o('two',1);o('msg',1);tx('mtxt','what you discard, you discard silently')}},
{c:'<b>The line to say:</b> diagnose before prescribing. Time to first token dominated? Prefix caching. Cost climbing with the trajectory? Compaction. Throughput poor under load? KV capacity and scheduling. Naming the bottleneck <i>is</i> the answer.',
 a:function(){bars(10,.045,'#E2EFE3');o('msg',1);tx('mtxt','name the bottleneck, then the technique')}}
];
"""%(BX,BW,BG,BY)
build("agent-context-growth.html","Why a long agent loop gets expensive",
      "The history grows steadily; the bill grows faster.",svg,js,"0 0 840 376")
print("ok")
