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
