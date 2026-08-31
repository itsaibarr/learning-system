---
name: visualize
description: Add a correct, minimal diagram to a lesson or note when an idea is genuinely clearer as a picture — dependency graphs, flows, sequences, state machines, trees, comparisons. Emits inline mermaid blocks that Obsidian renders natively. Adapted from amosblomqvist/learn (PNG maker pipeline removed).
---

# Visualize

A picture earns its place only when it shows something words can't — shape, structure,
direction, relationship. This skill produces ONE such picture as an inline
```mermaid``` block, which Obsidian (and most markdown renderers) render natively. No
render pipeline, no subagents, no image files.

## When to visualize (and when not to)

This system builds a **dependency graph in the learner's head** — a visual is powerful
exactly when it makes structure visible. Reach for one when the idea is a **structure or
relationship**: dependencies, a system with parts and arrows, a flow/pipeline, a
sequence of exchanges, a state machine, a tree/hierarchy, a comparison, a containment.

Do NOT visualize when prose or a single equation already carries it. A decorative
diagram that restates the sentence next to it adds noise and a chance to be wrong.
When in doubt, don't — a missing visual is cheaper than a false one.

Precise geometry (coordinate figures, vectors, plots) is out of scope for mermaid —
use LaTeX where it can carry the idea, or describe it in prose. If geometric figures
become a recurring need, that's the trigger to reintroduce an SVG path (see decision
log) — not before.

## One idea, fewest elements

The most common failure is **cramming** — every extra label makes the picture harder to
read AND easier to get wrong. Before writing the block, prune to the fewest elements
that carry the idea; for each element ask: *"if I delete this, is the idea still
clear?"* If yes, delete it. More than ~7 nodes means simplify first.

- BAD: a diagram "about how TCP works"
- GOOD: `graph TD`: `packet` at top, arrows down to `ordering` and `retransmit on
  loss`, both into `reliable stream` — showing reliability is built FROM packets.

## Correctness check

Mermaid renders from source, so what you write is what appears — but syntax parsing is
not truth. Before moving on, re-read the finished block and verify every arrow
direction, every label, and every containment actually asserts something true. A wrong
arrow is a failure even if it renders beautifully. If a diagram can't say the thing
truthfully in ~7 nodes, rethink or drop it.

## Placement

- Lesson dependency maps → the subject's map note in `Maps/`.
- Concept structure → inline in the relevant `Concepts/` note or chat reply.
- Introduce the visual in one sentence, then let it carry the idea — don't narrate
  every element back in prose.
