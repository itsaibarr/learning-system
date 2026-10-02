# Redesign plan: learning-system v2 (2026-10-03)

Status: built and validated 2026-10-03 (see final report in chat). Source of truth: the Phase 1 audit (chat, 2026-10-03) and the
learner's Phase 2 answers below.

## 1. Requirements

Learner's answers, verbatim intent:

1. Entry is OpenCode.
2. Code is acceptable.
3. Theory first, then quiz for active recall. Questions only on what was just taught.
   The four corrections from the 2026-09-11 session are the spec for teaching style:
   theory before questions, very easy language, everything happens in Obsidian,
   start from zero when lost.
4. Obsidian is the study surface. Route to kepano/obsidian-skills. The agent must know
   Obsidian is an app with interactive features, not a folder of markdown.
5. One note per learning session, so the learner never switches files mid-session.
6. FAIO is over. The redesign gets tested on a new subject.

Engineering requirements derived from them:

| Area | Requirement |
| --- | --- |
| Entry | `/learn <topic>` works in OpenCode from any directory. Plain "teach me X" also routes there. |
| Obsidian | obsidian-markdown, obsidian-cli, obsidian-bases installed globally and loaded by every learning session. A short capability map says which feature to use for what. |
| Teaching | Per block: theory in very simple words, then 1 or 2 questions on that block only, then grading with the why. No cold probing. |
| Recall | Mix multiple choice (with "I don't know") and short typed answers ("say it in your own words"). |
| Session note | One vault note per session holds theory, questions, your answers, feedback, and the closing summary. |
| Learner model | Persistent file with your preferences and per-concept mastery, review dates and mistake history. Read at start, written after every answer. |
| Adaptation | Explicit code rules for mastery, difficulty level, review scheduling and revisiting prerequisites. Each decision prints a one-line reason that also goes into the note. |
| Lifecycle | `start` shows where you are and what comes next. `end` writes a summary into the note, updates the dashboard and commits state. |
| Testing | Unit tests for the rules, scenario tests for the seven Phase 4 learner cases, one live OpenCode session. |

## 2. Ambiguities (defaults chosen; override at the approval gate)

- **"Native ask-question features."** Obsidian 1.12.7 has no question widget. The
  CLI docs list no prompt command. The interactive pieces are task checkboxes (CLI
  `tasks`/`task` read and set them, with line numbers and custom status characters),
  typed properties, Bases tables, foldable callouts, and `eval` (which can show a
  Notice). Default: answer by ticking a checkbox or typing under "Your answer", then
  send any message in OpenCode. Typing the letter in chat also works.
- **Obsidian CLI is off** (Settings > General > Advanced > Command line interface).
  Default: the system reads and writes vault files directly, so it works with the CLI
  off. When the CLI is on, the agent also uses it to open the session note in front of
  you and to read checkbox state.
- **Model.** The OpenCode orchestrator runs free models (`opencode/mimo-v2.5-free`;
  the 2026-09-11 session ran on muse-spark free). Teaching quality depends on this.
  Default: leave it as is. Option: pin `/learn` to a stronger model in its frontmatter.
- **Anki** stays as an optional extra. The review schedule in the learner model
  replaces it as the thing that brings old material back.
- **Concept notes.** The session note replaces per-concept notes during learning. The
  learning map stays one note per subject.

## 3. Gap analysis

| Area | Current | Desired | Change |
| --- | --- | --- | --- |
| Entry | Only if you name the repo; 3 of 4 study sessions bypassed it | `/learn` from anywhere | Global command + skill symlinks + routing line in global AGENTS.md |
| Teaching order | Probe first (quiz before teaching) | Theory, then recall on that block | Rewrite the process section of `teach-understanding` |
| Language | Not specified | Very simple words by default | Stored preference, applied every session |
| Study surface | Chat plus scattered vault notes | One session note in Obsidian | `Sessions/` folder + session-note template |
| Obsidian knowledge | None; treated as markdown | Capability map + kepano skills | Install skills, add capability section |
| Mastery | Free-text map row, one correct answer = floor | Rule-based statuses with evidence | `scripts/learn.py` + `state/learner.json` |
| Review | Anki, never used | Due items come back at session start | Leitner intervals in `learn.py` |
| Mistakes | Logged, never closed | Closed by a later correct answer on another day | Same rule in code |
| Repeated failure | Model judgment | 2 misses in a session leads to revisiting a prerequisite | Rule in code |
| Session end | Undefined, never happened | Summary, dashboard, commit | `learn.py end` |
| Preferences | Lost after the session | Persisted profile | `profile` block in learner file |
| Contradictions | Checkbox decision vs chat quiz | One answer channel | Decision-log row superseding 2026-09-08 |

## 4. Design

```
YOU: /learn <topic>  (OpenCode, any directory)
  -> command loads skills: teach-understanding, obsidian-markdown, obsidian-cli
  -> python3 learn.py start <topic>
       prints: preferences, due reviews, concept states, open mistakes,
               last session's "next time" line; creates today's session note
  -> agent asks the goal only if the topic is new; shows a <=7 node map in the note
  LOOP per block:
     theory block (simple words, why it exists, one example)   -> session note
     1-2 questions on that block (checkbox options or typed)    -> session note
     you answer (tick / type in Obsidian, or reply in chat)
     agent grades: right/wrong + why                            -> feedback callout
     python3 learn.py record <topic> <concept> correct|wrong|idk [--kind]
       -> rule decision + reason ("2 in a row: solid", "2 misses: revisit X")
     python3 learn.py next <topic> -> what to teach next and why
  -> "stop" or block plan done: python3 learn.py end --next "<one line>"
       writes summary callout, re-renders dashboard, commits state
NEXT SESSION: start reads the same file, so due reviews come first
```

Components:

| Component | Status | Responsibility |
| --- | --- | --- |
| `~/.config/opencode/commands/learn.md` | new | Entry; names the repo path, the skills to load, the session loop |
| `~/.config/opencode/skills/{teach-understanding,obsidian-*}` | new symlinks | Global discovery of repo skill and kepano skills (clone at `~/.config/opencode/vendor/obsidian-skills`) |
| `~/.config/opencode/AGENTS.md` | edit, 3 lines | Route "teach me / I want to learn / quiz me" to `/learn` |
| `skills/teach-understanding/SKILL.md` | edit | Keep principles i/ii, quiz construction, accuracy. Replace probe-plan-teach with the block loop above. Add learner preferences and the Obsidian capability map |
| `scripts/learn.py` | new, stdlib only | start, add, record, next, answers, end, status. All rules below |
| `scripts/test_learn.py` | new | Unit + scenario tests |
| `state/learner.json` | new | Single source of truth: profile, topics, concepts, history, session log |
| `templates/session-note.md` | new | Shape of the one note per session |
| vault `Sessions/` + `Sessions/Sessions.base` | new | Session notes; a Base listing them with topic, date, score |
| vault `Maps/Learner dashboard.md` | generated | Read-only view of what the system believes you know and what's next |
| `AGENTS.md`, `workflows.md`, `docs/operating-guide.md` | edit | Point to the new loop, six vault folders, retire the "five folders" and probe-first wording |
| `decision-log.md` | append | Rows for: code allowed, theory-first, session note, answer channel |
| `faio-2026/` | archive | Brief status `done`; commit the pending mistake-log row |
| `templates/concept-card.md`, study-cycle, brief, Anki | keep | Unchanged; still used by exam/book playbooks |

Rules in `learn.py` (explicit, testable):

- Status ladder: `new -> learning -> solid -> mastered`.
- Correct: streak +1. Two in a row makes it `solid` (review in 1 day). A correct
  review on a later day than it became solid moves it up a box: intervals 1, 3, 7, 21
  days; box 2 or higher is `mastered`.
- Wrong: streak 0, status `learning`, review tomorrow, difficulty level -1. Kind
  (slip, gap, misconception) is recorded; misconceptions open a mistake entry.
- "I don't know": recorded as a gap; decision is "teach the block again, simpler",
  never "ask again".
- Two misses on one concept in the same session: if a prerequisite is not solid,
  the decision is "revisit <prereq>"; otherwise "re-teach with a new example".
- Difficulty: each concept has level 1-3; two correct in a row at a level raises it.
- Mistake entries close only on a correct answer on a later day.
- `next` order: due reviews, then the weakest prerequisite of a struggling concept,
  then the first new concept whose prerequisites are solid, then "topic complete".
- Every decision returns a reason string; the agent copies it into the note
  ("Why this next: ...").

Error handling: `learn.py` validates topic and concept ids and fails loudly; a
missing vault folder is created; `end` without `start` errors; the git commit is
skipped with a warning if nothing changed. The agent falls back to file IO when the
Obsidian CLI is off.

## 5. Tasks

1. Install kepano/obsidian-skills globally (clone + three symlinks); verify OpenCode
   lists them. Acceptance: `opencode debug skill` (or the skill list) shows
   obsidian-markdown, obsidian-cli, obsidian-bases, teach-understanding.
2. `scripts/learn.py` + `state/learner.json` with the rules, TDD. Acceptance: unit
   tests for every rule pass.
3. Session note template + vault `Sessions/` + `Sessions.base` + dashboard render.
   Acceptance: `start` creates a note that renders in Obsidian; `end` writes the
   summary and dashboard.
4. Rewrite the teach-understanding process section + preferences + Obsidian
   capability map. Acceptance: no probe-first wording remains; preferences seeded
   from the 2026-09-11 corrections.
5. `/learn` command + global AGENTS.md routing line. Acceptance: `/learn` in a
   session started from `~` loads the skills and runs `start`.
6. Docs, decision log, FAIO archive. Acceptance: no doc contradicts the new loop.
7. Phase 4 validation (below), fix what it finds.

## 6. Validation

Scenario tests in `test_learn.py` (deterministic, rules level):
new learner; learner who already knows A and B; wrong answer with misconception;
repeated failure leading to prerequisite revisit; mastery across two days; topic
change keeping the old topic's state; returning learner whose due reviews come first.

Live check: one real `/learn` session in OpenCode on a fresh subject, with me playing
the learner (one right answer, one wrong, one "I don't know", a topic switch, end,
then a second session). Judged on: theory before every question, questions only on
taught material, simple language, everything readable in one note, decisions with
reasons, state correct after restart.
