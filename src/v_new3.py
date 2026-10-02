from shell import build
B_F,B_S="#E3EDF9","#A9C4E4"; G_F,G_S="#E2EFE3","#A8CBAC"
A_F,A_S="#FBEBD2","#E2BC85"; N_F,N_S="#F1F1F4","#D5D5DC"; R_F,R_S="#F7DADA","#DF9C9C"; P_F,P_S="#F7E4EC","#DFAFC3"

# ---------------- PIPELINE BUBBLE ----------------
CW,CH,X0,Y0=54,30,120,66
svg=f'<text x="24" y="34" class="lbl-b" id="ttl">One batch through four stages</text>\n'
for r in range(4):
    svg+=f'<text x="106" y="{Y0+r*(CH+8)+20}" class="tiny" text-anchor="end">stage {r+1}</text>'
    for c in range(10):
        svg+=f'''<g id="c{r}_{c}" class="fd"><rect x="{X0+c*(CW+4)}" y="{Y0+r*(CH+8)}" width="{CW}" height="{CH}" rx="4" fill="{N_F}" stroke="{N_S}" stroke-width="1" stroke-dasharray="2 2"/>
<text x="{X0+c*(CW+4)+CW/2}" y="{Y0+r*(CH+8)+19}" class="tiny" text-anchor="middle" id="t{r}_{c}"></text></g>'''
svg+=f'''<text x="{X0+5*(CW+4)}" y="{Y0+4*(CH+8)+22}" class="tiny" text-anchor="middle">time →</text>
<g id="util" class="fd"><text x="24" y="250" class="lbl-b">Hardware doing useful work</text>
<rect x="240" y="238" width="330" height="16" rx="8" fill="#F1F1F4"/>
<g id="ub" transform="translate(240,238) scale(0,1)"><rect width="330" height="16" rx="8" fill="{G_S}"/></g>
<text x="584" y="251" class="tiny" id="ut"></text></g>
<g id="msg" class="fd"><text x="420" y="288" class="lbl-b" text-anchor="middle" id="mt"></text>
<text x="420" y="306" class="tiny" text-anchor="middle" id="mt2"></text></g>'''
js="""
var F={n:['#F1F1F4','#D5D5DC'],w:['#E3EDF9','#A9C4E4'],b:['#F7DADA','#DF9C9C'],
       g:['#E2EFE3','#A8CBAC'],a:['#FBEBD2','#E2BC85']};
function cell(r,c,k,t){var e=$('c'+r+'_'+c);if(!e)return;
  var f=F[k]||F.n;e.firstChild.setAttribute('fill',f[0]);e.firstChild.setAttribute('stroke',f[1]);
  e.firstChild.setAttribute('stroke-dasharray',k==='n'?'2 2':'0');tx('t'+r+'_'+c,t||'')}
function clearAll(){for(var r=0;r<4;r++)for(var c=0;c<10;c++)cell(r,c,'n','')}
function bar(s,t){$('ub').setAttribute('transform','translate(240,238) scale('+s+',1)');tx('ut',t)}
function base(){clearAll();o('util',0);o('msg',0);tx('mt','');tx('mt2','');bar(0,'');
  tx('ttl','One batch through four stages')}
var S=[
{c:'Pipeline parallelism gives each GPU a different block of layers. That makes it <b>sequential by construction</b>: stage 2 cannot start until stage 1 hands something over.',
 a:function(){cell(0,0,'w','batch')}},
{c:'So with one batch in flight, the work simply walks down the pipeline. At any moment <b>exactly one stage is busy</b>.',
 a:function(){cell(0,0,'w','batch');cell(1,1,'w','batch');cell(2,2,'w','batch');cell(3,3,'w','batch');
   o('util',1);bar(.25,'one stage of four')}},
{c:'Colour the idle time and the problem is obvious. Three quarters of the hardware is doing <b>nothing</b>, all the time. That red region is the <b>pipeline bubble</b>.',
 a:function(){
   var seq=[[0,0],[1,1],[2,2],[3,3]];
   for(var r=0;r<4;r++)for(var c=0;c<4;c++){var busy=false;
     for(var i=0;i<seq.length;i++)if(seq[i][0]===r&&seq[i][1]===c)busy=true;
     cell(r,c,busy?'w':'b',busy?'batch':'idle')}
   o('util',1);bar(.25,'75% idle');
   o('msg',1);tx('mt','you bought four GPUs and are using one at a time');tx('mt2','')}},
{c:'<b>Micro-batching fixes it.</b> Split the batch into four smaller ones and feed them in back to back, so the stages can work on <b>different micro-batches simultaneously</b>.',
 a:function(){tx('ttl','Four micro-batches through four stages');
   for(var m=0;m<4;m++)cell(0,m,'g','µ'+(m+1))}},
{c:'Watch it fill. Micro-batch 1 moves to stage 2 while micro-batch 2 enters stage 1. Two steps later, <b>all four stages are busy at once</b> on four different micro-batches.',
 a:function(){tx('ttl','Four micro-batches through four stages');
   for(var m=0;m<4;m++)for(var r=0;r<4;r++){var c=m+r;if(c<10)cell(r,c,'g','µ'+(m+1))}
   o('util',1);bar(.8,'most stages busy most of the time')}},
{c:'The bubble has not vanished — look at the two corners. The pipeline still has to <b>fill up</b> at the start and <b>drain</b> at the end, and those triangles are irreducible.',
 a:function(){tx('ttl','Four micro-batches through four stages');
   for(var m=0;m<4;m++)for(var r=0;r<4;r++){var c=m+r;if(c<10)cell(r,c,'g','µ'+(m+1))}
   for(var r=0;r<4;r++){for(var c=0;c<r;c++)cell(r,c,'b','');for(var c=r+4;c<8;c++)cell(r,c,'b','')}
   o('util',1);bar(.8,'warm-up and drain remain');
   o('msg',1);tx('mt','the bubble shrinks with more micro-batches — it never reaches zero');tx('mt2','')}},
{c:'More micro-batches shrink those corners further, relative to the useful middle. The rule of thumb: you want <b>many more micro-batches than stages</b>.',
 a:function(){tx('ttl','Eight micro-batches — a longer steady state');
   for(var m=0;m<7;m++)for(var r=0;r<4;r++){var c=m+r;if(c<10)cell(r,c,'g','µ'+(m+1))}
   for(var r=0;r<4;r++){for(var c=0;c<r;c++)cell(r,c,'b','')}
   o('util',1);bar(.92,'the steady state dominates')}},
{c:'<b>But there is a cost.</b> Each micro-batch is smaller, so every GPU is now doing <b>less efficient work</b> — smaller matrices use the hardware worse. And more in-flight micro-batches means more stored activations.',
 a:function(){tx('ttl','The tradeoff');
   for(var m=0;m<7;m++)for(var r=0;r<4;r++){var c=m+r;if(c<10)cell(r,c,'a','small')}
   o('util',1);bar(.92,'busy, but with smaller chunks');
   o('msg',1);tx('mt','fewer bubbles  ↔  less efficient per GPU, more activation memory');
   tx('mt2','schedules like 1F1B interleave forward and backward to claw the memory back')}},
{c:'<b>The line to say:</b> pipeline parallelism creates the pipeline; micro-batches keep it full. Gradients accumulate across micro-batches before a single optimizer step, so correctness is unchanged — only the scheduling improved.',
 a:function(){tx('ttl','PP creates the pipeline · micro-batches keep it full');
   for(var m=0;m<7;m++)for(var r=0;r<4;r++){var c=m+r;if(c<10)cell(r,c,'g','µ'+(m+1))}
   o('util',1);bar(.92,'')}}
];
"""
build("pipeline-bubble.html","The pipeline bubble — and how micro-batches fill it",
      "Why splitting by layer leaves most of your GPUs idle, until you keep more work in flight.",svg,js,"0 0 840 320")

# ---------------- NCCL COLLECTIVES ----------------
GX=[80,270,460,650]
svg=f'<text x="24" y="32" class="lbl-b" id="ttl">AllReduce</text>\n<text x="24" y="50" class="tiny" id="sub2">combine everyone’s tensor — everyone gets the whole result</text>\n'
for k in range(4):
    svg+=f'''<g id="g{k}" class="fd"><rect x="{GX[k]}" y="72" width="130" height="44" rx="7" fill="{B_F}" stroke="{B_S}" stroke-width="1.3"/>
<text x="{GX[k]+65}" y="92" class="tiny" text-anchor="middle" font-weight="650">GPU {k+1}</text>
<text x="{GX[k]+65}" y="108" class="tiny" text-anchor="middle" id="in{k}">[1,2]</text></g>
<g id="o{k}" class="fd"><rect x="{GX[k]}" y="210" width="130" height="44" rx="7" fill="{G_F}" stroke="{G_S}" stroke-width="1.3"/>
<text x="{GX[k]+65}" y="238" class="tiny" text-anchor="middle" id="out{k}">[4,6]</text></g>'''
svg+=f'''<g id="hub" class="fd"><rect x="300" y="140" width="240" height="42" rx="9" fill="{A_F}" stroke="{A_S}" stroke-width="1.5"/>
<text x="420" y="166" class="tiny" text-anchor="middle" font-weight="650" id="hubt">AllReduce</text></g>
<g id="up" class="fd">'''
for k in range(4):
    svg+=f'<path id="pu{k}" d="M{GX[k]+65},116 C{GX[k]+65},134 420,124 420,140" stroke="{N_S}" stroke-width="1.2" fill="none"/>'
svg+='</g><g id="dn" class="fd">'
for k in range(4):
    svg+=f'<path id="pd{k}" d="M420,182 C420,198 {GX[k]+65},192 {GX[k]+65},210" stroke="{G_S}" stroke-width="1.2" fill="none" marker-end="url(#an)"/>'
svg+=f'''</g>
<g id="a2a" class="fd">'''
for a in range(4):
    for b in range(4):
        if a!=b:
            svg+=f'<path id="x{a}_{b}" d="M{GX[a]+65},116 C{GX[a]+65},170 {GX[b]+65},156 {GX[b]+65},210" stroke="{P_S}" stroke-width="1" fill="none" opacity=".75"/>'
svg+=f'''</g>
<g id="note" class="fd"><rect x="80" y="278" width="700" height="52" rx="9" fill="#fff" stroke="{N_S}"/>
<text x="430" y="300" class="tiny" text-anchor="middle" font-weight="650" id="n1"></text>
<text x="430" y="318" class="tiny" text-anchor="middle" id="n2"></text></g>
<defs><marker id="an" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0,1 L9,5 L0,9 z" fill="{G_S}"/></marker></defs>'''
js="""
var GX=[80,270,460,650];
function ins(a){for(var k=0;k<4;k++)tx('in'+k,a[k])}
function outs(a){for(var k=0;k<4;k++){o('o'+k,a?1:0);if(a)tx('out'+k,a[k])}}
function paths(kind){o('up',kind==='hub'?1:0);o('dn',kind==='hub'?1:0);o('a2a',kind==='a2a'?1:0)}
function base(){o('hub',0);paths('');outs(null);o('note',0);tx('n1','');tx('n2','');
  ins(['[1,2]','[3,4]','[5,6]','[7,8]']);
  tx('ttl','GPU collectives');tx('sub2','four patterns, and which parallelism each one serves')}
var S=[
{c:'Split a model across GPUs and they must constantly exchange tensors. Four GPUs, each holding a different piece — the question is always <b>what shape of exchange</b> is needed.',
 a:function(){}},
{c:'<b>AllReduce.</b> Every GPU contributes a tensor, they are combined (usually summed), and <b>every GPU receives the full result</b>.',
 a:function(){tx('ttl','AllReduce');tx('sub2','combine everyone\\'s tensor — everyone gets the whole result');
   o('hub',1);tx('hubt','sum');paths('hub');outs(['[16,20]','[16,20]','[16,20]','[16,20]'])}},
{c:'This is the <b>tensor-parallelism workhorse</b>. Each GPU computed a partial result for the same layer, and the layer cannot proceed until those partials are summed and shared back.',
 a:function(){tx('ttl','AllReduce');tx('sub2','the tensor-parallelism workhorse');
   o('hub',1);tx('hubt','sum');paths('hub');outs(['[16,20]','[16,20]','[16,20]','[16,20]']);
   o('note',1);tx('n1','TP leans on AllReduce');tx('n2','partial results for one layer, combined at every layer')}},
{c:'<b>AllGather.</b> No combining at all — each GPU holds one <b>shard</b>, and afterwards every GPU holds the <b>whole tensor</b>. Used to reconstruct sharded state.',
 a:function(){tx('ttl','AllGather');tx('sub2','collect shards — everyone ends up with the full tensor');
   ins(['shard A','shard B','shard C','shard D']);o('hub',1);tx('hubt','gather');paths('hub');
   outs(['A B C D','A B C D','A B C D','A B C D'])}},
{c:'<b>ReduceScatter.</b> Combine like AllReduce, but then <b>scatter the result</b> — each GPU keeps only its own slice. The result stays distributed rather than replicated.',
 a:function(){tx('ttl','ReduceScatter');tx('sub2','combine, then keep only your slice');
   ins(['[1,2]','[3,4]','[5,6]','[7,8]']);o('hub',1);tx('hubt','sum, then split');paths('hub');
   outs(['slice 1','slice 2','slice 3','slice 4'])}},
{c:'Worth noticing: <b>AllReduce = ReduceScatter + AllGather</b>. That is not trivia — it is exactly how efficient ring implementations are built, which is why the two appear together so often.',
 a:function(){tx('ttl','ReduceScatter + AllGather');tx('sub2','= AllReduce');
   o('hub',1);tx('hubt','reduce-scatter, then all-gather');paths('hub');
   outs(['[16,20]','[16,20]','[16,20]','[16,20]']);
   o('note',1);tx('n1','the decomposition is the implementation');tx('n2','ring AllReduce is literally these two phases back to back')}},
{c:'<b>All-to-All</b> is the odd one. Every GPU sends <b>different data to every other GPU</b> — not one shared result, but a full redistribution.',
 a:function(){tx('ttl','All-to-All');tx('sub2','everyone sends something different to everyone else');
   ins(['tokens','tokens','tokens','tokens']);paths('a2a');
   outs(['for expert 1','for expert 2','for expert 3','for expert 4'])}},
{c:'That is the <b>MoE routing pattern</b>. Tokens scatter to whichever GPUs host the experts they selected — then a <b>second All-to-All</b> brings the results back to the GPUs that owned those tokens.',
 a:function(){tx('ttl','All-to-All');tx('sub2','the MoE / expert-parallelism pattern');paths('a2a');
   ins(['tokens','tokens','tokens','tokens']);outs(['expert out','expert out','expert out','expert out']);
   o('note',1);tx('n1','EP leans on All-to-All — twice per layer');tx('n2','which is why MoE performance lives and dies on the interconnect')}},
{c:'<b>And the cost they all share:</b> collectives <b>synchronise</b>. Every GPU must arrive before the operation completes, so the <b>slowest one sets the pace</b> and a single straggler stalls the whole group.',
 a:function(){tx('ttl','What every collective costs');tx('sub2','they are synchronisation points');
   o('hub',1);tx('hubt','everyone waits for the slowest');paths('hub');
   ins(['ready','ready','slow …','ready']);outs(['waiting','waiting','waiting','waiting']);
   o('note',1);tx('n1','scaling is limited by interconnect bandwidth and topology');tx('n2','not by GPU FLOPs alone — this is the systems point to make')}}
];
"""
build("nccl-collectives.html","GPU collectives — four shapes of exchange",
      "AllReduce, AllGather, ReduceScatter, All-to-All — and which parallelism needs each.",svg,js,"0 0 840 344")
print("ok")
