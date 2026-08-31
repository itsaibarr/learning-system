# Operating guide

## The contract

Three stores, no duplication: **Obsidian** holds what you know (maps, concepts,
sources, reviews). **Anki** holds what you must not forget (cards, human-gated).
**This repo** holds how you're learning it (briefs, cycles, mistake logs, decisions,
the queue). A session is scratch space — only template-shaped conclusions survive it.

## A session, end to end

1. Open the agent (OpenCode, or pi inside tmux for subagents) in this repo. AGENTS.md
   routes your request to one mode: Teach / Research / Plan / Quiz / Review / Cards / Notes.
2. Teaching always runs probe → plan → teach (`skills/teach-understanding`): the agent
   brackets what you know, presents a dependency-map plan, waits for your go-ahead,
   then teaches node by node with graded checks.
3. During the session the agent may update the subject's map, add a concept note for
   something that clicked, log a confirmed misconception, or draft cards — nothing else.
4. Session end: progress tick in the active study cycle. No transcripts, no reports.

## Multi-session continuity

Context is re-entered from artifacts, not memory: the learning brief says where you're
going, the map says what's solid (node status table), the mistake log says what to
re-check, the cycle says what's next. Starting a new session on a subject = agent reads
those four files (seconds, not a re-teaching). If a session produced something those
files don't capture, it wasn't durable — let it go.

## Weekly rhythm

Playbook 5 (workflows.md) once a week: review → Anki stats → mistake sweep → next
week's ≤3 priorities → prune. Then you (not the agent) approve card batches and run
`python3 scripts/anki_push.py`. Daily Anki reviews are yours alone — the agent never
sees or grades them; lapse rates surface at the weekly review.

## Rules that keep it small

- One artifact per fact; artifacts link, never restate each other.
- Every template has a size ceiling — hitting it means cut, not continue.
- No card for anything easily re-derived; no note for anything not yet understood.
- The agent never rewrites your own words in the vault, never pushes to Anki,
  never creates a note outside the five folders.
