# -*- coding: utf-8 -*-
BD = {}

BD["dsa-kernel"] = dict(
 ex=("What K = 2,048 does and does not mean",
  "<p>A common misreading: <code>K = 2048</code> does <em>not</em> mean the context is 2,048 tokens long. It means each query receives 2,048 <b>selected</b> historical KV positions out of however many exist.</p>"
  "<p>The context can be 100,000 tokens. The Lightning Indexer scores all of them and keeps 2,048. Our kernel then does attention over those — and the indices it gets look like <code>[17, 831, 9201, 45002, 103, …]</code>, not <code>KV[0:2048]</code>.</p>"
  "<p>That difference — a set of indices rather than a slice — is the entire difficulty of the kernel.</p>"),
 deep=[("Is a “query” the user's question?",
   "No, and the confusion matters. A query here is an <b>attention query vector for one token</b>: the model projects a token's hidden state into a query and uses it to decide which past information should flow in. So <code>T = 8</code> means the kernel is processing eight query tokens — not eight user requests. That is why the benchmark's tiny T is a hardware problem rather than a product decision."),
  ("Did the kernel choose the 2,048 tokens?",
   "No. The kernel assumes the sparse indices already exist; selection happens upstream in the indexer. Saying this clearly scopes the work: everything we did is about performing attention over an arbitrary scattered index list efficiently, not about deciding which tokens are relevant."),
  ("Does gathering make the entries contiguous?",
   "Only on chip, and only for the current tile. The source stays scattered in HBM forever — gather pulls the currently needed subset into a small shared-memory tile where the layout is regular enough for Tensor Cores, and then pays the scatter again for the next tile. Which is why hiding the gather (cp.async) and having more warps to hide it behind (Split-K) are both worth doing."),
  ("QK, weights, PV — the vocabulary",
   "<code>QKᵀ</code> gives attention <b>scores</b>; <code>softmax(QKᵀ)</code> gives attention <b>weights</b>; <code>softmax(QKᵀ)V</code> is the attention <b>output</b>. The mental model worth carrying: QK decides where to look, PV collects the information.")])

BD["b200-hardware"] = dict(
 ex=("Eight blocks on a hundred and forty-eight processors",
  "<p>The benchmark launches with <code>T = 8</code> query tokens and one block per token. The scheduler places those eight blocks on eight SMs. There are 148.</p>"
  "<p>Nothing is wrong with the code. The GPU is not confused. It simply has no mechanism to help — a block cannot be divided and migrated, so the remaining 140 SMs have no work to take.</p>"
  "<p><code>8 / 148 ≈ 5%</code>. Every microsecond of optimisation inside the block is being applied to 5% of the machine.</p>"),
 deep=[("Why a block cannot span SMs",
   "The threads in a block need a single shared-memory allocation and a single <code>__syncthreads()</code> barrier domain. Both are SM-local resources. Splitting a block across two SMs would mean shared memory that spans two physical memories and a barrier across two schedulers — which is precisely the cost the block abstraction exists to avoid. The indivisibility is the price of shared memory being fast."),
  ("Shared memory is per-SM, not per-GPU",
   "Each SM has its own shared-memory resource (up to 228 KB on B200), and CUDA carves a private region of it for every resident block. Ordinarily blocks never see each other's (clusters, below, are the one exception). The practical consequence shows up everywhere in this project: more shared memory per block means fewer blocks resident per SM, which means fewer warps available to hide a stall."),
  ("Why more warps hide memory latency",
   "A warp that issues a scattered load and misses cache stalls for hundreds of cycles. If another warp is resident and ready, the scheduler issues from that one instead and the execution units stay busy. With regular, coalesced access this matters less; with a gather from arbitrary HBM addresses it matters a lot — which is why the final split kernel doubled its warp count."),
  ("The exception: thread block clusters",
   "Since Hopper, blocks can be grouped into a <b>cluster</b> that the hardware guarantees to schedule together on neighbouring SMs. Blocks in a cluster can read and write each other's shared memory directly — <b>distributed shared memory</b> — instead of round-tripping through global memory. On B200 the portable cluster size is 8 blocks, with 16 available as a non-portable option. It refines the picture rather than overturning it: each block still lives on exactly one SM; the cluster just lets neighbours reach across."),
  ("Local memory is not local",
   "When a thread needs more registers than it is allowed (at most 255), or indexes a per-thread array dynamically, the compiler <b>spills</b> to “local memory” — which is private to the thread but physically lives in global memory, cached in L1/L2. A spill-heavy kernel quietly turns its fastest storage into its slowest. <code>nvcc -Xptxas -v</code> reports spill bytes; it is worth checking whenever a kernel is mysteriously slow."),
  ("Occupancy is a means, not a metric",
   "It is tempting to treat high occupancy as the goal. It is not — it is one way to buy latency hiding. A kernel that is genuinely compute-bound gains nothing from more resident warps, and a kernel that spends shared memory on deeper buffering may be better off with fewer. The question is always which resource is actually idle.")])

BD["wmma-tensor-cores"] = dict(
 ex=("One instruction instead of a loop",
  "<p>A 16×16×16 matrix multiply-accumulate written with scalar arithmetic is thousands of fused multiply-adds, each costing an issue slot and register-file traffic.</p>"
  "<p><code>WMMA m16n16k16 BF16</code> hands that whole tile to dedicated hardware: one cooperative instruction per warp, operands in BF16, accumulation in FP32.</p>"
  "<p>We used it for <b>both</b> matmuls in attention — QK and PV — which is what made the arithmetic stop being the expensive part. And then the kernel was still 600 microseconds, because the arithmetic was never the expensive part.</p>"),
 deep=[("Why BF16 in, FP32 out",
   "Fewer bits per number means less data movement and much higher Tensor Core throughput, but accumulating thousands of products in low precision loses bits fast. The standard shape — low-precision multiply, higher-precision accumulate — keeps the throughput while holding the running sum stable. It is the same reason FlashAttention accumulates its softmax state in FP32."),
  ("The correctness bound is what limits precision tricks",
   "The competition required matching the BF16 reference within <code>abs_err</code> under 0.1. That is a hard wall: it rules out FP8 shortcuts and approximate softmaxes. Worth mentioning unprompted — it turns “we used BF16” from a buzzword into a decision made inside a constraint."),
  ("WMMA is not FlashAttention",
   "They solve different bottlenecks and get conflated constantly. WMMA maps matrix math onto Tensor Cores. FlashAttention-style tiling stops intermediate score and probability matrices from being written to HBM at all. You can have either without the other; this kernel has both, for different reasons."),
  ("Why fixing the wrong bottleneck first was still right",
   "It is easy to call v1 wasted effort. It was not — until the arithmetic was fast, you could not see that memory was the limit, and the measurement that showed 600 µs after a large compute speedup is exactly the evidence that pointed at the gather. Optimisation is mostly a sequence of measurements that relocate the bottleneck.")])

BD["cp-async-buffering"] = dict(
 ex=("Ten units becomes five",
  "<p>With one buffer, the loop alternates: load A, compute A, load B, compute B. Four tiles at one unit each costs eight units, and one of the two pieces of hardware is idle the whole time.</p>"
  "<p>With two buffers, the load for tile B is issued while tile A is being consumed. The loads occupy one track, the computes occupy another, and the total is the length of the longer track plus one stage of fill — five units instead of eight.</p>"
  "<p>Same bytes. Same FLOPs. The difference is that the DMA engine and the Tensor Cores are different hardware, and they were taking turns for no reason.</p>"),
 deep=[("Why the win was 130 microseconds and not 300",
   "In steady state the stage cost is <code>max(T_load, T_compute)</code>, not the average. If the gather costs 10 and the compute costs 2, you hide 2 and the other 8 are still on the critical path. The measured 600 → 470 µs says the gather was much larger than the compute — which is the diagnostic that pointed at the next optimisation."),
  ("Why not three or four buffers",
   "Deeper pipelining is possible, but each stage costs shared memory per block, and shared memory caps how many blocks stay resident per SM. Past a point you are spending occupancy — which is itself a latency-hiding mechanism — to buy more overlap. The two levers compete for the same budget."),
  ("cp.async is asynchronous, which is the whole trick",
   "An ordinary global load occupies the issuing warp until it returns. <code>cp.async</code> issues a global→shared copy that the warp does not wait on, so the warp can continue issuing MMA work and synchronise on the copy later. Without the async form, two buffers would buy you nothing — the warp would still be blocked."),
  ("When pipelining is the wrong lever entirely",
   "If the kernel is saturating memory bandwidth, overlap does not help — there is no idle transfer capacity to fill, and the answer is to move fewer bytes. Here the problem was latency on scattered accesses rather than raw bandwidth, which is why hiding it worked at all.")])

BD["split-k"] = dict(
 ex=("Cutting the index list, not the matrix",
  "<p>Before: one block per query token owns all 2,048 selected KV entries and tiles through them. <code>T = 8</code> gives 8 blocks.</p>"
  "<p>After: each query's 2,048 entries are cut into <code>S = 32</code> chunks of 64. Each chunk gets its own block. <code>T × S = 8 × 32 = 256</code> blocks.</p>"
  "<p>Every block does less work, more blocks exist, and the grid finally exceeds the SM count. <b>470 µs → 95 µs</b> — the largest single step in the project, and it came from changing the shape of the launch rather than the contents of the kernel.</p>"),
 deep=[("The misreading to avoid: it is not about fitting",
   "Split-K is often explained as “the working set doesn't fit in shared memory, so split it”. That is not what is happening here. A single block could already stream all 2,048 entries with tiling and double buffering — nothing overflowed. The purpose is to <b>expose more independent block-level parallelism</b>. Getting this right is the difference between reciting the name and understanding the decision."),
  ("It adds work and still wins",
   "Split-K creates S partial states per query, writes them to global scratch, and requires a second kernel to read them back and merge. Total work goes up. Wall-clock latency goes down, because far more of the machine is computing simultaneously. Latency and throughput are different quantities and this is the cleanest example of them diverging."),
  ("Which is why S has an optimum",
   "More splits means more parallelism and more reduction overhead. At small S the GPU is underfilled; at large S the reduce kernel dominates and each block's tile is too small to amortise its own setup. Somewhere in between is the minimum, and where it sits depends on the workload — hence v4."),
  ("The same instinct appears at cluster scale",
   "“The work does not divide into enough independent pieces to fill the hardware” is the same complaint as a pipeline bubble or an unbalanced tensor-parallel shard. The fix is always to re-cut the problem along a different axis and pay a combination cost. Here the axis is the KV index list and the cost is an online-softmax reduction.")])

BD["online-softmax-merge"] = dict(
 ex=("Why you cannot average two softmaxes",
  "<p>Chunk A has scores <code>[10, 9]</code>. Chunk B has scores <code>[1, 0]</code>. Normalise each on its own and both give roughly <code>[0.73, 0.27]</code>.</p>"
  "<p>But globally, a score of 1 next to a score of 10 should contribute essentially nothing. Adding the local softmaxes gives chunk B the same total weight as chunk A — a completely different answer from the true attention.</p>"
  "<p>The information that would have said so — <em>how big were your scores compared to everyone else's</em> — was thrown away by the local normalisation. So you keep it instead: the maximum, the un-normalised sum, and the un-normalised output.</p>"),
 deep=[("The three numbers, and why they are sufficient",
   "<code>mᵢ</code> is the chunk's maximum score, <code>lᵢ = Σ exp(s − mᵢ)</code> is its un-normalised denominator, and <code>oᵢ = Σ exp(s − mᵢ)V</code> its un-normalised output. Rescaling by <code>exp(mᵢ − m)</code> onto a common maximum <code>m</code> converts any chunk's statistics into the global frame, so the merge is exact and does not depend on the order chunks arrive in."),
  ("Subtracting the max is not cosmetic",
   "It is what keeps <code>exp</code> from overflowing. Attention scores can be large; <code>exp(score)</code> in FP32 overflows well before the scores become unusual. Carrying a running max and exponentiating only differences is the numerically stable form — the same reason single-kernel softmax implementations do a max pass first."),
  ("The same state, two different granularities",
   "FlashAttention carries <code>(m, l, o)</code> from tile to tile inside one block so the S×S score matrix never reaches HBM. Split-K carries the identical state from block to block so 32 processors can reconstruct one softmax. Recognising that these are the same trick at different scales is a good thing to say out loud."),
  ("Exactness is a requirement here, not a preference",
   "The correctness bar was matching the BF16 reference within abs_err 0.1. An approximate merge — averaging, or dropping small chunks — would have failed outright. Split-K is only available as an optimisation <em>because</em> an exact merge exists.")])

BD["autotune-polish"] = dict(
 ex=("Two configurations, same grid, different machine",
  "<p>v3 picked S with a heuristic: <code>S ≈ 2·SMs / T</code>, aiming for roughly 256 blocks. The reasoning is that block count is what fills the GPU.</p>"
  "<p>But <code>T = 8, S = 32</code> gives 64 KV entries per block, and <code>T = 32, S = 8</code> gives 256. Both are 256 blocks. They differ in memory traffic per block, execution time per block, register pressure, shared-memory pressure, reduction cost and scheduling behaviour.</p>"
  "<p>No single formula captures six things at once — so v4 sweeps the valid powers of two that divide <code>TOPK / BLOCK_K</code>, benchmarks each, and keeps the winner. It is frequently not where the heuristic pointed.</p>"),
 deep=[("The two warp changes that came with it",
   "The <b>reduce kernel</b> ran 4 warps over 16 heads — four serial passes. v4 uses 16 warps (512 threads), one per head, in a single pass. The <b>split kernel</b> went from 4 warps (128 threads) to 8 (256), so more independent warps are resident to cover a stalled scattered read. Neither is clever; both are about not leaving units idle."),
  ("Autotuning finds the winner without explaining it",
   "A sweep tells you which configuration is fastest, not why. That is fine for shipping and unsatisfying for understanding — the honest answer in an interview is that the measurement decides and the profiler explains. If you can say which resource the winning configuration stopped wasting, you are ahead of the sweep."),
  ("Where autotuning stops being practical",
   "It costs compilation and benchmarking time, which is acceptable offline and awkward when shapes arrive at runtime. The usual production compromise is a cached table keyed by shape, with a heuristic as the fallback for anything unseen — which is roughly what v3 was, used correctly."),
  ("Measured beats predicted, repeatedly",
   "It is the same lesson as least-outstanding-requests beating round-robin in a load balancer: a model of the system is a simplification, and where the simplification is wrong the measurement is not. Reaching for a formula is the right instinct; refusing to check it against the hardware is not.")])
