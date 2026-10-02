# Per-topic depth: a worked example, and two or three "going deeper" notes.
D = {}

D["self-attention"] = dict(
 ex=("Resolving what a word refers to",
  "<p><em>“The cat that chased the mouse was hungry.”</em> When the model processes <b>hungry</b>, "
  "that token emits a query meaning roughly <em>who is this about?</em> It scores highly against the key "
  "of <b>cat</b> and weakly against <b>mouse</b>, so the value it pulls in is mostly cat's.</p>"
  "<p>Nothing told the model that <em>cat</em> is the subject. The match between one token's query and "
  "another's key is the entire mechanism — which is why attention is the part that resolves pronouns, "
  "agreement and long-range reference.</p>"),
 deep=[("Why three projections instead of using the hidden state directly",
   "If you compared raw hidden states, matching would collapse into plain similarity — a token could only "
   "attend to tokens that look like itself. Separate Q and K projections let the model learn an "
   "<em>asymmetric</em> relation: <b>hungry</b> can ask for a subject without resembling one."),
  ("Why divide by √d",
   "Dot products of d-dimensional vectors grow with d. Without the scaling, scores get large, softmax "
   "saturates to nearly one-hot, and gradients through it vanish. The divisor keeps the logits in a range "
   "where softmax stays soft and trainable."),
  ("What the interviewer usually asks next",
   "“Why is it quadratic?” Because every query meets every key — S² pairs, each a d-dimensional dot product. "
   "That single fact is the origin of FlashAttention, sparse attention, linear attention, and most of the "
   "long-context literature.")])

D["full-vs-linear-attention"] = dict(
 ex=("The question a fixed-size state cannot answer",
  "<p><em>“What was the variable named on line 200?”</em> Full attention treats this as a lookup: there is a "
  "key for that token and the query can match it exactly, however far back it sits.</p>"
  "<p>Linear attention has folded line 200 into a single fixed-size state along with everything else, so the "
  "name survives only as a blend. It will produce something plausible rather than something exact. Ask "
  "instead <em>“what is this document about?”</em> and the compressed summary answers perfectly well, at "
  "constant cost however long the document is.</p>"),
 deep=[("Where the linear form comes from",
   "Softmax attention cannot be reassociated because the softmax sits between Q·Kᵀ and V. Replace it with a "
   "feature map φ so scores become φ(q)·φ(k), and the computation reassociates: instead of (QKᵀ)V you compute "
   "Q(KᵀV). KᵀV is a fixed-size matrix independent of sequence length — that matrix <em>is</em> the recurrent state."),
  ("Why hybrids exist",
   "Retrieval-shaped work (copying an exact token, following a reference) is what a compressed state does "
   "worst. Interleaving a few full-attention layers among many linear ones recovers that ability while keeping "
   "most of the cost saving — which is why most published “linear” models are not purely linear."),
  ("The honest comparison",
   "Linear attention is not a strict improvement. It trades an exact, addressable memory for a lossy summary. "
   "If your workload is long-context retrieval, that trade is bad; if it is long-context summarisation, it is good.")])

D["flashattention"] = dict(
 ex=("The matrix that never needed to exist",
  "<p>For a long sequence, the score matrix of a single attention head can be far larger than all the fast "
  "on-chip memory available. The naive path writes that whole thing to slow memory, reads it back to apply "
  "softmax, writes the result out again, then reads it once more to multiply by V.</p>"
  "<p>But every one of those numbers is needed exactly <b>once</b>, on its way to the output. FlashAttention "
  "loads a tile, folds it into a running total, and throws it away. Same arithmetic, same answer — the data "
  "simply never makes the round trip.</p>"),
 deep=[("How online softmax stays exact",
   "Softmax normally needs the whole row before it can divide by the sum. Instead, carry a running max <em>m</em> "
   "and running sum <em>ℓ</em>. When a new tile arrives with a larger max, rescale the accumulated output by "
   "exp(m_old − m_new) before adding the new contribution. The correction is exact, so the final result is "
   "bit-for-bit what the naive version produces."),
  ("Why recomputation can be the cheaper option",
   "In the backward pass FlashAttention recomputes the attention tiles rather than storing them. That is more "
   "FLOPs but far less memory traffic — and since the kernel is bandwidth-bound, trading arithmetic for traffic "
   "is a win. It is the same reasoning as the forward pass, applied to gradients."),
  ("FA1 vs FA2 vs FA3",
   "FlashAttention-1 introduced the tiled, fused, IO-aware formulation. FlashAttention-2 kept the idea and fixed "
   "how work is partitioned across warps and thread blocks, cutting non-matmul overhead. Later versions target "
   "newer hardware features. The <em>idea</em> has not changed since FA1 — the implementations got better at "
   "feeding the GPU.")])

D["prefill-vs-decode"] = dict(
 ex=("Summarising a long document",
  "<p>You paste a long report and ask for a short summary. <b>Prefill</b> reads the entire report in one pass — "
  "a big, efficient piece of work, and what the user experiences as the wait before anything appears.</p>"
  "<p><b>Decode</b> then emits the summary one token at a time. Each step does almost no arithmetic but must "
  "re-read the model weights and the whole cache, so the pace of text appearing is set by memory speed. Flip the "
  "shape — a short prompt with a long answer — and the cost moves almost entirely into decode.</p>"),
 deep=[("Arithmetic intensity is the real distinction",
   "Prefill multiplies a big matrix by a big matrix: many FLOPs per byte moved, so the GPU is well fed. Decode "
   "multiplies a matrix by a single vector: the same weights are read to do a fraction of the work. That ratio — "
   "FLOPs per byte — is what makes one compute-bound and the other bandwidth-bound."),
  ("Why batching helps decode but not prefill",
   "Batching decode turns vector-matrix products back into matrix-matrix products, amortising the weight read "
   "across many requests — the whole reason continuous batching exists. Prefill is already compute-saturated, so "
   "batching it adds little and can hurt latency."),
  ("Chunked prefill, and why schedulers care",
   "A long prefill run in one piece blocks every in-flight decode step. Splitting it into chunks interleaved with "
   "decode keeps token streams smooth at a small throughput cost — the same problem prefill–decode disaggregation "
   "solves by moving the phases apart entirely.")])

D["kv-cache"] = dict(
 ex=("Generating the five-hundredth token",
  "<p>Without a cache, producing token 500 means pushing the previous 499 tokens through every layer again, just "
  "to rebuild keys and values identical to last time. With a cache you compute one token's worth of work and read "
  "the rest.</p>"
  "<p>The catch shows up with concurrency. One long conversation's cache is manageable; a hundred simultaneous "
  "long conversations can need more memory than the model weights themselves — and when the GPU fills, the server "
  "has to queue or evict, so the symptom users see is not slowness but <b>rejected requests</b>.</p>"),
 deep=[("Reading the size formula",
   "Memory ≈ 2 · L · S · N<sub>kv</sub> · d<sub>head</sub> · bytes. The 2 is K and V; L is layers; S is sequence "
   "length; N<sub>kv</sub> is KV heads. Everything is linear, which is what makes the levers obvious: halve the KV "
   "heads (GQA) or halve the bytes (quantise to fp8/int8) and you halve the cache."),
  ("Why it is the capacity limit, not the compute limit",
   "Weights are a fixed cost paid once. The KV cache is a per-request cost that grows with every token generated, "
   "so as concurrency rises it is the cache — not FLOPs — that fills the card first. This is why serving papers "
   "talk about memory almost exclusively."),
  ("What you can do when it does not fit",
   "Four levers, in rough order of how often they are used: fewer KV heads (GQA/MQA), fewer bits per entry "
   "(quantisation), better allocation (PagedAttention), and less history to store at all (eviction, compaction, or "
   "a sliding window).")])

D["mha-gqa-mqa"] = dict(
 ex=("The same model, three cache sizes",
  "<p>Take a model with 32 query heads. Under <b>MHA</b> it stores 32 keys and values per token. Under <b>MQA</b>, "
  "one. Under <b>GQA</b> with 8 groups, eight — a quarter of MHA's cache.</p>"
  "<p>That quarter is not an abstract saving: it is roughly four times as many concurrent users on the same GPU, "
  "or four times the context length for one user. MQA would save more still, but collapsing 32 heads onto a single "
  "shared key/value is where quality starts to show strain — which is why 8 is the sort of number real models pick.</p>"),
 deep=[("What is actually lost",
   "Query heads sharing a KV head can still weight it differently — their queries differ — but they can no longer "
   "attend to <em>different things</em>. Heads within a group are forced to look at the same set of keys, which "
   "removes some of the specialisation multi-head attention exists to provide."),
  ("It interacts with tensor parallelism",
   "Under TP, heads are split across GPUs. With very few KV heads, either some GPUs hold no KV head at all or the "
   "KV must be replicated — so the KV-head count is not a free parameter; it is constrained by how you plan to shard."),
  ("Why it is decided at training time",
   "Unlike batching or paging, this is architectural. You cannot convert an MHA checkpoint to GQA without "
   "retraining or at least a distillation-style conversion step, which is why it is chosen with serving economics "
   "already in mind.")])

D["paged-attention"] = dict(
 ex=("You cannot know how long an answer will be",
  "<p>One request asks for a yes-or-no answer; the next asks for a long essay. Both arrive looking identical. "
  "Reserving the worst case for every request wastes most of the memory; reserving too little means a request dies "
  "halfway through.</p>"
  "<p>Blocks dissolve the problem — each request claims another block only when it actually needs one. The bonus: "
  "two chat sessions that open with the same system prompt can <b>point at the same blocks</b> rather than each "
  "holding a copy.</p>"),
 deep=[("The operating-system analogy, and where it stops",
   "Block table ≈ page table; KV block ≈ page; the allocator ≈ the OS memory manager. The difference is that there "
   "is no swap — a GPU cannot page to disk cheaply — so when blocks run out the system must preempt a request and "
   "recompute its cache later, rather than transparently faulting it back in."),
  ("Why block size is a real tuning decision",
   "Large blocks mean less bookkeeping but more waste in the final partly-filled block. Small blocks waste less but "
   "add indirection and kernel overhead. Typical values are a handful of tokens per block — small enough that "
   "internal fragmentation is negligible."),
  ("Copy-on-write makes branching cheap",
   "Sharing blocks is what lets parallel samples from one prompt, or beam-search branches, share a prefix instead of "
   "duplicating it. When one branch diverges, only the block it writes to is copied.")])

D["continuous-batching"] = dict(
 ex=("One long request holding up seven short ones",
  "<p>A batch of eight requests starts together. Seven finish quickly; one is writing a long document and keeps going.</p>"
  "<p>With a fixed batch, those seven slots sit <b>empty</b> until the long one finishes — the GPU doing a fraction "
  "of the work it could. With continuous batching, each slot is refilled from the queue the moment it frees up, so "
  "the long request stops being everyone else's problem.</p>"),
 deep=[("What makes it possible at all",
   "Decode steps are independent across requests: each one reads its own KV cache and produces one token. Nothing "
   "couples request A's step to request B's, so membership can change between iterations without breaking anything. "
   "Paged KV is what makes joining and leaving cheap in memory terms."),
  ("Admission control is the hard part",
   "Adding a request needs KV capacity for its whole future, which you cannot know. Admit too eagerly and you run out "
   "mid-generation and must preempt someone; admit too cautiously and the GPU idles. Real schedulers reserve "
   "headroom and can preempt-and-recompute the newest request when they guess wrong."),
  ("What it does to your latency numbers",
   "Throughput rises, but per-request latency becomes dependent on load. A p50 measured on an idle server tells you "
   "nothing about production. This is why serving benchmarks quote latency <em>at a given throughput</em>, not alone.")])

D["prefix-caching"] = dict(
 ex=("A coding agent on its twentieth step",
  "<p>Every call this agent makes begins the same way: system prompt, tool definitions, repository context. Only the "
  "tail — the latest action and its result — is new. Without prefix caching, step 20 re-prefills that entire preamble "
  "from scratch, as it did on all nineteen previous steps.</p>"
  "<p>The fragility is worth remembering: change <b>one character</b> near the start — inject a timestamp, reorder the "
  "tool list — and the shared prefix ends there, so the reuse mostly disappears. Keeping the volatile parts of a "
  "prompt at the <b>end</b> is a real engineering decision.</p>"),
 deep=[("Why a radix tree rather than a hash map",
   "A hash map can only answer “have I seen this exact prompt?” A radix tree over token sequences answers the "
   "question you actually have: “what is the longest prefix of this prompt that I have already computed?” Branches "
   "naturally share their common ancestors, so many conversations sharing one system prompt store it once."),
  ("It is not free memory-wise",
   "Cached prefixes occupy the same KV memory that running requests need, so the cache needs an eviction policy — "
   "typically LRU with a bias toward keeping long, widely-shared prefixes, since those are the expensive ones to rebuild."),
  ("Where it changes system design",
   "Because reuse depends on an exact match, prompt construction becomes a caching problem: stable instructions "
   "first, per-request content last, and no timestamps or randomised ordering near the top. It also gives the router "
   "a reason to send a request to a <em>specific</em> replica — cache affinity."),
  ("Compaction is its natural enemy",
   "A prompt that only ever grows at the tail is a perfect cache workload \u2014 every request is a prefix of the next. Context compaction rewrites the middle, which invalidates everything after the edit. In one measured agent run the append-only baseline served 70% of prompt tokens from cache and the compacted run managed 57%. Both techniques are right; they just pull against each other, and raw token counts overstate what compaction actually saves.")])

D["service-mesh"] = dict(
 ex=("Where the mesh stops and the engine starts",
  "<p>A request arrives at the gateway and the mesh picks one of three healthy inference replicas. That is the last "
  "decision the mesh makes.</p>"
  "<p>Inside that replica, an entirely separate scheduler decides which requests share the next decode iteration, "
  "which KV blocks to allocate, and when to admit a queued request. The mesh has no visibility into any of it — which "
  "is exactly why LLM-aware routing has to be added on top.</p>"),
 deep=[("Data plane vs control plane",
   "The data plane (Envoy sidecars) carries actual traffic and must be fast. The control plane (Istio) never touches a "
   "request — it distributes configuration. If the control plane dies, existing proxies keep routing with their last "
   "known config; that split is the point of the design."),
  ("Why LLM traffic strains the usual assumptions",
   "Mesh defaults assume short, uniform, idempotent requests. LLM calls are long-lived and streamed, so a default "
   "timeout can kill a legitimate generation, and a retry can duplicate expensive work. Timeouts, retry policy and "
   "streaming support all need revisiting."),
  ("What it gives you that is genuinely hard otherwise",
   "Uniform mTLS between services, consistent retry and circuit-breaking, and per-service traffic telemetry — without "
   "shipping that logic in every application in every language you use.")])

D["load-balancing"] = dict(
 ex=("When “least connections” picks wrong",
  "<p>Replica A: five active requests, 70% utilised — but it already caches the 15K-token prefix this request shares. "
  "Replica B: two active requests, 40% utilised, no useful cache.</p>"
  "<p>Least-connections sends it to B, which must prefill all 15K tokens. The cache-aware router sends it to A, reuses "
  "the prefix, and prefills only the new tail. A is busier and still cheaper. The catch worth volunteering: if every "
  "request with that prefix routes to A, A becomes a hotspot.</p>"),
 deep=[("Why queue length is a poor proxy",
   "Two requests in a queue could be 100 tokens or 100K. Without prompt length, expected output length and KV "
   "pressure, a count tells you almost nothing about how long the queue will take to drain."),
  ("Estimating output length",
   "Nobody knows how long a generation will be, so routers approximate: request type, prompt shape, historical "
   "averages per endpoint, or an explicit max_tokens. Getting it wrong is survivable — the router only needs to rank "
   "replicas, not predict precisely."),
  ("The tension to name out loud",
   "Cache affinity pulls traffic toward one replica; load balancing pushes it apart. Production routers blend them — "
   "affinity as a strong preference, overridden once a replica's pressure crosses a threshold.")])

D["pd-disaggregation"] = dict(
 ex=("A 20K prompt and a 500-token answer",
  "<p>On a shared pool, that 20K-token prefill monopolises the GPU while it runs, and every other user's tokens pause.</p>"
  "<p>Disaggregated: a prefill worker builds the KV cache, ships it to a decode worker, and that worker streams the 500 "
  "tokens while the prefill pool moves on to the next prompt. Nobody's stream stutters. The bill: a 20K-token KV cache "
  "is large, and it crossed the network to get there.</p>"),
 deep=[("Do the transfer arithmetic before believing the design",
   "The KV cache to move is roughly 2 · L · S · N<sub>kv</sub> · d<sub>head</sub> · bytes — for a long prompt this is "
   "gigabytes. On NVLink or InfiniBand that is milliseconds; over ordinary Ethernet it can exceed the prefill you were "
   "trying to protect. This is why the technique appears in large deployments and not small ones."),
  ("It lets the two pools differ in kind",
   "Prefill wants raw compute; decode wants memory bandwidth and capacity. Once separated you can give them different "
   "GPU types, different batch policies, even different parallelism strategies — impossible when one pool does both."),
  ("Layer-wise streaming hides some of the cost",
   "The transfer does not have to wait for the whole prefill to finish: each layer's KV can start moving as soon as it "
   "is computed, overlapping transfer with the remaining compute.")])

D["model-parallelism"] = dict(
 ex=("Why TP stays inside the node",
  "<p>With TP=4, four GPUs split every layer's matrices and must combine partial results at each one — many times per "
  "forward pass. Put those four on NVLink inside one node and it works; stretch them across a slower network and "
  "communication dominates, making four GPUs slower than one would have been if the model fit.</p>"
  "<p>With PP=4, GPU 0 holds layers 1–20, GPU 1 holds 21–40, and data crosses only at the three boundaries. That "
  "tolerates a slower link — which is why the common layout is TP within a node, PP across nodes.</p>"),
 deep=[("Row-parallel and column-parallel, and why they pair",
   "Splitting a weight matrix by columns lets each GPU compute an independent slice of the output with no "
   "communication. Splitting the next matrix by rows means each GPU consumes exactly the slice it already holds, and "
   "one AllReduce at the end combines the result. Transformer MLP and attention blocks are deliberately arranged as a "
   "column-parallel layer followed by a row-parallel one, so each block costs one collective rather than two."),
  ("What each strategy costs in memory",
   "TP shards weights <em>and</em> activations, so it reduces per-GPU memory the most. PP shards weights by layer but "
   "each stage must hold activations for every in-flight micro-batch. EP shards only the expert weights — attention "
   "layers are still replicated or TP-sharded."),
  ("Why real systems combine all three",
   "A large MoE model might run TP=8 inside a node, PP=4 across nodes, and EP across the whole cluster. The dimensions "
   "are orthogonal; the art is matching each one's communication pattern to the link that can carry it.")])

D["pipeline-bubble"] = dict(
 ex=("Four stages, one batch versus four micro-batches",
  "<p>One batch of 64 through four stages: stage 1 works while 2, 3 and 4 wait; then stage 2 works while the rest wait. "
  "Three quarters of the hardware is idle at any moment.</p>"
  "<p>Split it into four micro-batches of 16 and after a short warm-up all four stages are busy on different "
  "micro-batches at once. Same total work, most of the idle time gone — but each stage is now doing a smaller, less "
  "efficient chunk, which is the trade you accept.</p>"),
 deep=[("The bubble fraction, roughly",
   "With <em>p</em> stages and <em>m</em> micro-batches, the pipeline spends about (p−1) steps filling and (p−1) "
   "draining out of roughly (m + p − 1) total — so the wasted fraction is approximately (p−1)/(m+p−1). Push m well "
   "above p and it shrinks; it never reaches zero."),
  ("What 1F1B is actually for",
   "The naive schedule runs all forwards then all backwards, so every micro-batch's activations are held "
   "simultaneously — peak memory scales with m. One-forward-one-backward starts backward passes as soon as possible, "
   "so activations are freed early and peak memory scales with p instead. It is a memory optimisation, not a speed one."),
  ("Interleaved stages trade communication for a smaller bubble",
   "Giving each GPU several non-contiguous chunks of layers instead of one contiguous block shortens the fill and "
   "drain, at the cost of more boundary crossings — worth it when the interconnect can absorb them.")])

D["nccl-collectives"] = dict(
 ex=("The four, concretely",
  "<p>Two GPUs holding <code>[1,2]</code> and <code>[3,4]</code>: <b>AllReduce</b> → both end with <code>[4,6]</code>. "
  "<b>AllGather</b> → both end with <code>[1,2,3,4]</code>. <b>ReduceScatter</b> → one keeps <code>4</code>, the other "
  "keeps <code>6</code>.</p>"
  "<p><b>All-to-All</b> is the odd one: each GPU sends a <em>different</em> chunk to each destination. In MoE, tokens "
  "scatter to whichever GPUs host their chosen experts, then a second All-to-All brings the results home — which is why "
  "MoE performance lives and dies on interconnect quality.</p>"),
 deep=[("Why ring AllReduce is the standard implementation",
   "A ring moves each shard around the GPUs in two passes — reduce-scatter then all-gather — so every GPU sends "
   "roughly 2(N−1)/N of the data regardless of how many GPUs there are. Bandwidth cost is near-constant in N; only "
   "latency grows. That is why AllReduce = ReduceScatter + AllGather is an implementation fact, not just an identity."),
  ("Latency-bound vs bandwidth-bound collectives",
   "Small tensors are dominated by per-hop latency, so tree algorithms win. Large tensors are dominated by bandwidth, "
   "so ring algorithms win. NCCL picks per call based on size and topology — which is why a microbenchmark at one "
   "message size can badly mispredict real performance."),
  ("Overlap is where the real wins are",
   "Communication that cannot be removed can often be hidden: launch the collective on a separate stream and keep "
   "computing while it runs. Gradient bucketing in data-parallel training exists precisely so that AllReduce for early "
   "layers overlaps with the backward pass of later ones.")])

D["agent-context-growth"] = dict(
 ex=("A thirty-step debugging agent",
  "<p>The agent reads a file, runs the tests, reads the failure log, edits, re-runs. Each step appends its observations "
  "— and a single test log or source file can dwarf everything said so far.</p>"
  "<p>By step 30 the model is re-reading the output of steps 1 through 29 to decide one more action, and most of it is "
  "long dead: a file it already fixed, a log it already diagnosed. The cost per step keeps climbing even though the "
  "<em>useful</em> state — what is broken and what has been tried — stays small.</p>"),
 deep=[("Where the quadratic comes from",
   "If each step appends d tokens, call t carries about d·t tokens, so the total across T calls is "
   "d(1+2+…+T) = d·T(T+1)/2 — quadratic in <em>steps</em>, even though the history itself only grows linearly. "
   "Conflating those two quantities is the classic mistake."),
  ("Caching and compaction fix different problems",
   "Caching removes the cost of re-reading history that is still present; the window fills at exactly the same rate. "
   "Compaction removes the history itself. If you are hitting a cost ceiling, cache. If you are hitting the context "
   "limit, only compaction helps."),
  ("Designing against drift",
   "Compaction discards silently, and you find out several steps later. Practical mitigations: keep a structured "
   "summary the agent maintains deliberately rather than a free-text one, keep artifact references rather than "
   "artifact contents, and keep the failed approaches — re-trying a ruled-out fix is the most common drift symptom."),
  ("What the ratio actually looks like",
   "In one measured coding run the agent spent 463,000 prompt tokens against 13,000 completion tokens \u2014 roughly 35 to 1. The bill is for re-reading, not for thinking, which is why every lever in this section targets the prompt rather than the generation.")])

D["agent-checkpointing"] = dict(
 ex=("The payment that must not run twice",
  "<p>An agent charges a card, then crashes before recording the result. On resume it re-reads its plan: “step 7, "
  "charge the card — not marked complete.” With no durable action record it charges again.</p>"
  "<p>With an idempotency key written <b>before</b> the call and reconciled after, the runtime can ask the payment "
  "provider whether that key already succeeded, and skip it. This is why a state machine matters: “we sent it and "
  "don't know the outcome” is a different state from “we never sent it”.</p>"),
 deep=[("Snapshot, replay, or both",
   "Pure replay rebuilds state by re-running an event log — exact, but slow and dangerous if events had side effects. "
   "Pure snapshots are fast but lose everything since the last one. Production systems take periodic snapshots and "
   "replay only the log since, which bounds both recovery time and loss."),
  ("Write the intent before the action",
   "The durable record has to exist <em>before</em> the side effect, not after — otherwise the crash window between "
   "acting and recording is exactly the case you cannot recover from. Write “about to charge, key=abc”, then charge, "
   "then reconcile."),
  ("What belongs in a checkpoint and what does not",
   "In: goal, plan, step status, pending action and approval state, artifact references, environment handles. Out: "
   "the full transcript, and anything reconstructible. A checkpoint that grows with the conversation has become "
   "another context problem."),
  ("Outcome metrics hide process failures",
   "A run can reach a correct final state while a quarter of its steps produced no action at all. Grading only the outcome misses that entirely. Inspect trajectories for the behaviour you care about \u2014 steps with no tool call, repeated identical actions, retries after a permanent failure \u2014 and A/B the <em>harness</em>, not just the model, because the interface is as much of the system as the weights are.")])

D["mcp"] = dict(
 ex=("The layers in one call",
  "<p>You ask an agent to file an issue. The <b>model</b> emits a function call: <code>create_issue(repo, title, body)</code> "
  "— that is function calling. The <b>orchestrator</b> checks permissions and approval, then routes it through the "
  "<b>MCP client</b> to a GitHub <b>MCP server</b>, which translates it into a real GitHub API call.</p>"
  "<p>Swap GitHub for Linear and the model's half is unchanged — a different server handles it. That substitutability "
  "is the entire point. Note also that MCP bypasses nothing: permission and sandbox checks still belong to the "
  "orchestrator.</p>"),
 deep=[("Tools, resources and prompts are not the same thing",
   "A <b>tool</b> is an action with side effects the model may choose to call. A <b>resource</b> is addressable data "
   "the host can read into context without the model deciding anything. A <b>prompt</b> is a reusable template the "
   "server offers. Conflating tools and resources is the most common misreading of the protocol."),
  ("Discovery is what makes it a protocol",
   "A host can ask a server what it offers at runtime and present those capabilities to the model, instead of having "
   "them hard-coded at build time. That is the difference between a standard and a convention — and it is what turns "
   "N×M integrations into N+M."),
  ("The security surface it creates",
   "Every connected server widens what the agent can reach, and tool descriptions are text the model reads — so a "
   "malicious server can attempt to influence behaviour through them. Permission checks, approval gates and treating "
   "server-supplied text as untrusted data remain the host's responsibility.")])

D["rag-vs-memory"] = dict(
 ex=("The same question, two retrievals",
  "<p>“Fix the flaky test in the payments module.”</p>"
  "<p><b>RAG</b> pulls the module's source, the test file, and the framework docs — external knowledge, equally "
  "available to anyone. <b>Memory</b> pulls “we tried bumping the timeout last week and it did not help” and “this "
  "user wants the root cause, not a retry” — things that exist only because of prior interaction.</p>"
  "<p>Drop RAG and the agent lacks the code. Drop memory and it cheerfully re-tries the timeout fix it already ruled out.</p>"),
 deep=[("Memory needs a write policy; RAG does not",
   "Documents already exist — nobody decided they were worth writing for the agent's benefit. Memories must be "
   "<em>chosen</em>, which adds a whole problem RAG never has: what, when, and at what granularity to save, and when "
   "to overwrite something now false."),
  ("Why retrieval quality dominates both",
   "The model can only use what enters the context. Chunk boundaries that split a function in half, or an embedding "
   "that matches on topic rather than intent, fail silently — the answer looks confident and is simply missing the "
   "relevant material. Hybrid retrieval (lexical + semantic) exists because each covers the other's blind spot."),
  ("Memory can compound its own errors",
   "A wrong conclusion written once gets retrieved forever, and each retrieval makes it look better established. "
   "Practical defences: store what was <em>observed</em> rather than what was concluded, timestamp entries, and allow "
   "later evidence to supersede rather than accumulate."),
  ("Why production coding agents do not use a vector database for the transcript",
   "Retrieval assumes the query resembles what you need. Much of what an agent must not forget fails that test: \u201cI already tried X and it failed\u201d has to be present regardless of what the next step is about, and nothing in that step\u2019s text would retrieve it. Summaries also preserve order and causality, which retrieved fragments lose \u2014 and retrieval hands back the raw output you were trying to shed. Retrieval does belong in coding agents, but on the <em>codebase</em>, not the transcript.")])

D["agent-loop"] = dict(
 ex=("Where each layer's responsibility actually sits",
  "<p>Ask an agent to fix a failing test. The <b>model</b> emits <code>run_tests(\"payments\")</code>. It does not run "
  "anything — it produces a decision.</p>"
  "<p>The <b>orchestrator</b> decides whether that is allowed, runs it in a sandbox, and enforces a timeout. This "
  "layer is yours to build; no model provides it. The <b>observation</b> comes back as 400 lines of stack trace — "
  "larger than the entire conversation so far. That asymmetry is why agent context behaves nothing like chat context.</p>"),
 deep=[("The loop is where the engineering lives",
   "Tool schemas, permission policy, sandboxing, retries, timeouts, budget limits, and the stopping rule are all code "
   "you write around the model. Improving the model rarely fixes a badly designed loop, which is why agent quality "
   "differs so much between products using the same model."),
  ("Stopping rules, and how they fail",
   "Common conditions: the goal is verifiably met, a step budget is exhausted, no progress across N steps, or a human "
   "must approve. Each fails differently — verification is often impossible, budgets truncate mid-task, and "
   "no-progress detection needs a definition of progress. Most production agents combine several."),
  ("Why observations dominate the budget",
   "In chat, both sides produce sentences. In an agent, one side produces sentences and the other produces files, "
   "logs and pages. Trimming, summarising or referencing observations rather than inlining them is usually the "
   "highest-leverage change available."),
  ("Hidden reasoning can quietly eat the context",
   "Some providers attach a full chain of thought to every response. Storing the whole response object in history resends all of it forever. One measured chess run carried 204,027 characters of reasoning against 7,585 characters of actual board observations \u2014 games took 31 minutes instead of 3.5. Reasoning is per-turn scratch work, not conversation: keep visible text and tool calls, drop the rest."),
  ("Parallel tool calls are safe on reads, unsafe on writes",
   "A model can emit several calls in one response, all chosen from the same picture of the world. If they only read, that is a free speed-up. If any of them writes, every call after the first was chosen from a world that no longer exists. The chess harness executes the first move and rejects the rest with an explanation, because the opponent has already replied.")])

D["coding-agent"] = dict(
 ex=("Why hypothesis-first beats edit-first",
  "<p><em>“The payments test fails intermittently.”</em></p>"
  "<p><b>Edit-first:</b> change three things that look suspicious, re-run, still fails. You now know less than when "
  "you started — which of the three was wrong?</p>"
  "<p><b>Hypothesis-first:</b> state the claim — “the retry path shares a connection pool across threads” — then make "
  "the single smallest change that tests it. Now the result carries information either way: it confirms the root "
  "cause, or rules it out cleanly and you move to the next hypothesis.</p>"),
 deep=[("Localization is the step that decides the outcome",
   "Empirically, most failures on repository benchmarks are localization failures, not editing failures: the model "
   "could have written the right patch if it had been looking at the right file. This is why retrieval quality and "
   "dependency-aware search matter more than raw code-generation ability."),
  ("Intermittent failures break the loop's core assumption",
   "The loop assumes the test result is a signal. A flaky test makes it noise — a passing run may mean nothing. "
   "Handling that means running repeatedly, seeding randomness, or isolating the nondeterminism before trusting any "
   "result at all."),
  ("What the sandbox is really protecting",
   "The agent runs shell commands it wrote itself against a repository it only partly understands. Scoped file "
   "access, no network by default, resource limits, and no credentials in the environment turn a destructive mistake "
   "into a failed step rather than an incident."),
  ("How SWE-bench actually grades",
   "Each instance gives the repository before the fix, the issue text, and hidden tests. The grading is <b>two-sided</b>: <code>FAIL_TO_PASS</code> proves the bug is fixed, and <code>PASS_TO_PASS</code> proves nothing else broke. Only the pair is meaningful — the second is what catches an agent that made things green by deleting a test.")])

# ---- harness topics ----
D["message-protocol"] = dict(
 ex=("Why a broken call still needs a reply",
  "<p>The model emits <code>execute({\"cmd\": )</code> — malformed JSON. The tempting implementation raises, logs it, and moves on.</p>"
  "<p>But the assistant message with that tool call is already in the history, and the API requires every call to be answered. The next request is now structurally invalid and fails before the model sees anything.</p>"
  "<p>So the dispatcher returns a <em>string</em>: <code>{\"error\": \"Arguments were not valid JSON\"}</code>, carrying that call's id. The model reads it and fixes the call on the next step. Nothing raises.</p>"),
 deep=[("The assistant message is a commitment",
   "Once the model has emitted a tool call, the harness has no way to un-emit it. Every path out of the dispatcher — success, bad JSON, unknown tool, wrong argument type, non-zero exit — has to produce exactly one observation carrying that id. Treating it as a total function rather than one that can throw is the design."),
  ("Why cost is quadratic and not linear",
   "Step t resends everything from steps 1..t−1. If each step adds d tokens, the sum across T steps is d·T(T+1)/2. Completion tokens grow linearly; prompt tokens grow as the square. That is why one measured run showed 463k prompt against 13k completion — a ratio of about 35 to 1."),
  ("Provider-specific fields need a deliberate decision",
   "Some models attach hidden reasoning to every response. Storing the whole response object in history resends all of it forever. In one run that was 204,027 characters of reasoning against 7,585 characters of actual observations — the prompt was 96% scratch work. Keep visible text and tool calls; drop the rest.")])

D["context-compaction"] = dict(
 ex=("What five compactions actually bought",
  "<p>Same model, same prompts, same 200-step budget on <code>django__django-15368</code>. One run compacting at a 6,000-token threshold, one with compaction disabled.</p>"
  "<p><b>Compacted:</b> 44 steps, 5 compactions, 221,187 tokens, peak prompt 5,974. <b>Full context:</b> 39 steps, 475,642 tokens, peak prompt 24,463. Both produced a patch that resolved the instance.</p>"
  "<p>Half the tokens and a quarter of the peak — while taking five <em>more</em> steps and paying for five extra summariser calls. The baseline climbs about 600 tokens per step and never comes down, so its total is the area under a rising line.</p>"),
 deep=[("Merge the memory, never stack it",
   "Each compaction is handed the <em>previous</em> working memory along with the new prefix, and told to drop what later steps made obsolete. A memory that only appends recreates the exact problem it was built to solve — it just grows more slowly."),
  ("Render the prefix as text before summarising",
   "The summariser reads a readable transcript, not raw JSON message objects. It is a one-off rendering cost that buys a markedly better summary, because the model is being asked to read a conversation rather than parse a data structure."),
  ("Check the summariser's finish_reason",
   "Two of five summaries in the measured run came back with finish_reason <code>length</code> — they hit the 1,200-token output cap mid-sentence and the tail was lost. Nothing failed, nothing logged an error, and the run still succeeded. Either raise the cap or keep more recent steps verbatim, but first make the truncation visible.")])

D["error-policy"] = dict(
 ex=("The 17-million-token retry loop",
  "<p>A chess game hit its 200-step limit having played only 22 moves. The other 165 steps produced nothing at all.</p>"
  "<p>The sandbox had reached its 30-minute lifetime and been reclaimed mid-game. Every subsequent move returned a transport error — correctly formatted as a recoverable observation — and the model dutifully tried again, 165 times, at roughly 100k tokens of prompt each time.</p>"
  "<p>The error policy had no notion of a failure the model cannot possibly fix. An illegal move is the model's problem; a dead environment is not.</p>"),
 deep=[("Probe, then abort — and keep a backstop",
   "On a transport failure, ask the environment whether it is still alive and abort with a clear message if it is not. Add a five-consecutive-failure backstop for the case the probe itself succeeds over a dead tunnel. Illegal moves never increment the counter, and any success resets it."),
  ("The two failure modes are symmetric",
   "Too eager to recover gives an infinite loop billed by the token. Too eager to crash gives brittleness — a single flaky network call kills a run that would have succeeded on retry. Both are error-policy bugs; only the first one is expensive enough to notice immediately."),
  ("This is where checkpointing earns its keep",
   "A deliberate abort is only cheap if the run can resume. Terminating on a dead sandbox and then starting the whole task over is not much better than retrying. The termination condition and the checkpoint are two halves of the same design.")])

D["observation-budget"] = dict(
 ex=("A two-line catalogue against a 4,771-character body",
  "<p>A skill is a folder with a <code>SKILL.md</code> whose frontmatter gives a name and a description. Loading it splits the file in two.</p>"
  "<p>The <b>catalogue entry</b> — two lines — goes into the system prompt on every request. The <b>full body</b>, 4,771 characters of strategy, is revealed only when the model calls <code>invoke_skill</code>.</p>"
  "<p>Ten skills therefore cost ten lines of prompt, not ten documents. And with no skills loaded, the agent is never told about the submission protocol at all — which is exactly what the tests check.</p>"),
 deep=[("Head-and-tail, not head",
   "Truncating a 120,000-character result to its first 10,000 throws away the end of the stack trace — usually the line that names the failure. Keeping the first and last 4,900 with an elision notice between them costs the same tokens and keeps the part that identifies the problem."),
  ("The same reasoning applies to tool descriptions",
   "Progressive disclosure is usually discussed for skills or documents, but a tool schema with a long description is the same cost in the same place. Anything carried in every request to describe a capability the agent might not use is a candidate for the split."),
  ("Which lever to reach for, diagnostically",
   "If a single step blew up the prompt, you need truncation. If the prompt crept up over forty steps, you need compaction. If the prompt was already large before the agent did anything, you need progressive disclosure. The symptom tells you which.")])

D["programmatic-tools"] = dict(
 ex=("Twenty-one round trips, or one step",
  "<p>A two-ply search over twenty candidate moves needs twenty <code>simulate_move</code> calls and one <code>play_move</code>. As individual tool calls that is 21 round trips, each a full model call resending the entire transcript.</p>"
  "<p>As a snippet it is one step: the code loops over the candidates, calls <code>simulate_move</code> inside the sandbox where it is just a function, keeps the best line, and calls <code>play_move</code> exactly once as its last statement.</p>"
  "<p>The tools still ran 21 times. The model was called once.</p>"),
 deep=[("It raises the ceiling, not just the speed",
   "The saving in round trips is the obvious part. The less obvious part is that procedures too long to spell out as individual calls become possible at all — a deeper search, a retry loop, a multi-stage transformation. The unit of work stops being the thing that limits the algorithm."),
  ("Re-read the world afterwards",
   "A snippet may have changed live state several times before returning. The harness cannot assume its cached picture is still accurate, so after every snippet it re-reads the environment. Skipping this is exactly the stale-state bug, just at procedure scale."),
  ("The debuggability cost is real",
   "A sequence of individual tool calls leaves a readable trail: you can see which call failed and what it returned. A failed snippet gives you one opaque observation. That is a genuine argument for keeping ordinary tool calls as the default and reaching for code only when the work is loop-shaped.")])

from _bwd import BD
D.update(BD)
from _mld import MD
D.update(MD)
