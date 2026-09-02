# Source: LeCun — "World Models: Enabling the next AI revolution"

Yann LeCun · ETH Zürich, *Frontiers of Embodied AI* · delivered 2026-05-29 · posted 2026-06-09
Video: https://www.youtube.com/watch?v=72Xj8k5WQX4 (id `72Xj8k5WQX4`)
Transcript: auto-generated captions, supplied by the learner 2026-09-02. Type: primary
(speaker's own words) but ASR-noisy — every name and number below was re-derived or
cross-checked, and the known ASR corruptions are listed at the bottom.

## Skeleton — the talk's twelve moves, in order

Rewatch against this. Each move is a box in [map.md](../map.md).

| # | Move | The claim | Map node |
| --- | --- | --- | --- |
| 1 | Machine learning sucks | Humans and animals learn new tasks in few trials; machines don't. Current AI can't handle continuous, high-dimensional, noisy data — "language is easy by comparison." | motivation |
| 2 | Moravec's paradox | Chess and symbolic integration are easy for machines; what a 10-year-old does effortlessly is not. A teenager learns to drive in ~20 hours; self-driving has millions of hours and no level 5. | motivation |
| 3 | What intelligence is | Not accumulated declarative knowledge (that's what LLMs are good at), not a collection of skills — it's fast adaptation to new tasks. Therefore "AGI" is a nonsense phrase; human intelligence is specialized. | motivation |
| 4 | How babies learn | Mostly by observation in the first months. 3D structure comes early (parallax is the best explanation of how the view changes when you move). Object permanence early; **intuitive physics — inertia, gravity — takes ~9 months**. | U1 |
| 5 | **Violation of expectation** | The car-off-the-platform demo: a 6-month-old barely attends, a 10-month-old is visibly surprised. This is how psychologists measure whether an infant holds a concept — **and LeCun states outright that the same technique can test machines**. Credits a paper largely written by Emmanuel Dupoux. | U4 → D7 |
| 6 | The data-volume argument | LLM: ~20T words ≈ 30T tokens × ~3 bytes ≈ 10¹⁴ bytes ≈ 400,000 human reading-years. Four-year-old: ~16,000 h wake time × 2×10⁶ optic fibres × ~1 byte/s ≈ 10¹⁴ bytes. Same volume through vision in 4 years. Redundancy in video is "a feature, not a bug" — self-supervised learning needs it. | U1 |
| 7 | Inference by optimization | Two modes: propagate through a fixed stack of layers (LLM), or **search for an output that minimizes an energy at inference time**. The second is strictly more powerful computationally. Chain-of-thought is "tricking it into generating more tokens" — we don't reason in token space. | planning |
| 8 | The architecture | perception → state (+ memory) → world model ← proposed action sequence → objective (0 if task accomplished) + guardrail objectives → optimize the action sequence. Multi-step rollout = **model-predictive control**, "very classical, going back to the 1960s." Guardrails are argued to be un-jailbreakable because the system can do nothing but optimize them. Written up in his 2022 position paper. | planning |
| 9 | Hierarchical planning | The NYU-office-to-Paris example: you cannot plan a trip in 10 ms muscle actions — you lack the information and the horizon. **"This is an unsolved problem… completely open. Nobody knows how to do this."** Offered as a PhD topic. | open |
| 10 | Why generative fails on video | Masked-token self-supervision works for text because the output space is a finite dictionary; you can emit a distribution over it. Video has no such finite space. The room example: a model can predict "auditorium, finite size, windows" but **cannot** predict what each person looks like — the information is not there. Train it to try and "you kill it." His own record: ~15 years on world models, failing for the first 10 while using generative ones. Blurry predictions = the model emitting the average of everything that could happen. | U2, U3 → D2 |
| 11 | JEPA | Encode **both** x and y; predict in representation space. The encoder can then discard whatever about y is unpredictable — predictions become more abstract, fewer details, more accurate. Justified by the abstraction hierarchy in science (quantum fields → particles → … → societies) and by CFD: you model air as velocity and density fields, never as colliding molecules, because tracking every detail diverges from reality fast. **Therefore world models should not be simulators, not digital twins, not generative, not video generation.** | D3 |
| 12 | Collapse and how to stop it | A JEPA trained only to minimize prediction error collapses: ignore the input, emit a constant, error is zero. In energy terms, collapse = a flat energy landscape. Two families: **contrastive** (push energy up at points outside the data) and **regularized** (shrink the volume of space that can take low energy) — he prefers the second. Information-maximization view of a batch matrix: make the rows different (sample-contrastive) or the columns different (dimension-contrastive). Names MCR, MCR², VICReg, Barlow Twins. | U5 → D4 → D5 |

## The two results that matter for the paper

**The physics-violation claim (move 12b).** V-JEPA is given a sliding 16-frame window and its
internal prediction error is monitored frame by frame. On a video where something physically
impossible happens — his example: a thrown ball that disappears — **the prediction error spikes**.
LeCun draws the analogy explicitly to the surprised 10-month-old, and calls it the first time he
has seen a fully self-supervised system acquire "some level of common sense." Note his own
hedge: the system *"understands"* — with, in his words, double quotes.

**The depth result.** A head trained on frozen V-JEPA 2.1 representations predicts depth from a
single image, reportedly better than DINOv3 — offered as evidence the model learned that the
world is 3D purely from filling in blanks in video. Cross-check this number before citing.

## SIGReg — the newest piece, and the admission under it

The chain he actually walks: prevent collapse → do it by maximizing information → **but we have
no usable measure of information content**, for two reasons he states plainly:

1. Proper definitions need the distribution; we only have finitely many samples from an encoder.
2. Maximizing requires a *lower* bound, and every empirical measure we have is an *upper* bound.
   His words: come up with a good upper bound and cross your fingers.

SIGReg (sketched isotropic Gaussian regularization) sidesteps the measurement problem by fixing a
target distribution instead. Make the batch's embeddings isotropic Gaussian — chosen because its
coordinates are independent (and, incidentally, it is max-entropy at fixed variance, which he says
he doesn't care about). Enforced from finite samples by sketching:

```
  project the batch onto one random direction        → a 1-D marginal
  build the empirical CDF of those projections       → a staircase
  compare it to the Gaussian CDF                     → each point sits left or right of ideal
  that comparison gives a gradient per sample        → backprop, move the points
  repeat over many random directions                 → in the limit the joint law is isotropic Gaussian
```

The limiting step is the Cramér–Wold argument: a distribution is pinned down by all of its 1-D
projections. Claimed practical properties: simple, source available, trains on one GPU, already
used for action-conditioned world models with planning; **not yet scaled** — he says scaling it up
is the main remaining job. Contrast with the distillation methods (stop-gradient plus an EMA
target encoder, from BYOL) which *have* been scaled and produced I-JEPA, V-JEPA and DINO.

## Closing position and status

Abandon generative models for joint-embedding ones; abandon probabilistic models for energy-based
ones; minimize reinforcement learning ("what you do when you're desperate") — learn representations
by observation first, then RL needs few samples. Advice to academics: don't work on LLMs. He notes
this makes him unpopular in Silicon Valley, that he left Meta at the end of 2025, and that he
founded **AMI Labs** (ASR renders it "Emmy Labs") for physical AI — robotics, industrial process
control, "anything high-dimensional, continuous and noisy" where LLMs are helpless.

Q&A worth keeping: asked how an engineer injects a constraint like "don't hit the wall" when
everything lives in representation space, he answers that you train a small projector head on top
of the representation to read off the quantity you want — cheap, few samples.

## What the talk does NOT address

- **The confound.** He reports that error spikes on impossible video. He does not test whether the
  spike tracks *impossibility* or merely *unfamiliarity* — impossible clips are out-of-distribution
  by construction. No matched-statistics control is described. This is the gap the paper attacks.
- No benchmark numbers, protocols, or chance baselines are given for the surprise result in the talk.
- No account of *which* physical properties V-JEPA gets right and which it fails.

## ASR corruptions — corrected

| Transcript reads | Actually | How verified |
| --- | --- | --- |
| "16 hours of wake time" | **16,000 hours** | Arithmetic: 16 h gives 1.15×10¹¹ bytes, a factor of 1000 below his own stated 10¹⁴. 16,000 h gives 1.15×10¹⁴. |
| "Marave paradox" | Moravec's paradox | standard term |
| "Emmy Labs" | **AMI Labs** | LeCun's post-Meta company |
| "WE cig" / "cigg" / "cigreg" | **SIGReg** | sketched isotropic Gaussian regularization, as he expands it |
| "VCRG" / "WE cig" | **VICReg** | variance–invariance–covariance regularization |
| "B twins" | Barlow Twins | — |
| "aa and VJ Japa" | I-JEPA and V-JEPA | — |
| "bol" | BYOL (bootstrap your own latent) | he expands it himself |
| "Emanuel Du" | Emmanuel Dupoux | the IntPhys / VoE-for-machines line |
| "Jeanh"/"Gitandra"/"Vladin" | Seymour Papert; and two co-speakers at the event | Papert identified from context (perceptron book, MIT, Piaget) |
| "NTO's partial differential equations" | Navier–Stokes | CFD context |
| "Jeep"/"jetpack"/"JPEA"/"Japa" | JEPA | — |

Register row: [../source-register.md](../source-register.md)
