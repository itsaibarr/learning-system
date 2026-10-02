# learning-system

A private, markdown-only learning system: an AI agent that teaches for understanding
(not summaries), backed by Obsidian for durable knowledge and Anki for retrieval practice.

Works from **OpenCode** (primary): `/learn <topic>` from any folder. `scripts/learn.py`
(on PATH as `learn`) holds the learner state and the teaching rules; the agent writes
the content and follows the engine's `NEXT:` lines. Every new topic is researched first
(PRAXIST method, source-backed brief in vault `Sources/`); lessons cite that brief.

Install on a machine: `bash scripts/install.sh` (idempotent). `scripts/anki_push.py` pushes
approved cards.

## How it fits together

| Information | Lives in |
|---|---|
| Long-term knowledge: maps, concept notes, source notes | Obsidian vault |
| Spaced repetition and active recall | Anki (via a human-gated queue) |
| Learner state: preferences, mastery, reviews, mistakes | `state/learner.json` (this repo) |
| One note per learning session | Obsidian vault `Sessions/` |
| Study plans, cycles, mistake logs, decisions | This repository |
| Temporary agent work | Session only — durable conclusions graduate out |

## Start here

- `docs/setup.md` — one-time wiring (frameworks, tmux subagents, AnkiConnect, vault).
- `docs/operating-guide.md` — what a learning session looks like end to end.
- `workflows.md` — the five playbooks (learn from zero, exam prep, book/course,
  build-to-learn, weekly review).
- `AGENTS.md` — the router the agent itself follows.

## Attribution

The teaching pedagogy — dependency-graph teaching, unconditional truths first,
"how could I have discovered this?", the probe → plan → teach loop, and the
quiz-construction rules — is adapted from
[amosblomqvist/learn](https://github.com/amosblomqvist/learn) by Amos Blomqvist,
shared as-is in [How I Use AI to Learn Things](https://www.youtube.com/watch?v=kzcI5F4tGiU).
The original is a pi TUI configuration; this repo ports the pedagogy to a portable
markdown core and adds the study-planning, Obsidian, and Anki layers around it.
The upstream repo carries no license file; this adaptation is private and not redistributed.

The research step uses [sapientinc/PRAXIST](https://github.com/sapientinc/PRAXIST):
its `praxist-scientific-research` skill (installed unmodified from a clone) and its
no-key literature lookup (`praxist` package, called by `learn lit`). PRAXIST is under the
Fair Source License 1.0 (free below USD 1M annual revenue, internal use);
`skills/teach-understanding/references/research.md` adapts its method for teaching.
