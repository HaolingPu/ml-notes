from shell import build

B_F,B_S="#E3EDF9","#A9C4E4"   # blue  (Q)
G_F,G_S="#E2EFE3","#A8CBAC"   # green (K,V / done)
A_F,A_S="#FBEBD2","#E2BC85"   # amber (scores)
R_F,R_S="#F7DADA","#DF9C9C"   # red   (the bad path)
N_F,N_S="#F1F1F4","#D5D5DC"   # neutral

def tile(i,x,y,f,s,t="",fs=10):
    o=f'<g id="{i}" class="mv fd"><rect width="56" height="28" rx="4" fill="{f}" stroke="{s}" stroke-width="1.2"/>'
    if t: o+=f'<text x="28" y="18" class="tiny" text-anchor="middle">{t}</text>'
    return o+f'</g>'

QH=[[36,84+36*k] for k in range(4)]
KH=[[112,84+36*k] for k in range(4)]
OH=[[396,84+36*k] for k in range(4)]
QS,KS,OS=(548,92),(624,92),(624,250)

svg=f'''
<rect x="16" y="44" width="470" height="306" rx="10" fill="#FAFAFB" stroke="#DCDCE2" stroke-width="1"/>
<text x="26" y="36" class="lbl-b">HBM — large, but slow to reach</text>
<rect x="520" y="44" width="324" height="306" rx="10" fill="#F2F7FC" stroke="#C8DCEF" stroke-width="1"/>
<text x="530" y="36" class="lbl-b">On-chip SRAM — tiny, but fast</text>
<text x="64" y="76" class="lbl">Q</text><text x="140" y="76" class="lbl">K, V</text>
<text x="424" y="76" class="lbl">output</text>
'''
for k in range(4):
    x,y=QH[k]; svg+=f'<rect x="{x}" y="{y}" width="56" height="28" rx="4" fill="{N_F}" stroke="{N_S}" stroke-width="1" stroke-dasharray="3 2"/>'
    x,y=KH[k]; svg+=f'<rect x="{x}" y="{y}" width="56" height="28" rx="4" fill="{N_F}" stroke="{N_S}" stroke-width="1" stroke-dasharray="3 2"/>'
    x,y=OH[k]; svg+=f'<g id="oh{k}" class="fd"><rect x="{x}" y="{y}" width="56" height="28" rx="4" fill="{N_F}" stroke="{N_S}" stroke-width="1.2"/></g>'
# the S x S matrix that naive attention builds
svg+=f'''<g id="bigS" class="fd"><rect x="206" y="84" width="150" height="136" rx="6" fill="{R_F}" stroke="{R_S}" stroke-width="1.5"/>
<text x="281" y="140" class="lbl-b" text-anchor="middle">S × S scores</text>
<text x="281" y="158" class="tiny" text-anchor="middle">every query × every key</text></g>
<g id="strike" class="fd"><path d="M212,90 L350,214" stroke="{R_S}" stroke-width="2.5"/><path d="M350,90 L212,214" stroke="{R_S}" stroke-width="2.5"/></g>
<g id="naiveArrows" class="fd">
<path d="M172,110 L200,110" stroke="{R_S}" stroke-width="1.4" marker-end="url(#ar)"/>
<path d="M360,124 L392,124" stroke="{R_S}" stroke-width="1.4" marker-end="url(#ar)"/>
<text x="281" y="238" class="tiny" text-anchor="middle" fill="#B36A6A">written out, read back, written, read again</text></g>
<g id="slots" class="fd">
<rect x="548" y="92" width="56" height="28" rx="4" fill="none" stroke="#B9D2EA" stroke-width="1.2" stroke-dasharray="3 2"/>
<rect x="624" y="92" width="56" height="28" rx="4" fill="none" stroke="#B9D2EA" stroke-width="1.2" stroke-dasharray="3 2"/>
<text x="576" y="86" class="tiny" text-anchor="middle">Q block</text>
<text x="652" y="86" class="tiny" text-anchor="middle">K,V block</text></g>
<g id="stile" class="fd"><rect x="548" y="140" width="132" height="40" rx="5" fill="{A_F}" stroke="{A_S}" stroke-width="1.4"/>
<text x="614" y="158" class="tiny" text-anchor="middle" font-weight="650">score tile</text>
<text x="614" y="172" class="tiny" text-anchor="middle">this block only</text></g>
<g id="acc" class="fd"><rect x="548" y="200" width="272" height="96" rx="6" fill="#fff" stroke="#C8DCEF" stroke-width="1.3"/>
<text x="560" y="218" class="tiny" font-weight="650">running state</text>
<text x="560" y="240" class="tiny">max  m</text><text x="700" y="240" class="tiny" id="am" text-anchor="end">—</text>
<text x="560" y="260" class="tiny">sum  ℓ</text><text x="700" y="260" class="tiny" id="al" text-anchor="end">—</text>
<text x="560" y="280" class="tiny">output accumulator</text><text x="700" y="280" class="tiny" id="ao" text-anchor="end">—</text>
<rect x="712" y="228" width="96" height="56" rx="5" fill="{B_F}" stroke="{B_S}" stroke-width="1.2" id="accbar"/>
<text x="760" y="252" class="tiny" text-anchor="middle" id="acct">O</text>
<text x="760" y="268" class="tiny" text-anchor="middle" id="acct2">row block</text></g>
<g id="disc" class="fd"><text x="614" y="192" class="tiny" text-anchor="middle" fill="#B36A6A">discarded — never written to HBM</text></g>
<text x="16" y="378" class="lbl">HBM traffic</text>
<rect x="104" y="366" width="300" height="13" rx="6.5" fill="#F1F1F4"/>
<g id="tbarG" transform="translate(104,366) scale(0,1)"><rect width="300" height="13" rx="6.5" fill="#DF9C9C" id="tbar"/></g>
<text x="416" y="376" class="tiny" id="tlab"></text>
<defs><marker id="ar" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0,1 L9,5 L0,9 z" fill="{R_S}"/></marker></defs>
'''
for k in range(4): svg+=tile(f"mq{k}",0,0,B_F,B_S,f"Q{k+1}")
for k in range(4): svg+=tile(f"mkv{k}",0,0,G_F,G_S,f"K,V {k+1}")
svg+=tile("mo",0,0,G_F,G_S,"O1")

js="""
var QH=%s,KH=%s,OH=%s;
function base(){
  o('bigS',0);o('strike',0);o('naiveArrows',0);o('slots',0);o('stile',0);o('acc',0);o('disc',0);
  for(var k=0;k<4;k++){o('mq'+k,0);o('mkv'+k,0);mv('mq'+k,QH[k][0],QH[k][1]);mv('mkv'+k,KH[k][0],KH[k][1]);
  }
  o('mo',0);mv('mo',624,250);
  for(var k=0;k<4;k++){var e=$('oh'+k);if(e){e.firstChild.setAttribute('fill','#F1F1F4');e.firstChild.setAttribute('stroke','#D5D5DC')}}
  tx('am','—');tx('al','—');tx('ao','—');tx('tlab','');
  $('tbarG').setAttribute('transform','translate(104,366) scale(0,1)');
  $('tbar').setAttribute('fill','#DF9C9C');
}
function traffic(s,c,t){$('tbarG').setAttribute('transform','translate(104,366) scale('+s+',1)');
  $('tbar').setAttribute('fill',c);tx('tlab',t)}
function odone(k){var e=$('oh'+k);e.firstChild.setAttribute('fill','#E2EFE3');e.firstChild.setAttribute('stroke','#A8CBAC')}
function loaded(n){
  for(var k=0;k<4;k++){o('mq'+k,1);o('mkv'+k,1)}
  mv('mq0',548,92); mv('mkv'+n,624,92); o('slots',1)}

var S=[
{c:'<b>The problem, first.</b> Plain attention computes the score for <i>every</i> query against <i>every</i> key — an S × S matrix. For a long sequence that matrix is enormous, and it lives in <b>HBM</b>: the big, slow memory.',
 a:function(){o('bigS',1);o('naiveArrows',1);traffic(.9,'#DF9C9C','huge')}},
{c:'And it is not computed once and used. It gets <b>written out, read back</b> for the softmax, written again, then read once more to multiply by V. Four trips across the slow bus for data that is only ever needed on its way to the output.',
 a:function(){o('bigS',1);o('naiveArrows',1);traffic(1,'#DF9C9C','four round trips')}},
{c:'So the bottleneck is <b>not arithmetic</b> — GPUs are already good at big matrix multiplies. The bottleneck is <b>moving this matrix in and out of slow memory</b>. That reframing is the whole insight.',
 a:function(){o('bigS',1);traffic(1,'#DF9C9C','this is the real cost')}},
{c:'FlashAttention\\'s move: <b>never build the matrix at all.</b> If each number is only needed once on its way to the output, it never has to exist in HBM.',
 a:function(){o('bigS',.28);o('strike',1);traffic(.2,'#A8CBAC','')}},
{c:'Instead, <b>cut the work into tiles</b>. Q is split into row blocks and K,V into blocks small enough that a pair of them fits inside SRAM — the fast scratchpad right next to the compute units.',
 a:function(){o('slots',1);for(var k=0;k<4;k++){o('mq'+k,1);o('mkv'+k,1)}traffic(.2,'#A8CBAC','')}},
{c:'<b>Load the first pair.</b> Watch Q block 1 and K,V block 1 travel from HBM into SRAM. This is the <i>only</i> HBM traffic that happens — and each block makes the trip once.',
 a:function(){loaded(0);o('acc',1);traffic(.2,'#A8CBAC','one trip per block')}},
{c:'<b>Compute the score tile on chip.</b> Just this block of scores, never the full matrix. It is born in fast memory and it will die there.',
 a:function(){loaded(0);o('stile',1);o('acc',1);traffic(.2,'#A8CBAC','')}},
{c:'<b>Online softmax.</b> Normally softmax needs the whole row before it can divide by the sum. Instead we keep a <span class="q">running max</span> and a <span class="q">running sum</span>, and fold each tile into an output accumulator as it arrives.',
 a:function(){loaded(0);o('stile',1);o('acc',1);tx('am','from tile 1');tx('al','from tile 1');tx('ao','partial');traffic(.2,'#A8CBAC','')}},
{c:'<b>Then throw the score tile away.</b> It was used and discarded inside SRAM — it never touched HBM. That is the traffic the naive version was paying for.',
 a:function(){loaded(0);o('acc',1);o('disc',1);tx('am','from tile 1');tx('al','from tile 1');tx('ao','partial');traffic(.2,'#A8CBAC','')}},
{c:'<b>Next K,V block.</b> Block 1 goes home, block 2 comes in. If its scores are larger than anything seen so far, the running max changes — so the accumulator so far is <b>rescaled</b> to stay exact. This correction is what keeps the result identical.',
 a:function(){loaded(1);o('stile',1);o('acc',1);tx('am','updated ↑');tx('al','rescaled');tx('ao','corrected');traffic(.4,'#A8CBAC','')}},
{c:'Block 3, block 4 — same loop. Each K,V block is loaded once, folded in, and released. The accumulator for this row block keeps converging on the true answer.',
 a:function(){loaded(3);o('stile',1);o('acc',1);tx('am','final');tx('al','final');tx('ao','complete');traffic(.55,'#A8CBAC','')}},
{c:'<b>Only now is anything written back.</b> One finished output row block goes out to HBM. Not scores, not probabilities — just the result.',
 a:function(){o('acc',1);tx('am','final');tx('al','final');tx('ao','complete');o('mo',1);mv('mo',OH[0][0],OH[0][1]);odone(0);traffic(.6,'#A8CBAC','')}},
{c:'Repeat for every row block and the output is complete — <b>bit-for-bit identical</b> to the naive version. FlashAttention is <b>exact</b>, and still quadratic in arithmetic. All it removed was the round trips.',
 a:function(){for(var k=0;k<4;k++)odone(k);o('bigS',.18);o('strike',1);traffic(.28,'#A8CBAC','a fraction of the naive traffic')}},
{c:'<b>The line to say:</b> tiling a single matmul was never the problem — GEMMs already tile. FlashAttention tiles and <b>fuses the whole attention operation</b>, and online softmax is what makes that legal. FlashAttention-2 keeps the idea and improves how the work is split across the GPU.',
 a:function(){for(var k=0;k<4;k++)odone(k);o('bigS',.18);o('strike',1);o('acc',1);tx('am','final');tx('al','final');tx('ao','complete');traffic(.28,'#A8CBAC','a fraction of the naive traffic')}}
];
"""%(QH,KH,OH)

build("flashattention.html","FlashAttention — why the big matrix never gets built",
      "Step through what actually moves between slow and fast memory.",svg,js,"0 0 860 396")
print("built")
