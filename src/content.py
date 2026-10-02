# Topic content for Brian's ML Notes.
# (label, subtitle, area)   area 0 = Infrastructure, area 1 = Agents
GROUPS = [
 ("Inside the model", "how a transformer actually computes", 0),
 ("One request, one GPU", "what happens between a prompt and a token", 0),
 ("Serving many requests", "the machinery around the model", 0),
 ("Across many GPUs", "when one card is not enough", 0),
 ("How an agent runs", "the loop, and one real instance of it", 1),
 ("What it carries", "context and state across a long run", 1),
 ("What enters the context", "retrieval, memory, and reaching out", 1),
]
AREAS = [
 ("infra", "Infrastructure", "what happens between a prompt and a token"),
 ("agents", "Agents", "the loop that wraps the model"),
 ("blackwell", "Blackwell", "one CUDA kernel, 600 \u00b5s to 57"),
 ("foundations", "Foundations", "neuron \u2192 network \u2192 gradient \u2192 update"),
]

T = [
dict(id="self-attention", g=0, title="Self-attention", tag="how a word finds what it refers to",
 intro="Attention is the operation that lets one token pull information from another. Everything else in a transformer is scaffolding around it — and every efficiency technique later in these notes is a response to what it costs.",
 problem="A token's meaning depends on other tokens, but a neural network processes a fixed-size vector per position. Nothing in the word <em>hungry</em> tells you who is hungry.",
 solves="It lets every token ask a question and pull the answer from wherever it lives in the sequence — learned, not rule-based. This is what resolves pronouns, agreement and long-range reference.",
 method="Each token emits a <b>Query</b>, a <b>Key</b> and a <b>Value</b>. The query is compared against every key to produce scores; softmax turns those into weights; the output is the weighted sum of values. Q and K decide <em>routing</em>; V is the <em>payload</em>.",
 rel=[("flashattention","the same operation, made IO-efficient"),("kv-cache","caching K and V works because only they get reused"),("full-vs-linear-attention","what you give up by not storing every token"),("prefill-vs-decode","the quadratic term lives in prefill")],
 trade=[("Cost is quadratic in sequence length","every token is compared with every token, so doubling the context quadruples the attention work"),("Memory too","the score matrix is S×S, which is what FlashAttention refuses to materialise")],
 say="Q and K decide who attends to whom; V is what gets carried. That split is why you can cache K and V, and why RoPE only touches Q and K."),

dict(id="full-vs-linear-attention", g=0, title="Full vs linear attention", tag="keep every token, or keep a summary",
 intro="Two ways to store the past. Full attention keeps every token individually; linear attention folds them into one fixed-size state. The difference is a compression-versus-recall trade.",
 problem="Full attention pays for every token pair and stores every past key and value, so both cost and memory grow with the length of the sequence.",
 solves="Linear attention makes per-step cost constant and memory flat, so sequence length stops being the thing that limits you.",
 method="Reorder the computation around a feature map so the past collapses into a <b>recurrent state</b>. Each new key and value updates the state; each query reads from it. No explicit token-by-token score matrix ever forms.",
 rel=[("self-attention","the exact version this approximates"),("flashattention","exact and still quadratic — a different axis entirely"),("kv-cache","what linear attention replaces with a fixed-size state")],
 trade=[("Precise recall is lost","a fixed-size state blurs specific tokens — <em>what was the variable on line 200</em> is exactly what it is bad at"),("Broad questions still work","a summary answers <em>what is this document about</em> perfectly well, at constant cost"),("Hence hybrids","mostly linear layers with a few full-attention layers kept for the lookups that matter")],
 say="Full attention is lossless lookup at quadratic cost; linear attention is lossy lookup at constant cost."),

dict(id="flashattention", g=0, title="FlashAttention", tag="the matrix that never gets built",
 intro="An IO-aware, <b>exact</b> attention implementation. It does not change the result and does not reduce the arithmetic — it removes memory traffic, which turns out to be where the time actually went.",
 problem="Attention runs as several stages, and the huge S×S score and probability matrices get written to slow GPU memory between them — written, read, written, read. For a long sequence that matrix is larger than all the fast on-chip memory available.",
 solves="Every one of those numbers is needed exactly once on its way to the output, so none of them ever has to exist in HBM. Removing those round trips is a large wall-clock win at zero accuracy cost.",
 method="<b>Tile</b> Q, K and V into blocks that fit in SRAM. <b>Fuse</b> score → softmax → weighted-sum into one kernel so each tile is consumed immediately. Use an <b>online softmax</b> that carries a running max and normaliser, so the result stays exact tile by tile.",
 rel=[("self-attention","the operation being optimised"),("prefill-vs-decode","biggest effect on the compute-bound phase"),("full-vs-linear-attention","approximate alternatives — a different axis")],
 trade=[("No accuracy cost at all","it is exact, which is the whole point"),("Still quadratic","it removes IO, not arithmetic — saying otherwise fails the question"),("Extra FLOPs are sometimes traded for less traffic","recomputing in the backward pass can be cheaper than storing")],
 say="GEMMs were already tiled — that was never the problem. FlashAttention tiles and fuses <em>the whole attention operation</em>, and online softmax is what makes that legal."),

dict(id="prefill-vs-decode", g=1, title="Prefill vs decode", tag="one request, two different machines",
 intro="A single request has two phases that stress completely different parts of the hardware. Almost every serving technique targets one or the other, so naming the phase is the first step in any answer.",
 problem="Prefill reads the whole prompt at once and is limited by compute. Decode emits one token at a time and is limited by memory bandwidth. Treating them as one workload optimises neither.",
 solves="Separating them tells you which lever to pull: prefix caching and chunked prefill attack prefill; GQA, KV quantisation and larger batches attack decode.",
 method="<b>Prefill</b> processes every prompt token in parallel and builds the KV cache — big matmuls, hardware well fed. <b>Decode</b> then produces one token per step, doing almost no arithmetic but re-reading the weights and the whole cache each time.",
 rel=[("kv-cache","built by prefill, read by decode"),("pd-disaggregation","running the two phases on separate pools"),("continuous-batching","scheduling that mostly helps decode"),("prefix-caching","skipping prefill work entirely")],
 trade=[("Prefill sets time-to-first-token","the wait before anything appears"),("Decode sets time-per-output-token","the pace the text arrives at"),("The balance moves with workload","a long document with a short summary is nearly all prefill; a short question with a long essay is nearly all decode")],
 say="Prefill is throughput-shaped and compute-bound; decode is latency-shaped and bandwidth-bound. Name the phase before naming the fix."),

dict(id="kv-cache", g=1, title="KV cache", tag="what it saves, and what it costs",
 intro="The optimisation that makes autoregressive generation practical — and the single biggest consumer of GPU memory in a serving system. Almost everything in the serving section exists to manage it.",
 problem="Generation is autoregressive, so a naive implementation pushes the entire prefix through every layer again for each new token, rebuilding keys and values identical to last time.",
 solves="The past does not change, so its keys and values can be computed once and reused. Work per decode step goes from growing with the sequence to flat.",
 method="Each step computes Q, K and V for the <b>new token only</b>, appends its K and V to the cache, and attends across everything stored. Old queries are never reused — which is precisely why it is a K/V cache and not a Q cache.",
 rel=[("prefill-vs-decode","prefill builds it, decode reads it"),("mha-gqa-mqa","shrinking it by sharing KV heads"),("paged-attention","storing it without fragmentation"),("prefix-caching","reusing it across requests")],
 trade=[("Trades compute for memory","and memory is the scarcer resource in serving"),("Grows with length × concurrency","one long conversation is fine; a hundred can exceed the model weights themselves"),("When it fills, requests are rejected","not slowed — which is why capacity, not FLOPs, usually caps a deployment")],
 say="Only K and V are cached because old queries are never reused. The KV cache is why serving is a memory problem."),

dict(id="mha-gqa-mqa", g=1, title="MHA, GQA and MQA", tag="shrinking what decode has to read",
 intro="Three arrangements of the same attention mechanism, differing only in how many query heads share a set of keys and values. It is a serving decision that got made inside the architecture.",
 problem="Decode is bandwidth-bound and the KV cache is the thing being read every step — so the size of that cache directly sets how fast tokens come out and how many users fit on a card.",
 solves="Sharing KV heads across groups of query heads cuts the cache substantially while keeping enough query heads for the model to stay expressive.",
 method="<b>MHA</b> gives every query head its own KV head. <b>MQA</b> gives all of them one. <b>GQA</b> groups them — a handful of KV heads shared across groups. A model with 32 query heads and 8 KV groups holds a quarter of MHA's cache.",
 rel=[("kv-cache","the thing being shrunk"),("prefill-vs-decode","the win lands on the decode side"),("nccl-collectives","head layout interacts with tensor parallelism")],
 trade=[("Fewer KV heads means less representational freedom","MQA can measurably hurt quality; GQA mostly does not"),("A quarter of the cache is roughly four times the concurrency","or four times the context for one user"),("It is baked in at training time","unlike most serving choices, you cannot change it later")],
 say="GQA sits at the knee of the curve — near-MHA quality at close to MQA memory."),

dict(id="paged-attention", g=1, title="PagedAttention", tag="why KV memory is stored in blocks",
 intro="Virtual memory, applied to the KV cache. It changes nothing about how attention is computed and everything about how many requests fit on a GPU.",
 problem="Requests have unpredictable lengths. Reserving a contiguous worst-case region for each one wastes most of it, and when requests finish they leave holes that no new request fits into — classic fragmentation.",
 solves="Removing reservation waste and fragmentation, so nearly all of the memory does real work. It also makes prefix sharing cheap, which is what prefix caching is built on.",
 method="Store KV in fixed-size <b>blocks</b> with a per-request block table, so a request's cache no longer has to be contiguous. It claims another block only when it needs one, and two requests sharing a prompt can point at the <b>same blocks</b>.",
 rel=[("kv-cache","the thing being stored"),("prefix-caching","block sharing is what makes reuse cheap"),("continuous-batching","requests join and leave freely because blocks are freed incrementally")],
 trade=[("Needs a custom attention kernel","one that can follow the indirection"),("Bookkeeping overhead","block tables and an allocator to maintain"),("Pure capacity win","it makes nothing faster — it stops memory being wasted")],
 say="PagedAttention is about <em>where KV lives</em>, not how attention is computed."),

dict(id="continuous-batching", g=2, title="Continuous batching", tag="rescheduling every decode step",
 intro="Iteration-level scheduling. The insight is not a faster kernel but a better moment to make the decision.",
 problem="Generation lengths vary wildly. A fixed batch runs until its slowest member finishes, so a batch of eight where seven finish early leaves seven slots idle while one long request runs.",
 solves="Keeping the GPU saturated on variable-length work. Throughput rises substantially without any individual request getting faster.",
 method="Re-decide batch membership at <b>every decode iteration</b>. Finished requests are evicted immediately and waiting ones admitted in their place, so a slot never sits empty behind someone else's long answer.",
 rel=[("prefill-vs-decode","it is decode that gets scheduled this way"),("paged-attention","blocks are freed incrementally, which is what lets requests leave mid-batch"),("load-balancing","cluster-level routing sits above this")],
 trade=[("Scheduler complexity","admission, eviction and fairness all become real problems"),("Latency becomes contextual","a request's speed now depends on what else is running"),("Contrast with dynamic batching","which only picks when to launch, then runs to completion")],
 say="It is iteration-level scheduling rather than request-level. Nothing got faster — the hardware stopped waiting."),

dict(id="prefix-caching", g=2, title="Prefix caching", tag="reuse across requests, not within one",
 intro="Also called RadixAttention. The observation is simple: a token's KV depends only on the tokens before it, so an identical prefix always produces identical KV — no matter which request it belongs to.",
 problem="Agents, chat threads and tool-heavy prompts resend nearly the same preamble every call. The same system prompt, tool definitions and document context get prefilled again and again.",
 solves="Prefill cost and time-to-first-token collapse to the size of what is genuinely new, which for an agent on its twentieth step is a tiny fraction of the prompt.",
 method="Cached prefixes are indexed in a <b>radix tree</b>. A new request walks it to find the longest prefix already computed, reuses that KV, and prefills only the unmatched tail.",
 rel=[("kv-cache","reuse within one request — this extends it across requests"),("paged-attention","block sharing makes the reuse cheap"),("load-balancing","cache affinity is a routing signal"),("agent-context-growth","the workload that makes this matter most")],
 trade=[("Only exact prefix matches help","change one character near the start and the reuse ends there"),("So put volatile content last","a timestamp at the top of a system prompt destroys the whole benefit"),("Costs cache memory and an eviction policy","the tree is not free")],
 say="Cached tokens are still fully attended to. What is skipped is <em>recomputing</em> their K and V, not attending to them."),

dict(id="service-mesh", g=2, title="Service mesh", tag="routing between services",
 intro="The infrastructure layer that handles service-to-service communication. Worth knowing precisely because of where it <em>stops</em>.",
 problem="Once a platform runs many services and many replicas, every one of them needs retries, timeouts, health checks, TLS and routing. Reimplementing that inside each application is duplicated, inconsistent, and impossible to change centrally.",
 solves="Networking concerns move out of application code into infrastructure that can be configured in one place, so failover and routing policy change without touching any service.",
 method="A proxy — commonly <b>Envoy</b> — sits beside each service and handles its traffic: the <b>data plane</b>. A controller — commonly <b>Istio</b> — configures all those proxies centrally: the <b>control plane</b>.",
 rel=[("load-balancing","LLM-aware routing has to be added on top of this"),("continuous-batching","what happens once the request is inside a replica")],
 trade=[("Another hop and another moving part","latency and operational surface both grow"),("It knows nothing about LLM cost","prompt length, KV pressure and cache locality are invisible to it"),("Different granularity entirely","the mesh routes requests; the engine scheduler decides tokens")],
 say="A service mesh routes <em>between services</em>; the inference scheduler decides execution <em>inside one replica</em>."),

dict(id="load-balancing", g=2, title="LLM-aware load balancing", tag="why the busiest replica can be cheapest",
 intro="Ordinary load balancing assumes requests cost about the same. For LLM serving that assumption is wrong in a way that flips the routing decision.",
 problem="Two requests that look identical on arrival can differ by orders of magnitude in cost — prompt length, output length, prefill versus decode mix, KV pressure, and whether a replica already holds a reusable prefix.",
 solves="Routing on expected serving cost rather than connection count, which can cut prefill work dramatically by sending a request where its cache already lives.",
 method="Score replicas on signals a web balancer never needed: queue depth, GPU and KV-cache pressure, prompt length, estimated output length, and above all <b>prefix-cache affinity</b>.",
 rel=[("prefix-caching","the cache whose location drives the routing"),("service-mesh","the layer this sits on top of"),("pd-disaggregation","adds another routing dimension — which pool"),("kv-cache","the pressure signal being measured")],
 trade=[("Needs live telemetry from every replica","and a cost model that can be wrong"),("Affinity fights balancing","routing every shared-prefix request to one replica creates a hotspot"),("So real routers blend the two","and fall back once a replica saturates")],
 say="The least-busy server is not always the cheapest server. Route on estimated total serving cost."),

dict(id="pd-disaggregation", g=2, title="Prefill–decode disaggregation", tag="stopping the two phases fighting",
 intro="Take the prefill/decode distinction seriously enough to put them on different machines.",
 problem="On a shared pool a long prefill occupies the GPU while it runs, so every other user who was mid-answer stops receiving tokens. Their stream visibly stutters.",
 solves="Interference disappears, and each pool can be sized and tuned for its own bottleneck — compute on one side, memory bandwidth on the other — and scaled independently.",
 method="Prefill workers ingest the prompt and build the KV cache; that cache is <b>transferred over the interconnect</b> to a decode worker, which streams tokens out.",
 rel=[("prefill-vs-decode","the distinction this is built on"),("kv-cache","the thing that has to cross the network"),("load-balancing","routing now has to pick a pool as well as a replica"),("nccl-collectives","the interconnect that decides whether this pays off")],
 trade=[("The KV cache must cross the network on every request","pure overhead, and it is what decides whether this pays off"),("Compare with chunked prefill","same pool, prefill sliced and interleaved — less interference, nothing moves"),("So it is an interconnect question","fast links favour disaggregation; slow ones favour chunking")],
 say="Disaggregation removes interference but pays a transfer; chunked prefill reduces interference and moves nothing."),

dict(id="model-parallelism", g=3, title="Tensor, pipeline and expert parallelism", tag="three ways to cut a model",
 intro="When a model does not fit on one GPU it has to be split. There are three places to cut, and each creates a different communication pattern — which is what actually decides the choice.",
 problem="Weights and activations exceed a single GPU's memory, and every way of splitting introduces communication the single-GPU version never paid.",
 solves="Models far larger than one device become trainable and servable, provided the communication pattern matches the hardware topology.",
 method="<b>TP</b> splits the matrices inside a layer — GPUs cooperate on one layer and exchange partial results constantly. <b>PP</b> gives each GPU a different block of layers — data crosses only at stage boundaries. <b>EP</b> puts different MoE experts on different GPUs and routes tokens to the ones they selected.",
 rel=[("nccl-collectives","TP leans on AllReduce, EP on All-to-All"),("pipeline-bubble","the cost PP introduces"),("pd-disaggregation","another axis of splitting, at the request level")],
 trade=[("TP communicates constantly","so it belongs on the fast links inside one node"),("PP communicates rarely but bubbles","stages wait on each other"),("EP routing is data-dependent","a popular expert becomes a straggler everyone waits for")],
 say="TP splits tensors, PP splits layers, EP splits experts — and the choice follows the hardware topology, not preference."),

dict(id="pipeline-bubble", g=3, title="Pipeline bubbles and micro-batching", tag="keeping the stages full",
 intro="Pipeline parallelism is sequential by construction, so its first version wastes most of the hardware. Micro-batching is the fix, and it has its own cost.",
 problem="Stage 2 cannot start until stage 1 hands something over. With one batch in flight, exactly one stage is busy and the rest idle — the bubble.",
 solves="Keeping several micro-batches in flight overlaps the stages, so after a short warm-up all of them are working on different micro-batches at once.",
 method="Split the batch into <b>micro-batches</b> fed in back to back. Gradients accumulate across them before a single optimizer step, so correctness is unchanged. Schedules like <b>1F1B</b> interleave forward and backward passes to cut activation memory.",
 rel=[("model-parallelism","PP is what creates the bubble"),("nccl-collectives","gradient synchronisation across the pipeline")],
 trade=[("Smaller chunks are less efficient per GPU","smaller matrices use the hardware worse"),("More in-flight micro-batches means more stored activations","which is what 1F1B claws back"),("Warm-up and drain never disappear","the bubble shrinks toward zero but never reaches it")],
 say="PP creates the pipeline; micro-batches keep it full. You want many more micro-batches than stages."),

dict(id="nccl-collectives", g=3, title="GPU collectives", tag="four shapes of exchange",
 intro="Split a model across GPUs and they must constantly exchange tensors. Collectives are how that exchange is expressed so the library can use the whole topology at once.",
 problem="Done naively — point to point, one pair at a time — communication becomes the bottleneck and the extra GPUs stop paying for themselves.",
 solves="Topology-aware implementations that saturate NVLink, NVSwitch or the network, turning communication from the limiting factor into a manageable cost.",
 method="<b>AllReduce</b>: combine, everyone gets the full result. <b>AllGather</b>: collect shards, everyone ends with the whole. <b>ReduceScatter</b>: combine, each keeps one slice. <b>All-to-All</b>: everyone sends different data to everyone. Note that AllReduce = ReduceScatter + AllGather, which is how ring implementations are built.",
 rel=[("model-parallelism","TP leans on AllReduce, EP on All-to-All"),("pipeline-bubble","stage boundaries are communication points"),("pd-disaggregation","the interconnect that carries the KV transfer")],
 trade=[("Collectives synchronise","the slowest GPU sets the pace and one straggler stalls everyone"),("Scaling is bounded by interconnect, not FLOPs","this is the systems point to make"),("Topology dictates placement","which is why TP stays inside a node")],
 say="Match the collective to the parallelism: TP leans on AllReduce, EP leans on All-to-All."),

dict(id="agent-context-growth", g=5, title="Agent context growth", tag="why long loops get expensive",
 intro="An agent is a loop of model calls, each appending to a history that every later call re-reads. The cost behaviour surprises people because two quantities get conflated.",
 problem="The history grows linearly in steps, but since call <em>t</em> re-reads everything before it, the total input processed across the run grows <b>quadratically</b> in the number of steps.",
 solves="Separating <em>context size</em> (what one call sees) from <em>cumulative work</em> (what the run paid for) tells you which fix applies — and they are not interchangeable.",
 method="Two different levers. <b>Caching</b> avoids recomputing history that is still present — cost falls, the window still fills. <b>Compaction</b> summarises or drops old history — the bars actually come down.",
 rel=[("prefix-caching","the caching half of the fix"),("kv-cache","what is being reused"),("agent-checkpointing","structured state as an alternative to carrying raw history"),("full-vs-linear-attention","an architectural answer to the same pressure")],
 trade=[("Caching does not reduce the window","only the cost of re-reading it"),("Compaction risks drift","you discard something that turns out to matter, and find out several steps later"),("Agent context is observation-dominated","one test log can outweigh many turns of dialogue")],
 say="Caching fixes cost; compaction fixes window pressure. Diagnose which one you have before prescribing."),

dict(id="agent-checkpointing", g=5, title="Agent state and checkpointing", tag="surviving the interruption",
 intro="Long agent runs hit crashes, restarts, truncated context and human-approval waits. What you persist decides whether any of those means starting over.",
 problem="If the only record is conversation history, resuming means re-deriving where the agent was from a transcript — and if that transcript was truncated, the information is simply gone.",
 solves="Structured execution state makes resume mechanical: load the checkpoint, see which steps are done, carry on.",
 method="Checkpoint the goal and plan, completed and pending steps, key observations, artifacts touched, pending actions and approval state, and environment references. <b>Snapshot</b> saves state directly; <b>replay</b> rebuilds it from an event log; real systems combine both.",
 rel=[("agent-context-growth","structured state instead of unbounded history"),("mcp","the tool calls whose status must be tracked"),("rag-vs-memory","memory is knowledge; a checkpoint is progress")],
 trade=[("Costs writes and a schema to maintain","and deciding what to persist is genuinely hard"),("Too little and resume is impossible; too much and it becomes another context problem",""),("Irreversible actions are the hard part","track action IDs and idempotency keys, or recovery sends the email twice")],
 say="Memory is knowledge worth keeping, a checkpoint is execution progress, conversation history is the raw trace."),

dict(id="mcp", g=6, title="MCP", tag="standardising how agents reach the world",
 intro="The Model Context Protocol standardises the boundary between an agent runtime and external capabilities. It sits at a different layer from function calling, and that distinction is what gets tested.",
 problem="Every agent that wants GitHub, a database or a file system writes its own integration, each with its own auth, schema and failure modes. N agents times M services means N×M integrations.",
 solves="Wrapping each service once and teaching each agent the protocol once turns N×M into N+M, and makes servers substitutable between hosts.",
 method="A <b>host</b> contains an <b>MCP client</b> that speaks to an <b>MCP server</b> wrapping one external system. Servers expose <b>Tools</b> (actions), <b>Resources</b> (data) and <b>Prompts</b> (templates).",
 rel=[("agent-checkpointing","tool-call status is what has to survive a crash"),("rag-vs-memory","MCP can expose retrieval — that is integration, not strategy")],
 trade=[("Another layer and another process to run",""),("A standard interface can hide capabilities a native API exposes",""),("It widens what an agent can reach","a security surface, which is why permission checks stay with the orchestrator")],
 say="Function calling is the model deciding which tool and what arguments. MCP is how the runtime discovers and reaches it."),

dict(id="rag-vs-memory", g=6, title="RAG vs memory", tag="two retrievals, two questions",
 intro="Both put retrieved text into the working context and both may sit on the same vector store. What differs is the semantics of what is stored — and how each one fails.",
 problem="The working context is small and the candidates are vast: external corpora on one side, everything this agent has already learned and decided on the other.",
 solves="Knowing which one you need. RAG supplies knowledge the agent never had; memory supplies conclusions it already reached.",
 method="<b>RAG</b> asks <em>what external knowledge is relevant to this task?</em> — retrieving from docs, code or databases by vector search, BM25 or hybrid. <b>Memory</b> asks <em>what from earlier should persist?</em> — decisions, preferences, failed hypotheses.",
 rel=[("agent-checkpointing","memory is knowledge, a checkpoint is progress"),("mcp","how a retrieval capability gets connected"),("agent-context-growth","both spend the same scarce context")],
 trade=[("Both spend context on text that may not help",""),("RAG is only as good as its chunking and index",""),("Memory has a write problem RAG does not","documents already exist; memories must be chosen — and a wrong one gets retrieved forever")],
 say="RAG says what does the world know; memory says what did we learn. Same plumbing, different semantics."),
]

T = [t for t in T]  # keep order stable
T[0:0] = []  # no-op guard

AGENT_NEW = [
dict(id="agent-loop", g=4, title="The agent loop", tag="what an agent actually is",
 intro="An agent is not one model call. It is a loop — the model picks an action, something executes it, an observation comes back, and round it goes. Nearly every hard problem in agent systems comes from the loop rather than the model.",
 problem="A single model call can only answer from what it was given. It cannot look something up, run a test, check whether its answer was right, or take a second attempt informed by the first.",
 solves="Wrapping the model in a loop with tools turns prediction into something closer to work: the agent can act on the world, see what happened, and revise. It is also what makes the system expensive, stateful and risky.",
 method="Each turn: the <b>model</b> reads the context and emits an action; the <b>orchestrator</b> checks permissions and runs it in a sandbox; a <b>tool</b> executes; an <b>observation</b> returns; <b>state</b> updates. Then it repeats — often dozens of times — until a stopping rule fires.",
 rel=[("coding-agent","one real instance of this loop, end to end"),("agent-context-growth","what the observations do to your budget"),("agent-checkpointing","how the state survives an interruption"),("mcp","how the tool step reaches systems you do not own")],
 trade=[("Observations dominate the context","a single test log or file can outweigh many turns of dialogue"),("The orchestrator is code you write","permissions, approval gates and sandboxing are not provided by the model"),("Termination is a design decision","an agent without a clear stopping rule either quits early or burns budget rediscovering dead ends")],
 say="An agent is a model in a loop with tools, state and a stopping rule. The model reasons, the orchestrator controls, the tools act, and the observations are what make it expensive."),

dict(id="coding-agent", g=4, title="Coding agent architecture", tag="the verification loop",
 intro="A coding agent is the clearest instance of the agent loop, because its environment can answer back. Tests turn a guess into a fact, which is what separates it from retrieval plus generation.",
 problem="A real repository is orders of magnitude larger than any context window, so the agent cannot read it. And a plausible-looking patch is worth nothing — the only thing that counts is whether the change actually works without breaking anything else.",
 solves="Retrieval brings in only the code that matters; the verification loop replaces confidence with evidence. The deliverable is a patch plus proof that it passes.",
 method="<b>Search</b> the repo — grep and symbol search for exact names, semantic search for intent, dependency paths for what calls what. <b>Localize</b> to the code on the real execution path. <b>Hypothesise</b> a root cause <em>before</em> editing. Make the <b>smallest change</b> that tests it. <b>Run the tests</b>. A failure is a new observation, so go back to localization with more information.",
 rel=[("agent-loop","the general shape this specialises"),("rag-vs-memory","repo retrieval is RAG applied to code"),("agent-checkpointing","long runs need progress that survives a crash"),("agent-context-growth","every file read stays in the history")],
 trade=[("Localization quality dominates","get the wrong files and every step after it is wasted"),("Large speculative edits make failure uninterpretable","when tests still fail you cannot tell which part was wrong"),("Verification costs real time","running the suite is slow, and running only the targeted test risks silent regressions")],
 say="Search → localize → hypothesise → edit → test → replan. RAG retrieves and generates; a coding agent retrieves, acts, observes and repeats — the interactive verification loop is the whole difference."),
]
# splice the two new agent topics in front of the existing agent topics
_i = min(i for i, t in enumerate(T) if t["g"] >= 4)
T[_i:_i] = AGENT_NEW

# ---- area 1, group 7: building the harness (from the 11-768 assignment) ----
GROUPS.append(("Building the harness", "what a real implementation forces you to decide", 1))
GROUPS.append(("The problem", "sparse attention, and the machine it lands on", 2))
GROUPS.append(("Making it fast", "three versions, three different bottlenecks", 2))
GROUPS.append(("Making it correct, then tuned", "merging the pieces, and choosing the shape", 2))
GROUPS.append(("From a neuron to a network", "what a model computes, with real numbers", 3))
GROUPS.append(("Learning from mistakes", "how the numbers get better", 3))

HARNESS = [
dict(id="message-protocol", g=7, title="The prompt is the state", tag="four roles, one structural rule",
 intro="A chat completion is stateless: text in, text out. Everything an agent knows on step 40 is in the message list you rebuild and resend on step 40 — so memory, persistence and continuity are all properties of that list, not of the model.",
 problem="Because the whole transcript is resent every step, the context window becomes a hard ceiling on run length, and cost becomes the area under a rising curve — quadratic in steps rather than linear.",
 solves="Getting the protocol right is what makes everything downstream possible: tool results that the model can act on, errors it can correct, and a history that compaction can safely rewrite.",
 method="Four roles with rules the API enforces. <b>system</b> carries standing instructions (exactly one, first), <b>user</b> poses the task, <b>assistant</b> carries the model's text and its tool calls, and <b>tool</b> carries one observation tagged with the <code>tool_call_id</code> it answers.",
 rel=[("agent-loop","the loop this protocol serves"),("context-compaction","why the cut must land on an assistant boundary"),("error-policy","why a broken call still needs an answer"),("agent-context-growth","what resending everything costs")],
 trade=[("Every tool call must be answered","even a malformed one — an unanswered call makes the next request invalid, which is why errors return as text rather than raising"),("History cannot be cut at an arbitrary index","slice between an assistant message and its tool reply and the observation is orphaned"),("Prompt tokens dominate","one measured coding run spent 463k prompt tokens against 13k of completion — the bill is for re-reading, not thinking")],
 say="The prompt is the state, and the state is a budget. Nothing about an agent's memory lives in the model."),

dict(id="context-compaction", g=7, title="Context compaction", tag="the sawtooth, and its caching bill",
 intro="Rewriting the old part of a transcript into a written summary so the prompt stops growing. The interesting part is not the mechanism — it is what the summary is instructed to preserve, and the hidden cost it creates.",
 problem="A prompt that grows about 600 tokens a step and never comes down makes total cost quadratic, and eventually the context window ends the run outright.",
 solves="Capping the prompt turns that area from quadratic into roughly linear. Measured on a real SWE-bench instance: half the tokens and a quarter of the peak prompt, with both runs still producing a patch that resolved the issue.",
 method="At a threshold, the harness makes a <b>separate model call</b> — its own system prompt, no tools — whose only job is to write working memory. That replaces the old prefix; system and task messages and the recent steps stay verbatim. The cut lands on an assistant boundary, and each new memory <b>merges</b> the previous one rather than stacking on it.",
 rel=[("message-protocol","the boundary rule that constrains where you can cut"),("prefix-caching","the cache that compaction quietly invalidates"),("agent-context-growth","the problem it exists to solve"),("observation-budget","the lever it represents, among three")],
 trade=[("It fights prompt caching","an append-only prompt caches beautifully; rewriting near the front invalidates everything after it — cache hits fell from 70% to 57%, so the real saving is smaller than the token counts suggest"),("It is lossy by construction","what the summary is told to keep is the entire design — drop the failed approaches and the agent retries what it already ruled out"),("The summariser can be truncated silently","two of five summaries hit the output cap mid-sentence; the run still succeeded, which is what makes it dangerous")],
 say="Compaction is lossy by construction, so what the summary is told to preserve is the design. And name the caching tension unprompted — it is the difference between reading the docs and paying the bill."),

dict(id="error-policy", g=7, title="Error policy", tag="recoverable, or terminal",
 intro="Every failure an agent hits falls into one of two classes, and confusing them is expensive in both directions — too eager to recover gives an infinite loop, too eager to crash gives brittleness.",
 problem="A harness that treats all failures as recoverable will retry a permanently broken environment forever. One did exactly that: 165 wasted steps and 17.1 million tokens after a sandbox hit its lifetime limit mid-run.",
 solves="Separating the two classes turns that same failure into a single step, while still letting the model correct its own mistakes without human intervention.",
 method="<b>Failures the model can fix</b> — bad arguments, malformed JSON, an illegal move, a failing test — are formatted into the observation so it reads the error and corrects itself. <b>Failures nothing can fix</b> — the environment is gone — must <b>terminate</b>. On a transport error, probe whether the environment is alive before deciding which it is.",
 rel=[("agent-loop","where the policy is enforced"),("message-protocol","why a failed call still returns a string"),("agent-checkpointing","what has to survive a deliberate abort"),("coding-agent","failed tests are the recoverable kind")],
 trade=[("A health probe can itself lie","so add a consecutive-failure backstop — five in a row aborts even if the probe says fine"),("Recoverable failures must not count toward it","an illegal move is not evidence the world is broken, and any success resets the counter"),("Cost per retry is what makes it urgent","at 100k tokens a retry, a policy gap stops being untidy and becomes a bill")],
 say="Graceful degradation without a termination condition is an expensive infinite loop. Every retry policy needs to separate what the model can fix from what nothing can fix."),

dict(id="observation-budget", g=7, title="Three levers on the context", tag="truncation, compaction, disclosure",
 intro="Three different things flood a context window, and each needs its own lever. Reaching for only one is why “just summarise the history” is an incomplete answer to how you run an agent for hours.",
 problem="A single observation can swamp the prompt on its own; well-behaved observations still accumulate across forty steps; and the description of what the agent <em>can do</em> costs context in every request before any work happens.",
 solves="Bounding all three keeps a long run inside the window and keeps capability count independent of prompt size.",
 method="<b>Truncation</b> caps one result — keeping the <b>head and the tail</b>, because the end of a stack trace is the part that identifies the failure. <b>Compaction</b> bounds their accumulation. <b>Progressive disclosure</b> advertises each capability as a name plus one line and loads the full instructions only when the model asks — a two-line catalogue entry against a 4,771-character body.",
 rel=[("context-compaction","the middle lever, in detail"),("agent-context-growth","the pressure all three respond to"),("mcp","tool descriptions have the same problem"),("message-protocol","the list all of this is trimming")],
 trade=[("Truncation can cut the part that mattered","head-and-tail is a heuristic, not a guarantee"),("Progressive disclosure costs a round trip","the model must ask before it can act on the full instructions"),("They are complementary, not alternatives","naming all three is what separates a real answer from “summarise the history”")],
 say="Truncation bounds one observation, compaction bounds their accumulation, progressive disclosure bounds what you carry before work starts."),

dict(id="programmatic-tools", g=7, title="Programmatic tool calling", tag="code that composes the tools",
 intro="Instead of emitting one tool call per turn, the model writes a snippet that calls the tools as ordinary functions, and the harness runs it somewhere isolated. The unit of work stops being a round trip.",
 problem="One call per response caps how much a single step can do — which caps how deep a search or how long a procedure the agent can execute at all. A two-ply search over twenty candidates is 21 round trips, each resending the whole transcript.",
 solves="Collapsing those 21 round trips into one step. Loops, branching and search stop costing a model call each, so procedures too long to spell out as individual calls become routine.",
 method="The tools already exist as functions inside the sandbox. The model sends code — in the measured run, base64-encoded Python — that calls them in a loop, evaluates the results, and commits only the final choice as its last statement. The tools ran 21 times; the model was called once.",
 rel=[("agent-loop","the step this compresses"),("message-protocol","each round trip resends everything, which is what makes them expensive"),("coding-agent","the same idea, applied to a repository"),("error-policy","snippet failures are recoverable, sandbox death is not")],
 trade=[("You are executing model-written code","it belongs in the sandbox beside the tools, never in the agent process"),("The world may have moved","after a snippet runs, the harness must re-read state — the snippet may already have changed it"),("Harder to inspect","a failed procedure gives you one opaque observation instead of a readable trail of calls")],
 say="It changes the unit of work from a call to a procedure — the difference between an agent that takes twenty actions and one that runs an algorithm."),
]
T.extend(HARNESS)
from _bw import BW
T.extend(BW)
from _ml import ML
T.extend(ML)
