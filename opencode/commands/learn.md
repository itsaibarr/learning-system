---
description: Start or continue a learning session in Obsidian, theory first then active recall, with tracked mastery
model: opencode/muse-spark-1.3-contributor-free
---

You are running a learning session for the learner. Topic: $ARGUMENTS

Do exactly this, yourself. Do not delegate any step to a subagent.

1. Load the skill `teach-understanding` (exact name). Also load `obsidian-markdown`.
2. Read `references/obsidian.md`, `references/example-session.md` and `references/visuals.md` in that skill's folder
   (`/Users/itsaibarr/conductor/repos/learning-system/skills/teach-understanding/`).
3. Run in the shell: `learn start $ARGUMENTS`
   If $ARGUMENTS is empty, run `learn status` and ask the learner which topic, in one line.
4. From now on, after every `learn` command, do what its `NEXT:` line says. Nothing else.
   When NEXT says research, also load `praxist-scientific-research` and follow
   `references/research.md`: no teaching before the research brief is saved.
5. Keep chat replies to 1-2 lines. All theory, questions and feedback live in the Obsidian note.
6. When the learner says stop, done, or bye: run `learn end --next-time "..."` before replying.
