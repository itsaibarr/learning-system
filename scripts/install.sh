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
# Claude Code sessions (T3 Code, the terminal) get the same teaching skill, so "teach me this paper" works there too.
[ -d "$HOME/.claude" ] && link "$REPO/skills/teach-understanding" "$HOME/.claude/skills/teach-understanding"
link "$REPO/opencode/commands/learn.md" "$OC/commands/learn.md"

clone https://github.com/kepano/obsidian-skills "$HOME/repos/obsidian-skills"
for s in obsidian-markdown obsidian-bases obsidian-cli json-canvas; do
  link "$HOME/repos/obsidian-skills/skills/$s" "$OC/skills/$s"
done

# Research framework: PRAXIST (sapientinc, Fair Source License 1.0): skill + no-key literature lookup.
clone https://github.com/sapientinc/PRAXIST "$HOME/repos/PRAXIST"
link "$HOME/repos/PRAXIST/skills/praxist-scientific-research" "$OC/skills/praxist-scientific-research"
python3 -m pip install -q "praxist==0.5.0" "httpx>=0.27"

# Visuals: Manim Community in its own venv + TinyTeX for LaTeX (MathTex). No admin rights needed.
MANIM_VENV="$HOME/.local/share/learning-system/manim-venv"
TEX_BIN="$HOME/Library/TinyTeX/bin/universal-darwin"
command -v pkg-config >/dev/null || brew install -q pkgconf          # pycairo builds from source on macOS
[ -x "$MANIM_VENV/bin/manim" ] || { python3 -m venv "$MANIM_VENV" && "$MANIM_VENV/bin/pip" install -q "manim==0.21.0"; }
[ -x "$TEX_BIN/latex" ] || curl -sL "https://yihui.org/tinytex/install-bin-unix.sh" | sh || true   # PATH step may ask for sudo; not needed
"$TEX_BIN/tlmgr" install amsmath babel-english cbfonts-fd cm-super count1to ctex doublestroke dvisvgm everysel \
  fontspec frcursive fundus-calligra gnu-freefont jknapltx latex-bin mathastext microtype multitoc physics preview \
  prelim2e ragged2e relsize rsfs setspace standalone tipa wasy wasysym xcolor xetex xkeyval psnfss helvetic >/dev/null \
  || echo "warning: tlmgr could not install the LaTeX packages (it may need: tlmgr update --self). Already-installed ones keep working."
SMOKE="$(mktemp -d)"
printf 'from manim import *\nclass S(Scene):\n    def construct(self):\n        self.add(MathTex(r"f = \\frac{1}{T}"))\n' > "$SMOKE/s.py"
PATH="$TEX_BIN:$PATH" "$MANIM_VENV/bin/manim" -ql -s --disable_caching --media_dir "$SMOKE/m" "$SMOKE/s.py" S >/dev/null 2>&1 \
  && echo "manim + LaTeX: ok" || echo "warning: manim + LaTeX smoke render failed (run it by hand: $SMOKE/s.py)"

# Visuals for everything that is not maths: HyperFrames (HeyGen, Apache-2.0), run through npx at the version pinned in
# learn.py (HF_VERSION). Needs Node 22+ and ffmpeg; the first run downloads its own headless Chromium.
HF_VERSION="$(sed -n 's/^HF_VERSION = "\(.*\)"/\1/p' "$(dirname "$0")/learn.py")"
if command -v node >/dev/null && [ "$(node -p 'process.versions.node.split(".")[0]')" -ge 22 ] && command -v ffmpeg >/dev/null; then
  npx --yes "hyperframes@$HF_VERSION" --version >/dev/null 2>&1 && echo "hyperframes $HF_VERSION: ok" \
    || echo "warning: hyperframes $HF_VERSION did not start (try: npx hyperframes@$HF_VERSION doctor)"
else
  echo "warning: HyperFrames needs Node 22+ and ffmpeg (brew install node ffmpeg); non-maths visuals will not render"
fi

# Narration: Voicebox (jamiepine/voicebox, MIT) server pinned to v0.5.0, Kokoro-82M engine only (slim deps),
# Python 3.12 venv via uv (Voicebox pins numba<0.61). Kokoro weights (~313 MB) go to the Hugging Face cache.
VOICEBOX="$HOME/.local/share/learning-system/voicebox"
command -v uv >/dev/null || curl -LsSf https://astral.sh/uv/install.sh | sh
[ -d "$VOICEBOX/.git" ] || git clone -q --depth 1 --branch v0.5.0 https://github.com/jamiepine/voicebox "$VOICEBOX"
[ -x "$VOICEBOX/.venv/bin/python" ] || { (cd "$VOICEBOX" && uv venv -q --python 3.12 .venv) \
  && uv pip install -q --python "$VOICEBOX/.venv/bin/python" -r "$REPO/scripts/voicebox-requirements.txt"; }
PYTHONPATH="$REPO/scripts" python3 - <<'PY' && echo "narration voice (Voicebox + Kokoro): ok" || echo "warning: narration smoke test failed; animations will stay silent until it works"
import tempfile, pathlib, learn
learn.tts_lines(["Narration check: the local voice is ready."], learn.DEFAULT_VOICE, pathlib.Path(tempfile.mkdtemp()))
PY

grep -q "<!-- learning-system -->" "$OC/AGENTS.md" 2>/dev/null || cat "$REPO/opencode/agents-block.md" >> "$OC/AGENTS.md"

python3 -m unittest discover -s "$REPO/scripts" -q
command -v learn >/dev/null || echo "warning: ~/.local/bin is not on PATH; the agent will use the full script path"
echo "learning-system ready. In OpenCode: /learn <topic>"
