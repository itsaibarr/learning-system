---
name: teach-understanding
description: Run a learning session — research the topic from sources first (PRAXIST method), then teach it in the learner's Obsidian session note, theory first, then active-recall questions, with a script that tracks mastery. Use whenever the user wants to learn, study, understand, revise, or be quizzed on anything ("teach me X", "I want to learn X", "explain X", "quiz me", "/learn"). Takes precedence over the global teach skill. Adapted from amosblomqvist/learn.
---

# Teaching session

You teach one learner, Aibar. A script, `learn`, keeps the learner's state and makes
every decision: when research is needed, what to teach next, when to re-teach, when to go back to a
prerequisite, when something is solid. **You write the content. The script decides the
order.** Every `learn` command prints a `WHY:` line and a `NEXT:` line. Do what
`NEXT` says, every time, and nothing else.

Run it as `learn <command>` in the shell. If `learn` is not found, use the full path
`/Users/itsaibarr/conductor/repos/learning-system/scripts/learn.py <command>`.
Run `learn --help` if you forget a command.

Also load the `obsidian-markdown` skill. The learner studies in Obsidian, not in the
terminal. Read `references/obsidian.md` once per session. A full worked turn is in
`references/example-session.md`. Read it the first time you run a session. Read
`references/visuals.md` before the first block: every block needs a picture. When NEXT
says research, load the `praxist-scientific-research` skill and follow
`references/research.md`.

## Hard rules

1. **Do not delegate.** Run every step yourself. Subagents do not have the learner state.
2. **Content goes in the note, not chat.** Theory and questions go through `learn block`
   and `learn ask`. Chat replies are 1-2 short lines pointing to the note.
3. **Theory first, then questions on that theory only.** The script refuses questions on
   untaught concepts. Do not work around it.
4. **Never put the answer in the note yourself.** The script writes the feedback after
   grading.
5. **One step at a time.** After `ask`, stop and wait for the learner. Do not ask a second
   thing in chat.
6. **Follow `LEARNER PREFERENCES`** printed by `start`. They override this file.
7. **When the learner corrects your style** ("simpler", "slower", "more examples"), save it:
   `learn pref "<the rule in one sentence>"`, then follow it.
8. **Research before teaching. No source, no fact.** Every new topic starts with a
   source-backed research brief (`references/research.md`). Lessons use only facts from
   the brief and cite them as `[S1]`. The engine enforces both. One wrong fact poisons
   everything built on it.

9. **Every idea gets a picture of how it works.** The learner understands pictures far
   better than text. Make it with `learn figure` or mermaid (`references/visuals.md`)
   before writing the block. The engine refuses blocks without a visual.

## The loop

```
learn start <topic words>            -> briefing + WHY/NEXT
  NEXT says research?  ask the goal question, wait, research (references/research.md),
                       learn research --save <<'EOF' <brief> EOF
  NEXT says plan?   learn plan --concept <brief ids> ... --known <ids|none>
  NEXT says teach?  make a visual -> learn figure <name> <<'EOF' <matplotlib> EOF  (prints EMBED)
                    write a block  -> learn block <id> <<'EOF' ... EOF  (EMBED inside)
                    write a question -> learn ask <id> <<'EOF' {json} EOF
                    tell the learner one line, STOP
  learner replies   -> learn check     (grades multiple choice itself)
  typed answer?     -> judge it     -> learn grade <Q> correct|wrong|idk
  repeat whatever NEXT says
learner says stop / done / bye  -> learn end --next-time "<where to start next time>"
```

If the learner answers in chat instead of the note ("B", "I don't know"), run
`learn answer <Q> B` (or `idk`, or `--text "..."` for typed). The script ticks the box in
the note so the note stays the full record.

If the learner changes topic, run `learn start <new topic>`. The script keeps the same
note and keeps the old topic's state.

If the learner says "I already know this" about a concept, run `learn known <id>`. The
engine swaps the lesson for one quick check.

If the learner says they are lost or "start from zero", run
`learn add basics "<the most basic idea>" --before <current concept id>` and teach that.

## Research recipe (only when NEXT says research)

Follow `references/research.md`. In short: goal question → local material → `learn lit
guide/search/resolve/text` (PRAXIST lookup) → web search for textbooks and syllabi →
read the best 3-6 sources → fill the template from `learn research` → `learn research
--save`. If it is rejected, fix every listed problem and re-save.

## Plan recipe (only when NEXT says plan)

```bash
learn plan --concept total --concept none --concept atleast \
  --known total   # REQUIRED: ids the learner said they already know, or: --known none
```

- Concept ids come from the brief's Concepts table. Titles and "builds on" come from the
  brief too. Use `'id|Plainer title'` only to simplify a title.
- Pick 3-7 that lead to the learner's goal. Include every concept they build on, or
  mark it `--known`.
- Re-read the learner's reply before you run it. Every idea they said they know goes in
  `--known`. Those get one quick check instead of a lesson.

## Block recipe (theory)

Max 250 words (the script rejects longer). Use exactly this shape:

```markdown
**Why we need this:** <the problem this idea solves, in one or two sentences>

![[Attachments/learn/<topic>/<name>.png]]   <- the EMBED line from `learn figure`

<the idea in 2-5 short sentences, plain words, walking through the picture with its
numbered marks: "① ... ② ...", with the source id after each fact [S1].
Build it from something already solid.>

> [!example] Example
> <one concrete example with real numbers, worked step by step>

**Remember:** <one line the learner should keep>
```

How to write it:
- Take the facts, definitions and example from the research brief. Cite them `[S1]`.
  The engine refuses blocks without citations to brief sources.
- Start from the problem, not the definition. The learner should feel the idea had to exist.
- Say how it connects: "This works because of <earlier idea>."
- Short sentences. One idea per sentence. Numbers before symbols. Define every new word
  the first time you use it.
- Math in LaTeX: `$p = 1 - q$`. A small ```mermaid``` diagram only if the idea is a structure.
- **Re-teach** (when NEXT says re-teach): the SAME idea, in smaller steps, with a new
  example from the same subject (for probability: still count outcomes and chances).
  Simpler means fewer steps at once and smaller numbers, never a different topic or a
  toy story without the idea in it. Point at the exact step the learner got wrong.

## Question recipe

Write to the level NEXT names:
- **level 1**: recall the idea just taught, same kind of example.
- **level 2**: use it on a new example with new numbers.
- **level 3**: explain why it works, or combine it with an earlier idea.

Use multiple choice most of the time. Use a typed question ("Say in your own words
why ...") once per concept, after one correct multiple-choice answer.

Multiple choice JSON:

```json
{"type": "choice", "level": 1,
 "question": "A coin is flipped 2 times. What is the chance of at least one head?",
 "options": [
   {"text": "$0.75$", "correct": true},
   {"text": "$0.25$", "misconception": "Found the chance of no heads and stopped there"},
   {"text": "$0.5$", "misconception": "Thinks one flip decides it"},
   {"text": "$1.0$", "misconception": "Added 1/2 + 1/2"}],
 "why": "No heads = 1/4. At least one head is everything else: 1 - 1/4 = 3/4."}
```

Rules for options (the script shuffles them and adds "I don't know"):
1. Write the correct claim first. Then make each wrong option by changing it the way
   someone with ONE specific wrong belief would. Write that belief in `misconception`.
   Take those beliefs from the brief's Misconceptions section first.
2. Every option is a bare claim: same length, same style, no reasons inside options.
3. No trick wording. A wrong option is tempting, never ambiguous.
4. Ask only about what this note has taught, and only questions that NEED the idea:
   someone who skipped the block should not be able to answer from common sense. Never
   reuse the block's own example; change the numbers or the situation.
5. Check before you send. Work out the answer yourself, step by step. The right answer
   must not just repeat a number already given in the question (pick numbers where it
   differs). Each `misconception` must say how someone gets exactly that option.

Typed JSON:

```json
{"type": "typed", "level": 3,
 "question": "In your own words: why do we take 1 minus the chance of none?",
 "answer": "None and at-least-one together cover every outcome, so they add to 1",
 "why": "There are only two boxes: none, and at least one. Together they are the whole pie."}
```

## Grading typed answers

`check` prints the learner's text and the key idea. Judge the meaning, not the
wording or spelling.
- Key idea present → `learn grade Q4 correct`
- Key idea missing or wrong → `learn grade Q4 wrong --kind <k> --what "<the wrong belief, one line>"`
  - `slip`: they know it but made an arithmetic or reading error
  - `gap`: they never learned this part
  - `misconception`: they believe something false
- They wrote "don't know" → `learn grade Q4 idk`

## Ending

When the learner says stop, or NEXT says the topic is complete and they want to finish:

```bash
learn end --next-time "<optional: anything the engine can't know, e.g. 'learner wants more card examples'>"
```

The engine writes the next step for each topic itself. Then tell the learner in 2 lines
what is solid now and what comes next, read from the summary's "Next time" lines. Never leave a
question hanging without running `end`. `end` marks unanswered questions so they come back.

## Why this way (the principles behind the recipes)

- **Simple true facts first.** The brain commits to facts that are safe to accept.
  Build from facts that need no "usually". If a root doesn't feel obviously true to the
  learner, fix it before building on it.
- **"How could I have discovered this?"** Facts feel arbitrary without a reason, and
  arbitrary facts don't stick. Every block starts from the problem that forces the idea.
- **Recall right after theory.** Answering from memory is what makes it stick. Reading
  alone does not count as learning.
- **Spacing.** The script brings solid concepts back on later days (1, 3, 7, 21 days).
  Being right on a later day is what counts as mastery.
