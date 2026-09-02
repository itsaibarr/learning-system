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
| 2026-09-02 | Plain mode added: on machines without the Obsidian vault, vault notes land in `subjects/<subject>/` in this repo | The iMac has no Obsidian; the alternative was losing durable notes entirely on that machine | the vault is available everywhere |
| 2026-09-02 | In plain mode math is written in Unicode (`sₓ`, `‖·‖²`, `−`, `Σ`) with display math in fenced code blocks; `$...$` is banned outside `anki/queue.md` | Plain markdown viewers render `$...$` as literal dollar signs; Anki keeps LaTeX because the push script converts it | a plain-mode viewer with LaTeX rendering becomes the norm |
| 2026-09-02 | Teaching runs theory-first: continuous exposition per block, quiz batch at the end — not the skill's per-node interleaved quiz-check | Learner reported the interleaved rhythm read as being tested rather than taught, and that content arriving as quiz post-mortems did not feel like instruction | the learner asks for Socratic teaching |

