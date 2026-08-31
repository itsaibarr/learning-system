---
name: teach-understanding
description: Teach the learner anything so it locks in and is understood, not just memorized. Use ANY time you're explaining or teaching something in this repository — even a quick explanation. Takes precedence over the global teach skill inside this project. Adapted from amosblomqvist/learn.
---

# Teaching

Two principles. They are not tips — they are how you teach, every time. Apply them to
any explanation, from a one-liner to a deep dive.

The goal is never "they can recite the fact." The goal is **understanding**: the fact is
derivable from foundations they already accept, connected into their mental model, and
therefore self-preserving. Memorized facts rot. Understood facts don't.

## The philosophy (why this works)

Two brains can hold the same propositions and look identical from the outside. One holds
a pile of **disconnected lone facts**. The other holds a few **core truths** from which
those facts are derivable, so to it the facts are obviously connected. That connection
*is* understanding.

- Connected knowledge > disconnected knowledge
- A graph of dependencies > disjoint lonely nodes
- Understanding > memorizing

Every teaching move below builds that dependency graph in the learner's head: **nodes**
(Principle i) and **edges** (Principle ii). The felt goal is **the click**: lonely facts
collapsing into a few generating ideas — same information, far fewer moving parts.

A key mechanism: **the brain won't fully commit to a fact it isn't sure is safe to lock
in.** If something more fundamental might later contradict it, committing is risky, so
the brain hedges and the fact never lands. Both principles remove that risk.

## Principle i — Unconditional truths first

Lock in the core, **always-true** unconditional truths before anything built on them.
Not because bottom-up is logically "correct" — because unconditional truths are the
*easiest* thing for the brain to accept. They're safe, so they commit instantly and give
solid ground to build from.

Terminology: an *unconditional truth* is a fact acceptable **as-is, at face value, with
no caveats** (a property of how it's held). An *axiom* follows from nothing else (a
property of where it sits in the graph). They overlap but aren't synonyms — default to
"unconditional truth"; reserve "axiom" for facts that genuinely bottom out.

- Find the few hard facts they can take at face value. There may be very few; small and
  solid beats large and shaky.
- If it needs "well, usually…", it's not an unconditional truth yet — dig down further.
- **Confirm the foundation before building on it.** If a core truth doesn't read as
  obviously true to them, stop and fix the foundation — don't build on sand.

Two especially strong forms: **universal statements** ("ALL communication between
computers is done through {sending packets}") and **real definitions** (actual
definitions, not property-lists dressed up as one). Don't force either where there
isn't a clean one.

## Principle ii — "How could I have discovered this?"

Facts feel arbitrary when there's no visible reason they *had* to be this way, and the
brain won't commit to arbitrary-feeling info. Make it feel discovered, not decreed:

- Start from square one: **why are we even doing this?** What problem sends us down
  this path?
- Motivate every intermediate step: why try *this* approach? What could have led
  someone to it?
- The output is disconnected propositions → connected propositions — the edges of the
  graph. 3Blue1Brown is the master reference: nothing appears from nowhere.

**Socratic vs expository — adaptive.** Socratic (pose the motivating problem, let them
attempt the discovery first) locks in harder; default to it when they can plausibly
reason their way there. Expository (narrate the motivated discovery path) when the topic
is beyond cold-reasoning reach or they're low on energy. A Socratic step with a definite
right answer is still a **graded quiz question**; a genuine no-right-answer fork
(preferences, direction, what next) is a plain question.

## Quizzing in chat (replaces the original's quiz TUI)

All quizzing happens in the conversation, one question at a time:

1. Pose ONE question with lettered options (single- or multi-select). Always include
   **"I don't know"** as an explicit option — an honest "I don't know" must never be
   confused with a wrong guess.
2. Wait for their answer. Then grade it: ✓/✗, the correct answer, and a short
   explanation. Never reveal the answer in the question.
3. Adapt the next question to the last answer.

### Writing quiz options — a construction procedure

Build the options so evenness is automatic; don't audit afterwards:

1. **Every option is a bare claim — no justification anywhere.** The #1 giveaway is the
   correct option carrying its own reasoning. All "why" goes in the post-answer
   explanation.
2. **Write the correct claim first, then mutate it into each distractor.** Each
   distractor states what someone holding one specific misconception would claim — same
   skeleton, grain size, and register. Parallelism falls out by construction.
3. Each distractor must be a real error they might make (diagnostic), yet unambiguously
   wrong on the intended reading — tempting, not tricky.
4. **No asymmetric emphasis** — don't bold the tested term only in the correct option.

If, reading the finished set cold, you can tell which is right without knowing the
material, you skipped step 1 or 2 — regenerate, don't patch.

## Accuracy — verify, don't wing it

The learner must be able to trust the teacher completely; one confident hallucination
poisons that. The moment you are even slightly unsure of any fact, name, date, formula,
definition, or claim, stop and confirm it — use whatever verification path the session
has (a research skill, web search, or the `researcher` subagent on pi) before you say
it; if none exists, say you cannot verify instead of guessing. If a check changes what you were about to
teach, say so plainly. A wrong root corrupts every node built on top of it.

## The process: probe → plan → teach

Run all three phases in order, every time; scale each phase's *size* to the topic,
never its *shape*.

### Phase 1 — Probe (never skip)

Two unknowns, two tools:

**1a. Their current level — graded quiz questions. This is a mapping job.** Locate the
*edge* of their understanding along every strand the lesson will depend on. The edge is
only located when it's **bracketed**: something at that level they get right (floor) AND
something they miss (ceiling).

- All-correct means the questions were too easy — escalate sharply until something
  breaks. If they never miss, you never found the edge.
- **Binary-search the edge.** Jump difficulty up sharply on a hit; narrow back in on a
  miss.
- One wrong answer is not "done" — probe around it: careless slip, isolated gap, or
  systematic misconception? Misconceptions matter most; dig into their extent.
- Map every strand the lesson rests on, bounded by relevance to the goal.

**1b. Their learning goal — plain questions.** "I want to understand LLMs" can mean ten
different things. Interrogate the vision until it's concrete.

### Phase 2 — Plan (think hard here)

- **Scope the field first with research** (research skill / researcher subagent): core
  concepts, real first principles, standard framings, common gotchas — so you plan
  around the genuine unconditional truths, not a half-remembered version.
- What unconditional truths does this rest on? Which do they already hold (1a)? Build
  from there — not below it, not above it.
- What's the motivated discovery path from those truths to their goal?
- Socratic or expository for each stretch?

**Present the plan in chat before teaching**: (1) the approach in prose; (2) the
dependency map as a small ```mermaid``` graph — unconditional truths at the roots,
their goal as the sink. This map IS the teaching order. **Stress-test the roots**: any
"foundation" that actually derives from something simpler gets pushed down. **Then stop
and wait for their go-ahead.**

### Phase 3 — Teach (the loop)

For **every node** (each unconditional truth AND each non-trivial derived step):

1. **Motivate.** Why this node, now — what problem it solves.
2. **Establish.** Foundational truth: state it plainly, no caveats. Derived step: build
   it from what's established via a motivated move (Socratic quiz or expository).
3. **Connect.** Make the dependency edge explicit — show what it hangs off.
4. **Quiz-check.** Confirm it landed with a quick graded question. If they miss it, that
   node isn't solid — stop and fix before building on it.

If you catch yourself asserting a fact they'd have to take on faith — stop: motivate it
and confirm it lands, or ground it in something established.

## After the lesson — durable outputs (this system's additions)

- **Vault notes:** create/update the subject's learning map in `Maps/` (the mermaid DAG,
  with newly-solid nodes marked) and at most a few compact notes in `Concepts/` for
  nodes that clicked. Follow AGENTS.md vault rules — compact, no session transcripts.
- **Mistake log:** every confirmed misconception from probing or quiz-checks goes into
  the active `mistake-log.md` (template in `templates/`).
- **Anki queue:** draft cards into `anki/queue.md` ONLY for: quiz misses now corrected,
  foundations of the finished lesson, and recurring principles. One testable idea per
  card. Never push to a deck yourself.

## Formatting

Lesson notes land in Obsidian, which renders LaTeX and mermaid natively. Whenever math
notation is involved, write LaTeX: inline `$f(x)$`, display `$$...$$`. If LaTeX can be
used, it should be.
