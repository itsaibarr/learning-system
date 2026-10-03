# Obsidian: what it is and what to use

Obsidian is an app with a live renderer, not a folder of plain text. The learner reads
in Live Preview or Reading view. Everything below renders natively, with no plugins.
For full syntax, load the `obsidian-markdown` skill (and `obsidian-bases` or
`obsidian-cli` when you need them).

Vault: `~/Documents/Obsidian Vault`. CLI: `obsidian` (needs the app running). `learn`
writes the files directly and uses the CLI only to open the note and show a pop-up.

## Use this for that

| In a session you want to | Use | Syntax |
| --- | --- | --- |
| Show a worked example | example callout | `> [!example] Example` + `> lines` |
| Warn about a common trap | warning callout | `> [!warning] Trap` |
| Give an optional hint the learner opens on click | folded callout | `> [!tip]- Hint` (the `-` folds it) |
| Highlight the one line to keep | highlight or bold | `==text==` or `**Remember:**` |
| Math | LaTeX | `$x^2$` inline, `$$...$$` display |
| Show structure (steps, dependencies, a flow) | mermaid | a ```mermaid``` block, ≤7 nodes |
| Link to an older idea | wikilink | `[[Sessions/2026-10-03 Topic#2. Idea]]` |
| Pull an old explanation into this note | embed | `![[Note#Heading]]` |
| Show how something works | Manim video or still | `![[Attachments/learn/<topic>/<name>.mp4]]` from `learn figure` (plays inline) |
| Let the learner answer | checkboxes / typed line | written by `learn ask`, never by hand |

## Written by `learn`, do not hand-edit

- The session note's properties (`type`, `topic`, `date`, `status`, `correct`, `wrong`, `idk`).
  They feed `Sessions/Sessions.base`, a table of all sessions.
- Question sections (`### Q3 · level 2` ... `%% Q3 end %%`). `%% ... %%` is an Obsidian
  comment, hidden in Reading view. The script uses it to find answers.
- `Maps/Learner dashboard.md`, rebuilt after every session.

## Limits to know

- A folded callout hides text on screen but not in the file. That is why answer keys
  never go into the note before grading.
- There is no built-in quiz widget. Checkboxes are the native click-to-answer element:
  a click writes `[x]` into the file, and that is how `learn check` reads it.
- Typed answers need Live Preview (editing). Reading view is read-only.

## CLI (when useful)

```bash
obsidian open path="Sessions/<note>.md"        # bring the note to the front
obsidian tasks path="Sessions/<note>.md" format=json   # checkbox state with line numbers
obsidian search query="<text>" limit=10        # find an older note
obsidian eval code='new Notice("Q2 is ready")' # small pop-up in the app
```
