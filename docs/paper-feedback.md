# Paper teaching: feedback log

One place to record what worked and what did not when teaching a real paper, so each round of feedback becomes a rule or a test
instead of staying in a chat. Newest first. Each entry says what happened, which paper, and what it turns into.

## How to add an entry

Write three lines and hand them to the agent ("log this in docs/paper-feedback.md and fix it"):

```
YYYY-MM-DD | <paper title or link> | <part: fetch, brief, plan, scene, quiz, report, style>
Saw: <what you saw, with the video or note name>
Want: <what should have happened>
```

The agent turns it into one of: an engine check (code plus a test), a rule in `references/hyperframes.md` or `references/papers.md`,
a template change, or a decision-log row. Anything that is only a taste ("bigger captions") goes into the house style section of
`references/visuals.md`.

## Where to look when something is off

| Symptom | Look at |
| --- | --- |
| A video has overlapping or cut-off labels | the `PREVIEW:` sheet `learn figure` prints (`~/.local/share/learning-system/previews/`) |
| The engine rejects a scene | the exact failure it prints; the rules are in `references/hyperframes.md` |
| The paper was read only in part | the `FIDELITY` line of `learn paper`, and the brief's `Access` section |
| A claim or author role looks invented | the brief's Claims and Authors tables: every row needs a source id |
| The report is thin | `learn report` prints the ten-part template; the engine checks structure, not quality |
| The look differs between Manim and HyperFrames | `visuals.md`, "House style", and `MANIM_HARNESS` in `learn.py` |

## Known gaps at the first release (2026-10-15)

1. Layout defects between text and shapes are caught only by looking at the preview sheet.
2. The rules "at most 4 text items on screen" and "one caption per beat" are guidance, not checks.
3. The free OpenCode model (muse 1.3) wrote a valid scene once, with a plainer picture than a hand-built one. A full unattended paper
   session with it has not been run.
4. Only an arXiv paper was taught end to end. A history article was ingested (read as `partial`) but not taught.
5. Maps are not drawn yet. A history paper that needs one gets a schematic made from the paper's own description.
6. Axes and number lines in Manim keep Manim's pure white; text and shapes use the house palette.

## Log

(empty)
