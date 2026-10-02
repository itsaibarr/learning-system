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
  The teach skill's fact-verification step needs some research capability in the
  session (a global research skill or web search) — on a fresh machine, check one exists.
  Note: the project skill is named `teach-understanding`, not `teach` — OpenCode
  dedupes by name and a global `teach` would win the collision.
- **pi** — `.pi/skills` (committed symlink) exposes the same files; `.pi/agents/`
  holds the researcher subagent definition.
  - ☐ `pi` → `/login` with your provider (required before any pi use).

## 2b. Global wiring for `/learn`: `bash scripts/install.sh`

Idempotent. It sets up:
- `~/.local/bin/learn` → `scripts/learn.py`.
- `~/.config/opencode/commands/learn.md` → `opencode/commands/learn.md` (pinned to
  `opencode/muse-spark-1.3-contributor-free`).
- Skills in `~/.config/opencode/skills/`: `teach-understanding` → this repo;
  kepano/obsidian-skills (`~/repos/obsidian-skills`): `obsidian-markdown`,
  `obsidian-bases`, `obsidian-cli`, `json-canvas`; PRAXIST (`~/repos/PRAXIST`):
  `praxist-scientific-research`.
- `pip install praxist==0.5.0 httpx` for `learn lit` (no API keys).
- The routing block `opencode/agents-block.md` appended to `~/.config/opencode/AGENTS.md`.
- Obsidian CLI: Settings > General > Advanced > Command line interface (optional; the
  engine writes files directly and uses the CLI to open notes).
- Tests: `python3 -m unittest discover scripts`.

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

Vault (`~/Documents/Obsidian Vault`) uses six folders: `Maps/`, `Concepts/`,
`Sources/`, `Reviews/`, `Templates/` (templates copied from `templates/`), and
`Sessions/` (created by `learn start`). No
community plugins required — mermaid and LaTeX render natively.
