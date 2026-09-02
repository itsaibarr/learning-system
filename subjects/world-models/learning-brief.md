# Learning Brief: world models (physics-violation detection)

Created: 2026-09-02 · Status: active · Mode: plain (`docs/plain-mode.md`)

| Field | Value |
| --- | --- |
| Why this, why now | Writing a paper on whether world models detect physics violations; surveying who is active in the field. |
| Target outcome | Can defend a position on whether prediction-error "surprise" constitutes physical understanding — naming the benchmarks, their protocols and chance baselines, the strongest evidence each way, and the confound that separates them. Observable: writes the related-work and critique sections without a secondary explainer. |
| Secondary outcome | Reads I-JEPA / V-JEPA / LeJEPA directly; understands what each loss term prevents well enough to implement one. |
| Deadline / cadence | Paper in progress — front-load the evidence map, then the mechanism. |
| Constraints | No Obsidian on this machine (plain mode). Source lecture (LeCun, ETH Zürich, 2026-05-29) is on YouTube, which this environment's egress policy blocks — taught from primary papers instead. |
| Map | [map.md](map.md) |
| Active cycle | (set after the teaching plan is agreed) |

## Probe result — 2026-09-02

Bracketed by three graded questions. **Reasoning is strong; domain vocabulary is the gap.**

| Strand | Floor (got right) | Ceiling (blank) |
| --- | --- | --- |
| Autoregressive generation | Error compounding: each sampled token enters the conditioning context for all later tokens | — not probed higher |
| Self-supervised prediction | Derived unaided that prediction error is the free test-time signal, because reality supplies the target | held it as inference, not as knowledge |
| Violation-detection measurement | — | how IntPhys / GRASP / InfLevel actually measure detection: matched possible/impossible pairs, compared within-pair |
| Representation learning | — | not probed; self-reported as unfamiliar (collapse, contrastive vs regularized) |

Key signal: on Q3 the answer was *"logically I would say A, but really E"* — the derivation was
correct but not trusted. Teach so facts get **confirmed**, not just stated; this learner will
derive ahead of the lesson and needs the derivation ratified to commit to it.

Stated background: transformers/LLMs comfortable. Backprop-and-training-loops, self-supervised
learning, and RL/control all unselected.

## Open gaps
- The measurement paradigm: violation-of-expectation, its origin in infant looking-time studies, and why the protocol is within-pair rather than absolute.
- Representation space vs pixel space — what "predict in embedding space" buys and costs.
- Representation collapse and the anti-collapse mechanisms (the reason JEPA training is hard).
- The deflationary confound: impossible videos are out-of-distribution by construction, so elevated prediction error may track statistical novelty rather than physical impossibility. This is the paper's crux and is not yet resolved for this learner.

## Scope decision
Requested "structure only" math, but targets are "read the papers" and "build something" — those
conflict. Agreed approach: structure-first, with the actual expression written at exactly three
points where the structure *is* the math (the collapse problem, VICReg, SIGReg). Revisit if the
learner pushes back.
