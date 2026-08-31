# Todo: Private Learning System

## Task 1: Repo skeleton, README, AGENTS.md router

**Description:** Create the `learning-system/` structure in this workspace. README explains
the system in ~30 lines and credits amosblomqvist/learn (repo + video; no LICENSE upstream,
so explicit attribution + adapted-not-copied prose). AGENTS.md is the router: mode selection
(Explain / Research / Plan / Quiz / Review / Cards / Notes), durable-context rules (save only
brief-sized conclusions; no research dumps), and ownership boundaries (Obsidian = long-term
knowledge, Anki = retrieval, repo = plans/progress/decisions, session = scratch).

**Acceptance criteria:**
- [ ] Structure matches plan.md's target tree (empty dirs allowed via .gitkeep)
- [ ] AGENTS.md ≤ ~120 lines, includes router table + context rules + tool ownership
- [ ] README includes attribution block

**Verification:**
- [ ] Manual: tree matches plan; no secrets; `git status` clean after commit

**Dependencies:** None · **Scope:** S

## Task 2: Port and adapt the two skills; wire both frameworks

**Description:** Adapt `skills/teach/SKILL.md` from the original: keep philosophy, probe →
plan → teach loop, and quiz-construction rules verbatim in spirit; replace `quiz` /
`ask_user_question` tool references with chat quizzing; replace md-log references with
direct vault writes; researcher references point to available research skill (OpenCode) or
researcher subagent (pi). Adapt `skills/visualize/SKILL.md`: keep when-to/when-not rules,
replace maker pipeline with inline ```mermaid``` blocks. Wire project-scoped discovery for
OpenCode (verify current mechanism via context7 docs first) and pi.

**Acceptance criteria:**
- [ ] Both skills are plain markdown, no pi tool names remain
- [ ] OpenCode session in the repo lists/loads project `teach` without touching global Pocock skill
- [ ] pi session in the repo loads the same canonical files (no duplication)

**Verification:**
- [ ] Manual smoke: `opencode` + `pi` in repo dir, confirm skill discovery both sides

**Dependencies:** 1 · **Scope:** M

## Checkpoint A
- [ ] Both frameworks discover project skills; global skills untouched; commit

## Task 3: Nine compact templates

**Description:** Write `templates/`: learning-brief, learning-map, source-register (adapt
from `~/harness/agent/modules/research/source-register.md`), concept-card (adapt from
evidence-card.md), mistake-log, anki-review-queue, study-cycle, weekly-review, decision-log.
Each ≤ ~40 lines, table/checklist-shaped, designed for agent retrieval not prose.

**Acceptance criteria:**
- [ ] 9 templates present, each ≤ ~40 lines
- [ ] source-register + concept-card demonstrably derived from harness versions
- [ ] anki-review-queue format matches what `anki_push.py` will parse (Q/A/Tags/Deck blocks)

**Verification:**
- [ ] Manual read-through against the "compact durable context" principle

**Dependencies:** 1 · **Scope:** M

## Task 4: Anki queue + push script + smoke test

**Description:** Define `anki/queue.md` card format (basic + cloze; one testable idea per
card; source link back to vault note). Write `scripts/anki_push.py` (stdlib only): parse
queue, push approved batch via AnkiConnect `addNotes`, move pushed cards to `anki/pushed.md`,
fail loud if Anki isn't running. Smoke test against a throwaway `_LearningSystemTest` deck,
then delete that deck.

**Acceptance criteria:**
- [ ] Script pushes only cards marked approved; unapproved cards stay queued
- [ ] Duplicate push is prevented (AnkiConnect dup detection on)
- [ ] Never writes to any deck other than the one named in the batch header

**Verification:**
- [ ] Smoke: 2 test cards round-trip into `_LearningSystemTest`, visible in Anki, deck removed after

**Dependencies:** 3 · **Scope:** M

## Task 5: Obsidian vault folders + templates (LIVE-VAULT CHANGE — approved at gate)

**Description:** In `~/Documents/Obsidian Vault`: create `Maps/`, `Concepts/`, `Sources/`,
`Reviews/`, `Templates/`; copy the relevant templates into `Templates/`. Touch nothing else
(existing Untitled notes and images stay).

**Acceptance criteria:**
- [ ] 5 folders exist; templates copied; zero existing files modified/moved/deleted

**Verification:**
- [ ] `ls` diff of vault before/after shows only additions

**Dependencies:** 3 · **Scope:** XS

## Task 6: tmux + pi-interactive-subagents + researcher (pi side)

**Description:** `brew install tmux`; install amosblomqvist/pi-interactive-subagents per its
README; adapt the original `agents/researcher.md` for the user's pi model config (no
hardcoded openrouter model — use configured provider). cmux remains the terminal app; tmux
exists only as the subagent substrate.

**Acceptance criteria:**
- [ ] pi can spawn the researcher subagent and get a sourced brief back
- [ ] Failure here does not block the rest of the system (documented degraded mode)

**Verification:**
- [ ] Smoke: one researcher run on a trivial factual question

**Dependencies:** 2 · **Scope:** S

## Checkpoint B
- [ ] Card round-trip works; vault ready; researcher spawns (or degraded mode documented); commit

## Task 7: workflows.md — five playbooks

**Description:** One file, five compact playbooks matching the prompt's Phase 5: learn-from-
zero, exam prep, book/course/research collection, build-to-learn experiment, weekly review.
Each playbook: trigger, steps, which templates it touches, what gets saved where, exit
criteria. No playbook over ~30 lines.

**Acceptance criteria:**
- [ ] 5 playbooks, each referencing only templates/skills that exist
- [ ] Each names its durable outputs (vault note / repo file / Anki queue) explicitly

**Verification:**
- [ ] Cross-check every referenced path resolves

**Dependencies:** 2, 3 · **Scope:** S

## Task 8: docs/setup.md + docs/operating-guide.md

**Description:** setup.md: clone → wire OpenCode + pi → tmux/subagents → AnkiConnect check →
vault folders. operating-guide.md: what a session looks like end-to-end, role boundaries,
how context stays compact across sessions, what /wrap-session saves.

**Acceptance criteria:**
- [ ] A fresh machine could reproduce the setup from setup.md alone
- [ ] Operating guide fits in one screen-read (~100 lines)

**Verification:**
- [ ] Dry-run setup.md steps against actual system state (all already true)

**Dependencies:** 2–6 · **Scope:** S

## Task 9: Example 1 — academic exam prep (AS Physics slice)

**Description:** Run the exam-prep playbook for real on one narrow AS Physics topic:
study-cycle plan, compact learning map (inline mermaid), mistake log with 2–3 seeded
entries, drafted Anki batch (≤10 cards) left in the queue for user approval. Artifacts in
`examples/exam-prep-physics/`.

**Acceptance criteria:**
- [ ] All artifacts use the real templates unmodified
- [ ] Cards obey card-writing rules; batch is NOT pushed to a real deck

**Verification:**
- [ ] Playbook exit criteria met; artifacts ≤ ~150 lines total

**Dependencies:** 7 · **Scope:** M

## Task 10: Example 2 — technical deep dive

**Description:** Run the from-zero/build-to-learn playbooks on "how LLM context windows
work": source register (3–4 sources), 2–3 concept cards, one small applied exercise, one
weekly review. Artifacts in `examples/technical-deep-dive/`.

**Acceptance criteria:**
- [ ] Same template fidelity + compactness rules as Task 9
- [ ] Includes at least one retrieval-practice artifact, not only summaries

**Verification:**
- [ ] Playbook exit criteria met

**Dependencies:** 7 · **Scope:** M

## Task 11: Review, simplify, ship

**Description:** /code-review on the repo (script + docs), then /simplify pass: delete any
template/section/doc the two examples never used. Write the simplification report (what was
excluded and why — including everything dropped from the original). Create private GitHub
repo `learning-system`, push.

**Acceptance criteria:**
- [ ] Simplification report lists ≥ the audit's removals + anything cut in D
- [ ] All 8 Phase-8 validation criteria from the original prompt checked off
- [ ] `gh repo view` shows repo is Private; no secrets in history

**Verification:**
- [ ] Final read-through of AGENTS.md + operating-guide against actual repo contents

**Dependencies:** 9, 10 · **Scope:** S

## Checkpoint D — Definition of Done
- [ ] System works from OpenCode; nothing depends on the pi TUI extensions
- [ ] Obsidian / Anki / repo have distinct, stated roles
- [ ] Active recall is produced by the workflows, not just summaries
- [ ] Repo smaller + clearer than original; user has reviewed
