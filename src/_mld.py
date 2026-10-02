# -*- coding: utf-8 -*-
MD = {}

MD["perceptron"] = dict(
 ex=("One update, by hand",
  "<p>Start with w = (0, 1), b = −3 — the line x₂ = 3. The point (2, 3) has label +1 but s = 0·2 + 1·3 − 3 = 0, which is not &gt; 0, so it is misclassified.</p>"
  "<p>Apply the rule: w ← (0, 1) + (+1)·(2, 3) = <b>(2, 4)</b>, b ← −3 + 1 = <b>−2</b>. Now s = 2·2 + 4·3 − 2 = 14 &gt; 0: the point is on the right side. The line rotated toward the point because adding x to w makes w·x larger for that x in particular.</p>"
  "<p>Six updates later, w = (1.4, 1.4), b = −5 separates all eight points. Different update orders give different final lines — the theorem promises <em>a</em> separator, not the best one.</p>"),
 deep=[("Why XOR needs a hidden layer, in one sentence",
   "A single neuron's decision boundary is the set where w·x + b = 0 — a line — and XOR's two classes sit on opposite corners of a square, so no line puts both +1 corners on one side without one −1 corner. Two hidden ReLUs, h₁ = ReLU(x₁ + x₂) and h₂ = ReLU(x₁ + x₂ − 1), map the four corners to (0,0), (1,0), (1,0), (2,1), which <em>are</em> separable."),
  ("From the perceptron rule to gradient descent",
   "The rule w ← w + t·x is gradient descent on the loss max(0, −t·(w·x + b)) with learning rate 1: the gradient of that loss on a mistake is exactly −t·x. Swap the step output for a sigmoid and the hinge for cross-entropy and you have logistic regression — same neuron, differentiable loss, and the gradient now carries <em>how</em> wrong, not just whether."),
  ("What the interviewer usually asks next",
   "“Why do we need nonlinear activations?” Because a stack of linear layers is one linear layer: W₂(W₁x + b₁) + b₂ = (W₂W₁)x + b′. The activation between them is the only thing that lets depth draw anything but a line."),
  ("The classic pictures",
   "The <a href=\"https://playground.tensorflow.org/\">TensorFlow Playground</a> lets you watch a tiny network bend the plane on exactly these datasets, XOR included, live in the browser. Rosenblatt’s 1958 paper and Minsky &amp; Papert’s <em>Perceptrons</em> (1969) are the historical bookends; the <a href=\"https://en.wikipedia.org/wiki/Perceptron\">Wikipedia article</a> has the convergence theorem and the original learning rule.")])

MD["forward-pass"] = dict(
 ex=("The numbers, end to end",
  "<p>x = (1.0, 0.5). W₁ = [[0.7, −0.6], [0.3, 1.0]], b₁ = (0.1, 0.2), w₂ = (0.4, −0.8), b₂ = 0.6.</p>"
  "<p>z₁ = 0.7·1.0 + (−0.6)·0.5 + 0.1 = <b>0.5</b> · z₂ = 0.3·1.0 + 1.0·0.5 + 0.2 = <b>1.0</b> · h = ReLU(z) = (0.5, 1.0).</p>"
  "<p>u = 0.4·0.5 + (−0.8)·1.0 + 0.6 = <b>0.0</b> · ŷ = σ(0) = <b>0.5</b> · with y = 1, L = −log 0.5 = <b>0.693</b>.</p>"
  "<p>The network is exactly undecided and the loss is ln 2 — the loss of a coin flip. Every page in this group reuses these numbers.</p>"),
 deep=[("Which activation, and why ReLU won",
   "Sigmoid and tanh saturate: for large |z| their slope is nearly zero, so gradients vanish through deep stacks. ReLU's slope is exactly 1 wherever it is on, so signals pass through unchanged, and it costs one comparison. Its flaw is units that are off for every input (dead ReLUs); GELU and SiLU, used in transformers, smooth the corner so there is always some slope."),
  ("Why cross-entropy and not squared error for a probability",
   "With a sigmoid output and squared error, the gradient at the logit is (ŷ − y)·ŷ(1 − ŷ), which goes to zero exactly when the network is confidently wrong (ŷ near 0 or 1) — the worst time to stop learning. With cross-entropy the σ′ factor cancels and the gradient is just ŷ − y: largest when most wrong."),
  ("The classic pictures",
   "3Blue1Brown’s <a href=\"https://www.3blue1brown.com/topics/neural-networks\">neural-network series</a> (chapter 1) animates exactly this forward pass on handwritten digits. Stanford’s <a href=\"https://cs231n.github.io/neural-networks-1/\">CS231n notes</a> draw the layer-as-matrix picture used here."),
  ("Shapes at real scale",
   "For a batch of B examples, X is B × d_in and the layer computes X W + b with W of size d_in × d_out — one matmul of B·d_in·d_out multiply-adds. A transformer's MLP has d_in = 4096, d_out = 16384; with B = 4096 tokens that is 2.7 × 10¹¹ multiply-adds in one line. The forward pass is the reason the infrastructure notes exist.")])

MD["backprop"] = dict(
 ex=("Every gradient, derived",
  "<p>Stored from the forward pass: x = (1.0, 0.5), z = h = (0.5, 1.0), u = 0, ŷ = 0.5, y = 1.</p>"
  "<p><b>Output.</b> ∂L/∂u = ŷ − y = <b>−0.5</b>. ∂L/∂w₂ = (∂L/∂u)·h = (−0.25, −0.5). ∂L/∂b₂ = −0.5.</p>"
  "<p><b>Back through w₂.</b> ∂L/∂h = (∂L/∂u)·w₂ = −0.5·(0.4, −0.8) = (−0.2, +0.4).</p>"
  "<p><b>Through ReLU.</b> Both z &gt; 0, so ∂L/∂z = (−0.2, 0.4) unchanged.</p>"
  "<p><b>First layer.</b> ∂L/∂W₁ = ∂L/∂z ⊗ x = [[−0.2·1.0, −0.2·0.5], [0.4·1.0, 0.4·0.5]] = [[−0.2, −0.1], [0.4, 0.2]]. ∂L/∂b₁ = (−0.2, 0.4).</p>"
  "<p>One chain checked by hand: ∂L/∂w₁₁ = (∂L/∂u)(∂u/∂h₁)(∂h₁/∂z₁)(∂z₁/∂w₁₁) = (−0.5)(0.4)(1)(1.0) = −0.2. ✓</p>"),
 deep=[("Why ŷ − y, and why that matters",
   "∂L/∂ŷ = −1/ŷ and ∂ŷ/∂u = ŷ(1 − ŷ); multiply and the ŷ cancels, leaving ŷ − y. The same cancellation happens for softmax + cross-entropy in a classifier with many classes: the gradient at the logits is simply (probabilities − one-hot). That is why those two are always paired, and why the error signal at the output of a classifier is literally the error."),
  ("Where the 2× comes from",
   "For a layer h = W a, backward needs two products: ∂L/∂W = (∂L/∂h) aᵀ to update the weights and ∂L/∂a = Wᵀ (∂L/∂h) to keep going. Each is the same size as the forward matmul, so backward ≈ 2× forward, and a training step ≈ 3× a forward pass — the figure behind every FLOPs estimate for training."),
  ("The classic pictures",
   "3Blue1Brown’s <a href=\"https://www.3blue1brown.com/lessons/backpropagation-calculus\">Backpropagation calculus</a> draws the chain-rule tree for a one-neuron-per-layer network, the same shape as the chain panel here. Karpathy’s <a href=\"https://github.com/karpathy/micrograd\">micrograd</a> (and its two-hour video) builds backprop in 100 lines of Python on a graph just like the one on the autodiff page."),
  ("Vanishing and exploding gradients",
   "Each layer multiplies the signal by its weight matrix and by the activation's slope. Across 50 layers that product either shrinks toward zero (sigmoid, small weights) or grows without bound. Residual connections add an identity path so the product always has a 1 in it; LayerNorm keeps the scale of activations fixed; careful initialisation starts the products near 1.")])

MD["autodiff"] = dict(
 ex=("Reading the graph the framework built",
  "<p><code>h = torch.relu(W1 @ x + b1)</code> creates two nodes (a matrix–vector product, then an add) and a ReLU node; <code>yhat = torch.sigmoid(w2 @ h + b2)</code> adds three more; <code>loss = -torch.log(yhat)</code> two more. Each node stores a <code>grad_fn</code> and the tensors its derivative needs — ReLU keeps the mask (z &gt; 0), sigmoid keeps ŷ, every matmul keeps its input.</p>"
  "<p><code>loss.backward()</code> walks them in reverse. At −log: incoming 1, local −1/ŷ = −2.0. At sigmoid: −2.0 × ŷ(1 − ŷ) = −0.5 — the framework never used the shortcut ŷ − y, it multiplied the two local pieces. At the second linear node it produces three outputs at once: a gradient for h (−0.5·w₂) that continues, and gradients for w₂ and b₂ that stop at those leaves.</p>"
  "<p>Afterwards <code>W1.grad</code> is <code>[[−0.2, −0.1], [0.4, 0.2]]</code> — the hand-derived answer.</p>"),
 deep=[("Forward mode vs reverse mode",
   "Both use the same local derivatives. Forward mode pushes a perturbation of one input through the graph (a Jacobian–vector product) and gets the sensitivity of every output to that one input; reverse mode pulls a weight on one output back through the graph (a vector–Jacobian product) and gets the sensitivity of that one output to every input. Training has one output (the loss) and billions of inputs, so reverse mode wins by a factor of billions."),
  ("What is actually in memory during training",
   "Weights, their gradients, the optimizer state (two more copies for Adam), and the saved activations — which for a transformer are every layer's input, attention scores and MLP intermediate for every token in the batch. The activations usually dominate at long sequence lengths. Activation checkpointing keeps only the layer boundaries and recomputes the rest during backward, trading ~30% more compute for a large memory cut."),
  ("The classic pictures",
   "PyTorch’s <a href=\"https://pytorch.org/docs/stable/notes/autograd.html\">Autograd mechanics</a> note is the authoritative description of what gets saved and when; Baydin et al., <a href=\"https://arxiv.org/abs/1502.05767\">Automatic differentiation in machine learning: a survey</a>, has the canonical forward-vs-reverse mode tables. Karpathy’s micrograd is the smallest working implementation worth reading end to end."),
  ("Define-by-run vs a static graph",
   "PyTorch records the graph fresh on every forward call, so Python control flow (if, loops, early exit) just works, at the cost of re-recording each time. Static-graph systems (TensorFlow 1, JAX's jit, torch.compile) capture the graph once and can optimise it — fuse kernels, plan memory — but need the structure to be fixed. Modern practice is eager for development and compiled for the training run.")])

MD["optimizers"] = dict(
 ex=("The same valley, five walkers",
  "<p>f(w) = ½(w₁² + 10w₂²), starting at (−9, 1.4). The gradient is (w₁, 10w₂): ten times steeper in w₂.</p>"
  "<p><b>GD, η = 0.15.</b> In w₂ each step multiplies by 1 − 1.5 = −0.5: it overshoots and flips sign. In w₁ each step multiplies by 0.85: a crawl. After 12 steps w₁ = −1.3.</p>"
  "<p><b>η = 0.21.</b> The w₂ multiplier is −1.1, magnitude above 1: the walk diverges, f goes from 1 to 39. <b>η = 0.03</b> is stable but reaches only w₁ = −6.2.</p>"
  "<p><b>Momentum, β = 0.8, η = 0.04.</b> Alternating w₂ steps cancel in the velocity; the consistent w₁ steps accumulate. Reaches f = 0.15 — smoother and faster.</p>"
  "<p><b>Adam, η = 0.8.</b> Each coordinate's step is normalised by its own gradient scale, so w₁ (gradient 9) and w₂ (gradient 14) move about the same distance per step. The steepness difference stops mattering.</p>"),
 deep=[("Why Adam's step is roughly ±η",
   "m is a running mean of g and v a running mean of g², so m/√v is g divided by its own typical magnitude: about ±1 while the gradient keeps its sign, smaller when it oscillates. The step is therefore about η per parameter whatever the gradient's scale — which is what lets one η serve embeddings, attention and MLP weights whose gradients differ by orders of magnitude."),
  ("AdamW, and why decay is decoupled",
   "L2 regularisation adds λw to the gradient — but Adam then divides that term by √v, so heavily-updated parameters are barely regularised. AdamW instead subtracts ηλw directly from the weight, outside the adaptive scaling. It is the default for transformer training; typical λ is 0.1, far larger than the 1e-4 people used with SGD."),
  ("The classic pictures",
   "Alec Radford’s optimizer animations in <a href=\"https://cs231n.github.io/neural-networks-3/\">CS231n notes part 3</a> are the race through a valley and over a saddle that this page’s plot imitates. Adam is Kingma &amp; Ba, <a href=\"https://arxiv.org/abs/1412.6980\">arXiv:1412.6980</a>; AdamW is Loshchilov &amp; Hutter, <a href=\"https://arxiv.org/abs/1711.05101\">arXiv:1711.05101</a>; Ruder’s <a href=\"https://www.ruder.io/optimizing-gradient-descent/\">overview</a> walks the whole ladder with the same pictures."),
  ("Warm-up and cosine decay",
   "Adam's v̂ is a poor estimate for the first few hundred steps and the initial weights are random, so a full-size η early on can wreck the run; warming η up linearly from zero avoids it. Decaying η afterwards (cosine to ~10% of peak is the common choice) lets the walk settle into the minimum instead of bouncing around it. Batch size interacts: larger batches tolerate larger η, roughly proportionally up to a point.")])

MD["activation-functions"] = dict(
 ex=("Ten layers, three activations",
  "<p>Backprop multiplies one slope per layer. At a typical pre-activation |z| ≈ 1: sigmoid′(1) = 0.20, tanh′(1) = 0.42, ReLU′(1) = 1.</p>"
  "<p>Across ten layers the gradient reaching the first layer is scaled by 0.20¹⁰ ≈ 10⁻⁷ (sigmoid), 0.42¹⁰ ≈ 2 × 10⁻⁴ (tanh), or 1 (ReLU, if every unit on the path is on). With a learning rate of 0.01, the first layer of the sigmoid network moves by 10⁻⁹ per step: it is frozen.</p>"
  "<p>Softmax, by hand: logits (2.0, 1.0, 0.1) → e^z = (7.389, 2.718, 1.105), sum 11.212 → p = (0.659, 0.242, 0.099). With the true class first, the gradient at the logits is p − onehot = (−0.341, 0.242, 0.099): push the right logit up, the others down, in proportion to how much probability they stole.</p>"),
 deep=[("Why ReLU, and then why GELU",
   "ReLU won in 2012 because its slope is 1 and it costs a comparison; the price is dead units and a kink at zero. GELU (z·Φ(z)) and SiLU (z·σ(z)) are smooth, never have slope exactly zero, and in practice give slightly better transformers at the same cost — GPT-2/3 and BERT use GELU, Llama uses SiLU inside a gated unit (SwiGLU)."),
  ("Why the output layer is different",
   "Hidden activations are chosen for their slope. The output activation is chosen to match the loss: sigmoid + binary cross-entropy for one probability, softmax + cross-entropy for a distribution, identity + squared error for a regression. In each matched pair the gradient at the logits collapses to prediction − target — the same ‘gradient = error’ every time."),
  ("The classic pictures",
   "The table on <a href=\"https://en.wikipedia.org/wiki/Activation_function\">Wikipedia’s activation-function page</a> plots every function with its derivative. Stanford’s <a href=\"https://cs231n.github.io/neural-networks-1/\">CS231n notes (neural networks part 1)</a> walk through sigmoid, tanh, ReLU and leaky ReLU with the same ‘what does it do to the gradient’ framing used here. The GELU paper is Hendrycks &amp; Gimpel, arXiv:1606.08415.")])

MD["sgd"] = dict(
 ex=("One parameter, 1,000 examples",
  "<p>Fit w to 1,000 numbers drawn around μ = 3.03 (σ ≈ 1), loss = average of ½(w − xᵢ)². The exact gradient is w − μ. From w = 0 with η = 0.3, full-batch GD takes one step per pass over the data: w = 0.91 after one epoch, 1.99 after three.</p>"
  "<p>A random batch of 32 has mean 2.94, so its gradient is −2.94 instead of −3.03: nearly the same direction at 1/31 of the cost. Thirty-one such steps per epoch put w ≈ 3.0 before the first epoch is a tenth over. The noise per step is σ/√B ≈ 0.18; near the minimum w jitters by about ησ/√B ≈ ±0.07 and never fully settles — the reason to decay η.</p>"),
 deep=[("Batch size, learning rate and the critical batch",
   "Doubling B halves the gradient variance, so the same per-epoch progress survives doubling η too — the linear scaling rule (Goyal et al., arXiv:1706.02677, trained ImageNet in an hour on 8k-image batches with it, plus a warm-up). It stops working past the critical batch size, where the gradient is already accurate and extra examples per step buy nothing; beyond that only more steps help."),
  ("Sharp vs flat minima",
   "Keskar et al. (arXiv:1609.04836) observed that large-batch training lands in sharper minima and generalises worse, and attributed it to the missing noise. The picture is widely used and well supported but still argued about — later work showed the gap can mostly be closed by scaling η and training longer. In an interview, say ‘tends to’, not ‘always’."),
  ("The classic pictures",
   "The loss-landscape renders everyone has seen — the spiky ResNet-56 surface that skip connections smooth out — are from Li et al., <a href=\"https://arxiv.org/abs/1712.09913\">Visualizing the Loss Landscape of Neural Nets</a>. The optimizer-race animations (SGD, momentum, NAG, Adagrad, Adadelta, RMSprop racing through a saddle and a valley) are Alec Radford’s, reproduced in <a href=\"https://cs231n.github.io/neural-networks-3/\">CS231n notes part 3</a>, which also covers batch size, learning-rate schedules and gradient checks. Sebastian Ruder’s <a href=\"https://www.ruder.io/optimizing-gradient-descent/\">overview of gradient descent optimization algorithms</a> is the standard written tour.")])
