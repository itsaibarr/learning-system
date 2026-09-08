# Decision Log: learning-system

Append-only. One row per decision that a future session must not re-litigate.

| Date | Decision | Why | Revisit when |
| --- | --- | --- | --- |
| 2026-08-31 | Adapt amosblomqvist/learn as portable markdown; port none of its 4 pi-TUI TypeScript extensions | The pedagogy is markdown; the TUI is pi-only and chat covers quizzing | never |
| 2026-08-31 | Diagrams are inline mermaid only; the SVG/PNG maker pipeline (svg-maker, mermaid-maker, visual-tools) was removed | Obsidian renders mermaid natively; pipeline needed Chrome + rsvg + subagents for rare geometric figures | geometric figures become a recurring need |
| 2026-08-31 | Project teach skill named `teach-understanding`, not `teach` | OpenCode dedupes skills by name and the global (Pocock) `teach` wins the collision; both must coexist | OpenCode gives project skills precedence |
| 2026-08-31 | cmux is the terminal; tmux exists solely as the pi-interactive-subagents substrate | User decision at the audit gate | dropping the pi subagents stack |
| 2026-08-31 | Anki cards enter decks only via anki/queue.md + human approval + scripts/anki_push.py | Prevents unverified AI card floods; user rule | never |
| 2026-08-31 | Queue card fields are single-line; the push script errors on continuation lines rather than supporting wrapping | Silent truncation was the alternative; loud failure beats a multi-line grammar | a real need for long-form card backs |
| 2026-09-08 | Quiz questions are authored as notes in the Obsidian vault, not asked in chat; answers are captured by clicking task checkboxes | A checkbox click in Reading View / Live Preview writes `[x]` into the .md file, so it is the only core-Obsidian interaction whose state the agent can read back. Quiz plugins render widgets whose state stays in memory | a plugin is installed that persists answers to the file |
| 2026-09-08 | Probe and quiz notes live in vault `Reviews/`; no sixth folder is created | They are diagnostics, the closest existing class to a review; the five-folder rule in AGENTS.md stays intact | quiz notes outgrow Reviews/ and need their own folder |
| 2026-09-08 | Answer keys are never written into a question note before it is answered | The note is plain markdown the learner can open in edit mode; a foldable callout hides an answer visually but not from the source. Grading is written in the following round | never |
