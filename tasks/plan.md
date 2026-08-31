# Implementation Plan: Private Learning System (adapted from amosblomqvist/learn)

## Overview

Build a private, markdown-only learning-system repository that preserves the pedagogy of
`amosblomqvist/learn` (dependency-graph teaching, probe → plan → teach loop, graded
quizzing, one-correct-diagram discipline) while replacing its pi-TUI implementation with
a portable core that both OpenCode and pi can load. Add the ~70% that the original repo
does not cover: Anki integration (AnkiConnect + human-gated review queue), study
plans/cycles, exam prep, mistake log, weekly review, and Obsidian vault conventions.

Built in this workspace, then pushed to a new **private** GitHub repository.

## Approved Decisions (from audit gate, 2026-08-31)

| # | Decision | Resolution |
|---|---|---|
| 1 | Target framework | **A+C**: OpenCode-first, portable markdown core (plain SKILL.md files loadable by both OpenCode and pi; zero TypeScript ported) |
| 2 | Terminal | **cmux stays the terminal app; install tmux** as the substrate for pi-interactive-subagents (user expects to keep using the subagents stack) |
| 3 | Teach-skill conflict | **Pocock's `teach` stays global** (`~/.config/opencode/skills/teach` untouched); **amos's adapted teach skill is project-scoped** to this repo only |
| 4 | Anki path | AnkiConnect (addon already installed) + markdown review queue; cards reach the real deck only after human approval of a batch |
| 5 | Obsidian structure | Minimal 5 folders in the (currently empty) vault: Maps, Concepts, Sources, Reviews, Templates |
| 6 | Diagrams | Inline ```mermaid``` blocks (Obsidian renders natively); no PNG pipeline, no svg-maker |

## Architecture Decisions

- **Portable core = plain markdown.** Skills live in `skills/` at repo root. Wiring is
  per-framework config pointing at that one canonical copy (OpenCode project skill dir /
  symlink; pi project `.pi` or settings `skills` path). No file is duplicated.
- **AGENTS.md at repo root is the router.** It replaces the suggested `/agent` directory
  (learning-router.md, skill-triggers.md collapse into it). It defines: when to Explain /
  Research / Plan / Quiz / Review / Create cards / Update notes; the durable-context
  rules (what gets saved after a session, what doesn't); and ownership boundaries
  (Obsidian = long-term knowledge, Anki = retrieval, repo = plans/progress/decisions).
- **Quizzing happens in chat.** The 1,062-line quiz TUI is not ported; its real value —
  the option-construction procedure, "I don't know" option, grade-then-explain flow — is
  already text in the teach skill and stays there. Chat quizzes feed two outputs: probe
  results (session-local) and card candidates (→ Anki queue).
- **md-log is replaced by direct vault writes.** Instead of mirroring the session, the
  agent writes/updates the lesson's map + concept notes in the vault at natural
  checkpoints. Less output, more durable.
- **One script total.** `scripts/anki_push.py` (Python stdlib only: `json`, `urllib`)
  parses `anki/queue.md` and pushes approved batches via AnkiConnect (localhost:8765).
  Everything else in the system is markdown.
- **Reuse harness assets.** `source-register.md` and `evidence-card.md` from
  `~/harness/agent/modules/research/` are adapted (evidence-card → concept-card), not
  reinvented.
- **Attribution.** Source repo has no LICENSE file; README credits the author, the repo,
  and the video. Prose is adapted/rewritten where practical rather than copied verbatim;
  the teach skill (the author's shared-as-is config, with published install instructions)
  is credited explicitly.

## Preserved / Replaced / Removed (from the approved matrix)

- **Preserved (adapted):** teach skill (crown jewel), visualize skill's judgment rules,
  researcher's verification role, md-log's "render in Obsidian" idea.
- **Replaced:** quiz/ask-user-question TUI → chat; md-log → direct vault writes;
  visual-tools + makers → inline mermaid; pi researcher agent def → OpenCode research
  skill (and a pi-interactive-subagents researcher for the pi side).
- **Removed:** all 4 TS extensions (~2,400 loc), svg-maker, mermaid-maker, visual-tools
  package, Chrome/mermaid-cli/rsvg deps.
- **Net-new:** Anki rules + queue + push script, 5 workflow playbooks, 9 compact
  templates, setup + operating guides, 2 validated examples.

## Target Repository Structure

```
learning-system/
  README.md                 # what this is, attribution, 60-second orientation
  AGENTS.md                 # router + durable-context rules (read by OpenCode & pi)
  skills/
    teach/SKILL.md          # adapted amos teach skill (project-scoped)
    visualize/SKILL.md      # when-to-diagram rules + inline mermaid
  workflows.md              # 5 playbooks: from-zero, exam-prep, book/course, build-to-learn, weekly review
  templates/                # each ≤ ~40 lines, structured for agent retrieval
    learning-brief.md  learning-map.md  source-register.md  concept-card.md
    mistake-log.md  anki-review-queue.md  study-cycle.md  weekly-review.md  decision-log.md
  anki/
    queue.md                # drafted cards awaiting human approval
  scripts/
    anki_push.py            # stdlib-only AnkiConnect pusher (approved batches → deck)
  docs/
    setup.md                # wiring both frameworks, tmux/subagents, AnkiConnect, vault folders
    operating-guide.md      # how a session runs; Obsidian/Anki/repo role boundaries
  examples/
    exam-prep-physics/      # validation artifact (Phase D)
    technical-deep-dive/    # validation artifact (Phase D)
```

Smaller than the prompt's suggested structure: `/agent` (3 files) → `AGENTS.md`;
5 integration docs → 2; 5 workflow files → 1.

## Task List

### Phase A — Foundation (repo core)
- [ ] Task 1: Repo skeleton, README with attribution, AGENTS.md router
- [ ] Task 2: Port + adapt the two skills (teach, visualize), wire into OpenCode and pi

### Checkpoint A
- [ ] Both frameworks discover the project-scoped skills; Pocock's global teach untouched

### Phase B — Integrations
- [ ] Task 3: Nine compact templates (reuse harness source-register / evidence-card)
- [ ] Task 4: Anki queue format + `anki_push.py` + AnkiConnect smoke test
- [ ] Task 5: Obsidian vault minimal folders + template copies (live-vault change, approved)
- [ ] Task 6: tmux + pi-interactive-subagents + researcher agent for the pi side

### Checkpoint B
- [ ] A drafted card batch round-trips queue → approval → test deck; vault folders exist; pi can spawn researcher

### Phase C — Workflows and docs
- [ ] Task 7: `workflows.md` — the five playbooks
- [ ] Task 8: `docs/setup.md` + `docs/operating-guide.md`

### Phase D — Validation and ship
- [ ] Task 9: Example 1 — academic exam prep (AS Physics slice)
- [ ] Task 10: Example 2 — technical deep dive
- [ ] Task 11: Review + simplify pass, simplification report, push to private GitHub repo

### Checkpoint D (Definition of Done)
- [ ] All 8 validation criteria from the original prompt's Phase 8 pass
- [ ] Final repo is smaller and simpler than the original + net-new scope demands
- [ ] Nothing secret/personal committed

## Risks and Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| OpenCode project-skill discovery path differs by version (1.18.25) | Med | Verify against current OpenCode docs (context7) in Task 2 before wiring; fall back to symlink into `~/.claude/skills` (both frameworks already load it) with a project-name prefix |
| AnkiConnect requires Anki running; API shape drift | Low | Smoke test in Task 4 pushes to a throwaway `_LearningSystemTest` deck first; script fails loud with a "start Anki" message |
| Live vault edits | Low | Scope: create 5 empty folders + copy templates only; never edit/delete existing notes |
| pi-interactive-subagents install friction (external repo, tmux-only) | Med | Task 6 is isolated; if it fails, system still works subagent-less (per original README) — mark as known-degraded, don't block |
| No LICENSE in source repo | Low | Private repo, explicit attribution, adapted prose; no redistribution |
| Two teach skills colliding | Low | Amos's skill is project-scoped only; AGENTS.md states the precedence explicitly |

## Open Questions (non-blocking, defaults chosen)

- Private repo name: defaulting to **`learning-system`** under your GitHub account.
- Example topics: defaulting to **AS-level Physics** (matches the prompt's exam example)
  and **how LLM context windows work** (technical). Say otherwise if you want different ones.
