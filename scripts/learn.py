#!/usr/bin/env python3
"""Learning-session engine: learner state, mastery rules, and the session note.

The agent runs one subcommand per step and follows the WHY/NEXT lines it prints.
The rules live here, not in the prompt, so every model gets the same decisions.

  start <topic...>                 begin or resume a session (switches topic if one is open)
  research [--save]                research gate: show the brief template / save a brief (stdin) for this topic
  lit search|resolve|text|guide|db ...   PRAXIST no-key literature lookup (OpenAlex, arXiv, Crossref, PubMed...)
  plan --concept id ... --known id,id|none   concepts come from the research brief
  known <concept>                  learner says they already know it -> quick check instead of teaching
  add <id> <title...> [--prereqs a,b] [--before c]
  figure <name> [--still]          Manim scene on stdin -> checked MP4 (or PNG with --still) in the vault, prints the embed
                                   (matplotlib is the fallback, unlocked after 3 failed Manim attempts in a row)
  block <concept>                  theory markdown (with a visual) on stdin -> session note
  ask <concept>                    question JSON on stdin -> session note
  check                            read answers from the note; grades choice questions
  answer <Q> <letter|idk> | answer <Q> --text T     learner answered in chat
  grade <Q> correct|wrong|idk [--kind slip|gap|misconception] [--what W]   typed answers
  next                             what to do now, and why
  pref <text...>                   save a learner preference for every future session
  end [--next-time T]              summary into the note, dashboard, commit
  status                           what the system believes the learner knows

Env: LEARN_STATE, LEARN_VAULT, LEARN_TODAY (YYYY-MM-DD), LEARN_NO_CLI=1, LEARN_NO_GIT=1,
     LEARN_MANIM (manim binary), LEARN_TEX_BIN (TeX bin dir), LEARN_REQUIRE_MANIM=0 (accept any visual).
"""

import argparse
import json
import os
import random
import re
import shutil
import subprocess
import sys
from datetime import date, timedelta
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
STATE = Path(os.environ.get("LEARN_STATE", REPO / "state" / "learner.json"))
VAULT = Path(os.environ.get("LEARN_VAULT", Path.home() / "Documents" / "Obsidian Vault"))
SESSIONS = "Sessions"
DASHBOARD = "Maps/Learner dashboard.md"

INTERVALS = {1: 1, 2: 3, 3: 7, 4: 21}  # review box -> days until next review
# Solid = 2 correct in a row, the last one at level 2+ (applied, not just recalled).
SOLID = ("solid", "mastered")
MAX_BLOCK_WORDS = 250
MAX_PLAN = 7
LEVELS = {1: "recall the idea just taught, in the same setting",
          2: "apply it to a new example with new numbers",
          3: "explain why it works, or combine it with an earlier idea"}

SOURCES_DIR = "Sources"
FIG_DIR = "Attachments/learn"
FIG_MAX_BYTES = 3_000_000
FIG_TIMEOUT = 90
MANIM = Path(os.environ.get("LEARN_MANIM", Path.home() / ".local/share/learning-system/manim-venv/bin/manim"))
TEX_BIN = Path(os.environ.get("LEARN_TEX_BIN", Path.home() / "Library/TinyTeX/bin/universal-darwin"))
MANIM_TIMEOUT = 180
VIDEO_MAX_BYTES = 15_000_000
VIDEO_SECONDS = (2, 90)
MANIM_FALLBACK_AFTER = 3
# Old 3Blue1Brown manimlib / legacy names that free models reproduce from training data -> Manim Community fix.
OLD_MANIM_API = [
    (r"\bmanimlib\b", "use `from manim import *` (Manim Community), not manimlib/ManimGL"),
    (r"\bShowCreation\b", "ShowCreation -> Create"),
    (r"\bTextMobject\b", "TextMobject -> Text (plain text) or Tex (LaTeX text)"),
    (r"\bTexMobject\b", "TexMobject -> MathTex"),
    (r"\bOldTex(Text)?\b", "OldTex/OldTexText -> MathTex/Tex"),
    (r"\bGraphScene\b", "GraphScene was removed: use a normal Scene with `axes = Axes(...)` and `axes.plot(...)`"),
    (r"\bCONFIG\s*=\s*\{", "CONFIG dicts are gone: pass settings as arguments or set attributes in construct()"),
    (r"\bget_graph\(", "get_graph -> axes.plot(...)"),
    (r"\bFadeInFrom(Down|Large|Point)?\b", "FadeInFrom... -> FadeIn(mob, shift=DOWN) / FadeIn(mob, scale=...)"),
    (r"\bscale_in_place\b", "scale_in_place -> scale"),
    (r"\bInteractiveScene\b", "InteractiveScene is ManimGL: subclass Scene"),
    (r"\bself\.embed\(", "self.embed() is ManimGL-only: remove it"),
]
# Wraps the agent's scene: after every play()/wait(), text that overlaps other text or leaves the frame is recorded.
MANIM_HARNESS = r"""
import json, os
from manim import *
from manim import Scene as _Base
_ns = {"__name__": "figure"}
exec(compile(open(os.environ["LEARN_FIG_SCRIPT"]).read(), "figure.py", "exec"), _ns)
_found = [v for v in _ns.values() if isinstance(v, type) and issubclass(v, _Base) and v.__module__ == "figure"]
if len(_found) != 1:
    raise SystemExit(f"LEARN: define exactly one Scene class, found {len(_found)}")
_TEXT = (Text, MarkupText, MathTex, Tex, SingleStringMathTex, Paragraph, DecimalNumber, Integer)
_problems = []

def _texts(mobs):
    out = []
    def walk(m):
        if isinstance(m, _TEXT):
            out.append(m)
            return
        for sub in m.submobjects:
            walk(sub)
    for m in mobs:
        walk(m)
    return out

def _label(m):
    return (getattr(m, "original_text", None) or getattr(m, "tex_string", None) or getattr(m, "text", None)
            or type(m).__name__)[:30]

def _visible(m):
    return max((max(x.get_fill_opacity(), x.get_stroke_opacity()) for x in m.family_members_with_points()), default=0) > 0.05

class LearnChecked(_found[0]):
    def _learn_check(self):
        W, H = config.frame_width / 2, config.frame_height / 2
        ts = [t for t in _texts(self.mobjects) if _visible(t)]
        boxes = [(t.get_left()[0], t.get_right()[0], t.get_bottom()[1], t.get_top()[1]) for t in ts]
        when = f"at {self.renderer.time:.1f}s"
        for t, (x0, x1, y0, y1) in zip(ts, boxes):
            if x0 < -W - 0.05 or x1 > W + 0.05 or y0 < -H - 0.05 or y1 > H + 0.05:
                _problems.append(f"{_label(t)!r} is cut off at the edge of the frame {when}")
        pad = 0.04
        for i in range(len(ts)):
            for j in range(i):
                a, b = boxes[i], boxes[j]
                if a[0] + pad < b[1] - pad and b[0] + pad < a[1] - pad and a[2] + pad < b[3] - pad and b[2] + pad < a[3] - pad:
                    _problems.append(f"{_label(ts[j])!r} overlaps {_label(ts[i])!r} {when}")
    def play(self, *args, **kwargs):
        super().play(*args, **kwargs)
        self._learn_check()
    def wait(self, *args, **kwargs):
        super().wait(*args, **kwargs)
        self._learn_check()
    def construct(self):
        super().construct()
        self._learn_check()
        seen = list(dict.fromkeys(_problems))
        json.dump(seen, open(os.environ["LEARN_FIG_REPORT"], "w"))
"""
CANVAS_COLORS = {"claimed": "6", "learning": "3", "solid": "4", "mastered": "5"}  # new = no colour (grey)
FIG_EMBED = re.compile(r"!\[\[(Attachments/learn/[^\]|]+)(?:\|[^\]]*)?\]\]")
MERMAID = re.compile(r"```mermaid\n(.*?)```", re.S)
# Runs the agent's figure script, then checks every open figure for overlapping labels.
FIG_HARNESS = r"""
import json, sys, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
out_png, out_gif, script = sys.argv[1:4]
g = {"__name__": "__main__", "OUT_PNG": out_png, "OUT_GIF": out_gif}
exec(compile(open(script).read(), "figure.py", "exec"), g)
problems = []
for num in plt.get_fignums():
    fig = plt.figure(num)
    fig.canvas.draw()
    r = fig.canvas.get_renderer()
    texts = [t for ax in fig.axes for t in list(ax.texts) + [ax.title]] + list(fig.texts)
    texts = [t for t in texts if t.get_visible() and t.get_text().strip()]
    boxes = [t.get_window_extent(r).shrunk(0.96, 0.9) for t in texts]
    for i in range(len(texts)):
        for j in range(i):
            if boxes[i].overlaps(boxes[j]):
                problems.append(f"{texts[j].get_text()[:30]!r} overlaps {texts[i].get_text()[:30]!r}")
    for ax in fig.axes:
        for line in ax.lines:
            xs, ys = line.get_data()
            if len(xs) < 2:
                continue
            pts = line.get_transform().transform(list(zip(xs, ys)))
            for t, b in zip(texts, boxes):
                if t.axes is ax and any(b.contains(px, py) for px, py in pts):
                    problems.append(f"{t.get_text()[:30]!r} sits on top of a plotted line")
print("LEARN-CHECK " + json.dumps(problems))
"""
BRIEF_SECTIONS = ["Concepts", "Definitions", "Misconceptions", "Worked examples", "Sources", "Open questions"]
SOURCE_TYPES = {"primary", "textbook", "review", "secondary", "vendor"}
STRONG_TYPES = {"primary", "textbook", "review"}
MIN_SOURCES = 3
CITE = re.compile(r"\[(S\d+)\]")
BRIEF_TEMPLATE = """# Research brief: <Topic>

Goal: <what the learner wants to be able to do, from their reply>
Domain: <machine_learning | biology | chemistry | medicine | robotics_control | physics_materials | generic>
Date: YYYY-MM-DD

## Concepts
| Id | Concept | Builds on | Sources |
| --- | --- | --- | --- |
| short-id | Plain title | - | S1 |
| next-id | Plain title | short-id | S1, S2 |

## Definitions
- **term**: the exact definition, as the sources state it [S1]

## Misconceptions
- <a wrong belief learners hold> -> <why it is wrong> [S2]
- <another one> -> <why> [S3]

## Worked examples
- short-id: <a small example with real numbers and the result> [S1]

## Sources
| Id | Source | Type | Reliability | Supports | Retrieved |
| --- | --- | --- | --- | --- | --- |
| S1 | <title>, <URL or doi:/arXiv: id> | primary/textbook/review/secondary/vendor | high/med/low | <which claims> | YYYY-MM-DD |

## Open questions
- <what sources disagree on or what you could not verify; "none" if nothing>
"""

DEFAULT_PREFS = [
    "Theory first, then questions. Only ask about what was just taught in this note.",
    "Very easy words. Short sentences. One idea per sentence. A concrete example before any formula.",
    "Everything the learner reads goes into the Obsidian session note. Chat replies are 1-2 lines that point to the note.",
    "If the learner says they are lost, restart from the most basic idea, from zero.",
    "Always say why a step exists before showing how to do it.",
    "One note per session. Never send the learner to another file mid-session.",
    "Visual learner: every idea gets a Manim animation of how it works (3Blue1Brown style), plus normal text.",
]


SUPERSEDED_PREFS = {
    "Visual learner: every idea gets a picture of how it works (diagram, animation or plot), plus normal text.",
}


class LearnError(Exception):
    pass


def today():
    return date.fromisoformat(os.environ["LEARN_TODAY"]) if os.environ.get("LEARN_TODAY") else date.today()


def iso(d):
    return d.isoformat()


def slug(text):
    s = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    if not s:
        raise LearnError(f"Cannot make an id from {text!r}")
    return s


# ---------- state ----------

def load():
    if STATE.exists():
        s = json.loads(STATE.read_text())
        prefs = s["profile"]["preferences"]
        prefs[:] = [p for p in prefs if p not in SUPERSEDED_PREFS]
        prefs += [p for p in DEFAULT_PREFS if p not in prefs]  # new defaults reach existing learners
        return s
    return {"version": 1, "profile": {"preferences": list(DEFAULT_PREFS)},
            "topics": {}, "session": None, "history": [], "mistakes": []}


def save(s):
    STATE.parent.mkdir(parents=True, exist_ok=True)
    tmp = STATE.with_suffix(".tmp")
    tmp.write_text(json.dumps(s, indent=2, ensure_ascii=False) + "\n")
    tmp.replace(STATE)


def need_session(s):
    if not s["session"]:
        raise LearnError("No open session. Run `learn start <topic>` first.")
    return s["session"]


def topic_of(s):
    return s["topics"][need_session(s)["topic"]]


def concept(s, cid):
    t = topic_of(s)
    if cid not in t["concepts"]:
        raise LearnError(f"Unknown concept {cid!r} in topic {t['title']!r}. Known: {', '.join(t['concepts']) or 'none'}. "
                         "Add it with `learn add` or `learn plan`.")
    return t["concepts"][cid]


def new_concept(title, prereqs):
    return {"title": title, "prereqs": prereqs, "status": "new", "taught": False, "streak": 0,
            "level": 1, "box": 0, "next_review": None, "solid_date": None, "promoted": None,
            "last_seen": None, "history": []}


# ---------- session note ----------

def note_file(s):
    return VAULT / need_session(s)["note"]


def note_lines(s):
    return note_file(s).read_text().split("\n")


def write_lines(s, lines):
    note_file(s).write_text("\n".join(lines))


def append(s, text):
    with note_file(s).open("a") as f:
        f.write("\n" + text.rstrip() + "\n")


def set_props(s, **props):
    lines = note_lines(s)
    if lines[0] != "---":
        return
    end = lines.index("---", 1)
    for k, v in props.items():
        row = f"{k}: {v}"
        idx = next((i for i in range(1, end) if lines[i].startswith(f"{k}:")), None)
        if idx is None:
            lines.insert(end, row)
            end += 1
        else:
            lines[idx] = row
    write_lines(s, lines)


def q_span(lines, qid):
    """Return (header_index, end_marker_index) of a question section."""
    head = next((i for i, l in enumerate(lines) if l.startswith(f"### {qid} ")), None)
    end = next((i for i, l in enumerate(lines) if l.strip() == f"%% {qid} end %%"), None)
    if head is None or end is None:
        raise LearnError(f"{qid} not found in the session note. Was the note edited? Re-ask the question.")
    return head, end


def insert_after(s, qid, text):
    lines = note_lines(s)
    _, end = q_span(lines, qid)
    lines[end + 1:end + 1] = [""] + text.rstrip().split("\n")
    write_lines(s, lines)


def cli(*args):
    """Best-effort Obsidian CLI call; the system works without it."""
    if os.environ.get("LEARN_NO_CLI") or not shutil.which("obsidian"):
        return
    try:
        subprocess.run(["obsidian", *args], capture_output=True, timeout=5)
    except (OSError, subprocess.SubprocessError):
        pass


def notice(msg):
    cli("eval", f"code=new Notice({json.dumps(msg)})")


def ensure_base():
    base = VAULT / SESSIONS / "Sessions.base"
    if base.exists():
        return
    base.write_text(
        "filters:\n  and:\n    - file.inFolder(\"Sessions\")\n    - 'type == \"learning-session\"'\n"
        "views:\n  - type: table\n    name: Sessions\n    order:\n      - file.name\n      - topic\n"
        "      - date\n      - status\n      - correct\n      - wrong\n      - idk\n"
        "    sort:\n      - property: date\n        direction: DESC\n")


# ---------- research brief (PRAXIST method, adapted for learning) ----------

def sections(text):
    out, cur = {}, None
    for line in text.split("\n"):
        m = re.match(r"^##\s+(.+?)\s*$", line)
        if m:
            cur = m.group(1).strip().lower()
            out[cur] = []
        elif cur is not None:
            out[cur].append(line)
    return out


def table_rows(lines):
    rows = [[c.strip() for c in l.strip().strip("|").split("|")] for l in lines if l.strip().startswith("|")]
    return [r for r in rows[1:] if not all(re.fullmatch(r":?-{3,}:?", c) for c in r)]


def parse_brief(text):
    """Validate a research brief. Returns (brief, errors)."""
    errs = []
    sec = sections(text)
    for name in BRIEF_SECTIONS:
        if name.lower() not in sec:
            errs.append(f"missing section '## {name}'")
    goal = next((l.split(":", 1)[1].strip() for l in text.split("\n") if l.lower().startswith("goal:")), "")
    if not goal or goal.startswith("<"):
        errs.append("missing 'Goal: ...' line (the learner's goal, from their reply)")
    sources = {}
    for r in table_rows(sec.get("sources", [])):
        if len(r) < 6:
            errs.append(f"source row needs 6 columns (Id | Source | Type | Reliability | Supports | Retrieved): {r}")
            continue
        sid, src, typ, rel, sup, got = r[:6]
        if not re.fullmatch(r"S\d+", sid):
            errs.append(f"source id must look like S1, got {sid!r}")
            continue
        if not re.search(r"https?://\S+|\bdoi:\S+|\b10\.\d{4,}/\S+|\barxiv:\S+", src, re.I):
            errs.append(f"{sid}: needs a URL or a doi:/arXiv: identifier")
        if typ.lower() not in SOURCE_TYPES:
            errs.append(f"{sid}: type must be one of {', '.join(sorted(SOURCE_TYPES))}")
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", got):
            errs.append(f"{sid}: Retrieved must be a YYYY-MM-DD date")
        sources[sid] = {"source": src, "type": typ.lower(), "reliability": rel, "supports": sup, "retrieved": got}
    if len(sources) < MIN_SOURCES:
        errs.append(f"need at least {MIN_SOURCES} sources, found {len(sources)}")
    if sources and not any(v["type"] in STRONG_TYPES for v in sources.values()):
        errs.append("need at least one primary, textbook or review source")
    concepts = {}
    for r in table_rows(sec.get("concepts", [])):
        if len(r) < 4:
            errs.append(f"concept row needs 4 columns (Id | Concept | Builds on | Sources): {r}")
            continue
        cid, title, builds, cites = r[:4]
        try:
            cid = slug(cid)
        except LearnError:
            errs.append(f"bad concept id {r[0]!r}")
            continue
        prereqs = [slug(x) for x in builds.split(",") if x.strip() and x.strip() != "-"]
        cited = re.findall(r"S\d+", cites)
        if not cited:
            errs.append(f"concept {cid}: cite at least one source id")
        concepts[cid] = {"title": title, "prereqs": prereqs, "sources": cited}
    if len(concepts) < 3:
        errs.append(f"need at least 3 concepts, found {len(concepts)}")
    for cid, c in concepts.items():
        for pr in c["prereqs"]:
            if pr not in concepts:
                errs.append(f"concept {cid}: builds on unknown id {pr!r}")
    for name, need in (("misconceptions", 2), ("definitions", 1), ("worked examples", 1)):
        n = sum(1 for l in sec.get(name, []) if l.strip().startswith("- "))
        if n < need:
            errs.append(f"'## {name.capitalize()}' needs at least {need} bullet(s)")
    used = set(CITE.findall(text)) | {x for c in concepts.values() for x in c["sources"]}
    for sid in sorted(used - set(sources)):
        errs.append(f"{sid} is cited but not in the Sources table")
    return {"goal": goal, "concepts": concepts, "sources": sources}, errs


def brief_of(s):
    t = topic_of(s)
    r = t.get("research")
    if not r:
        raise LearnError(f"'{t['title']}' has no research brief yet. Run `learn research` first.")
    path = VAULT / r["note"]
    if not path.exists():
        raise LearnError(f"Research brief {r['note']} is missing from the vault. Re-save it with `learn research --save`.")
    brief, errs = parse_brief(path.read_text())
    if errs:
        raise LearnError("The research brief no longer validates: " + "; ".join(errs[:5]))
    return brief


# ---------- visuals ----------

def cli_eval(js):
    """Run JS inside Obsidian via its CLI. Returns the result text, or None when the CLI is unavailable."""
    if os.environ.get("LEARN_NO_CLI") or not shutil.which("obsidian"):
        return None
    try:
        r = subprocess.run(["obsidian", "eval", f"code={js}"], capture_output=True, text=True, timeout=15)
    except (OSError, subprocess.SubprocessError):
        return None
    out = r.stdout.strip()
    return out[3:].strip() if out.startswith("=>") else None


def mermaid_problems(md):
    """Parse every mermaid block with Obsidian's own mermaid. Returns (errors, unchecked_count)."""
    errors, unchecked = [], 0
    for i, code in enumerate(MERMAID.findall(md), 1):
        js = ("(async()=>{if(!window.mermaid)return 'UNLOADED';try{await window.mermaid.parse(%s);return 'OK'}"
              "catch(e){return 'ERR '+String(e.message||e).slice(0,300)}})()" % json.dumps(code))
        res = cli_eval(js)
        if res is None or res == "UNLOADED":
            unchecked += 1
        elif res.startswith("ERR"):
            errors.append(f"mermaid diagram {i}: {res[4:]}")
    return errors, unchecked


def render_canvas(s, tid):
    """Write Maps/<topic> map.canvas: concepts coloured by status, arrows from prerequisites."""
    t = s["topics"][tid]
    cs = t["concepts"]
    if not cs:
        return None
    depth = {}

    def d(cid):
        if cid not in depth:
            depth[cid] = 1 + max((d(p) for p in cs[cid]["prereqs"] if p in cs), default=-1)
        return depth[cid]
    rows = {}
    nodes, edges = [], []
    for cid, c in cs.items():
        col = d(cid)
        row = rows[col] = rows.get(col, -1) + 1
        node = {"id": cid, "type": "text", "x": col * 340, "y": row * 150, "width": 280, "height": 100,
                "text": f"**{c['title']}**\n\n{c['status']}" + (f" · box {c['box']}" if c["box"] else "")}
        if c["status"] in CANVAS_COLORS:
            node["color"] = CANVAS_COLORS[c["status"]]
        nodes.append(node)
        edges += [{"id": f"{p}->{cid}", "fromNode": p, "fromSide": "right", "toNode": cid, "toSide": "left"}
                  for p in c["prereqs"] if p in cs]
    last = max(depth.values()) + 1
    nodes.append({"id": "goal", "type": "text", "x": last * 340, "y": 0, "width": 280, "height": 100,
                  "text": f"**Goal**\n\n{t['goal'] or '-'}", "color": "1"})
    edges += [{"id": f"{cid}->goal", "fromNode": cid, "fromSide": "right", "toNode": "goal", "toSide": "left"}
              for cid in cs if not any(cid in o["prereqs"] for o in cs.values())]
    nodes.append({"id": "legend", "type": "text", "x": 0, "y": -170, "width": 520, "height": 90,
                  "text": "grey = new · purple = you said you know it · yellow = learning · "
                          "green = solid · cyan = mastered"})
    rel = f"Maps/{t['title']} map.canvas"
    path = VAULT / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"nodes": nodes, "edges": edges}, indent=1))
    return rel


# ---------- decisions ----------

def step(action, cid=None, reason="", level=None):
    return {"action": action, "concept": cid, "reason": reason, "level": level}


def choose_fresh(s):
    t = topic_of(s)
    cs = t["concepts"]
    d = iso(today())
    for cid, c in cs.items():
        if c["status"] in SOLID and c["next_review"] and c["next_review"] <= d and c["last_seen"] != d:
            return step("review", cid, f"'{c['title']}' is due for review (box {c['box']}, last seen {c['last_seen']}).",
                        max(2, c["level"]))
    for cid, c in cs.items():
        if c["status"] == "claimed":
            return step("check", cid, f"You said you already know '{c['title']}'. One quick check before we build on it.", 2)
    for cid, c in cs.items():
        if c["status"] == "learning":
            if c["taught"]:
                return step("ask", cid, f"'{c['title']}' is not solid yet ({c['streak']} of 2 correct in a row).", c["level"])
            return step("teach", cid, f"'{c['title']}' still needs teaching.")
    for cid, c in cs.items():
        if c["status"] == "new":
            weak = [p for p in c["prereqs"] if cs[p]["status"] not in SOLID]
            if not weak:
                base = (f"it builds on {', '.join(repr(cs[p]['title']) for p in c['prereqs'])}, which you have solid"
                        if c["prereqs"] else "it needs nothing else, so it is a starting point")
                return step("teach", cid, f"Next new idea: '{c['title']}', because {base}.")
    blocked = [cid for cid, c in cs.items() if c["status"] == "new"]
    if blocked:
        return step("teach", blocked[0], f"'{cs[blocked[0]]['title']}' is the next idea in the plan.")
    return step("complete", None, "Every concept in this topic is solid or mastered.")


def current_step(s):
    sess = need_session(s)
    t = topic_of(s)
    if sess["pending"]:
        return step("wait", None, f"{', '.join(sess['pending'])} waiting for the learner's answer.")
    if not t.get("research"):
        return step("research", None, f"'{t['title']}' has no research brief yet. Research comes before any teaching.")
    if not t["concepts"]:
        return step("plan", None, f"'{t['title']}' has a research brief but no plan yet.")
    st = sess.get("step")
    if st and (st["concept"] is None or st["concept"] in t["concepts"]):
        return st
    return choose_fresh(s)


def instruction(s, st):
    t = topic_of(s)
    c = t["concepts"].get(st["concept"]) if st["concept"] else None
    title = c["title"] if c else ""
    cid = st["concept"]
    lvl = st["level"] or (c["level"] if c else 1)
    lvl_txt = f"level {lvl} ({LEVELS[lvl]})"
    a = st["action"]
    if a == "wait":
        return ("Tell the learner in ONE line which question to answer in the note. Then STOP and wait. "
                "When they send any message, run `learn check`. If they answer in chat instead, run "
                "`learn answer <Q> <letter>` or `learn answer <Q> --text \"...\"`.")
    if a == "research":
        return ("1) If you don't know the learner's goal yet, ask ONE plain question in chat: what do you want to be "
                f"able to do with '{t['title']}', and what do you already know about it? Wait for the reply. "
                "2) Run the research pipeline in references/research.md (PRAXIST method): `learn lit guide <domain>`, "
                "2-4 `learn lit search \"<query>\"`, web search for textbooks/official syllabi/docs, open and read the "
                "best 3-6 sources. 3) Write the brief from `learn research` (template) and pipe it to "
                "`learn research --save`. Do not teach anything before the brief is saved.")
    if a == "plan":
        return ("Pick 3-7 concept ids from the brief's Concepts table that lead to the learner's goal, simplest "
                "first, and run `learn plan --concept <id> --concept <id> ... --known <ids|none>`. "
                "--known is required: the ids the learner SAID they already know (they get a quick check instead "
                "of teaching), or --known none. Never teach what they already know.")
    if a == "teach":
        return (f"Make 1 Manim visual of how '{title}' works: pick the closest template in references/visuals.md "
                f"(things moving: physical; a system of parts: diagram with --still; a curve or numbers: graph; a "
                f"formula: derivation; steps: process), adapt it, and run `learn figure <name>`. Then write the theory block from the research "
                f"brief (cite sources as [S1]) with the visual embedded, using the block recipe in the skill, pipe it to "
                f"`learn block {cid}`, then write 1 question at {lvl_txt} and pipe it to `learn ask {cid}`.")
    if a == "reteach":
        return (f"Re-teach '{title}': write a NEW block on the SAME idea with smaller steps, smaller numbers and a "
                f"different example from the same subject (not a toy story without the idea), and a NEW Manim visual "
                f"that shows the step they got wrong (references/visuals.md). Name that step. Pipe it to `learn block {cid}`. Then 1 question at "
                f"level 1 via `learn ask {cid}`.")
    if a == "ask":
        return (f"Write 1 NEW question on '{title}' at {lvl_txt}. Do not repeat an earlier question; change the "
                f"numbers or the situation. Pipe it to `learn ask {cid}`.")
    if a == "review":
        return (f"Ask 1 review question on '{title}' at {lvl_txt}. No theory first: this checks memory from an "
                f"earlier session. Pipe it to `learn ask {cid}`. The engine labels it as a review in the note.")
    if a == "check":
        return (f"Ask 1 quick check question on '{title}' at {lvl_txt}. No theory: the learner said they know it. "
                f"Pipe it to `learn ask {cid}`.")
    if a == "confused":
        return (f"Three misses on '{title}'. Stop quizzing. Ask the learner ONE plain question in chat: which "
                f"exact step is confusing? Then make that step its own smaller concept with "
                f"`learn add <id> <Title> --before {cid}` and teach it.")
    if a == "complete":
        return ("Tell the learner in 2 lines what is now solid (see `learn status`). Ask: go deeper "
                "(add concepts with `learn add`) or finish (`learn end --next-time \"...\"`)?")
    raise LearnError(f"Unknown step {a!r}")


def print_next(s, extra=""):
    st = current_step(s)
    if extra:
        print(extra)
    print(f"WHY: {st['reason']}")
    print(f"NEXT: {instruction(s, st)}")


# ---------- rules ----------

def record(s, qid, result, kind=None, what=""):
    """Apply a graded answer. Returns the one-line decision reason."""
    sess = need_session(s)
    p = sess["pending"].pop(qid)
    t = topic_of(s)
    cid = p["concept"]
    c = t["concepts"][cid]
    d = today()
    ds = iso(d)
    c["history"].append({"date": ds, "q": qid, "result": result, "level": p["level"], "kind": kind})
    c["last_seen"] = ds
    sess["counts"][result] = sess["counts"].get(result, 0) + 1
    key = f"{sess['topic']}/{cid}"
    sess["touched"].setdefault(key, sess["start_status"].get(key, c["status"]))

    if result == "correct":
        closed = [m for m in s["mistakes"] if m["concept"] == cid and m["topic"] == sess["topic"]
                  and not m["closed"] and m["date"] < ds]
        for m in closed:
            m["closed"] = ds
        tail = f" Closed {len(closed)} old mistake(s)." if closed else ""
        if c["status"] == "claimed":
            c.update(status="solid", taught=True, streak=1, box=1, solid_date=ds, promoted=ds,
                     next_review=iso(d + timedelta(days=1)))
            sess["step"] = None
            return f"Quick check passed: '{c['title']}' counts as solid. Review tomorrow.{tail}"
        if c["status"] in SOLID:
            c["streak"] += 1
            sess["step"] = None
            if c["promoted"] != ds:
                c["box"] = min(c["box"] + 1, 4)
                c["status"] = "mastered" if c["box"] >= 2 else "solid"
                c["promoted"] = ds
                c["next_review"] = iso(d + timedelta(days=INTERVALS[c["box"]]))
                return (f"Remembered '{c['title']}' on a later day: box {c['box']} ({c['status']}), "
                        f"next review in {INTERVALS[c['box']]} days.{tail}")
            return f"Correct again. Same day, so no promotion: spacing needs a later day.{tail}"
        c["status"] = "learning"
        c["streak"] += 1
        if c["streak"] >= 2 and p["level"] < 2:
            c["level"] = max(c["level"], 2)
            sess["step"] = step("ask", cid, f"{c['streak']} correct in a row on '{c['title']}', but only recall so far. "
                                            "One question that applies it to a new example (level 2) before it counts as solid.", 2)
            return f"Correct, {c['streak']} in a row on '{c['title']}' at level 1."
        if c["streak"] >= 2:
            c.update(status="solid", box=1, solid_date=ds, promoted=ds, next_review=iso(d + timedelta(days=1)),
                     level=min(3, c["level"] + 1))
            sess["misses"].pop(key, None)
            if sess["stack"]:
                back = sess["stack"].pop()
                sess["step"] = step("ask", back, f"'{c['title']}' is fixed, so back to '{t['concepts'][back]['title']}'.")
            else:
                sess["step"] = None
            return f"2 correct in a row: '{c['title']}' is solid. Review tomorrow.{tail}"
        sess["step"] = step("ask", cid, f"Correct (1 of 2 in a row). One more question on '{c['title']}' makes it solid.",
                            c["level"])
        return f"Correct, 1 of 2 in a row on '{c['title']}'.{tail}"

    # wrong or "I don't know"
    was = c["status"]
    c.update(streak=0, level=max(1, c["level"] - 1), box=0, status="learning",
             next_review=iso(d + timedelta(days=1)))
    kind = kind or ("gap" if result == "idk" else "misconception")
    s["mistakes"].append({"topic": sess["topic"], "concept": cid, "date": ds, "q": qid, "kind": kind,
                          "what": what or ("said I don't know" if result == "idk" else ""), "closed": None})
    misses = sess["misses"][key] = sess["misses"].get(key, 0) + 1

    if was == "claimed":
        c["taught"] = False
        sess["step"] = step("teach", cid, f"You said you knew '{c['title']}', but the check says not yet. Teaching it now.")
    elif result == "idk":
        sess["step"] = step("reteach", cid, f"'I don't know' on '{c['title']}': teaching it again, simpler, before asking.")
    elif misses >= 3:
        sess["step"] = step("confused", cid, f"Three misses on '{c['title']}' this session.")
    elif misses == 2:
        weak = next((pr for pr in c["prereqs"] if t["concepts"][pr]["status"] not in SOLID), None)
        if weak:
            sess["stack"].append(cid)
            w = t["concepts"][weak]
            sess["step"] = step("teach" if not w["taught"] else "reteach", weak,
                                f"Two misses on '{c['title']}'. It rests on '{w['title']}', which is not solid, "
                                f"so we go back to '{w['title']}' first.")
        else:
            sess["step"] = step("reteach", cid, f"Two misses on '{c['title']}' and its foundations are solid, "
                                                "so it gets re-taught with a new, simpler example.")
    elif was in SOLID:
        sess["step"] = step("reteach", cid, f"'{c['title']}' was forgotten since last time: short re-teach, then a new question.")
    else:
        sess["step"] = step("ask", cid, f"Missed once. The feedback explains the fix. Now a new question on the same idea.",
                            c["level"])
    return sess["step"]["reason"]


def feedback(qid, p, result, picked=None):
    if p["type"] == "choice":
        right = f"{p['correct']}. {p['options'][p['correct']]}"
        if result == "correct":
            body = [f"> [!success] {qid}: correct ({right})", f"> {p['why']}"]
        elif result == "idk":
            body = [f"> [!tip] {qid}: \"I don't know\" is a real answer. Right answer: {right}", f"> {p['why']}"]
        else:
            body = [f"> [!failure] {qid}: you picked {picked}. Right answer: {right}", f"> {p['why']}",
                    f"> Why {picked} is tempting: {p['misconceptions'].get(picked, '')}"]
    else:
        tag = {"correct": "[!success]", "idk": "[!tip]", "wrong": "[!failure]"}[result]
        body = [f"> {tag} {qid}: {result}. A good answer: {p['answer']}", f"> {p['why']}"]
    return body


def grade(s, qid, result, kind=None, what="", picked=None):
    sess = need_session(s)
    p = sess["pending"][qid]
    body = feedback(qid, p, result, picked)
    reason = record(s, qid, result, kind, what)
    render_canvas(s, sess["topic"])
    st = current_step(s)
    insert_after(s, qid, "\n".join(body + [">", f"> **Next:** {st['reason']}"]))
    c = sess["counts"]
    set_props(s, correct=c.get("correct", 0), wrong=c.get("wrong", 0), idk=c.get("idk", 0))
    return reason


# ---------- commands ----------

def cmd_start(s, a):
    title = " ".join(a.topic).strip()
    tid = slug(title)
    d = iso(today())
    sess = s["session"]
    if sess and sess["date"] != d:
        finish(s, "Ended automatically: this session was never closed.")
        sess = None
    if tid not in s["topics"]:
        s["topics"][tid] = {"title": title, "goal": "", "created": d, "concepts": {}}
    t = s["topics"][tid]
    msg = ""
    if sess and sess["topic"] != tid:
        sess.update(topic=tid, step=None, stack=[])
        sess["start_status"].update({f"{tid}/{cid}": c["status"] for cid, c in t["concepts"].items()})
        if tid not in sess["topics"]:
            sess["topics"].append(tid)
        append(s, f"---\n\n## Switched topic: {t['title']}")
        set_props(s, topic=json.dumps(", ".join(s["topics"][x]["title"] for x in sess["topics"])))
        msg = f"Switched the open session to '{t['title']}'. Same note: {sess['note']}"
    elif sess:
        msg = f"Resuming the open session: {sess['note']}"
    else:
        folder = VAULT / SESSIONS
        folder.mkdir(parents=True, exist_ok=True)
        ensure_base()
        name = f"{d} {t['title']}"
        n = 2
        while (folder / f"{name}.md").exists():
            name, n = f"{d} {t['title']} ({n})", n + 1
        rel = f"{SESSIONS}/{name}.md"
        s["session"] = sess = {"date": d, "topic": tid, "topics": [tid], "note": rel, "pending": {}, "qn": 0,
                               "blocks": 0, "misses": {}, "stack": [], "step": None, "counts": {},
                               "touched": {}, "start_status": {f"{tid}/{cid}": c["status"] for cid, c in t["concepts"].items()}}
        (VAULT / rel).write_text(
            f"---\ntype: learning-session\ntopic: {json.dumps(t['title'])}\ndate: {d}\nstatus: active\n"
            f"correct: 0\nwrong: 0\nidk: 0\n---\n# {t['title']}: session {d}\n\n"
            "> [!info] How this works\n> Read each theory block. Answer the question right under it: tick one box, "
            "or type under **Your answer**. Then send any message in OpenCode. \"I don't know\" is a real answer, "
            "never a wrong one.\n")
        last = next((h for h in reversed(s["history"]) if tid in h.get("next_by_topic", {})), None)
        if last:
            append(s, f"> [!note] Last time ({last['date']})\n> {last['next_by_topic'][tid]}")
        msg = f"New session note: {rel}"
    render_canvas(s, tid)
    cli("open", f"path={sess['note']}")
    print(msg)
    print_briefing(s, tid)
    print_next(s)


def print_briefing(s, tid):
    t = s["topics"][tid]
    d = iso(today())
    print("\nLEARNER PREFERENCES (apply to every block and every reply):")
    for p in s["profile"]["preferences"]:
        print(f"- {p}")
    print(f"\nTOPIC: {t['title']}" + (f" | goal: {t['goal']}" if t["goal"] else " | goal: not set yet"))
    if t["concepts"]:
        print(concept_table(t))
    open_m = [m for m in s["mistakes"] if not m["closed"] and m["topic"] == tid]
    if open_m:
        print("\nOPEN MISTAKES (they close after a correct answer on a later day):")
        for m in open_m:
            print(f"- {m['date']} {t['concepts'][m['concept']]['title']}: {m['kind']}. {m['what']}")
    other = [(ot["title"], c["title"]) for oid, ot in s["topics"].items() if oid != tid
             for c in ot["concepts"].values() if c["status"] in SOLID and c["next_review"] and c["next_review"] <= d]
    if other:
        print("\nDUE IN OTHER TOPICS (mention to the learner, do not switch unasked): "
              + "; ".join(f"{a}: {b}" for a, b in other))
    last = next((h for h in reversed(s["history"]) if tid in h.get("topics", [])), None)
    if last:
        print(f"\nLAST SESSION {last['date']}: {last['correct']} correct, {last['wrong']} wrong, {last['idk']} I don't know. "
              f"Next for this topic: {last.get('next_by_topic', {}).get(tid) or last.get('next_time') or '-'}")
    print()


def concept_table(t):
    rows = ["| Concept | Id | Status | In a row | Level | Box | Next review | Builds on |",
            "| --- | --- | --- | --- | --- | --- | --- | --- |"]
    for cid, c in t["concepts"].items():
        rows.append(f"| {c['title']} | {cid} | {c['status']} | {c['streak']} | {c['level']} | {c['box']} | "
                    f"{c['next_review'] or '-'} | {', '.join(t['concepts'][p]['title'] for p in c['prereqs']) or '-'} |")
    return "\n".join(rows)


def parse_concept(spec, brief):
    """A plan concept is an id from the brief; 'id|Title|prereqs' may override title/prereqs."""
    parts = [x.strip() for x in spec.split("|")]
    cid = slug(parts[0])
    if cid not in brief["concepts"]:
        raise LearnError(f"Concept {cid!r} is not in the research brief. Brief ids: {', '.join(brief['concepts'])}. "
                         "Plan from the brief, or add it to the brief and re-save it.")
    b = brief["concepts"][cid]
    title = parts[1] if len(parts) > 1 and parts[1] else b["title"]
    prereqs = ([slug(p) for p in parts[2].split(",") if p.strip()] if len(parts) > 2 else b["prereqs"])
    return cid, title, prereqs


def add_concept(t, cid, title, prereqs):
    for p in prereqs:
        if p not in t["concepts"]:
            raise LearnError(f"Prerequisite {p!r} of {cid!r} is not a concept yet. Define prerequisites first.")
    if cid in t["concepts"]:
        t["concepts"][cid].update(title=title, prereqs=prereqs)
    else:
        t["concepts"][cid] = new_concept(title, prereqs)


def write_map(s, t):
    lines = ["## Plan", "", f"Goal: {t['goal'] or '-'}", "", "```mermaid", "graph TD"]
    for cid, c in t["concepts"].items():
        lines.append(f'  {cid.replace("-", "_")}["{c["title"]}"]')
        for p in c["prereqs"]:
            lines.append(f'  {p.replace("-", "_")} --> {cid.replace("-", "_")}')
    lines += ["```", "", "Arrows point from an idea to the ideas built on it. We go top to bottom."]
    rel = render_canvas(s, need_session(s)["topic"])
    if rel:
        lines += ["", "Live progress map (colours change as you learn):", "", f"![[{rel}]]"]
    append(s, "\n".join(lines))


def cmd_plan(s, a):
    t = topic_of(s)
    brief = brief_of(s)
    if a.known is None:
        raise LearnError("Pass --known: the ids of concepts the learner said they already know "
                         "(they get a quick check instead of teaching), or --known none.")
    specs = [parse_concept(x, brief) for x in a.concept]
    chosen = {x[0] for x in specs} | set(t["concepts"])
    for cid, _, prereqs in specs:
        for pr in prereqs:
            if pr not in chosen:
                raise LearnError(f"{cid!r} builds on {pr!r}, which is not in the plan. Add --concept {pr} "
                                 "(or mark it --known if the learner knows it).")
    if len(specs) > MAX_PLAN:
        raise LearnError(f"Keep the plan small: at most {MAX_PLAN} concepts. Add more later with `learn add`.")
    if a.goal:
        t["goal"] = a.goal
    elif brief["goal"]:
        t["goal"] = brief["goal"]
    order = []
    while len(order) < len(specs):  # prerequisites first, so add_concept sees them
        progress = False
        for sp in specs:
            if sp not in order and all(pr in t["concepts"] or pr in [o[0] for o in order] for pr in sp[2]):
                order.append(sp)
                progress = True
        if not progress:
            raise LearnError("The plan's prerequisites form a loop. Fix 'Builds on' in the brief.")
    for cid, title, prereqs in order:
        add_concept(t, cid, title, prereqs)
    for k in [x.strip() for x in a.known.split(",") if x.strip() and x.strip().lower() != "none"]:
        c = concept(s, slug(k))
        if c["status"] == "new":
            c["status"] = "claimed"
    write_map(s, t)
    need_session(s)["step"] = None
    print_next(s, f"Plan saved with {len(t['concepts'])} concepts and drawn into the note.")


def cmd_research(s, a):
    t = topic_of(s)
    if not a.save:
        r = t.get("research")
        print(f"Research brief: {r['note']} (saved {r['date']})" if r else "No research brief yet for this topic.")
        print("\nTEMPLATE (fill every section; cite sources as [S1]; pipe the result to `learn research --save`):\n")
        print(BRIEF_TEMPLATE)
        print_next(s)
        return
    text = sys.stdin.read().strip()
    brief, errs = parse_brief(text)
    if errs:
        raise LearnError("Brief rejected. Fix and re-save:\n- " + "\n- ".join(errs))
    rel = f"{SOURCES_DIR}/{t['title']} research brief.md"
    (VAULT / SOURCES_DIR).mkdir(parents=True, exist_ok=True)
    (VAULT / rel).write_text(text + "\n")
    t["research"] = {"note": rel, "date": iso(today()), "sources": len(brief["sources"])}
    if brief["goal"]:
        t["goal"] = brief["goal"]
    if s["session"]:
        append(s, f"> [!info] Research brief\n> Everything taught in this topic comes from [[{rel[:-3]}]] "
                  f"({len(brief['sources'])} sources). Facts carry their source id, like [S1].")
    print_next(s, f"Brief saved to {rel}: {len(brief['concepts'])} concepts, {len(brief['sources'])} sources.")


def cmd_lit(s, a):
    """PRAXIST no-key literature lookup (praxist.plugins.tools.literature_lookup)."""
    try:
        from praxist.plugins.tools.literature_lookup import adapter as lit
    except ImportError:
        raise LearnError("PRAXIST is not installed. Run `scripts/install.sh` (or `python3 -m pip install "
                         "praxist==0.5.0 httpx`). Until then use web search for sources.")
    arg = " ".join(a.args).strip()
    if a.action == "guide":
        r = lit.literature_source_guide(arg or "generic", a.objective or "")
        print(f"Domain: {r['domain']}\nRecommended sources: {'; '.join(r['recommended_sources'])}")
        print("Checks:\n- " + "\n- ".join(r["verification_checks"]))
        return
    if not arg:
        raise LearnError(f"`learn lit {a.action}` needs a query or identifier.")
    if a.action in ("search", "db"):
        fn = lit.literature_search if a.action == "search" else lit.scientific_database_search
        r = fn(arg, a.sources, a.max)
        if r.get("error"):
            raise LearnError(r["error"])
        print(f"{r['result_count']} results for {arg!r} (literature signal: screen for relevance, then open the best).")
        for i, x in enumerate(r["results"], 1):
            ident = x.get("doi") or x.get("url") or ""
            oa = " [open access]" if x.get("is_open_access") else ""
            print(f"\n[{i}] {x.get('title')} ({x.get('year') or '?'}) {x.get('source')}{oa}\n    {ident}")
            if x.get("abstract"):
                print(f"    {str(x['abstract'])[:300]}")
        for w in r.get("warnings") or []:
            print(f"warning: {w}")
        return
    if a.action == "resolve":
        r = lit.literature_resolve(arg)
        print(json.dumps(r.get("record") or r, indent=2, ensure_ascii=False)[:3000])
        return
    r = lit.literature_open_access_text(arg, a.chars)
    if r.get("error"):
        raise LearnError(f"{r['error']} (not open access? read the abstract via `learn lit resolve`, or use web search)")
    print(json.dumps({k: r[k] for k in r if k not in ("text", "resource_policy")}, ensure_ascii=False)[:800])
    print("\n" + str(r.get("text") or "")[: a.chars])


def cmd_known(s, a):
    cid = slug(a.concept)
    c = concept(s, cid)
    sess = need_session(s)
    waiting = [q for q, p in sess["pending"].items() if p["concept"] == cid]
    if waiting:
        if c["status"] not in SOLID:
            c["status"] = "claimed"
        print(f"WHY: {', '.join(waiting)} already checks '{c['title']}'. Right answer = it counts as solid.")
        print(f"NEXT: Tell the learner in ONE line: \"Then {waiting[0]} should be quick. Answer it in the note "
              f"and we move on.\" Then wait and run `learn check`.")
        return
    if c["status"] in SOLID:
        print_next(s, f"'{c['title']}' is already {c['status']}.")
        return
    if sess["step"] and sess["step"]["concept"] == cid:
        sess["step"] = None
    if c["history"] and c["history"][-1]["result"] == "correct" and c["history"][-1]["date"] == iso(today()):
        d = today()
        c.update(status="solid", taught=True, box=1, solid_date=iso(d), promoted=iso(d),
                 next_review=iso(d + timedelta(days=1)))
        print_next(s, f"'{c['title']}': said known and just answered correctly, so it is solid. Review tomorrow.")
        return
    c["status"] = "claimed"
    render_canvas(s, sess["topic"])
    print_next(s, f"Marked '{c['title']}' as known. One quick check, then we skip it.")


def cmd_add(s, a):
    t = topic_of(s)
    cid = slug(a.id)
    prereqs = [p.strip() for p in (a.prereqs or "").split(",") if p.strip()]
    add_concept(t, cid, " ".join(a.title), prereqs)
    if a.before:
        target = concept(s, slug(a.before))
        if cid not in target["prereqs"]:
            target["prereqs"].append(cid)
        sess = need_session(s)
        if sess["step"] and sess["step"]["concept"] == slug(a.before):
            sess["stack"].append(slug(a.before))
        sess["step"] = step("teach", cid, f"'{t['concepts'][cid]['title']}' is the smaller step under "
                                          f"'{target['title']}'. Teach it first.")
    render_canvas(s, need_session(s)["topic"])
    print_next(s, f"Added '{t['concepts'][cid]['title']}'.")


def save_figure(s, name, out, kind):
    sess = need_session(s)
    rel = f"{FIG_DIR}/{sess['topic']}/{name}{out.suffix}"
    dest = VAULT / rel
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(out.read_bytes())
    s.setdefault("figures", {})[rel] = kind
    print(f"Figure saved: {rel} ({kind})")
    print(f"EMBED: ![[{rel}]]")
    print("NEXT: Put the EMBED line in the theory block (or in a question's \"figure\" field), with text that "
          "walks through it using the numbered marks, then run `learn block <concept>`.")


def strip_ansi(text):
    return re.sub(r"\x1b\[[0-9;]*[A-Za-z]", "", text)


def render_manim(s, name, script, still, tmp):
    sess = need_session(s)
    old = [fix for pat, fix in OLD_MANIM_API if re.search(pat, script)]
    if old:
        raise LearnError("This is old 3Blue1Brown/ManimGL code. Rewrite it for Manim Community "
                         "(references/visuals.md):\n- " + "\n- ".join(old))
    if not MANIM.exists():
        raise LearnError(f"Manim is not installed at {MANIM}. Run `scripts/install.sh`.")
    (tmp / "figure.py").write_text(script)
    (tmp / "harness.py").write_text(MANIM_HARNESS)
    report = tmp / "report.json"
    env = dict(os.environ, LEARN_FIG_SCRIPT=str(tmp / "figure.py"), LEARN_FIG_REPORT=str(report),
               PATH=f"{TEX_BIN}{os.pathsep}{os.environ.get('PATH', '')}")
    cmd = [str(MANIM), "-s" if still else "-qm", "--disable_caching", "--media_dir", str(tmp / "media"),
           "-o", "out", str(tmp / "harness.py"), "LearnChecked"]
    if still:
        cmd.insert(2, "-qm")
    try:
        r = subprocess.run(cmd, cwd=tmp, env=env, capture_output=True, text=True, timeout=MANIM_TIMEOUT)
    except subprocess.TimeoutExpired:
        raise LearnError(f"Manim ran longer than {MANIM_TIMEOUT}s. Shorten the scene (5-20 s of animation) or "
                         "use fewer objects.")
    log = strip_ansi(r.stdout + "\n" + r.stderr)
    if r.returncode != 0:
        lines = [l.rstrip() for l in log.splitlines() if l.strip() and not set(l.strip()) <= set("─│╭╮╰╯ ")]
        latex = "LaTeX" in log or "latex" in log
        tex_errs = [l.strip() for f in (tmp / "media").rglob("*.log") for l in f.read_text(errors="ignore").splitlines()
                    if l.startswith("!") or l.startswith("l.")][:6]
        hint = ("\nLaTeX said:\n" + "\n".join(tex_errs) if tex_errs else "") + (
            "\nHint: a LaTeX error. Check the MathTex/Tex string: every { has a }, use raw strings r\"...\", "
            "and put plain words in Text(), not MathTex()." if latex else "")
        raise LearnError("Manim failed. Fix the scene and re-run:\n" + "\n".join(lines[-14:]) + hint)
    problems = json.loads(report.read_text()) if report.exists() else []
    if problems:
        raise LearnError("Text in the animation is hard to read. Move it with .next_to(...)/.to_edge(...)/"
                         "VGroup(...).arrange(...), shrink it, or FadeOut old text first. Then re-run:\n- "
                         + "\n- ".join(problems[:8]))
    found = list((tmp / "media").rglob("out.png" if still else "out.mp4"))
    if not found:
        raise LearnError("Manim produced no " + ("image" if still else "video") + ". Does construct() add or "
                         "animate anything?")
    out = found[0]
    if out.stat().st_size > VIDEO_MAX_BYTES:
        raise LearnError(f"The video is {out.stat().st_size // 1_000_000} MB; the limit is "
                         f"{VIDEO_MAX_BYTES // 1_000_000} MB. Shorten it.")
    if not still and shutil.which("ffprobe"):
        d = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(out)],
                           capture_output=True, text=True).stdout.strip()
        try:
            secs = float(d)
        except ValueError:
            secs = None
        if secs is not None and not VIDEO_SECONDS[0] <= secs <= VIDEO_SECONDS[1]:
            raise LearnError(f"The animation lasts {secs:.1f}s; keep it between {VIDEO_SECONDS[0]} and "
                             f"{VIDEO_SECONDS[1]} s (add self.wait() or shorten run_time).")
    return out


def render_matplotlib(script, tmp):
    (tmp / "figure.py").write_text(script)
    (tmp / "harness.py").write_text(FIG_HARNESS)
    png, gif = tmp / "out.png", tmp / "out.gif"
    try:
        r = subprocess.run([sys.executable, str(tmp / "harness.py"), str(png), str(gif), str(tmp / "figure.py")],
                           cwd=tmp, capture_output=True, text=True, timeout=FIG_TIMEOUT)
    except subprocess.TimeoutExpired:
        raise LearnError(f"Figure script ran longer than {FIG_TIMEOUT}s. Use fewer frames or less data.")
    if r.returncode != 0:
        tail = "\n".join(r.stderr.strip().splitlines()[-8:])
        raise LearnError(f"Figure script failed. Fix it and re-run:\n{tail}")
    check = next((l for l in r.stdout.splitlines() if l.startswith("LEARN-CHECK ")), None)
    problems = json.loads(check[len("LEARN-CHECK "):]) if check else []
    if problems:
        raise LearnError("Labels collide (with each other or with a plotted line), so the picture would be hard to "
                         "read. Move or shorten them and re-run:\n- " + "\n- ".join(problems[:8]))
    made = [f for f in (png, gif) if f.exists()]
    if len(made) != 1:
        raise LearnError("The script must save exactly one file: `fig.savefig(OUT_PNG, dpi=110, "
                         "bbox_inches=\"tight\")` for a picture, or `anim.save(OUT_GIF, writer=PillowWriter(fps=2))` "
                         "for an animation.")
    out = made[0]
    if out.stat().st_size > FIG_MAX_BYTES:
        raise LearnError(f"{out.suffix} is {out.stat().st_size // 1000} KB; the limit is {FIG_MAX_BYTES // 1000} KB. "
                         "Lower dpi, size or frame count.")
    if out.suffix == ".gif":
        from PIL import Image
        with Image.open(out) as im:
            if getattr(im, "n_frames", 1) < 2:
                raise LearnError("The GIF has one frame. Use a PNG for a still picture, or add frames.")
    return out


def manim_required():
    return os.environ.get("LEARN_REQUIRE_MANIM", "1") != "0"


def cmd_figure(s, a):
    import tempfile
    sess = need_session(s)
    name = slug(a.name)
    script = sys.stdin.read()
    if not script.strip():
        raise LearnError("Empty figure script. Pipe a Manim scene on stdin (templates: references/visuals.md).")
    is_manim = bool(re.search(r"^\s*(from|import)\s+manim", script, re.M))
    fails = sess.get("manim_failures", 0)
    if not is_manim and manim_required() and fails < MANIM_FALLBACK_AFTER:
        raise LearnError("Manim is the visual tool for this learner (3Blue1Brown style). Write a Manim Community "
                         "scene: `from manim import *`, one `class X(Scene)` with construct() (templates: "
                         f"references/visuals.md). matplotlib unlocks only after {MANIM_FALLBACK_AFTER} failed Manim "
                         f"attempts in a row (now {fails}).")
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        if is_manim:
            try:
                out = render_manim(s, name, script, a.still, tmp)
            except LearnError:
                sess["manim_failures"] = fails + 1
                left = MANIM_FALLBACK_AFTER - sess["manim_failures"]
                print(f"(Manim attempt failed {sess['manim_failures']} time(s) in a row"
                      + (f"; matplotlib fallback unlocks after {left} more)" if left > 0 else
                         "; matplotlib fallback is now unlocked if you need it)"))
                save(s)
                raise
            sess["manim_failures"] = 0
            save_figure(s, name, out, "manim")
        else:
            out = render_matplotlib(script, tmp)
            save_figure(s, name, out, "matplotlib")


def cmd_block(s, a):
    cid = slug(a.concept)
    c = concept(s, cid)
    sess = need_session(s)
    if sess["pending"]:
        raise LearnError(f"{', '.join(sess['pending'])} still waiting for an answer. Run `learn check` first.")
    md = sys.stdin.read().strip()
    if not md:
        raise LearnError("Empty block. Pipe the theory markdown on stdin.")
    brief = brief_of(s)
    cited = list(dict.fromkeys(CITE.findall(md)))
    if not cited:
        raise LearnError("Cite the research brief: put the source id after the facts it supports, like [S1]. "
                         f"Sources in the brief: {', '.join(brief['sources'])}.")
    unknown = [x for x in cited if x not in brief["sources"]]
    if unknown:
        raise LearnError(f"{', '.join(unknown)} not in the research brief. Brief sources: {', '.join(brief['sources'])}.")
    figs = FIG_EMBED.findall(md)
    missing = [f for f in figs if not (VAULT / f).exists()]
    if missing:
        raise LearnError(f"Embedded figure not found: {', '.join(missing)}. Make it with `learn figure <name>` "
                         "and paste the embed line it prints.")
    kinds = s.get("figures", {})
    has_manim = any(kinds.get(f) == "manim" for f in figs)
    fallback = sess.get("manim_failures", 0) >= MANIM_FALLBACK_AFTER or not manim_required()
    if not has_manim and not (fallback and (figs or MERMAID.search(md))):
        raise LearnError("Every block needs a Manim visual of how it works (learner preference, 3Blue1Brown "
                         "style). Make one with `learn figure <name>` (a Manim scene; references/visuals.md) and "
                         "paste the EMBED line. Mermaid can be added for structure, but does not replace it. "
                         "Then re-run `learn block`.")
    merr, unchecked = mermaid_problems(md)
    if merr:
        raise LearnError("Mermaid would not render in Obsidian. Fix it and re-run:\n- " + "\n- ".join(merr))
    words = len(re.sub(r"\$\$.*?\$\$|```.*?```", " ", md, flags=re.S).split())
    if words > MAX_BLOCK_WORDS:
        raise LearnError(f"Block is {words} words; the limit is {MAX_BLOCK_WORDS}. Cut it to one idea and re-run.")
    sess["blocks"] += 1
    c["taught"] = True
    if c["status"] == "new":
        c["status"] = "learning"
    key = f"{sess['topic']}/{cid}"
    sess["touched"].setdefault(key, sess["start_status"].get(key, "new"))
    refs = "\n".join(f"> {x}: {brief['sources'][x]['source']} ({brief['sources'][x]['type']})" for x in cited)
    append(s, f"## {sess['blocks']}. {c['title']}\n\n{md}\n\n> [!quote]- Sources\n{refs}")
    prev = sess["step"]
    lvl = 1 if (prev and prev["action"] == "reteach") else c["level"]
    sess["step"] = step("ask", cid, f"Theory for '{c['title']}' is in the note. Now active recall on it.", lvl)
    render_canvas(s, sess["topic"])
    print_next(s, "Block written to the note." + (f" ({unchecked} mermaid diagram(s) not checked: Obsidian not "
                                                    "reachable; open the note to confirm it renders.)" if unchecked else ""))


def cmd_ask(s, a):
    cid = slug(a.concept)
    c = concept(s, cid)
    sess = need_session(s)
    if not c["taught"] and c["status"] != "claimed":
        raise LearnError(f"'{c['title']}' has not been taught yet. Teach it first with `learn block {cid}`. "
                         "Learner rule: questions only on what was taught.")
    if len(sess["pending"]) >= 2:
        raise LearnError("Two questions are already waiting. Run `learn check` after the learner answers.")
    try:
        q = json.loads(sys.stdin.read())
    except json.JSONDecodeError as e:
        raise LearnError(f"Question must be JSON on stdin: {e}")
    kind = q.get("type")
    for field in ("question", "why"):
        if not str(q.get(field, "")).strip():
            raise LearnError(f"Question JSON needs a non-empty {field!r}.")
    level = int(q.get("level") or (sess["step"] or {}).get("level") or c["level"])
    if level not in LEVELS:
        raise LearnError("level must be 1, 2 or 3.")
    sess["qn"] += 1
    qid = f"Q{sess['qn']}"
    p = {"concept": cid, "type": kind, "level": level, "why": q["why"].strip(), "question": q["question"].strip()}
    out = [f"### {qid} · level {level}", "", q["question"].strip(), ""]
    fig = str(q.get("figure") or "").strip()
    if fig:
        m = FIG_EMBED.fullmatch(fig) or FIG_EMBED.fullmatch(f"![[{fig}]]")
        if not m or not (VAULT / m.group(1)).exists():
            raise LearnError(f"\"figure\" must be an embed printed by `learn figure`, got {fig!r}.")
        out[3:3] = ["", f"![[{m.group(1)}]]"]
        p["figure"] = m.group(1)
    if kind == "choice":
        opts = q.get("options") or []
        if not 2 <= len(opts) <= 5:
            raise LearnError("A choice question needs 2-5 options (I don't know is added automatically).")
        if sum(bool(o.get("correct")) for o in opts) != 1:
            raise LearnError("Exactly one option must have \"correct\": true.")
        for o in opts:
            if not o.get("correct") and not str(o.get("misconception", "")).strip():
                raise LearnError(f"Wrong option {o.get('text')!r} needs a \"misconception\": the wrong belief that leads to it.")
        opts = list(opts)
        random.Random(f"{sess['date']}{qid}{cid}").shuffle(opts)
        letters = "ABCDEF"
        p["options"] = {letters[i]: o["text"].strip() for i, o in enumerate(opts)}
        p["misconceptions"] = {letters[i]: o.get("misconception", "") for i, o in enumerate(opts)}
        p["correct"] = next(letters[i] for i, o in enumerate(opts) if o.get("correct"))
        p["idk"] = letters[len(opts)]
        out += [f"- [ ] {L}. {txt}" for L, txt in p["options"].items()]
        out.append(f"- [ ] {p['idk']}. I don't know")
    elif kind == "typed":
        if not str(q.get("answer", "")).strip():
            raise LearnError("A typed question needs \"answer\": what a good answer must contain.")
        p["answer"] = q["answer"].strip()
        out += ["**Your answer** (type below this line):", ""]
    else:
        raise LearnError("\"type\" must be \"choice\" or \"typed\".")
    out.append(f"%% {qid} end %%")
    prev = current_step(s)
    label = {"review": f"> [!question] Review: '{c['title']}', last seen {c['last_seen']}. No theory first: this checks memory.",
             "check": f"> [!question] Quick check: you said you know '{c['title']}'. Right answer = we skip the lesson."
             }.get(prev.get("action") if prev.get("concept") == cid else None)
    if label:
        out = [label, ""] + out
    sess["pending"][qid] = p
    sess["step"] = None
    append(s, "\n".join(out))
    notice(f"{qid} is ready in your session note")
    print(f"{qid} written to the note.")
    print("WHY: " + ("Spaced review: remembering on a later day is what makes it stick." if label and "Review" in label
                      else "A quick check instead of a lesson." if label else "Active recall right after the theory."))
    print(f"NEXT: Tell the learner in ONE line: \"{qid} is in the note. Answer there, then send any message.\" "
          "Then STOP and wait. When they reply, run `learn check`.")


def read_answer(s, qid, p):
    lines = note_lines(s)
    head, end = q_span(lines, qid)
    if p["type"] == "choice":
        picked = [m.group(2) for l in lines[head:end] if (m := re.match(r"^\s*- \[(?!\s\])(.)\] ([A-F])\.", l))]
        return picked
    start = next((i for i in range(head, end) if lines[i].startswith("**Your answer**")), None)
    return "\n".join(lines[start + 1:end]).strip() if start is not None else ""


def cmd_check(s, a):
    sess = need_session(s)
    if not sess["pending"]:
        print_next(s, "Nothing is waiting for an answer.")
        return
    for qid, p in list(sess["pending"].items()):
        ans = read_answer(s, qid, p)
        if p["type"] == "choice":
            if not ans:
                print(f"{qid}: no box ticked yet.")
                continue
            if len(ans) > 1:
                print(f"{qid}: {len(ans)} boxes ticked ({', '.join(ans)}). Ask the learner to keep only one.")
                continue
            pick = ans[0]
            result = "idk" if pick == p["idk"] else ("correct" if pick == p["correct"] else "wrong")
            reason = grade(s, qid, result, what=p["misconceptions"].get(pick, ""), picked=pick)
            print(f"{qid}: learner picked {pick} -> {result}. {reason}")
        else:
            if not ans:
                print(f"{qid}: nothing typed under 'Your answer' yet.")
                continue
            print(f"{qid} (typed) learner wrote: {ans!r}\n  A good answer must contain: {p['answer']}")
            print(f"NEXT: Judge the meaning, not the wording. Run `learn grade {qid} correct` if the key idea is "
                  f"there, or `learn grade {qid} wrong --kind slip|gap|misconception --what \"<the wrong belief>\"`. "
                  f"If the learner wrote that they don't know, run `learn grade {qid} idk`.")
            save(s)
            return
    if sess["pending"]:
        print("WHY: Some answers are missing.")
        print("NEXT: Ask the learner in ONE line to answer in the note (tick one box / type under Your answer), "
              "or to tell you in chat. Then wait.")
        return
    print_next(s)


def cmd_answer(s, a):
    sess = need_session(s)
    qid = a.qid.upper()
    if qid not in sess["pending"]:
        raise LearnError(f"{qid} is not waiting for an answer. Waiting: {', '.join(sess['pending']) or 'none'}.")
    p = sess["pending"][qid]
    lines = note_lines(s)
    head, end = q_span(lines, qid)
    if p["type"] == "choice":
        letter = (a.choice or "").strip().upper().rstrip(").")
        if letter in ("IDK", "?", "E?") or "DON" in letter:
            letter = p["idk"]
        valid = list(p["options"]) + [p["idk"]]
        if letter not in valid:
            raise LearnError(f"Answer must be one of {', '.join(valid)}.")
        for i in range(head, end):
            if re.match(rf"^\s*- \[.\] {letter}\.", lines[i]):
                lines[i] = re.sub(r"\[.\]", "[x]", lines[i], count=1)
    else:
        if not a.text:
            raise LearnError(f"{qid} is a typed question. Use `learn answer {qid} --text \"...\"`.")
        lines[end:end] = [a.text.strip()]
    write_lines(s, lines)
    cmd_check(s, a)


def cmd_grade(s, a):
    sess = need_session(s)
    qid = a.qid.upper()
    if qid not in sess["pending"]:
        raise LearnError(f"{qid} is not waiting for a grade.")
    if sess["pending"][qid]["type"] != "typed":
        raise LearnError(f"{qid} is multiple choice; `learn check` grades it automatically.")
    reason = grade(s, qid, a.result, kind=a.kind, what=a.what or "")
    print(f"{qid}: {a.result}. {reason}")
    if sess["pending"]:
        print("NEXT: Run `learn check` for the other waiting question.")
        return
    print_next(s)


def cmd_next(s, a):
    print_next(s)


def cmd_pref(s, a):
    text = " ".join(a.text).strip()
    if text and text not in s["profile"]["preferences"]:
        s["profile"]["preferences"].append(text)
    print(f"Saved. {len(s['profile']['preferences'])} preferences now apply to every session.")


def finish(s, why_line):
    sess = s["session"]
    d = sess["date"]
    for qid in list(sess["pending"]):
        insert_after(s, qid, f"> [!warning] {qid}: not answered this session. It will come back.")
    unanswered = list(sess["pending"])
    sess["pending"] = {}
    # The engine decides what comes next per topic; the agent's line is only a note on top.
    nbt = {}
    current = sess["topic"]
    for tid in sess.get("topics", [current]):
        sess["topic"], sess["step"] = tid, (sess["step"] if tid == current else None)
        st = current_step(s)
        c = s["topics"][tid]["concepts"].get(st["concept"]) if st["concept"] else None
        nbt[tid] = f"Start with '{c['title']}': {st['reason']}" if c else st["reason"]
    sess["topic"] = current
    if sess.get("next_time"):
        nbt[current] += f" Note: {sess['next_time']}"
    rows = ["| Concept | Before | Now | Next review |", "| --- | --- | --- | --- |"]
    for key, before in sess["touched"].items():
        tid, cid = key.split("/", 1)
        c = s["topics"][tid]["concepts"][cid]
        rows.append(f"| {c['title']} | {before} | {c['status']} | {c['next_review'] or '-'} |")
    opened = [m for m in s["mistakes"] if m["date"] == d and not m["closed"]]
    closed = [m for m in s["mistakes"] if m["closed"] == d]
    cnt = sess["counts"]
    text = ["## Summary", "", f"> [!abstract] {why_line}",
            f"> {cnt.get('correct', 0)} correct, {cnt.get('wrong', 0)} wrong, {cnt.get('idk', 0)} I don't know. "
            f"Mistakes opened: {len(opened)}, closed: {len(closed)}."]
    if unanswered:
        text.append(f"> Unanswered: {', '.join(unanswered)}.")
    text += ["", *rows, "", "> [!note] Next time"]
    text += [f"> **{s['topics'][tid]['title']}:** {line}" for tid, line in nbt.items()]
    append(s, "\n".join(text))
    set_props(s, status="done")
    s["history"].append({"date": d, "topics": sess.get("topics", [current]), "note": sess["note"],
                         "correct": cnt.get("correct", 0), "wrong": cnt.get("wrong", 0), "idk": cnt.get("idk", 0),
                         "next_time": sess.get("next_time"), "next_by_topic": nbt})
    note = sess["note"]
    s["session"] = None
    render_dashboard(s)
    return note


def cmd_end(s, a):
    sess = need_session(s)
    if a.next_time:
        sess["next_time"] = a.next_time
    note = finish(s, "Session finished.")
    save(s)
    commit(f"learn: session {sess['date']} {', '.join(sess.get('topics', [sess['topic']]))}")
    print(f"Session closed. Summary written to {note}. Dashboard: {DASHBOARD}")
    print("NEXT: Tell the learner in 2 lines what is solid now and what next session starts with "
          "(read it from the 'Next time' lines in the summary). Then stop.")


def cmd_status(s, a):
    print(dashboard_text(s))


def dashboard_text(s):
    d = iso(today())
    out = ["# Learner dashboard", "", f"Generated by learn.py on {d}. Do not edit: it is rebuilt after every session.", "",
           "## How I like to learn"] + [f"- {p}" for p in s["profile"]["preferences"]]
    for tid, t in s["topics"].items():
        out += ["", f"## {t['title']}", "", f"Goal: {t['goal'] or '-'}", ""]
        if t["concepts"]:
            out.append(concept_table(t))
        due = [c["title"] for c in t["concepts"].values() if c["next_review"] and c["next_review"] <= d]
        if due:
            out += ["", f"Due for review: {', '.join(due)}"]
    open_m = [m for m in s["mistakes"] if not m["closed"]]
    if open_m:
        out += ["", "## Open mistakes", "", "| Date | Topic | Concept | Kind | What |", "| --- | --- | --- | --- | --- |"]
        for m in open_m:
            t = s["topics"][m["topic"]]
            out.append(f"| {m['date']} | {t['title']} | {t['concepts'][m['concept']]['title']} | {m['kind']} | {m['what']} |")
    return "\n".join(out) + "\n"


def render_dashboard(s):
    path = VAULT / DASHBOARD
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(dashboard_text(s))


def commit(msg):
    if os.environ.get("LEARN_NO_GIT"):
        return
    try:
        subprocess.run(["git", "-C", str(REPO), "add", str(STATE)], check=True, capture_output=True)
        r = subprocess.run(["git", "-C", str(REPO), "commit", "-m", msg, "--", str(STATE)], capture_output=True, text=True)
        if r.returncode != 0 and "nothing to commit" not in r.stdout:
            print(f"warning: git commit failed: {r.stderr.strip() or r.stdout.strip()}")
    except (OSError, subprocess.CalledProcessError) as e:
        print(f"warning: git commit skipped: {e}")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("start"); p.add_argument("topic", nargs="+")
    p = sub.add_parser("research"); p.add_argument("--save", action="store_true")
    p = sub.add_parser("lit"); p.add_argument("action", choices=["search", "db", "resolve", "text", "guide"])
    p.add_argument("args", nargs="*"); p.add_argument("--sources"); p.add_argument("--max", type=int, default=6)
    p.add_argument("--chars", type=int, default=6000); p.add_argument("--objective")
    p = sub.add_parser("plan"); p.add_argument("--goal"); p.add_argument("--concept", action="append", default=[])
    p.add_argument("--known")
    p = sub.add_parser("known"); p.add_argument("concept")
    p = sub.add_parser("add"); p.add_argument("id"); p.add_argument("title", nargs="+")
    p.add_argument("--prereqs"); p.add_argument("--before")
    p = sub.add_parser("figure"); p.add_argument("name"); p.add_argument("--still", action="store_true")
    p = sub.add_parser("block"); p.add_argument("concept")
    p = sub.add_parser("ask"); p.add_argument("concept")
    sub.add_parser("check")
    p = sub.add_parser("answer"); p.add_argument("qid"); p.add_argument("choice", nargs="?"); p.add_argument("--text")
    p = sub.add_parser("grade"); p.add_argument("qid"); p.add_argument("result", choices=["correct", "wrong", "idk"])
    p.add_argument("--kind", choices=["slip", "gap", "misconception"]); p.add_argument("--what")
    sub.add_parser("next")
    p = sub.add_parser("pref"); p.add_argument("text", nargs="+")
    p = sub.add_parser("end"); p.add_argument("--next-time")
    sub.add_parser("status")
    a = ap.parse_args(argv)
    s = load()
    try:
        globals()[f"cmd_{a.cmd}"](s, a)
    except LearnError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1
    if a.cmd != "lit":  # lookups never touch learner state
        save(s)
    return 0


if __name__ == "__main__":
    sys.exit(main())
