# Teaching quality plan (2026-10-08)

Status: approved 2026-10-08 (build all 6), built 2026-10-08. Evidence: audit in chat (real state + session notes) and
`docs/research/teaching-quality/{learning-science,multimedia,assessment,exam-mode}.md`.

## Audit numbers that drive the plan

- Networking chapter: 29 concepts, 101 questions in one note, 27k words. ~3.9 questions per concept.
- Success rate 90-98% (10-05: 60 correct, 0 wrong). Research target is 70-85%.
- 148 real MCQs: correct option uniquely longest 47% of the time (chance 25%).
- Longest video 6.4 min. Caption boundaries synced within 0.4 s; drift is inside 12-27 s beats.
- Exam behaviour lives in global preferences and leaks into every topic.

## Changes, by impact

### 1. Units: teach schemas, question to decide (problem A)

- Root cause: brief recipe says "each a single teachable idea"; engine asks after every block;
  "solid" needs 2-in-a-row incl. level 2, per concept.
- Solution: a **unit** = 2-4 concepts that form one schema (~15-20 min, learner choice).
  - Brief Concepts table gets a `Unit` column; `learn plan --unit` groups concepts (existing briefs:
    one unit per concept, nothing breaks).
  - `learn block <unit>` teaches the whole unit as 2-4 **segments** (one sub-idea each).
  - After the block: one **unit check** of 3-5 questions across its concepts (one per concept,
    at least one transfer/scenario item). No questions after each segment.
  - Mastery: a concept is solid after ONE correct unseen application (level 2+) answer, or 2 correct
    otherwise; a misconception needs a correct answer on a differently-worded item later.
    Durable = correct in 3 later sessions on separate days (keep 1/3/7/21 boxes).
  - Difficulty band over the last 10 graded answers: >90% raise level / skip guided practice;
    70-90% hold; <70% smaller step, worked example, reteach.
  - Sessions open with a short review of due items (max ~5 questions).
- Component: `learn.py` (plan, block, ask, record, choose_fresh), research.md, SKILL.md.
- Avoids new problems: big units are bounded (2-4 concepts, 2-4 segments, 3-5 questions);
  per-concept tracking is kept, so a miss reteaches only that concept's segment.
- Validate: networking brief re-planned => ~7-9 units; a full unit session takes ~15-20 min of
  learner time with <=5 questions; tests for the new rules.

### 2. Questions that need understanding (problem D)

- Root cause: engine accepts any MCQ; no cue checks; recognition counts toward mastery.
- Solution (engine-enforced, from Haladyna 2002, NBME, Rodriguez 2005, Gierl 2017):
  - **3 options** (1 key + 2 distractors) + "I don't know". Each distractor carries a misconception,
    preferably one from the brief.
  - Reject: key length > 1.25x mean distractor length; key uniquely sharing stem words;
    absolute words only in distractors; all/none of the above; negative stems; duplicate options.
  - Stems must be closed questions (end with "?"); level 2+ stems must use a new scenario
    (not the block's example; checked by word overlap with the block).
  - New item types: **two-tier** (answer + reason, both must be right; optional confidence),
    **typed** with a 2-4 key-point rubric (existing typed type gets a `rubric` field).
  - Each unit check must include at least one typed or two-tier item.
- Component: `learn.py` cmd_ask/check/grade; SKILL.md question recipe.
- Validate: run the checks over the 148 real MCQs (expect most of the longest-key items rejected);
  tests per rule; a live free-model unit check.

### 3. Short synced scenes inside a big unit (problem C)

- Root cause: one video per block grew to 6.4 min (limits raised to 660 s / 1700 words);
  animations inside a step run on guessed durations.
- Solution:
  - **Audio-first sync**: `learn figure` speaks NARRATION first, measures each line, then renders.
    Scenes wrap events in `with self.voice(i):` (prototype verified); the harness starts line i
    there and pads the visuals to the line's real length. Old caption-based sync stays as fallback.
  - One narration line = one visual event (max ~35 words, ~8-15 s); 2 s hold at the end.
  - Scene cap 3 min (hard), target 60-120 s. A unit uses 2-4 scenes, one per segment.
  - Revert the 660 s / 1700-word / 1500 s raises; keep the cross-topic `record` bug fix.
- Component: `learn.py` MANIM_HARNESS, cmd_figure, narrate/compose; visuals.md templates.
- Validate: a 4-segment unit; measure speech-onset vs voice-mark offset (<0.3 s) on every line.

### 4. Structured notes (problem B)

- Root cause: block recipe asks for one prose paragraph with citations after every sentence;
  notes repeat the narration.
- Solution: per segment, a fixed shape (Mayer pre-training, signaling, coherence):
  big idea (1 line) -> key terms (term: 1-line meaning) -> video -> one structured element chosen by
  knowledge type (numbered steps / comparison table / formula + variable table / cause->effect) ->
  worked example (labelled substeps, if quantitative). One Sources block per unit, not per sentence.
  - Engine checks: each segment has a heading, a figure, and a list or table; no prose paragraph
    over ~60 words; citations allowed per segment, not required per sentence.
- Component: `cmd_block`, SKILL.md block recipe, example-session.md.
- Validate: render a unit note; check structure rules; compare with the cloud block above.

### 5. Exam mode as a reusable profile (problem E)

- Root cause: no mode; exam rules are global prefs; brief has no assessment fields.
- Solution:
  - `learn start <topic> --exam <profile>`; profiles in `skills/teach-understanding/exams/`
    (`cambridge-as-a-level.md`, `pearson-edexcel-ial.md`): paper codes, citation format, command
    words (quoted), mark-scheme abbreviations, approved sources + URL patterns, known pitfalls
    (PapaCambridge returns HTML for missing PDFs; GCE Guide is unsafe).
  - Exam brief adds required sections: Syllabus points (codes), Paper patterns (each with >=2
    cited real questions), Mark-scheme points, Examiner-report errors; source types `syllabus`,
    `past-paper`, `mark-scheme`, `examiner-report`.
  - Exam questions carry `source`: an authentic citation ("9702/22/M/J/23 Q3(b)", verbatim, marks)
    or `pattern: P#` from the brief. Typed answers graded by mark points (partial marks recorded).
  - Adaptive split: short teaching per unit, then practice; practice share rises as concepts
    become solid, falls back to teaching on a misconception.
  - Preferences get a topic scope (`learn pref --topic`); the existing 9702 prefs move to that topic.
- Component: `learn.py` (start, research parser, ask, grade, prefs), research.md, new exams/ folder.
- Validate: a 9702 unit using real PapaCambridge questions with mark-scheme grading; a concept-mode
  topic unaffected by exam prefs.

### 6. The teaching skill

Rewrite `teach-understanding` around the decision rules above (unit planning, step pattern,
when to explain vs test, question construction, distractors, difficulty band, move on / revisit,
feedback). `references/` gets a `questions.md` (item writing) and `exams/` profiles; the research
files are cited, not copied.

## Out of scope

No new framework, no change to Voicebox/Kokoro, no change to the research gate or Obsidian layout.

## Validation summary

1. Unit tests for every rule (existing 71 kept passing).
2. Retro-check of the 148 real MCQs and the 29-concept networking brief.
3. Scripted engine session: one substantial unit (4 concepts, 3 scenes, unit check) end to end.
4. Sync measurement on multi-scene unit (<0.3 s per line).
5. Exam-mode session on 9702 with authentic questions.
6. One live OpenCode run on the free model.
