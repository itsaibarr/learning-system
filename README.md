# learning-system

A private, markdown-only learning system: an AI agent that teaches for understanding
(not summaries), backed by Obsidian for durable knowledge and Anki for retrieval practice.

Works from **OpenCode** (primary) and **pi** — both load the same canonical skills in
`skills/`. There is exactly one script in the whole system (`scripts/anki_push.py`).

## How it fits together

| Information | Lives in |
|---|---|
| Long-term knowledge: maps, concept notes, source notes | Obsidian vault (or `subjects/` in plain mode) |
| Spaced repetition and active recall | Anki (via a human-gated queue) |
| Study plans, cycles, mistake logs, decisions, progress | This repository |
| Temporary agent work | Session only — durable conclusions graduate out |

## Start here

- `docs/setup.md` — one-time wiring (frameworks, tmux subagents, AnkiConnect, vault).
- `docs/plain-mode.md` — the layout for machines with no Obsidian vault (notes in
  `subjects/`, Unicode math instead of LaTeX).
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
