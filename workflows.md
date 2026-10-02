# Workflows

Five playbooks. The agent picks exactly one per AGENTS.md routing; each names its
durable outputs — anything not listed there dies with the session.

## 1. Learn a new subject from zero

Trigger: "I want to learn X" with no existing brief for X.

1. `/learn <subject>` in OpenCode. The engine asks for the goal, then `learn plan`
   draws the 3-7 concept map into the session note.
2. Loop per concept, all in the session note: theory block → recall question → graded
   feedback → the engine picks the next step (more practice, re-teach, prerequisite,
   or next concept).
3. Next sessions: `/learn <subject>` again. Due reviews come first.
4. Optional for big subjects: a learning brief and source register in the repo; cards
   for corrected misconceptions → `anki/queue.md`.
5. End of week → playbook 5.

Durable: session notes, `state/learner.json`, the dashboard; brief/register if used.
Exit: target outcome in the brief is demonstrated, not summarized.

## 2. Prepare for an exam

Trigger: named assessment with a date (e.g. AS Physics paper).

1. Map exam scope from the official spec → learning map with per-topic mark weight.
2. Diagnose weak foundations: probe hardest-first across topics (bracket the edge).
3. Prioritize high-mark × weak topics → `study-cycle.md` (1–2 weeks per cycle).
4. Per cycle task: practice questions BEFORE re-study; every miss → `mistake-log.md`.
5. Misconception rows → Anki drafts; slips get no cards.
6. Late cycles: timed past-paper mocks; log marks as cycle evidence.
7. Final review: re-quiz every mistake-log row still open.

Durable: map, study cycles with evidence, mistake log, queue drafts.
Exit: mock at target grade, mistake log rows closed.

## 3. Learn from a large book, course, or research collection

Trigger: a specific large source ("work through <book/course>").

1. Register the source; chapter/module map → vault `Maps/` (structure only, ≤15 nodes).
2. Per chapter: read/watch, then close the source and answer "what are the key claims?"
   from memory — that recall attempt IS the processing step.
3. Only claims that survive checking become `concept-card.md` notes in `Concepts/`
   (with page/section refs). No chapter summaries.
4. Apply: one problem or experiment per major section.
5. Cards only for claims you expect to need in six months.

Durable: source register + source note, concept notes, queue drafts.
Exit: you can reconstruct the book's argument from the map without opening it.

## 4. Technical experiment / build-to-learn

Trigger: "learn X by building" or a concept that only practice can teach.

1. Define the learning objective as a question the experiment answers → decision-log row.
2. Plan the smallest experiment that answers it; build/run it in the subject folder.
3. Observe: record what changed and why in the experiment's README (≤20 lines).
4. Explain the concept back (teach-understanding Phase 3 in reverse — learner teaches).
5. Cards only for principles that recurred across runs, not one-off incantations.

Durable: experiment code + short README, decision-log row, queue drafts.
Exit: the objective question has an evidence-backed answer.

## 5. Weekly learning review

Trigger: end of study week, or a cycle ends.

1. Fill `templates/weekly-review.md` → vault `Reviews/` (agent drafts, learner edits).
2. Pull Anki stats (reviews done, lapses) — flag decks with >20% lapse rate.
3. Open `Maps/Learner dashboard.md`: open mistakes, due reviews, concepts stuck at
   `learning`. Sweep repo mistake logs for exam subjects the same way.
4. Tick study-cycle progress; decide next week's ≤3 priorities.
5. Cleanup: archive/delete low-value notes and stale queue drafts (list them in the review).
6. User reviews `anki/queue.md`, flips batches to `approved`, runs
   `python3 scripts/anki_push.py`.

Durable: the weekly review note, updated cycle, pruned queue.
Exit: next week has ≤3 priorities and an empty "unreviewed" queue.
