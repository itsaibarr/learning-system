#!/usr/bin/env bash
# Wire learning-system into this machine for OpenCode. Idempotent: safe to re-run.
set -euo pipefail
REPO="$(cd "$(dirname "$0")/.." && pwd)"
OC="$HOME/.config/opencode"

link() {  # link <target> <link-path>; moves a different existing file aside first
  mkdir -p "$(dirname "$2")"
  if [ -L "$2" ] && [ "$(readlink "$2")" = "$1" ]; then return; fi
  if [ -e "$2" ] || [ -L "$2" ]; then mv "$2" "$2.bak.$(date +%Y%m%d%H%M%S)"; fi
  ln -s "$1" "$2" && echo "linked $2"
}
clone() {  # clone <url> <dir>, or fast-forward if present
  if [ -d "$2/.git" ]; then git -C "$2" pull -q --ff-only; else git clone -q "$1" "$2"; fi
}

chmod +x "$REPO/scripts/learn.py"
link "$REPO/scripts/learn.py" "$HOME/.local/bin/learn"
link "$REPO/skills/teach-understanding" "$OC/skills/teach-understanding"
link "$REPO/opencode/commands/learn.md" "$OC/commands/learn.md"

clone https://github.com/kepano/obsidian-skills "$HOME/repos/obsidian-skills"
for s in obsidian-markdown obsidian-bases obsidian-cli json-canvas; do
  link "$HOME/repos/obsidian-skills/skills/$s" "$OC/skills/$s"
done

# Research framework: PRAXIST (sapientinc, Fair Source License 1.0): skill + no-key literature lookup.
clone https://github.com/sapientinc/PRAXIST "$HOME/repos/PRAXIST"
link "$HOME/repos/PRAXIST/skills/praxist-scientific-research" "$OC/skills/praxist-scientific-research"
python3 -m pip install -q "praxist==0.5.0" "httpx>=0.27"

grep -q "<!-- learning-system -->" "$OC/AGENTS.md" 2>/dev/null || cat "$REPO/opencode/agents-block.md" >> "$OC/AGENTS.md"

python3 -m unittest discover -s "$REPO/scripts" -q
command -v learn >/dev/null || echo "warning: ~/.local/bin is not on PATH; the agent will use the full script path"
echo "learning-system ready. In OpenCode: /learn <topic>"
