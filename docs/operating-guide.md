# Operating guide

## The contract

Three stores, no duplication: **Obsidian** holds what you know (maps, concepts,
sources, reviews). **Anki** holds what you must not forget (cards, human-gated).
**This repo** holds how you're learning it (briefs, cycles, mistake logs, decisions,
the queue). A session is scratch space — only template-shaped conclusions survive it.

## A session, end to end

1. In OpenCode, from any folder: `/learn <topic>` (or just "teach me <topic>").
   `learn start` creates today's note in vault `Sessions/` and opens it in Obsidian.
   A new topic first gets researched: the agent asks your goal, searches literature
   (PRAXIST lookup via `learn lit`) and the web, reads the best sources, and saves a
   brief to vault `Sources/<topic> research brief.md`. The engine won't let it plan or
   teach before the brief passes validation (3+ sources, at least one textbook, primary
   or review, definitions, misconceptions, examples). Every lesson cites the brief.
2. You study in Obsidian, one **unit** at a time: 2-5 linked ideas (about 15-20 minutes)
   taught together. Each unit block has a big idea, key terms, then 2-4 segments; each segment
   is a short narrated Manim scene (60-120 s, voice and picture in sync, `learn voice`) with
   numbered steps or a table under it, and a worked example where there are numbers. A folded
   transcript sits under each video. `Maps/<topic> map.canvas` colours each concept by progress.
   After the block comes ONE unit check: one question per idea, at least one asking for the
   reason (two-tier, "B2") or a typed explanation. Tick a box or type under **Your answer**,
   then send any message in OpenCode.
3. `learn check` grades multiple choice and two-tier itself. The agent grades typed answers
   point by point (`--marks 2/3`). The feedback, with the reason for the next step, appears
   under your answer. Missed questions come back reworded; a wrong reason gets a short
   contrast re-teach.
   **Exam mode** (`learn start <topic> --exam cambridge-as-a-level`): the brief adds syllabus
   points, paper patterns and examiner-report errors from official papers; practice uses real
   past-paper questions (cited) marked on the mark scheme. Practice share grows as units become
   solid.
4. Say "stop". `learn end` writes a summary into the note, rebuilds
   `Maps/Learner dashboard.md`, and commits `state/learner.json`.

## Multi-session continuity

`state/learner.json` is the memory: your preferences, every concept's status, review
dates and mistakes. `learn start` prints all of it, so any model starts from the same
picture. The rules (one correct answer to a new scenario, or 2 in a row = solid; a correct answer on
a later day moves a concept up a review box of 1/3/7/21 days; a wrong reason = contrast
re-teach; 2 misses send you back to a weak prerequisite; "I don't know" means re-teach;
questions aim to keep you at 70-90% correct) live in `scripts/learn.py` and are tested
in `scripts/test_learn.py`.

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
  never creates a note outside the six folders.
