# Brian's ML Notes

Interactive notes on machine learning and AI infrastructure — forty mechanisms, from the
perceptron and backprop to attention, serving, agent systems and one CUDA kernel, each one a
step-through walkthrough rather than a wall of text.

**Live site:** https://haolingpu.github.io/ml-notes/

## What's here

Four areas, each with its own clickable map.

**Infrastructure** — one request's path through a serving stack: gateway, service mesh,
load balancer, prefill and decode, the attention internals, and the token stream back.

**Agents** — the loop that wraps the model: the model picks an action, the orchestrator
runs it, an observation returns, state updates, and round it goes. Plus the four problems
the loop creates, and a coding agent as a worked instance of it.

**Blackwell** — one CUDA kernel end to end: the NVIDIA MLSys 2026 sparse-attention project on
a B200, from what the kernel is handed through the four versions that took it from 600 µs to
57 — WMMA, cp.async, Split-K, autotuning — and the online-softmax merge that makes the split
mathematically legal.

**Foundations** — from one neuron to a trained network, with real numbers: one 2-2-1 network
carried from the perceptron through the forward pass, activation functions, backprop, autodiff,
mini-batch SGD and the optimizer, every value checkable by hand. Its map doubles as the roadmap: dashed boxes are the topics still to
write (training well, the transformer, classic ML).

Every box on any map is clickable and opens its own page.

Each concept page follows the same shape:

1. **Intro** — what this is, in two sentences
2. **The problem** — what goes wrong without it
3. **What it buys you** — the thing it actually solves
4. **How it works** — the mechanism, with a playable step-through animation
5. **Going deeper** — a worked example plus three collapsible notes: the mechanism behind
   the mechanism, the follow-up question an interviewer asks next, and the thing people get wrong
6. **How it connects** — links to the concepts it depends on or competes with
7. **What it costs** — the tradeoffs, stated plainly

### Topics

| Group | Concepts |
|---|---|
| Inside the model | self-attention · full vs linear attention · FlashAttention |
| One request, one GPU | prefill vs decode · KV cache · MHA/GQA/MQA · PagedAttention |
| Serving many requests | continuous batching · prefix caching · service mesh · LLM-aware load balancing · prefill–decode disaggregation |
| Across many GPUs | tensor/pipeline/expert parallelism · pipeline bubbles · GPU collectives |
| How an agent runs | the agent loop · coding agent architecture |
| What it carries | agent context growth · state and checkpointing |
| What enters the context | MCP · RAG vs memory |
| Building the harness | the prompt is the state · context compaction · error policy · three context levers · programmatic tool calling |
| The problem (Blackwell) | sparse attention as a kernel · the B200 and the one rule |
| Making it fast | WMMA and Tensor Cores · cp.async and double buffering · Split-K |
| Making it correct, then tuned | merging the splits · autotuning the split factor |
| From a neuron to a network | the perceptron · the forward pass · activation functions |
| Learning from mistakes | backpropagation · automatic differentiation · SGD and mini-batches · optimizers |

The harness topics carry measurements from a ReAct harness built for CMU 11-768 — token
counts, cache-hit rates and postmortems from real runs rather than estimates. The Blackwell
topics carry the measured latencies from the MLSys competition poster. The Foundations topics
share one worked example — x = (1.0, 0.5), y = 1 — whose forward values, gradients and first
update step are computed by hand and match what `loss.backward()` returns.

## Running it

`index.html` is fully self-contained — no build step, no dependencies, no network calls
except Google Fonts. Open it directly, or serve the folder:

```bash
python3 -m http.server 8000
```

## Rebuilding

The site is generated. Each visualization is a Python file that emits SVG plus a list of
steps; `assemble.py` stitches them into the single-page site.

```bash
cd src
python3 v_flash.py          # rebuild one visualization
python3 build.py            # collect topics + visualizations
python3 assemble.py         # emit dist/index.html
```

- `content.py` — the prose for every topic (intro, problem, tradeoffs, cross-links)
- `depth.py` — the worked example and deeper notes behind each topic's toggles
- `shell.py` — the shared step-through engine and styles
- `v_*.py` — one file per visualization
- `build.py` / `assemble.py` — page generation

## Deploying

Pushed to `main`, served by GitHub Pages from the repository root. `.nojekyll` stops Jekyll
from touching the output.
