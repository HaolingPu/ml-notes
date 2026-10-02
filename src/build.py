import json, glob, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from content import T, GROUPS, AREAS
from depth import D
from _figs import FIGS
from shell import CSS as VCSS, ENGINE as _E
import re

ENGINE = (_E.replace("document.getElementById('cap')", "ROOT.querySelector('[id=\"cap\"]')")
            .replace("document.getElementById('num')", "ROOT.querySelector('[id=\"num\"]')")
            .replace("document.getElementById('dots')", "ROOT.querySelector('[id=\"dots\"]')")
            .replace("document.addEventListener('keydown',function(e){",
                     "document.addEventListener('keydown',function(e){ if(ROOT.closest('.pane').hidden)return;"))
ENGINE = "\n".join(l for l in ENGINE.split("\n")
                   if not re.match(r"function (\$|o|mv|cl|tx|fill|stroke)\(", l))
assert "document.getElementById(x)" not in ENGINE

MODS = {}
for p in glob.glob("mods/*.json"):
    m = json.load(open(p)); MODS[m["id"]] = m
for t in T:
    assert t["id"] in MODS, "no visualization for " + t["id"]

GCOL  = ["#6B4FA8", "#2F6FB0", "#2E8B73", "#B0761F", "#B4506B", "#9A4F86", "#3D6E9C", "#7A5A2E", "#2E7D5B", "#C06A20", "#5B6CB0", "#C2602B", "#2A7F8F"]
GTINT = ["#F2EEF9", "#E9F1F9", "#E7F3EF", "#FBF1E1", "#FAEDF1", "#F8ECF4", "#EAF0F7", "#F6F0E4", "#E6F2EC", "#FAEEE1", "#EAEDF8", "#FBEBE1", "#E3F1F3"]

# ---------------------------------------------------------------- home graph
def home_svg():
    o = []
    def box(x, y, w, h, tid, label, sub, gi, big=False):
        col, tint = GCOL[gi], GTINT[gi]
        fs = 13 if big else 11.5
        o.append(f'<g class="node" data-go="{tid}" transform="translate({x},{y})">'
                 f'<rect class="nbox" width="{w}" height="{h}" rx="9" fill="{tint}" stroke="{col}" stroke-width="1.4"/>'
                 f'<text class="nt" x="{w/2}" y="{h/2 - (5 if sub else -4)}" text-anchor="middle" font-size="{fs}" font-weight="600" fill="#1D1D22">{label}</text>'
                 + (f'<text class="ns" x="{w/2}" y="{h/2+12}" text-anchor="middle" font-size="10" fill="#5E5E68">{sub}</text>' if sub else '')
                 + '</g>')
    def plain(x, y, w, h, label, sub=""):
        o.append(f'<g transform="translate({x},{y})"><rect width="{w}" height="{h}" rx="9" fill="#FFFFFF" stroke="#C9C9D2" stroke-width="1.3"/>'
                 f'<text x="{w/2}" y="{h/2 - (5 if sub else -4)}" text-anchor="middle" font-size="11.5" font-weight="600" fill="#1D1D22">{label}</text>'
                 + (f'<text x="{w/2}" y="{h/2+12}" text-anchor="middle" font-size="10" fill="#5E5E68">{sub}</text>' if sub else '') + '</g>')
    def band(x, y, w, h, label, gi):
        o.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="14" fill="{GTINT[gi]}" opacity=".42"/>'
                 f'<text x="{x+16}" y="{y+21}" font-size="10.5" font-weight="700" fill="{GCOL[gi]}" letter-spacing=".06em">{label.upper()}</text>')
    def arrow(d, cls="edge"):
        o.append(f'<path class="{cls}" d="{d}" fill="none" stroke="#A9A9B6" stroke-width="1.6" marker-end="url(#hm)"/>')

    # --- lane 1: the request path
    band(24, 44, 1072, 92, "the request reaches a GPU", 2)
    plain(44, 68, 118, 50, "user request", "a prompt arrives")
    box(194, 68, 118, 50, "service-mesh", "service mesh", "routing + health", 2)
    box(344, 68, 150, 50, "load-balancing", "load balancer", "which replica is cheapest?", 2)
    box(526, 68, 138, 50, "prefix-caching", "prefix cache", "seen this preamble?", 2)
    box(696, 68, 138, 50, "continuous-batching", "scheduler", "which requests run now", 2)
    plain(866, 68, 118, 50, "one replica", "a GPU, or several")
    for x in (162, 312, 494, 664, 834):
        arrow(f"M{x},93 L{x+30},93")

    # --- lane 2: the two phases
    band(24, 158, 1072, 116, "two phases, two bottlenecks", 1)
    box(60, 190, 176, 62, "pd-disaggregation", "prefill", "read the whole prompt", 1, big=True)
    box(292, 190, 176, 62, "pd-disaggregation", "decode", "one token at a time", 1, big=True)
    box(524, 182, 160, 40, "prefill-vs-decode", "why they differ", "compute vs bandwidth", 1)
    box(524, 228, 160, 40, "kv-cache", "KV cache", "built, then read", 1)
    box(706, 182, 150, 40, "mha-gqa-mqa", "GQA / MQA", "shrink what decode reads", 1)
    box(706, 228, 150, 40, "paged-attention", "PagedAttention", "store it in blocks", 1)
    arrow("M236,221 L292,221")
    arrow("M468,215 L524,202"); arrow("M468,228 L524,242")
    arrow("M684,202 L706,202"); arrow("M684,248 L706,248")
    o.append('<path class="edge" d="M925,118 C925,150 640,150 640,158" fill="none" stroke="#A9A9B6" stroke-width="1.6" marker-end="url(#hm)"/>')

    # --- lane 3: inside one forward pass
    band(24, 296, 660, 110, "inside one forward pass", 0)
    box(60, 328, 170, 58, "self-attention", "self-attention", "who attends to whom", 0, big=True)
    box(272, 328, 170, 58, "flashattention", "FlashAttention", "same math, less traffic", 0)
    box(484, 328, 170, 58, "full-vs-linear-attention", "linear attention", "a summary, not every token", 0)
    arrow("M230,357 L272,357"); arrow("M442,357 L484,357")
    o.append('<path class="edge" d="M148,252 L148,296" fill="none" stroke="#A9A9B6" stroke-width="1.6" marker-end="url(#hm)"/>')

    # --- lane 3b: many GPUs
    band(708, 296, 388, 110, "when one GPU is not enough", 3)
    box(730, 328, 112, 58, "model-parallelism", "TP / PP / EP", "where to cut", 3)
    box(858, 328, 108, 58, "pipeline-bubble", "bubbles", "keep stages full", 3)
    box(982, 328, 96, 58, "nccl-collectives", "collectives", "the exchange", 3)
    arrow("M842,357 L858,357"); arrow("M966,357 L982,357")
    o.append('<path class="edge" d="M900,274 L900,296" fill="none" stroke="#A9A9B6" stroke-width="1.6" marker-end="url(#hm)"/>')

    # --- lane 4: output + agents
    plain(60, 452, 150, 50, "tokens stream back", "the user sees text")
    o.append('<path class="edge" d="M148,386 L148,452" fill="none" stroke="#A9A9B6" stroke-width="1.6" marker-end="url(#hm)"/>')
    band(258, 428, 838, 98, "and if the caller is an agent, it happens again", 4)
    box(286, 456, 176, 56, "agent-context-growth", "context grows", "every call re-reads it", 4, big=True)
    box(494, 456, 160, 56, "agent-checkpointing", "checkpointing", "surviving a crash", 4)
    box(686, 456, 150, 56, "mcp", "MCP", "reaching tools", 4)
    box(868, 456, 200, 56, "rag-vs-memory", "RAG vs memory", "what enters the context", 4)
    arrow("M210,477 L286,477"); arrow("M462,484 L494,484"); arrow("M654,484 L686,484"); arrow("M836,484 L868,484")
    # the loop back to the top
    o.append('<path class="edge back" d="M1068,484 C1128,484 1148,300 1148,180 C1148,110 1080,93 994,93" fill="none" '
             'stroke="#B4506B" stroke-width="1.6" stroke-dasharray="6 4" marker-end="url(#hm2)"/>')
    o.append('<text x="1141" y="300" font-size="10" fill="#B4506B" text-anchor="middle" transform="rotate(90 1141 300)">the agent submits the next call</text>')

    # animated request packet
    defs = ('<defs><marker id="hm" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" '
            'orient="auto-start-reverse"><path d="M0,1 L9,5 L0,9 z" fill="#A9A9B6"/></marker>'
            '<marker id="hm2" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" '
            'orient="auto-start-reverse"><path d="M0,1 L9,5 L0,9 z" fill="#B4506B"/></marker></defs>')
    return f'<svg id="mapsvg" class="mapsvg" viewBox="0 0 1170 552" xmlns="http://www.w3.org/2000/svg">{defs}{"".join(o)}</svg>'


# ---------------------------------------------------------------- agents map
def agents_svg():
    import math
    o = []
    def box(x, y, w, h, tid, label, sub, gi, big=False):
        col, tint = GCOL[gi], GTINT[gi]
        fs = 13 if big else 11.5
        o.append(f'<g class="node" data-go="{tid}" transform="translate({x},{y})">'
                 f'<rect class="nbox" width="{w}" height="{h}" rx="9" fill="{tint}" stroke="{col}" stroke-width="1.4"/>'
                 f'<text class="nt" x="{w/2}" y="{h/2 - (5 if sub else -4)}" text-anchor="middle" font-size="{fs}" font-weight="600" fill="#1D1D22">{label}</text>'
                 + (f'<text class="ns" x="{w/2}" y="{h/2+12}" text-anchor="middle" font-size="10" fill="#5E5E68">{sub}</text>' if sub else '')
                 + '</g>')
    def plain(x, y, w, h, label, sub=""):
        o.append(f'<g transform="translate({x},{y})"><rect width="{w}" height="{h}" rx="9" fill="#FFFFFF" stroke="#C9C9D2" stroke-width="1.3"/>'
                 f'<text x="{w/2}" y="{h/2 - (5 if sub else -4)}" text-anchor="middle" font-size="11.5" font-weight="600" fill="#1D1D22">{label}</text>'
                 + (f'<text x="{w/2}" y="{h/2+12}" text-anchor="middle" font-size="10" fill="#5E5E68">{sub}</text>' if sub else '') + '</g>')
    def band(x, y, w, h, label, gi):
        o.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="14" fill="{GTINT[gi]}" opacity=".40"/>'
                 f'<text x="{x+16}" y="{y+21}" font-size="10.5" font-weight="700" fill="{GCOL[gi]}" letter-spacing=".06em">{label.upper()}</text>')

    plain(28, 168, 132, 52, "a goal arrives", "\u201cfix the failing test\u201d")
    band(186, 40, 470, 300, "the loop \u2014 it runs dozens of times", 4)
    CX, CY = 421, 200
    ring = [("the model", "picks an action", -90), ("orchestrator", "permissions, sandbox", -18),
            ("tool call", "shell, search, MCP", 54), ("observation", "a log, a file", 126),
            ("update state", "and checkpoint", 198)]
    pts = []
    for lab, sub, ang in ring:
        a = math.radians(ang); x = CX + 150*math.cos(a); y = CY + 96*math.sin(a)
        pts.append((x, y)); box(x-73, y-24, 146, 48, "agent-loop", lab, sub, 4)
    for i in range(len(pts)):
        a, b = pts[i], pts[(i+1) % len(pts)]
        o.append(f'<path class="edge" d="M{a[0]:.0f},{a[1]:.0f} Q{CX},{CY} {b[0]:.0f},{b[1]:.0f}" '
                 f'fill="none" stroke="#B9B9C4" stroke-width="1.3" opacity=".7"/>')
    o.append(f'<path class="edge" d="M160,194 L{pts[0][0]-74:.0f},{pts[0][1]:.0f}" fill="none" stroke="#A9A9B6" stroke-width="1.6" marker-end="url(#am3)"/>')
    o.append(f'<text x="{CX}" y="{CY-2}" text-anchor="middle" font-size="12.5" font-weight="600" fill="#5E5E68">the loop</text>')
    o.append(f'<text x="{CX}" y="{CY+16}" text-anchor="middle" font-size="10" fill="#8B8B95">not one model call</text>')

    band(684, 40, 400, 300, "what the loop makes hard", 5)
    box(706, 72, 356, 58, "agent-context-growth", "the context keeps growing", "every call re-reads the history", 5)
    box(706, 142, 356, 58, "agent-checkpointing", "the state must survive", "crashes, restarts, approval waits", 5)
    box(706, 212, 356, 58, "mcp", "it must reach systems you don\u2019t own", "MCP standardises that boundary", 6)
    box(706, 282, 356, 46, "rag-vs-memory", "and something decides what enters", "RAG vs memory", 6)
    for y in (101, 171, 241, 305):
        o.append(f'<path class="edge" d="M656,{y} L706,{y}" fill="none" stroke="#A9A9B6" stroke-width="1.4" marker-end="url(#am3)"/>')

    band(28, 366, 1056, 108, "the same loop, instantiated \u2014 a coding agent", 4)
    stages = [("search", "the repo"), ("localize", "what runs"), ("hypothesise", "root cause"),
              ("edit", "smallest change"), ("run tests", "find out")]
    for i, (a, b) in enumerate(stages):
        box(48 + i*168, 400, 150, 54, "coding-agent", a, b, 4)
        if i < 4:
            o.append(f'<path class="edge" d="M{198+i*168},427 L{216+i*168},427" fill="none" stroke="#A9A9B6" stroke-width="1.4" marker-end="url(#am3)"/>')
    o.append('<path class="edge back" d="M723,454 C723,492 384,492 384,458" fill="none" stroke="#B4506B" '
             'stroke-width="1.5" marker-end="url(#am4)"/>')
    o.append('<text x="556" y="512" text-anchor="middle" font-size="10" fill="#B4506B">a failed test is an observation \u2014 go back to localization with more information</text>')
    box(888, 400, 178, 54, "coding-agent", "patch + evidence", "not a plausible guess", 4)
    o.append('<path class="edge" d="M870,427 L888,427" fill="none" stroke="#A9A9B6" stroke-width="1.4" marker-end="url(#am3)"/>')

    band(28, 536, 1056, 100, "and what a real harness forces you to decide", 7)
    hb = [("message-protocol", "the prompt is the state", "four roles, one rule"),
          ("context-compaction", "compaction", "the sawtooth"),
          ("error-policy", "error policy", "recoverable or terminal"),
          ("observation-budget", "three levers", "on the context budget"),
          ("programmatic-tools", "programmatic tools", "code that composes them")]
    for i, (tid, a, b) in enumerate(hb):
        box(48 + i*208, 570, 190, 50, tid, a, b, 7)

    defs = ('<defs><marker id="am3" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" '
            'orient="auto-start-reverse"><path d="M0,1 L9,5 L0,9 z" fill="#A9A9B6"/></marker>'
            '<marker id="am4" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" '
            'orient="auto-start-reverse"><path d="M0,1 L9,5 L0,9 z" fill="#B4506B"/></marker></defs>')
    return f'<svg id="agentsvg" class="mapsvg" viewBox="0 0 1112 656" xmlns="http://www.w3.org/2000/svg">{defs}{"".join(o)}</svg>'


# ---------------------------------------------------------------- blackwell map
def blackwell_svg():
    o = []
    def box(x, y, w, h, tid, label, sub, gi, big=False):
        col, tint = GCOL[gi], GTINT[gi]
        fs = 13 if big else 11.5
        o.append(f'<g class="node" data-go="{tid}" transform="translate({x},{y})">'
                 f'<rect class="nbox" width="{w}" height="{h}" rx="9" fill="{tint}" stroke="{col}" stroke-width="1.4"/>'
                 f'<text class="nt" x="{w/2}" y="{h/2 - (5 if sub else -4)}" text-anchor="middle" font-size="{fs}" font-weight="600" fill="#1D1D22">{label}</text>'
                 + (f'<text class="ns" x="{w/2}" y="{h/2+12}" text-anchor="middle" font-size="10" fill="#5E5E68">{sub}</text>' if sub else '')
                 + '</g>')
    def plain(x, y, w, h, label, sub=""):
        o.append(f'<g transform="translate({x},{y})"><rect width="{w}" height="{h}" rx="9" fill="#FFFFFF" stroke="#C9C9D2" stroke-width="1.3"/>'
                 f'<text x="{w/2}" y="{h/2 - (5 if sub else -4)}" text-anchor="middle" font-size="11.5" font-weight="600" fill="#1D1D22">{label}</text>'
                 + (f'<text x="{w/2}" y="{h/2+12}" text-anchor="middle" font-size="10" fill="#5E5E68">{sub}</text>' if sub else '') + '</g>')
    def band(x, y, w, h, label, gi):
        o.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="14" fill="{GTINT[gi]}" opacity=".45"/>'
                 f'<text x="{x+16}" y="{y+21}" font-size="10.5" font-weight="700" fill="{GCOL[gi]}" letter-spacing=".06em">{label.upper()}</text>')
    def arrow(d, c="#A9A9B6", m="bm"):
        o.append(f'<path class="edge" d="{d}" fill="none" stroke="{c}" stroke-width="1.6" marker-end="url(#{m})"/>')

    # lane 1 - what the kernel is given
    band(24, 40, 1064, 96, "what the kernel is handed", 8)
    plain(44, 64, 124, 52, "100,000 tokens", "the KV cache")
    plain(196, 64, 140, 52, "Lightning Indexer", "scores every position")
    plain(364, 64, 136, 52, "top-K = 2,048", "scattered indices")
    box(528, 62, 196, 56, "dsa-kernel", "sparse attention kernel", "QK \u2192 softmax \u2192 PV", 8, big=True)
    plain(752, 64, 124, 52, "one output vector", "per query token")
    box(904, 62, 164, 56, "b200-hardware", "on a B200", "148 SMs \u00b7 228 KB each", 8)
    for a, b in ((168, 196), (336, 364), (500, 528), (724, 752), (876, 904)):
        arrow(f"M{a},90 L{b},90")

    # lane 2 - the bottleneck
    band(24, 158, 1064, 86, "the bottleneck it starts with", 8)
    o.append('<text x="48" y="206" font-size="12.5" font-weight="600" fill="#1D1D22">the 2,048 entries are scattered, not a slice</text>')
    o.append('<text x="48" y="226" font-size="11" fill="#5E5E68">sparse attention removes arithmetic and replaces it with irregular memory access \u2014 every optimisation below answers that</text>')
    o.append('<rect x="700" y="176" width="368" height="52" rx="9" fill="#FFFFFF" stroke="#DF9C9C" stroke-width="1.4"/>')
    o.append('<text x="884" y="198" text-anchor="middle" font-size="11.5" font-weight="600" fill="#1D1D22">8 blocks on 148 SMs</text>')
    o.append('<text x="884" y="215" text-anchor="middle" font-size="10" fill="#B5605F">\u2248 5% of the GPU has work \u00b7 a block never leaves its SM</text>')

    # lane 3 - the four versions
    band(24, 266, 1064, 228, "four versions, four different bottlenecks", 9)
    lad = [("wmma-tensor-cores", "v1 \u00b7 WMMA", "make the arithmetic fast", 600),
           ("cp-async-buffering", "v2 \u00b7 cp.async", "overlap the gather", 470),
           ("split-k", "v3 \u00b7 Split-K", "fill the whole GPU", 95),
           ("autotune-polish", "v4 \u00b7 autotune", "measure, do not guess", 57)]
    BASE, SC = 474, 0.125
    for i, (tid, lab, sub, lat) in enumerate(lad):
        x = 48 + i * 262
        box(x, 298, 236, 58, tid, lab, sub, 9, big=True)
        h = max(7, lat * SC)
        o.append(f'<rect x="{x}" y="{BASE - h:.0f}" width="236" height="{h:.0f}" rx="4" fill="{GTINT[9]}" stroke="{GCOL[9]}" stroke-width="1.3"/>')
        o.append(f'<text x="{x+118}" y="{BASE - h - 7:.0f}" text-anchor="middle" font-size="11.5" font-weight="650" fill="#1D1D22" font-family="IBM Plex Mono, monospace">~{lat} \u00b5s</text>')
        if i < 3:
            arrow(f"M{x+240},327 L{x+258},327")
    o.append(f'<line x1="48" y1="{BASE}" x2="1064" y2="{BASE}" stroke="#C9C9D2"/>')
    o.append('<text x="1064" y="290" text-anchor="end" font-size="10" fill="#5E5E68">bar height = measured latency, lower is better</text>')

    # lane 4 - correctness
    band(24, 516, 1064, 96, "and the state that makes v3\u2019s split legal", 10)
    box(48, 542, 300, 56, "online-softmax-merge", "online softmax merge", "what v3\u2019s 256 blocks merge into", 10, big=True)
    o.append('<rect x="380" y="542" width="684" height="56" rx="9" fill="#FFFFFF" stroke="#C9C9D2" stroke-width="1.3"/>')
    o.append('<text x="722" y="564" text-anchor="middle" font-size="11.5" font-weight="600" fill="#1D1D22">softmax(A \u222a B) \u2260 softmax(A) + softmax(B)</text>')
    o.append('<text x="722" y="582" text-anchor="middle" font-size="10" fill="#5E5E68">so each block keeps sufficient statistics \u2014 (M, LSE, O) \u2014 instead of a normalised answer: the same state FlashAttention carries tile to tile</text>')

    defs = ('<defs><marker id="bm" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" '
            'orient="auto-start-reverse"><path d="M0,1 L9,5 L0,9 z" fill="#A9A9B6"/></marker>'
            '<marker id="bm2" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" '
            'orient="auto-start-reverse"><path d="M0,1 L9,5 L0,9 z" fill="#5B6CB0"/></marker></defs>')
    return f'<svg id="bwsvg" class="mapsvg" viewBox="0 0 1112 634" xmlns="http://www.w3.org/2000/svg">{defs}{"".join(o)}</svg>'


# ---------------------------------------------------------------- foundations map (learning path + roadmap)
ROADMAP = [
 ("Training well", 12, [
   ("Initialisation", "Xavier / He, and why the scale of random weights decides whether signals survive depth"),
   ("Normalisation", "BatchNorm, LayerNorm, RMSNorm \u2014 keeping activations at a fixed scale so gradients stay usable"),
   ("Regularisation", "dropout, weight decay, early stopping \u2014 why a model that fits the training set can still be wrong"),
   ("Schedules & batch size", "warm-up, cosine decay, the batch-size\u2013learning-rate rule, gradient clipping"),
   ("Mixed precision & the loop", "bf16, loss scaling, gradient accumulation \u2014 the training loop as it is actually written")]),
 ("The transformer", 11, [
   ("Tokenisation & embeddings", "BPE, the embedding table, why the vocabulary is a design choice"),
   ("Positional encoding", "sinusoidal, learned, RoPE \u2014 how a set of vectors learns to be a sequence"),
   ("Attention", "already written up in the Infrastructure area \u2014 revisit it from the forward-pass side"),
   ("The transformer block", "attention + MLP, residual connections, pre-norm \u2014 one layer, then N of them"),
   ("Pretraining objective", "next-token prediction, perplexity, scaling laws"),
   ("Fine-tuning", "SFT, LoRA, RLHF / DPO \u2014 what changes after pretraining")]),
 ("Classic ML, for interviews", 12, [
   ("Linear & logistic regression", "the perceptron with a proper loss; closed form vs gradient descent"),
   ("Bias, variance, overfitting", "train/val/test, cross-validation, what the learning curves say"),
   ("Loss functions", "MSE, cross-entropy, softmax with many classes, hinge, contrastive"),
   ("CNNs and RNNs", "weight sharing, receptive fields, why sequences moved to attention")]),
]

def foundations_svg():
    o = []
    def box(x, y, w, h, tid, label, sub, gi, big=False):
        col, tint = GCOL[gi], GTINT[gi]
        fs = 13 if big else 11.5
        o.append(f'<g class="node" data-go="{tid}" transform="translate({x},{y})">'
                 f'<rect class="nbox" width="{w}" height="{h}" rx="9" fill="{tint}" stroke="{col}" stroke-width="1.4"/>'
                 f'<text class="nt" x="{w/2}" y="{h/2 - (5 if sub else -4)}" text-anchor="middle" font-size="{fs}" font-weight="600" fill="#1D1D22">{label}</text>'
                 + (f'<text class="ns" x="{w/2}" y="{h/2+12}" text-anchor="middle" font-size="10" fill="#5E5E68">{sub}</text>' if sub else '')
                 + '</g>')
    def todo(x, y, w, h, label, sub):
        o.append(f'<g transform="translate({x},{y})"><rect width="{w}" height="{h}" rx="9" fill="#FFFFFF" stroke="#C9C9D2" stroke-width="1.3" stroke-dasharray="5 4"/>'
                 f'<text x="{w/2}" y="{h/2 - (5 if sub else -4)}" text-anchor="middle" font-size="11.5" font-weight="600" fill="#5E5E68">{label}</text>'
                 + (f'<text x="{w/2}" y="{h/2+12}" text-anchor="middle" font-size="10" fill="#8B8B95">{sub}</text>' if sub else '')
                 + f'<rect x="{w-44}" y="-8" width="40" height="15" rx="7" fill="#F1F1F4" stroke="#C9C9D2"/>'
                 + f'<text x="{w-24}" y="3" text-anchor="middle" font-size="8.5" font-weight="700" fill="#8B8B95" letter-spacing=".06em">TO DO</text></g>')
    def plain(x, y, w, h, label, sub=""):
        o.append(f'<g transform="translate({x},{y})"><rect width="{w}" height="{h}" rx="9" fill="#FFFFFF" stroke="#C9C9D2" stroke-width="1.3"/>'
                 f'<text x="{w/2}" y="{h/2 - (5 if sub else -4)}" text-anchor="middle" font-size="11.5" font-weight="600" fill="#1D1D22">{label}</text>'
                 + (f'<text x="{w/2}" y="{h/2+12}" text-anchor="middle" font-size="10" fill="#5E5E68">{sub}</text>' if sub else '') + '</g>')
    def band(x, y, w, h, label, gi, dim=False):
        o.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="14" fill="{GTINT[gi]}" opacity="{".2" if dim else ".45"}"/>'
                 f'<text x="{x+16}" y="{y+21}" font-size="10.5" font-weight="700" fill="{GCOL[gi] if not dim else "#8B8B95"}" letter-spacing=".06em">{label.upper()}</text>')
    def arrow(d, c="#A9A9B6", m="fm"):
        o.append(f'<path class="edge" d="{d}" fill="none" stroke="{c}" stroke-width="1.6" marker-end="url(#{m})"/>')

    # lane 1 - the path so far
    band(24, 40, 1064, 120, "the path so far \u2014 one tiny network, carried through seven pages", 11)
    path = [("perceptron", "1 \u00b7 a neuron", "a line, from mistakes", 11),
            ("forward-pass", "2 \u00b7 a network", "matmul, bend, matmul", 11),
            ("activation-functions", "3 \u00b7 the bend", "ReLU, GELU, softmax", 11),
            ("backprop", "4 \u00b7 the gradient", "chain rule, backwards", 12),
            ("autodiff", "5 \u00b7 autodiff", "what backward() records", 12),
            ("sgd", "6 \u00b7 mini-batches", "the gradient you can afford", 12),
            ("optimizers", "7 \u00b7 the update", "GD \u2192 momentum \u2192 Adam", 12)]
    for i, (tid, lab, sub, gi) in enumerate(path):
        x = 48 + i * 150
        box(x, 70, 138, 58, tid, lab, sub, gi, big=False)
        if i < 6: arrow(f"M{x+140},99 L{x+146},99")
    o.append('<text x="48" y="150" font-size="10.5" fill="#5E5E68">the same example on every page: x = (1.0, 0.5), y = 1 \u00b7 forward gives L = 0.693 \u00b7 backprop gives eight gradients \u00b7 one step gives L = 0.599</text>')

    # lane 2 - training well (to do)
    band(24, 182, 1064, 104, "training well \u2014 to do", 12, dim=True)
    tw = ROADMAP[0][2]
    for i, (lab, sub) in enumerate(tw):
        x = 48 + i * 212
        short = {"Initialisation": "random weights at the right scale", "Normalisation": "BatchNorm \u00b7 LayerNorm \u00b7 RMSNorm",
                 "Regularisation": "dropout \u00b7 weight decay", "Schedules & batch size": "warm-up, cosine, clipping",
                 "Mixed precision & the loop": "bf16 \u00b7 the real training loop"}[lab]
        todo(x, 214, 188, 52, lab.replace("&", "&amp;"), short)
    o.append('<path class="edge" d="M1017,128 C1017,160 1017,160 1017,182" fill="none" stroke="#A9A9B6" stroke-width="1.6" marker-end="url(#fm)"/>')

    # lane 3 - the transformer (to do, attention exists)
    band(24, 308, 1064, 104, "the transformer \u2014 to do, except attention", 11, dim=True)
    tr = [("Tokenisation &amp; embeddings", "BPE \u00b7 the embedding table"), ("Positional encoding", "sinusoidal \u00b7 RoPE"),
          None, ("The transformer block", "attention + MLP + residual + norm"), ("Pretraining objective", "next token \u00b7 scaling laws"), ("Fine-tuning", "SFT \u00b7 LoRA \u00b7 RLHF / DPO")]
    for i, it in enumerate(tr):
        x = 48 + i * 176
        if it is None:
            box(x, 340, 160, 52, "self-attention", "Attention", "written \u2014 in Infrastructure", 0)
        else:
            todo(x, 340, 160, 52, it[0], it[1])
    for i in range(5):
        x = 48 + i * 176
        arrow(f"M{x+162},366 L{x+174},366")

    # lane 4 - classic ML chips
    band(24, 434, 1064, 62, "classic ML, for interviews \u2014 to do", 12, dim=True)
    cx = 48
    for lab, sub in ROADMAP[2][2]:
        w = len(lab) * 6.6 + 22
        o.append(f'<g transform="translate({cx},460)"><rect width="{w:.0f}" height="24" rx="12" fill="#FFFFFF" stroke="#C9C9D2" stroke-dasharray="4 3"/>'
                 f'<text x="{w/2:.0f}" y="16" text-anchor="middle" font-size="11" font-weight="600" fill="#5E5E68">{lab.replace("&","&amp;")}</text></g>')
        cx += w + 12

    defs = ('<defs><marker id="fm" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" '
            'orient="auto-start-reverse"><path d="M0,1 L9,5 L0,9 z" fill="#A9A9B6"/></marker></defs>')
    return f'<svg id="fsvg" class="mapsvg" viewBox="0 0 1112 512" xmlns="http://www.w3.org/2000/svg">{defs}{"".join(o)}</svg>'

def roadmap_html():
    out = ['<div class="roadmap"><h2 class="sec">Next up \u2014 the roadmap</h2>'
           '<p class="rmlede">What the next batches will cover, in the order they should be learned. Each becomes a step-through page like the five above.</p>']
    for title, gi, items in ROADMAP:
        li = "".join(f'<li><b>{a.replace("&","&amp;")}</b><span>{b}</span></li>' for a, b in items)
        out.append(f'<div class="rmgroup" style="--ac:{GCOL[gi]}"><h3>{title}</h3><ol>{li}</ol></div>')
    out.append('</div>')
    return "".join(out)

# ---------------------------------------------------------------- pages
def topic_html(t):
    gi = t["g"]
    rel = "".join(
        f'<li><a href="#/{r}" class="rel"><span class="reldot" style="background:{GCOL[[x["g"] for x in T if x["id"]==r][0]]}"></span>'
        f'<b>{[x["title"] for x in T if x["id"]==r][0]}</b><span>{why}</span></a></li>'
        for r, why in t["rel"])
    tr = "".join(f'<li><b>{a}</b>{("<span>"+b+"</span>") if b else ""}</li>' for a, b in t["trade"])
    m = MODS[t["id"]]
    d = D[t["id"]]
    dd = (f'<details class="dd ex"><summary>A worked example \u2014 {d["ex"][0]}</summary>'
          f'<div class="ddb">{d["ex"][1]}</div></details>')
    dd += "".join(f'<details class="dd"><summary>{h}</summary><div class="ddb"><p>{b}</p></div></details>'
                  for h, b in d["deep"])
    return f'''<section class="pane" id="pane-{t["id"]}" hidden>
<div class="phead" style="--ac:{GCOL[gi]};--tint:{GTINT[gi]}">
  <div class="eyebrow">{GROUPS[gi][0]}</div>
  <h1>{t["title"]}</h1><p class="tagline">{t["tag"]}</p>
</div>
<p class="lede">{t["intro"]}</p>
<div class="pq">
  <div class="pqcard"><h3>The problem</h3><p>{t["problem"]}</p></div>
  <div class="pqcard solve"><h3>What it buys you</h3><p>{t["solves"]}</p></div>
</div>
<h2 class="sec">How it works</h2>
<p class="method">{t["method"]}</p>
<div class="vizwrap" style="--ac:{GCOL[gi]}">
  <div class="vizhead"><b>{m["title"]}</b><span>{m["sub"]}</span></div>
  <div class="stage"><svg viewBox="{m["vb"]}" xmlns="http://www.w3.org/2000/svg">{m["svg"]}</svg></div>
  <div class="cap"><span class="capnum" id="num">1 / 1</span><span class="captxt" id="cap"></span></div>
  <div class="ctl"><button id="prev">←&nbsp; Back</button><button id="play">▶ Play</button>
    <button id="next">Next &nbsp;→</button><div class="dots" id="dots"></div></div>
</div>
<div class="says"><span>Say this</span><p>{t["say"]}</p></div>
{FIGS.get(t["id"], "")}
<h2 class="sec">Going deeper</h2>
<div class="ddgrp" style="--ac:{GCOL[gi]}">{dd}</div>
<div class="two">
  <div><h2 class="sec">How it connects</h2><ul class="rels">{rel}</ul></div>
  <div><h2 class="sec">What it costs</h2><ul class="trades">{tr}</ul></div>
</div>
</section>'''

def nav_html(area):
    out = []
    for gi, (g, gsub, ga) in enumerate(GROUPS):
        if ga != area: continue
        out.append(f'<div class="navgroup"><div class="navtitle" style="color:{GCOL[gi]}">{g}</div>'
                   f'<div class="navsub">{gsub}</div>')
        for t in T:
            if t["g"] == gi:
                out.append(f'<button class="nav" data-v="{t["id"]}" style="--ac:{GCOL[gi]}">'
                           f'<b>{t["title"]}</b><span>{t["tag"]}</span></button>')
        out.append('</div>')
    return "".join(out)

def cards_html(area):
    out = []
    for gi, (g, gsub, ga) in enumerate(GROUPS):
        if ga != area: continue
        items = "".join(
            f'<a class="card" href="#/{t["id"]}" style="--ac:{GCOL[gi]};--tint:{GTINT[gi]}">'
            f'<b>{t["title"]}</b><span>{t["tag"]}</span></a>' for t in T if t["g"] == gi)
        out.append(f'<div class="cardgroup"><h3 style="color:{GCOL[gi]}">{g}</h3><div class="cardrow">{items}</div></div>')
    return "".join(out)

scripts = ""
for t in T:
    m = MODS[t["id"]]
    scripts += f'''\nVIZ["{t["id"]}"]=function(ROOT){{
function $(x){{return ROOT.querySelector('[id="'+x+'"]')}}
function o(id,v){{var e=$(id);if(e)e.style.opacity=v}}
function mv(id,x,y){{var e=$(id);if(e)e.setAttribute('transform','translate('+x+','+y+')')}}
function cl(id,c,on){{var e=$(id);if(e)e.classList[on?'add':'remove'](c)}}
function tx(id,t){{var e=$(id);if(e)e.textContent=t}}
function fill(id,c){{var e=$(id);if(e)e.setAttribute('fill',c)}}
function stroke(id,c){{var e=$(id);if(e)e.setAttribute('stroke',c)}}
{m["js"]}
{ENGINE}
return {{go:go,stop:stop}};}};'''
open("_parts.json", "w").write(json.dumps(dict(
    home=home_svg(), agents=agents_svg(), blackwell=blackwell_svg(), foundations=foundations_svg(), roadmap=roadmap_html(),
    nav=[nav_html(0), nav_html(1), nav_html(2), nav_html(3)], cards=[cards_html(0), cards_html(1), cards_html(2), cards_html(3)],
    panes="".join(topic_html(t) for t in T), scripts=scripts,
    ids=[t["id"] for t in T],
    topicarea={t["id"]: GROUPS[t["g"]][2] for t in T},
    areas=[list(a) for a in AREAS], vcss=VCSS)))
print("parts built:", len(T), "topics")
