# Map: world models — does prediction-error surprise mean physical understanding?

Roots are unconditional truths; the sink is the paper's question. The map IS the teaching
order. Lecture moves in [sources/lecun-eth-2026.md](sources/lecun-eth-2026.md).

```mermaid
graph TD
  U1["U1 ✓ reality supplies the target<br/>the next frame IS the answer"]
  U2["U2 a predictor is scored on<br/>whatever space its output lives in"]
  U3["U3 some of the future is not<br/>determined by the past"]
  U4["U4 a system with no language channel<br/>can only be measured by what it already does"]
  U5["U5 an encoder mapping everything to<br/>one vector has exactly zero error"]
  U6["U6 an event absent from training is<br/>unfamiliar, whatever the reason it was absent"]

  D2["pixel prediction spends capacity<br/>on unpredictable detail"]
  D3["JEPA move: predict in<br/>representation space"]
  D6["latent z: a slot for what<br/>the past does not determine"]
  D4["representation collapse"]
  D5["anti-collapse IS the problem<br/>contrastive vs regularized"]
  D7["D7 ✓ violation of expectation:<br/>error as looking time, matched pairs"]
  D9["what the benchmarks measure:<br/>detection vs prediction vs QA"]
  D10["THE CONFOUND<br/>unfamiliar, or impossible?"]
  G["the paper: does surprise<br/>constitute understanding?"]

  U2 --> D2
  U3 --> D2
  D2 --> D3
  U3 --> D6
  D3 --> D6
  U5 --> D4
  D3 --> D4
  D4 --> D5
  U1 --> D7
  U4 --> D7
  D7 --> D9
  U6 --> D10
  D7 --> D10
  D9 --> D10
  D10 --> G
  D5 --> G
```

## Node status

| Node | Status | Evidence |
| --- | --- | --- |
| U1 reality supplies the target | solid | Derived unaided 2026-09-02 (Q3), then ratified |
| U2 scored in its output space | untouched | — |
| U3 future underdetermined | untouched | — |
| U4 no language channel ⟹ measure behaviour | seen once | Taught 2026-09-02 with the infant looking-time origin |
| U5 constant encoder ⟹ zero error | untouched | — |
| U6 absent ⟹ unfamiliar | seen once | Replaced a weaker draft root that needed a caveat (VFX and cartoons do contain impossible events) |
| D7 violation of expectation | seen once | Taught 2026-09-02 (Q2 was a blank; answer given with the matched-pair protocol) |
| U6 → D10 the confound | seen once | Taught 2026-09-02. Quiz-checked: missed the control question (chose a linear probe), corrected with the discrimination criterion |
| D9 benchmark taxonomy | seen once | Taught 2026-09-02; one correct answer (Q6) |
| D2, D3, D4, D5, D6 mechanism spine | delivered, then corrected | Expository block 2026-09-02; five corrections issued after verification (see Corrected roots). No retrieval yet |
| physics-violation evidence | delivered, unchecked | Verified numbers 2026-09-02; the dissociation and the IntPhys 1→2 collapse |
| G | untouched | — |

Status vocabulary: **solid** = retrieved correctly on a later occasion, not just answered when
first taught. **seen once** = taught and answered correctly at the time. **delivered, unchecked**
= exposition given, no retrieval attempted. Downgraded four nodes from solid to seen once on
2026-09-02 — a single same-session answer is not evidence of durable knowledge.

## Corrected roots — 2026-09-02, after the verification pass

Three roots I taught were serviceable but not the sharpest available. The verification pass
produced better ones; these replace them, and the teaching order changes accordingly.

| Was | Now | Why the new one is better |
| --- | --- | --- |
| U2 "a predictor is scored in its output space" | **normalization is global** — a probability distribution needs a normalizer summed over *every* possible output | Explains the text/video asymmetry exactly: a softmax over ~10⁵ tokens *is* the normalizer; over video it is an integral over a continuum. Shows the objection is to generative prediction in a continuous space, **not to autoregression**. |
| U5 "a constant encoder has zero error" | **d(a,a) = 0 is the floor, so if *both* arguments are trainable, both-constant is the global minimum** | Generates the insight the old root missed: in MAE the right-hand side is raw pixels, which are *not* trainable, so **pixel targets are collapse-proof for free**. Collapse is the price of the JEPA move, not a quirk. |
| (absent) | **a loss computed on f(y) cannot see what f discarded** | One root generating *both* halves of the case: the JEPA move (encoder may legally discard leaf motion) and the text-bandwidth argument (language already discarded the physics before the model saw anything). |

Two further roots worth carrying: **fixed vs elastic compute** (a fixed network spends compute set
by its shape; an optimizer spends what you let it) generates the System-1/System-2 framing and why
planning is optimization; and **world model = a function from (state, imagined action) to next
state, built to be searched over** — a stipulative definition, which is why "Sora renders realistic
video, therefore it has a world model" is a category error inside this vocabulary.

## Demoted candidates

Two "foundations" failed the stress test and were pushed down:

- *"Prediction error is available at test time"* — derives from U1, so it is a step, not a root.
  Evidence it derives: the learner reconstructed it from U1 without being told.
- *"Training video contains no physically impossible events"* — needs a caveat (VFX, animation,
  edited cuts), so it is not unconditional. Replaced by U6, which is a definition and carries the
  same load.

## Links

Brief: [learning-brief.md](learning-brief.md) · mistakes: [mistake-log.md](mistake-log.md)
· sources: [source-register.md](source-register.md) · Anki tag: `world-models`
