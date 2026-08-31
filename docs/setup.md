# Setup

One-time wiring. On the original machine everything below is done except the items
marked ☐.

## 1. Clone

```bash
git clone <private-remote> learning-system && cd learning-system
```

## 2. Agent frameworks

Both frameworks load the same canonical `skills/` directory:

- **OpenCode** — `opencode.json` (committed) points `skills.paths` at `skills/`.
  Verify: `opencode debug skill | grep teach-understanding` → must resolve to this repo.
  Note: the project skill is named `teach-understanding`, not `teach` — OpenCode
  dedupes by name and a global `teach` would win the collision.
- **pi** — `.pi/skills` (committed symlink) exposes the same files; `.pi/agents/`
  holds the researcher subagent definition.
  - ☐ `pi` → `/login` with your provider (required before any pi use).

## 3. Terminal + subagents

- **cmux** is the terminal app (`brew install --cask cmux`) — tabs host sessions.
- **tmux** exists only as the pi-interactive-subagents substrate: `brew install tmux`.
- Extension: `pi install https://github.com/amosblomqvist/pi-interactive-subagents`.
- To use subagents, launch pi inside tmux: `tmux new -A -s pi 'pi'`.
- ☐ Smoke test (after /login): ask pi to spawn `researcher` on a trivial factual
  question; expect a sourced brief. Until then the system runs subagent-less —
  teaching works, you lose independent fact verification.

## 4. Anki

- Install Anki + the AnkiConnect addon (code `2055492159`), keep Anki running
  during pushes.
- Verify: `curl -s 127.0.0.1:8765 -X POST -d '{"action":"version","version":6}'`
  → `{"result": 6, ...}`.
- Cards flow: agent drafts into `anki/queue.md` → you flip a batch's `status: draft`
  to `approved` → `python3 scripts/anki_push.py` (`--dry-run` to preview).
- Tests: `python3 -m unittest discover scripts`.

## 5. Obsidian

Vault (`~/Documents/Obsidian Vault`) needs five folders: `Maps/`, `Concepts/`,
`Sources/`, `Reviews/`, `Templates/` (templates copied from `templates/`). No
community plugins required — mermaid and LaTeX render natively.
