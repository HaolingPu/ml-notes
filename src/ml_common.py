# shared drawing for the 2-2-1 network used by forward-pass, backprop and autodiff
B_F,B_S="#E3EDF9","#A9C4E4"; G_F,G_S="#E2EFE3","#A8CBAC"
A_F,A_S="#FBEBD2","#E2BC85"; N_F,N_S="#F1F1F4","#D5D5DC"; P_F,P_S="#F7E4EC","#DFAFC3"
R_F,R_S="#F7DADA","#DF9C9C"; V_F,V_S="#EFEAF8","#B7A5DA"
INK,INK2,INK3="#2B2B30","#6B6B76","#8B8B95"
GRAD="#C2602B"   # gradient colour (amber-red)

# node centres
X1=(92,118); X2=(92,206); H1=(318,96); H2=(318,228); OUT=(548,162); LOSS=(726,162)
R=26
W1=[[0.7,-0.6],[0.3,1.0]]; B1=[0.1,0.2]; W2=[0.4,-0.8]; B2=0.6
XV=[1.0,0.5]; Z=[0.5,1.0]; H=[0.5,1.0]; U=0.0; YH=0.5; L=0.693

def _pt(a,b,t):
    return (a[0]+(b[0]-a[0])*t, a[1]+(b[1]-a[1])*t)

def edge(idp,a,b,label,t=0.5,dy=-7,col=N_S,w=1.6,lid=None):
    # shorten to circle rims
    import math
    dx,dy_=b[0]-a[0],b[1]-a[1]; d=math.hypot(dx,dy_); ux,uy=dx/d,dy_/d
    a2=(a[0]+ux*R,a[1]+uy*R); b2=(b[0]-ux*R,b[1]-uy*R)
    p=_pt(a2,b2,t)
    s=f'<path id="{idp}" class="fd" d="M{a2[0]:.1f},{a2[1]:.1f} L{b2[0]:.1f},{b2[1]:.1f}" stroke="{col}" stroke-width="{w}" fill="none"/>'
    if label is not None:
        s+=f'<text id="{lid or idp+"l"}" class="tiny mono fd" x="{p[0]:.1f}" y="{p[1]+dy:.1f}" text-anchor="middle" font-weight="600">{label}</text>'
    return s

def node(idp,c,fill,stroke,name,val="",above="",below_dy=44):
    s=f'<g id="{idp}" class="fd"><circle cx="{c[0]}" cy="{c[1]}" r="{R}" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>'
    s+=f'<text id="{idp}v" class="lbl-b mono" x="{c[0]}" y="{c[1]+4}" text-anchor="middle">{val}</text>'
    s+=f'<text class="tiny" x="{c[0]}" y="{c[1]+below_dy}" text-anchor="middle">{name}</text>'
    s+=f'<text id="{idp}a" class="tiny mono fd" x="{c[0]}" y="{c[1]-R-8}" text-anchor="middle" fill="{INK2}">{above}</text></g>'
    return s

def net_svg():
    s=''
    # edges with weight labels (labels offset so crossing edges do not collide)
    s+=edge("e11",X1,H1,"0.7",t=0.42,dy=-7)
    s+=edge("e12",X1,H2,"0.3",t=0.74,dy=12)
    s+=edge("e21",X2,H1,"−0.6",t=0.74,dy=-13)
    s+=edge("e22",X2,H2,"1.0",t=0.42,dy=12)
    s+=edge("eo1",H1,OUT,"0.4",t=0.5,dy=-8)
    s+=edge("eo2",H2,OUT,"−0.8",t=0.5,dy=12)
    s+=edge("eol",OUT,LOSS,None,col=N_S)
    # bias ticks
    for idp,c,b in (("bh1",H1,"+0.1"),("bh2",H2,"+0.2"),("bo",OUT,"+0.6")):
        s+=f'<text id="{idp}" class="tiny mono fd" x="{c[0]}" y="{c[1]+R+30}" text-anchor="middle" fill="{INK3}">b {b}</text>'
    s+=node("nx1",X1,B_F,B_S,"x₁",val="1.0")
    s+=node("nx2",X2,B_F,B_S,"x₂",val="0.5")
    s+=node("nh1",H1,N_F,N_S,"h₁",val="")
    s+=node("nh2",H2,N_F,N_S,"h₂",val="")
    s+=node("no",OUT,N_F,N_S,"ŷ = σ(u)",val="")
    s+=f'<g id="nl" class="fd"><rect x="{LOSS[0]-44}" y="{LOSS[1]-24}" width="88" height="48" rx="8" fill="{N_F}" stroke="{N_S}" stroke-width="1.5"/>'
    s+=f'<text id="nlv" class="lbl-b mono" x="{LOSS[0]}" y="{LOSS[1]+4}" text-anchor="middle"></text>'
    s+=f'<rect id="nlring" class="fd" x="{LOSS[0]-49}" y="{LOSS[1]-29}" width="98" height="58" rx="11" fill="none" stroke="#8A6D3B" stroke-width="2"/>'
    s+=f'<text class="tiny" x="{LOSS[0]}" y="{LOSS[1]+40}" text-anchor="middle">loss L (y = 1)</text></g>'
    return s

def ledger(x=24,y=300,w=560,h=86,lines=3,idp="led"):
    s=f'<g id="{idp}" class="fd"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="9" fill="#FAFAFB" stroke="{N_S}"/>'
    for i in range(lines):
        s+=f'<text id="{idp}{i}" class="lbl mono" x="{x+14}" y="{y+24+i*22}" fill="{INK}" xml:space="preserve" style="white-space:pre"></text>'
    s+='</g>'
    return s
