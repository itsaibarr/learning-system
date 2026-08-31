# Simplification report — what was intentionally excluded and why

Final size: ~30 markdown files + 1 script (~170 lines Python). The original repo was
~3,200 lines including ~2,400 lines of TypeScript; this adaptation ports zero of it
while adding the study-planning, Obsidian, and Anki layers the original lacked.

## Dropped from the original (amosblomqvist/learn)

| Excluded | Why |
| --- | --- |
| `quiz.ts` (1,062 loc TUI) | Quizzing works in chat; the real value — the option-construction procedure, "I don't know", grade-then-explain — is text and lives in the teach skill |
| `ask-user-question.ts` (669 loc) | Plain chat questions; both host frameworks already have an ask mechanism |
| `md-log.ts` (443 loc session mirror) | Replaced by direct vault writes — less output and more durable than a transcript mirror |
| `visual-tools/` + `mermaid-maker` + `svg-maker` (render-and-inspect PNG pipeline, Chrome + mermaid-cli + rsvg deps) | Obsidian renders mermaid natively; inline blocks get ~90% of the value with zero tooling. SVG geometry reintroduction trigger recorded in `decision-log.md` |
| `researcher.md` hardcoded model (`openrouter/z-ai/glm-5.3`) | Inherits the session's configured provider instead |
| pi-only install shape (repo *is* a `.pi` dir) | Canonical `skills/` + per-framework wiring (opencode.json, `.pi/skills` symlink) |

## Considered and rejected during design

| Excluded | Why |
| --- | --- |
| `/agent` directory (learning-router.md, learning-workflows.md, skill-triggers.md) | Collapsed into one `AGENTS.md` — three files of routing indirection for one reader |
| Five separate integration docs | Two docs (setup, operating guide) cover it |
| Five workflow files | One `workflows.md`; playbooks are ≤30 lines each |
| 8-folder Obsidian structure (Inbox/Archive/Projects…) | Vault was empty; 5 folders; archive/projects folders added only when something needs them |
| Anki .apkg/CSV export path | AnkiConnect was already installed; one HTTP call beats an export format |
| Multi-line card fields | Loud single-line contract beats a silent-truncation grammar (decision log) |
| Auto-push of cards, scheduled jobs, any further automation | The human approval gate is the point; nothing else earns automation |

## Kept — and why it survived the pass

All 9 templates are exercised by the two examples; both skills are loaded by both
frameworks; every doc is referenced from README. Nothing in the repo is currently
unreferenced or unused.
