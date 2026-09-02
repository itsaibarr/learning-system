# Anki queue

See templates/anki-review-queue.md for format and card-writing rules.

## Batch: example-kinematics | deck: AS-Physics::Kinematics | status: draft

Q: A ball is thrown straight up. At the highest point, what is its acceleration?
A: $9.8\ \text{m s}^{-2}$ downward (gravity acts throughout the flight)
Tags: kinematics misconception example
Src: [[Concepts/projectile-signs]]

Q: What single condition must hold for the SUVAT equations to be valid?
A: Constant (uniform) acceleration
Tags: kinematics suvat example
Src: [[Concepts/suvat]]

Text: On a velocity-time graph, displacement is the {{c1::area under the graph}} and acceleration is the {{c2::gradient}}
Tags: kinematics graphs example
Src: [[Concepts/motion-graphs]]

Q: A body moving in the negative direction speeds up. What is the sign of its acceleration?
A: Negative (acceleration points the same way as the velocity)
Tags: kinematics signs example
Src: [[Concepts/projectile-signs]]

Text: $s = ut + {{c1::\frac{1}{2}at^2}}$, valid only for {{c2::constant acceleration}}
Tags: kinematics suvat example
Src: [[Concepts/suvat]]

## Batch: example-context-windows | deck: Tech::LLM | status: draft

Q: What makes self-attention's compute cost grow with the square of sequence length?
A: Every token attends to every other token — the comparison is pairwise
Tags: context-windows example
Src: [[Concepts/attention-cost]]

Text: During generation, re-computing past tokens' keys and values is avoided by the {{c1::KV cache}}
Tags: context-windows example
Src: [[Concepts/attention-cost]]

Q: In a long prompt, where should critical facts and instructions go for best retrieval?
A: At the start or end — middle positions retrieve worst ("lost in the middle")
Tags: context-windows example
Src: examples/technical-deep-dive/experiment.md

## Batch: world-models-2026-09-02 | deck: Research::World-Models | status: draft

Q: In the violation-of-expectation protocol applied to a model, what plays the role of an infant's looking time?
A: The model's own prediction error
Tags: world-models voe measurement
Src: [[subjects/world-models/notes/surprise-is-not-understanding.md]]

Q: Why is violation detection scored within matched possible/impossible pairs instead of against an absolute error threshold?
A: Raw prediction error scales with scene complexity, so pairing cancels that out
Tags: world-models voe protocol
Src: [[subjects/world-models/sources/lecun-eth-2026.md]]

Q: When a world model's prediction error spikes on a physically impossible video, what is the competing explanation to "it understands physics"?
A: Novelty detection — the clip is absent from training, so it is unfamiliar whatever the reason
Tags: world-models confound
Src: [[subjects/world-models/notes/surprise-is-not-understanding.md]]

Q: What single property makes an experiment a control?
A: The competing explanations predict different outcomes
Tags: world-models methodology principle
Src: [[subjects/world-models/notes/surprise-is-not-understanding.md]]

Q: Why can a linear probe on a frozen representation not settle whether a model understands physics or merely detects novelty?
A: It separates the clips using the disputed novelty signal itself, so both explanations predict it succeeds
Tags: world-models confound methodology
Src: [[subjects/world-models/notes/surprise-is-not-understanding.md]]

Q: Why is trajectory prediction from a frozen representation stronger evidence of physical understanding than a surprise spike?
A: Forecasting requires carrying state forward, which distance-from-training cannot produce
Tags: world-models evidence
Src: [[subjects/world-models/notes/surprise-is-not-understanding.md]]

Q: Why does self-supervised prediction need no labels?
A: Reality supplies the target — the next frame is the answer
Tags: world-models ssl foundation
Src: [[subjects/world-models/map.md]]

Text: Physical-reasoning benchmarks split three ways: {{c1::violation detection}} (did it register something impossible), {{c2::physical prediction}} (can it forecast the outcome), and {{c3::physical QA}} (can it say what was wrong in language)
Tags: world-models benchmarks taxonomy
Src: [[subjects/world-models/notes/surprise-is-not-understanding.md]]

Q: In LeCun's information-maximization program, what does he concede about every empirical measure of information content?
A: They are upper bounds, while maximization requires a lower bound
Tags: world-models sigreg admission
Src: [[subjects/world-models/sources/lecun-eth-2026.md]]

