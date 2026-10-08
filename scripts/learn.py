#!/usr/bin/env python3
"""Learning-session engine: learner state, mastery rules, and the session note.

The agent runs one subcommand per step and follows the WHY/NEXT lines it prints.
The rules live here, not in the prompt, so every model gets the same decisions.

  start <topic...> [--exam <profile>]  begin or resume a session; --exam switches the topic to exam mode
  research [--save]                research gate: show the brief template / save a brief (stdin) for this topic
  lit search|resolve|text|guide|db ...   PRAXIST no-key literature lookup (OpenAlex, arXiv, Crossref, PubMed...)
  plan --concept id ... --known id,id|none   concepts come from the research brief
  known <concept>                  learner says they already know it -> quick check instead of teaching
  add <id> <title...> [--prereqs a,b] [--before c]
  figure <name> [--still|--silent] Manim scene on stdin -> checked, narrated MP4 (or PNG with --still) in the vault
                                   (narration = the scene's NARRATION list, spoken by a local Voicebox/Kokoro voice)
                                   (matplotlib is the fallback, unlocked after 3 failed Manim attempts in a row)
  block <concept>                  theory markdown (with a visual) on stdin -> session note
  ask <concept>                    question JSON on stdin -> session note
  check                            read answers from the note; grades choice questions
  answer <Q> <letter|idk> | answer <Q> --text T     learner answered in chat
  grade <Q> correct|wrong|idk [--kind slip|gap|misconception] [--what W]   typed answers
  next                             what to do now, and why
  pref <text...> [--topic]         save a learner preference (for every session, or only this topic)
  voice [id]                       show or set the narrator voice (Kokoro preset, e.g. af_heart)
  end [--next-time T]              summary into the note, dashboard, commit
  status                           what the system believes the learner knows

Env: LEARN_STATE, LEARN_VAULT, LEARN_TODAY (YYYY-MM-DD), LEARN_NO_CLI=1, LEARN_NO_GIT=1,
     LEARN_MANIM (manim binary), LEARN_TEX_BIN (TeX bin dir), LEARN_REQUIRE_MANIM=0 (accept any visual),
     LEARN_TTS=voicebox|fake|none, LEARN_VOICEBOX_URL, LEARN_VOICEBOX_DIR, LEARN_VOICEBOX_AUTOSTART=0.
"""

import argparse
import ast
import json
import os
import random
import re
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import wave
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
MAX_BLOCK_WORDS = 300            # one segment (or a single-concept block)
MAX_SEGMENTS = 4                  # a unit block holds 1-4 segments
MAX_PARAGRAPH_WORDS = 60          # longer prose must become a list, table or steps
MAX_PLAN = 12                     # concepts per `learn plan` call
MAX_UNIT_CONCEPTS = 5             # one unit = one schema, ~15-20 min
MAX_PENDING = 5                   # questions waiting at once (a unit check asks several)
SESSION_REVIEW_MAX = 5            # spaced-review questions at the start of a session
BAND = (0.70, 0.90)               # target success band over the last 10 graded answers (Rosenshine ~80%)
KEY_LENGTH_RATIO = 1.25           # key longer than 1.25x the mean distractor = length cue (Haladyna 2002)
STOPWORDS = set("that this with from what which when where there their they them then than have has had "
                "into over under about after before because while does done each other such only also more "
                "most some your will would could should these those being been were".split())
ABSOLUTES = re.compile(r"\b(always|never|all|none|only|every|completely|must|impossible)\b", re.I)
LEVELS = {1: "recall the idea just taught, in the same setting",
          2: "apply it to a new scenario the lesson did not use",
          3: "explain why it works, predict, or combine it with an earlier idea"}

SOURCES_DIR = "Sources"
FIG_DIR = "Attachments/learn"
FIG_MAX_BYTES = 3_000_000
FIG_TIMEOUT = 90
MANIM = Path(os.environ.get("LEARN_MANIM", Path.home() / ".local/share/learning-system/manim-venv/bin/manim"))
TEX_BIN = Path(os.environ.get("LEARN_TEX_BIN", Path.home() / "Library/TinyTeX/bin/universal-darwin"))
MANIM_TIMEOUT = 600
VIDEO_MAX_BYTES = 30_000_000
VIDEO_SECONDS = (2, 180)          # one scene = one segment; a unit uses 2-4 scenes (Guo 2014: <=3 min)
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
_marks = {}   # caption number -> [time it starts appearing, caption text]
_DUR = {int(k): v for k, v in json.loads(os.environ.get("LEARN_VOICE_DUR") or "{}").items()}
_vmarks = {}  # narration line -> time its voice block starts (audio-first sync)
from contextlib import contextmanager as _cm
import re as _re
_NUM = _re.compile(r"^\s*(\d{1,2})[\s.):]")

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

def _note_marks(mobs, t):
    for m in _texts([x for x in mobs if x is not None]):
        txt = getattr(m, "original_text", None) or getattr(m, "text", None) or ""
        hit = _NUM.match(txt)
        if hit and int(hit.group(1)) not in _marks:
            _marks[int(hit.group(1))] = [round(t, 3), txt.strip()]

class LearnChecked(_found[0]):
    @_cm
    def voice(self, i):
        # narration line i (1-based) is spoken from here; the block lasts at least as long as the line
        t0 = self.renderer.time
        _vmarks.setdefault(int(i), round(t0, 3))
        yield _DUR.get(int(i), 0.0)
        rest = _DUR.get(int(i), 0.0) - (self.renderer.time - t0)
        if rest > 0.02:
            self.wait(rest)
    def add(self, *mobs):
        _note_marks(mobs, self.renderer.time)
        return super().add(*mobs)
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
        t0 = self.renderer.time
        _note_marks([getattr(a, "target_mobject", None) or getattr(a, "mobject", None) for a in args], t0)
        super().play(*args, **kwargs)
        self._learn_check()
    def wait(self, *args, **kwargs):
        super().wait(*args, **kwargs)
        self._learn_check()
    def construct(self):
        super().construct()
        self._learn_check()
        json.dump({"problems": list(dict.fromkeys(_problems)), "marks": _marks, "voice": _vmarks},
                  open(os.environ["LEARN_FIG_REPORT"], "w"))
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
EXAM_SOURCE_TYPES = {"syllabus", "past-paper", "mark-scheme", "examiner-report"}
SOURCE_TYPES = {"primary", "textbook", "review", "secondary", "vendor"} | EXAM_SOURCE_TYPES
STRONG_TYPES = {"primary", "textbook", "review", "syllabus", "past-paper", "mark-scheme"}
EXAMS_DIR = REPO / "skills" / "teach-understanding" / "exams"
EXAM_SECTIONS = ["Syllabus points", "Paper patterns", "Examiner-report errors"]
EXAM_TEMPLATE = """
## Syllabus points
- <code, e.g. 1.2.2>: <the learning outcome, quoted from the syllabus> [S1]

## Paper patterns
| Id | Syllabus point | Pattern | Command words | Marks | Real questions | Mark scheme |
| --- | --- | --- | --- | --- | --- | --- |
| P1 | 1.2.2 | <stem shape + data given> | Determine, Show that | 2-3 | <2+ citations, e.g. 9702/21/M/J/23 Q1(b); 9702/22/F/M/24 Q1(b)> | <C1 ..., A1 ...> |

## Examiner-report errors
- <citation>: "<quoted common error>" (<frequency: majority / significant number / few>) [S3]
"""
MIN_SOURCES = 3
CITE = re.compile(r"\[(S\d+)\]")
BRIEF_TEMPLATE = """# Research brief: <Topic>

Goal: <what the learner wants to be able to do, from their reply>
Domain: <machine_learning | biology | chemistry | medicine | robotics_control | physics_materials | generic>
Date: YYYY-MM-DD

## Concepts
| Id | Concept | Builds on | Sources | Unit |
| --- | --- | --- | --- | --- |
| short-id | Plain title | - | S1 | unit-id |
| next-id | Plain title | short-id | S1, S2 | unit-id |

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
        for p in [p for p in prefs if p.startswith(("For the 9702 exam-prep", "Exam-prep:"))]:
            home = next((t for tid, t in s["topics"].items() if "9702" in tid), None)
            if home is not None:      # these were 9702 rules saved globally; they now apply to that topic only
                home.setdefault("prefs", [])
                if p not in home["prefs"]:
                    home["prefs"].append(p)
                prefs.remove(p)
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


# ---------- exam profiles (skills/teach-understanding/exams/*.md) ----------

def exam_profile(pid):
    path = EXAMS_DIR / f"{pid}.md"
    if not path.exists():
        have = ", ".join(sorted(p.stem for p in EXAMS_DIR.glob("*.md"))) or "none"
        raise LearnError(f"No exam profile {pid!r}. Available: {have}. Add a new board as exams/<id>.md.")
    text = path.read_text()
    m = re.match(r"---\n(.*?)\n---\n", text, re.S)
    meta = dict(l.split(":", 1) for l in (m.group(1).split("\n") if m else []) if ":" in l)
    prof = {k.strip(): v.strip() for k, v in meta.items()}
    prof["path"] = str(path)
    prof["re"] = re.compile(prof["citation_regex"])
    return prof


def topic_profile(t):
    return exam_profile(t["exam"]) if t.get("mode") == "exam" else None


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


def parse_brief(text, profile=None):
    """Validate a research brief. Returns (brief, errors). With an exam profile, exam sections are required."""
    errs = []
    sec = sections(text)
    for name in BRIEF_SECTIONS + (EXAM_SECTIONS if profile else []):
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
        unit = slug(r[4]) if len(r) > 4 and r[4].strip() not in ("", "-") else None
        concepts[cid] = {"title": title, "prereqs": prereqs, "sources": cited, "unit": unit}
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
    patterns, citations = {}, set()
    if profile:
        types = {v["type"] for v in sources.values()}
        for need in ("syllabus", "past-paper", "mark-scheme"):
            if need not in types:
                errs.append(f"exam mode: add at least one '{need}' source (official site, PapaCambridge or PMT)")
        if not any(l.strip().startswith("- ") for l in sec.get("syllabus points", [])):
            errs.append("'## Syllabus points' needs the learning outcomes you will teach, quoted with their codes")
        citations = set(m.group(0) for m in profile["re"].finditer(text))
        for r in table_rows(sec.get("paper patterns", [])):
            if len(r) < 7 or not re.fullmatch(r"P\d+", r[0]):
                errs.append(f"pattern row needs 7 columns starting with P1, P2...: {r[:2]}")
                continue
            real = [m.group(0) for m in profile["re"].finditer(r[5])]
            if len(real) < 2:
                errs.append(f"pattern {r[0]} needs 2+ real past-paper questions cited like "
                            f"{profile.get('citation_example')} (found {len(real)})")
            patterns[r[0]] = {"point": r[1], "pattern": r[2], "command": r[3], "marks": r[4], "real": real,
                              "scheme": r[6]}
        if not patterns:
            errs.append("'## Paper patterns' needs at least one pattern row built from real questions")
    return {"goal": goal, "concepts": concepts, "sources": sources, "patterns": patterns,
            "citations": citations}, errs


def brief_of(s):
    t = topic_of(s)
    r = t.get("research")
    if not r:
        raise LearnError(f"'{t['title']}' has no research brief yet. Run `learn research` first.")
    path = VAULT / r["note"]
    if not path.exists():
        raise LearnError(f"Research brief {r['note']} is missing from the vault. Re-save it with `learn research --save`.")
    brief, errs = parse_brief(path.read_text(), topic_profile(t))
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


# ---------- units ----------

def units_of(t):
    """Ordered {unit_id: {"title", "concepts"}}. Concepts outside any unit are their own one-concept unit."""
    units = {u: dict(v) for u, v in t.get("units", {}).items()}
    placed = {c for v in units.values() for c in v["concepts"]}
    for cid, c in t["concepts"].items():
        if cid not in placed:
            units[cid] = {"title": c["title"], "concepts": [cid]}
    return units


def unit_of(t, cid):
    for uid, u in units_of(t).items():
        if cid in u["concepts"]:
            return uid, u
    raise LearnError(f"Concept {cid!r} is in no unit.")


def band_note(s):
    """Difficulty signal from the last 10 graded answers (target ~70-90% correct)."""
    recent = need_session(s).get("recent", [])[-10:]
    if len(recent) < 5:
        return ""
    rate = sum(r == "correct" for r in recent) / len(recent)
    if rate > BAND[1]:
        return (f" DIFFICULTY: {rate:.0%} correct recently, too easy. Make these harder: level 3, a scenario the lesson "
                "never used, two-tier (answer + reason), fewer hints.")
    if rate < BAND[0]:
        return (f" DIFFICULTY: {rate:.0%} correct recently, too hard. Smaller steps: add a worked example before the "
                "next questions and ask one idea at a time.")
    return ""


def pending_concepts(sess):
    return {p["concept"] for p in sess["pending"].values()}


def unit_check_needed(s):
    """(unit_id, [concept ids still to ask]) for a unit whose concepts were taught but not yet checked."""
    sess = need_session(s)
    t = topic_of(s)
    waiting = pending_concepts(sess)
    for uid, u in units_of(t).items():
        cs = [t["concepts"][c] for c in u["concepts"]]
        if len(u["concepts"]) > 1 and all(c["taught"] for c in cs):
            todo = [cid for cid in u["concepts"] if not t["concepts"][cid].get("checked")
                    and t["concepts"][cid]["status"] not in SOLID and cid not in waiting]
            if todo:
                return uid, todo
    return None, []


# ---------- decisions ----------

def step(action, cid=None, reason="", level=None):
    return {"action": action, "concept": cid, "reason": reason, "level": level}


def choose_fresh(s):
    t = topic_of(s)
    sess = need_session(s)
    cs = t["concepts"]
    d = iso(today())
    if sess.get("reviews", 0) < SESSION_REVIEW_MAX:
        for cid, c in cs.items():
            if c["status"] in SOLID and c["next_review"] and c["next_review"] <= d and c["last_seen"] != d:
                return step("review", cid, f"'{c['title']}' is due for review (box {c['box']}, last seen "
                                           f"{c['last_seen']}).", max(2, c["level"]))
    for cid, c in cs.items():
        if c["status"] == "claimed":
            return step("check", cid, f"You said you already know '{c['title']}'. One quick check before we build on it.", 2)
    for cid, c in cs.items():
        if c["status"] == "learning":
            if c["taught"]:
                return step("ask", cid, f"'{c['title']}' is not solid yet: one new application question.", max(2, c["level"]))
            return step("teach", cid, f"'{c['title']}' still needs teaching.")
    if t.get("mode") == "exam":   # practice share grows as more of the topic is solid (adaptive split)
        solid = sum(c["status"] in SOLID for c in cs.values()) / max(1, len(cs))
        target = 2 + round(4 * solid)
        for uid, u in units_of(t).items():
            done = t.get("practice", {}).get(uid, 0)
            if all(cs[c]["status"] in SOLID for c in u["concepts"]) and done < target:
                return step("practice", uid, f"Exam practice on '{u['title']}': {done}/{target} past-paper questions "
                                             f"({solid:.0%} of the topic is solid, so practice takes a bigger share).")
    for uid, u in units_of(t).items():
        fresh = [c for c in u["concepts"] if cs[c]["status"] == "new"]
        if not fresh:
            continue
        outside = [p for c in u["concepts"] for p in cs[c]["prereqs"] if p not in u["concepts"]]
        weak = [p for p in outside if cs[p]["status"] not in SOLID]
        if weak:
            continue
        base = (f"it builds on {', '.join(repr(cs[p]['title']) for p in dict.fromkeys(outside))}, which you have solid"
                if outside else "it needs nothing else, so it is a starting point")
        if len(u["concepts"]) == 1:
            return step("teach", u["concepts"][0], f"Next new idea: '{u['title']}', because {base}.")
        return step("teach_unit", uid, f"Next unit: '{u['title']}' ({len(u['concepts'])} linked ideas taught "
                                       f"together), because {base}.")
    blocked = [cid for cid, c in cs.items() if c["status"] == "new"]
    if blocked:
        return step("teach", blocked[0], f"'{cs[blocked[0]]['title']}' is the next idea in the plan.")
    return step("complete", None, "Every concept in this topic is solid or mastered.")

def current_step(s):
    sess = need_session(s)
    t = topic_of(s)
    if not t.get("research"):
        return step("research", None, f"'{t['title']}' has no research brief yet. Research comes before any teaching.")
    if t.get("mode") == "exam" and t["research"].get("exam") != t["exam"]:
        return step("research", None, f"'{t['title']}' is in exam mode ({t['exam']}): the brief needs syllabus points, "
                                      "paper patterns from real questions, and examiner-report errors.")
    if not t["concepts"]:
        return step("plan", None, f"'{t['title']}' has a research brief but no plan yet.")
    uid, todo = unit_check_needed(s)
    if uid and len(sess["pending"]) < MAX_PENDING:
        names = ", ".join(repr(t["concepts"][c]["title"]) for c in todo)
        return step("unit_check", uid, f"Unit '{units_of(t)[uid]['title']}' is taught. Still to check: {names}.")
    if sess["pending"]:
        return step("wait", None, f"{', '.join(sess['pending'])} waiting for the learner's answer.")
    st = sess.get("step")
    if st and (st["concept"] is None or st["concept"] in t["concepts"] or st["concept"] in units_of(t)):
        return st
    for f in sess.get("followups", []):
        if f["concept"] in t["concepts"] and t["concepts"][f["concept"]]["status"] not in SOLID:
            return f
    return choose_fresh(s)

def instruction(s, st):
    t = topic_of(s)
    if st["action"] in ("teach_unit", "unit_check", "practice"):
        return unit_instruction(s, st)
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
    if a == "research" and t.get("mode") == "exam":
        prof = exam_profile(t["exam"])
        return (f"EXAM MODE. Read {prof['path']}. 1) If you don't know the goal, ask ONE plain question: which papers, "
                "which syllabus points, and when is the exam? 2) Download the syllabus and real past papers + mark "
                "schemes (+ examiner reports) ONLY from the sources the profile approves; check every download is a "
                "real PDF. 3) Build patterns from 4+ real questions per syllabus point (profile, 'Building a "
                "pattern'). 4) `learn research` prints the template with the exam sections; pipe the brief to "
                "`learn research --save`. Never invent a question pattern: every pattern cites real questions.")
    if a == "research":
        return ("1) If you don't know the learner's goal yet, ask ONE plain question in chat: what do you want to be "
                f"able to do with '{t['title']}', and what do you already know about it? Wait for the reply. "
                "2) Run the research pipeline in references/research.md (PRAXIST method): `learn lit guide <domain>`, "
                "2-4 `learn lit search \"<query>\"`, web search for textbooks/official syllabi/docs, open and read the "
                "best 3-6 sources. 3) Write the brief from `learn research` (template) and pipe it to "
                "`learn research --save`. Do not teach anything before the brief is saved.")
    if a == "plan":
        return ("Group the brief's concepts into UNITS: each unit is 2-5 concepts that only make sense together (one "
                "schema, ~15-20 min), e.g. a syllabus sub-section. Run `learn plan --unit 'id|Unit title|c1,c2,c3' "
                "--unit ... --known <ids|none>` (single concepts: --concept <id>). "
                "--known is required: the ids the learner SAID they already know (they get a quick check instead "
                "of teaching), or --known none. Never teach what they already know.")
    if a == "teach":
        return (f"Make 1 Manim visual of how '{title}' works: pick the closest template in references/visuals.md "
                f"(things moving: physical; a system of parts: diagram with --still; a curve or numbers: graph; a "
                f"formula: derivation; steps: process), adapt it, write its NARRATION (one spoken line per visual event, each event inside `with self.voice(i):`), and run `learn figure <name>`; it comes back narrated. Then write the theory block from the research "
                f"brief (cite sources as [S1]) with the visual embedded, using the block recipe in the skill, pipe it to "
                f"`learn block {cid}`, then write 1 question at level 2 ({LEVELS[2]}) by references/questions.md and pipe "
                f"it to `learn ask {cid}`." + band_note(s))
    if a == "reteach":
        last = next((m for m in reversed(s["mistakes"]) if m["concept"] == cid and not m["closed"]), None)
        belief = (f" Contrast the wrong belief (\"{last['what']}\") with the right one, side by side."
                  if last and last["kind"] == "misconception" and last["what"] else "")
        return (f"Re-teach '{title}': write a NEW block on the SAME idea with smaller steps, smaller numbers and a "
                f"different example from the same subject (not a toy story without the idea), and a NEW narrated "
                f"Manim scene (audio-first, references/visuals.md) that shows the step they got wrong. Name that "
                f"step.{belief} Pipe it to `learn block {cid}`. Then 1 question at level 1 via `learn ask {cid}`.")
    if a == "ask":
        what = "a scenario the lesson did not use" if lvl > 1 else "worded differently from any earlier question"
        if topic_profile(topic_of(s)):
            return (f"EXAM MODE: 1 NEW question on '{title}', {what}: another AUTHENTIC past-paper question from the "
                    f"brief's sources (quoted word for word, \"source\" + \"marks\"), or one generated from a brief "
                    f"pattern (\"source\": \"pattern:P#\"). Pipe it to `learn ask {cid}`." + band_note(s))
        return (f"Write 1 NEW question on '{title}' at {lvl_txt}, {what}, built by the "
                f"question recipe in references/questions.md. Pipe it to `learn ask {cid}`." + band_note(s))
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


def unit_instruction(s, st):
    t = topic_of(s)
    u = units_of(t)[st["concept"]]
    names = ", ".join(f"{c} ('{t['concepts'][c]['title']}')" for c in u["concepts"])
    exam = t.get("mode") == "exam"
    if st["action"] == "practice":
        return (f"Exam practice: ask AUTHENTIC past-paper questions on {names} (quoted word for word, with \"source\": "
                f"the citation and \"marks\"), mixing in earlier units when the paper does. `learn ask <concept>`; typed "
                f"answers are graded point by point against the mark scheme (`learn grade Q --marks got/total`)."
                + band_note(s))
    if st["action"] == "teach_unit" and exam:
        return (f"EXAM MODE, short teaching for unit '{u['title']}' ({names}): ONE block with 1-2 segments: the idea as "
                f"the syllabus states it, then a worked example of a REAL past-paper question (cite it) solved step by "
                f"step with the mark-scheme points, then the examiner-report trap. One narrated Manim scene per segment "
                f"(`learn figure`). Pipe to `learn block {st['concept']}`. Practice follows.")
    if st["action"] == "teach_unit":
        return (f"Teach the whole unit '{u['title']}' in ONE block: one segment per sub-idea (2-{MAX_SEGMENTS}), covering "
                f"{names}. For each segment make one short narrated Manim scene with `learn figure` (60-120 s, audio-first "
                f"`with self.voice(i):`, references/visuals.md). Write the block with the unit recipe in the skill (big idea, "
                f"key terms, per segment: video + steps/table, worked example), pipe it to `learn block {st['concept']}`. "
                f"No questions until the block is in the note.")
    _, todo = unit_check_needed(s)
    if exam:
        return (f"EXAM MODE unit check for '{u['title']}': ONE question for each of {', '.join(todo)}: an AUTHENTIC "
                f"past-paper question not used in the block (quoted word for word, \"source\": the citation, \"marks\"), "
                f"or one generated from a brief pattern (\"source\": \"pattern:P#\") when no unused real one exists. "
                f"Pipe each with `learn ask <concept>`; all wait together. Then tell the learner in one line and STOP."
                + band_note(s))
    return (f"Unit check for '{u['title']}': write ONE question for each of {', '.join(todo)} at level 2+ (a scenario "
            f"the lesson did not use; references/questions.md), at least one of them two-tier or typed with a rubric. "
            f"Pipe each with `learn ask <concept>`; all can wait in the note together. Then tell the learner in one "
            f"line and STOP." + band_note(s))


def print_next(s, extra=""):
    st = current_step(s)
    if extra:
        print(extra)
    print(f"WHY: {st['reason']}")
    print(f"NEXT: {instruction(s, st)}")


# ---------- rules ----------

def topic_of_concept(s, cid):
    """Return (topic_id, topic) that owns a concept id, searching all topics."""
    for tid, t in s["topics"].items():
        if cid in t["concepts"]:
            return tid, t
    raise LearnError(f"Unknown concept {cid!r} in any topic.")


def record(s, qid, result, kind=None, what=""):
    """Apply a graded answer. Returns the one-line decision reason."""
    sess = need_session(s)
    p = sess["pending"].pop(qid)
    cid = p["concept"]
    tid, t = topic_of_concept(s, cid)
    c = t["concepts"][cid]
    d = today()
    ds = iso(d)
    c["history"].append({"date": ds, "q": qid, "result": result, "level": p["level"], "kind": kind,
                         **({"marks": p["marks_got"]} if "marks_got" in p else {})})
    c["last_seen"] = ds
    c["checked"] = True
    sess["counts"][result] = sess["counts"].get(result, 0) + 1
    sess.setdefault("recent", []).append(result)
    sess["recent"] = sess["recent"][-10:]
    if p.get("review"):
        sess["reviews"] = sess.get("reviews", 0) + 1
    if p.get("practice"):
        t.setdefault("practice", {})[p["practice"]] = t.get("practice", {}).get(p["practice"], 0) + 1
    sess["followups"] = [f for f in sess.get("followups", []) if f["concept"] != cid]
    key = f"{tid}/{cid}"
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
        missed_today = sess["misses"].get(key, 0) > 0
        applied = p["level"] >= 2 and not missed_today     # one unseen application answer is enough evidence
        if not applied and c["streak"] >= 2 and p["level"] < 2:
            c["level"] = max(c["level"], 2)
            sess["step"] = step("ask", cid, f"{c['streak']} correct in a row on '{c['title']}', but only recall so far. "
                                            "One question that applies it to a new scenario (level 2) before it counts as solid.", 2)
            return f"Correct, {c['streak']} in a row on '{c['title']}' at level 1."
        if applied or c["streak"] >= 2:
            c.update(status="solid", box=1, solid_date=ds, promoted=ds, next_review=iso(d + timedelta(days=1)),
                     level=min(3, c["level"] + 1))
            sess["misses"].pop(key, None)
            if sess["stack"]:
                back = sess["stack"].pop()
                sess["step"] = step("ask", back, f"'{c['title']}' is fixed, so back to '{t['concepts'][back]['title']}'.")
            else:
                sess["step"] = None
            why = "applied to a new scenario" if applied else "2 correct in a row"
            return f"{why}: '{c['title']}' is solid. Review tomorrow.{tail}"
        if sess["pending"]:     # part of a unit check: decide after the whole check is graded
            return f"Correct on '{c['title']}', but recall only (level 1). It gets an application question later.{tail}"
        sess["step"] = step("ask", cid, f"Correct, recall only. One application question on '{c['title']}' makes it solid.",
                            max(2, c["level"]))
        return f"Correct, recall only, on '{c['title']}'.{tail}"

    # wrong or "I don't know"
    was = c["status"]
    c.update(streak=0, level=max(1, c["level"] - 1), box=0, status="learning",
             next_review=iso(d + timedelta(days=1)))
    kind = kind or ("gap" if result == "idk" else "error")
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
        sess["step"] = step("reteach" if kind == "misconception" else "ask", cid,
                            (f"Misconception on '{c['title']}': a short contrast re-teach of that step, then a "
                             "differently-worded question." if kind == "misconception" else
                             f"Missed once ({kind}). The feedback explains the fix. Now a new, differently worded question on the same idea."),
                            c["level"])
    if sess["pending"]:   # unit check still being graded: queue this, don't jump yet
        sess.setdefault("followups", []).append(sess["step"])
        sess["step"] = None
        return sess["followups"][-1]["reason"]
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
    elif p["type"] == "two-tier":
        right = f"{p['correct']}. {p['options'][p['correct']]}, because {p['reason_correct']}. {p['reasons'][p['reason_correct']]}"
        if result == "correct":
            body = [f"> [!success] {qid}: correct ({right})", f"> {p['why']}"]
        elif result == "idk":
            body = [f"> [!tip] {qid}: \"I don't know\" is a real answer. Right answer: {right}", f"> {p['why']}"]
        else:
            L, R = (picked or "??")[0], (picked or "??")[1:]
            wrong_bits = []
            if L != p["correct"]:
                wrong_bits.append(f"answer {L} comes from: {p['misconceptions'].get(L, '')}")
            if R != p["reason_correct"]:
                wrong_bits.append(f"reason {R} is the belief: {p['reason_misconceptions'].get(R, '')}")
            body = [f"> [!failure] {qid}: you picked {L} because {R}. Right answer: {right}", f"> {p['why']}",
                    "> " + "; ".join(wrong_bits)]
    else:
        tag = {"correct": "[!success]", "idk": "[!tip]", "wrong": "[!failure]"}[result]
        marks = f" ({p['marks_got']} marks)" if p.get("marks_got") else ""
        body = [f"> {tag} {qid}: {result}{marks}. A good answer: {p['answer']}", f"> {p['why']}"]
        if p.get("rubric"):
            body.append("> Marked on: " + "; ".join(p["rubric"]))
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
    if tid not in s["topics"] and (len(title.split()) > 8 or re.search(r"[.!?:;]\s", title)):
        known = ", ".join(t["title"] for t in s["topics"].values()) or "none yet"
        raise LearnError(f"{title!r} looks like a message, not a topic. Pass only the topic name, e.g. "
                         f"`learn start probability basics`. Existing topics: {known}.")
    d = iso(today())
    sess = s["session"]
    if sess and sess["date"] != d:
        finish(s, "Ended automatically: this session was never closed.")
        sess = None
    if tid not in s["topics"]:
        s["topics"][tid] = {"title": title, "goal": "", "created": d, "concepts": {}}
    t = s["topics"][tid]
    if getattr(a, "exam", None):
        exam_profile(a.exam)                 # validates the id
        t["mode"], t["exam"] = "exam", a.exam
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
    if t.get("prefs"):
        print(f"\nFOR THIS TOPIC ONLY ({t['title']}):")
        for p in t["prefs"]:
            print(f"- {p}")
    if t.get("mode") == "exam":
        print(f"\nEXAM MODE: profile {t['exam']} ({exam_profile(t['exam'])['path']})")
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
    unit_specs = []
    for spec in a.unit:
        parts = [x.strip() for x in spec.split("|")]
        if len(parts) != 3 or not parts[0] or not parts[2]:
            raise LearnError(f"--unit must look like 'id|Unit title|concept,concept', got {spec!r}")
        ids = [slug(x) for x in parts[2].split(",") if x.strip()]
        if not 1 <= len(ids) <= MAX_UNIT_CONCEPTS:
            raise LearnError(f"Unit {parts[0]!r} has {len(ids)} concepts; a unit holds 1-{MAX_UNIT_CONCEPTS} linked "
                             "concepts (one schema). Split it.")
        unit_specs.append((slug(parts[0]), parts[1] or parts[0], ids))
    if not a.unit and not a.concept:
        raise LearnError("Pass --unit 'id|Title|c1,c2' (preferred) or --concept <id>.")
    ids_in_units = [c for _, _, ids in unit_specs for c in ids]
    specs = [parse_concept(x, brief) for x in list(a.concept) + ids_in_units]
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
    units = t.setdefault("units", {})
    for uid, title, ids in unit_specs:
        for other in units.values():
            other["concepts"] = [c for c in other["concepts"] if c not in ids]
        units[uid] = {"title": title, "concepts": ids}
    if not unit_specs:   # group by the brief's Unit column when the plan names concepts only
        for cid, _, _ in specs:
            bu = brief["concepts"][cid].get("unit")
            if bu:
                units.setdefault(bu, {"title": bu.replace("-", " "), "concepts": []})
                if cid not in units[bu]["concepts"]:
                    units[bu]["concepts"].append(cid)
    for uid in [u for u, v in units.items() if not v["concepts"]]:
        del units[uid]
    for k in [x.strip() for x in a.known.split(",") if x.strip() and x.strip().lower() != "none"]:
        c = concept(s, slug(k))
        if c["status"] == "new":
            c["status"] = "claimed"
    write_map(s, t)
    need_session(s)["step"] = None
    n_units = len(units_of(t))
    print_next(s, f"Plan saved: {len(t['concepts'])} concepts in {n_units} unit(s), drawn into the note.")


def cmd_research(s, a):
    t = topic_of(s)
    if not a.save:
        r = t.get("research")
        print(f"Research brief: {r['note']} (saved {r['date']})" if r else "No research brief yet for this topic.")
        print("\nTEMPLATE (fill every section; cite sources as [S1]; pipe the result to `learn research --save`):\n")
        print(BRIEF_TEMPLATE)
        prof = topic_profile(t)
        if prof:
            print(f"EXAM MODE ({prof['board']}): also add these sections (rules: {prof['path']}):")
            print(EXAM_TEMPLATE)
        print_next(s)
        return
    text = sys.stdin.read().strip()
    brief, errs = parse_brief(text, topic_profile(t))
    if errs:
        raise LearnError("Brief rejected. Fix and re-save:\n- " + "\n- ".join(errs))
    rel = f"{SOURCES_DIR}/{t['title']} research brief.md"
    (VAULT / SOURCES_DIR).mkdir(parents=True, exist_ok=True)
    (VAULT / rel).write_text(text + "\n")
    t["research"] = {"note": rel, "date": iso(today()), "sources": len(brief["sources"]),
                     "exam": t.get("exam") if t.get("mode") == "exam" else None}
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


# ---------- narration (local TTS: Voicebox server running the Kokoro engine) ----------

DEFAULT_VOICE = "af_heart"
KOKORO_EN = ["af_alloy", "af_aoede", "af_bella", "af_heart", "af_jessica", "af_kore", "af_nicole", "af_nova",
             "af_river", "af_sarah", "af_sky", "am_adam", "am_echo", "am_eric", "am_fenrir", "am_liam",
             "am_michael", "am_onyx", "am_puck", "am_santa", "bf_alice", "bf_emma", "bf_isabella", "bf_lily",
             "bm_daniel", "bm_fable", "bm_george", "bm_lewis"]
VOICEBOX_URL = os.environ.get("LEARN_VOICEBOX_URL", "http://127.0.0.1:17493")
VOICEBOX_DIR = Path(os.environ.get("LEARN_VOICEBOX_DIR", Path.home() / ".local/share/learning-system/voicebox"))
VOICEBOX_DATA = VOICEBOX_DIR.parent / "voicebox-data"
TTS_LINE_TIMEOUT = 300
NARR_WORDS = (4, 40)          # per line: one phrase per visual event (Mayer: segments of 1-2 sentences)
NARR_TOTAL_WORDS = 450        # ~3 min of speech at 2.6 words/s
NARR_LEAD, NARR_GAP, NARR_TAIL = 0.25, 0.35, 2.0   # seconds; 2 s silent hold on the finished frame (segmenting)
NARRATION_MISSING = (
    "This animation has no NARRATION. Every animation is narrated for this learner. Add a module-level list "
    "with one spoken line per numbered caption, in order, explaining what to notice and why (not reading the "
    "caption):\n  NARRATION = [\"Watch the arrows: ...\", \"Now follow the red molecule ...\"]\n"
    "(see references/visuals.md, Narration). Use --silent only if a voice would add nothing.")


class TTSError(Exception):
    pass


def narration_of(script):
    """The scene's NARRATION list (module-level literal), or None."""
    try:
        tree = ast.parse(script)
    except SyntaxError:
        return None
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "NARRATION" for t in node.targets):
            try:
                val = ast.literal_eval(node.value)
            except ValueError:
                raise LearnError("NARRATION must be a plain list of strings, written out (no variables or f-strings).")
            if not isinstance(val, (list, tuple)) or not val or not all(isinstance(x, str) for x in val):
                raise LearnError("NARRATION must be a non-empty list of strings, one per numbered caption.")
            return [" ".join(x.split()) for x in val]
    return None


def validate_narration(lines):
    errs = []
    total = 0
    for i, line in enumerate(lines, 1):
        n = len(line.split())
        total += n
        if not NARR_WORDS[0] <= n <= NARR_WORDS[1]:
            errs.append(f"line {i} has {n} words; keep each line {NARR_WORDS[0]}-{NARR_WORDS[1]} words")
        if re.search(r"[\\$^_{}]", line):
            errs.append(f"line {i} has LaTeX/code symbols; write maths as spoken words "
                        "(\"f equals one over T\", \"x squared\")")
        if re.search(r"\[S\d+\]", line):
            errs.append(f"line {i} has a citation id; citations stay in the block text, not in speech")
        if re.search(r"\*\*|`|^#", line):
            errs.append(f"line {i} has markdown; write plain spoken sentences")
    if total > NARR_TOTAL_WORDS:
        errs.append(f"narration is {total} words; keep the whole clip under {NARR_TOTAL_WORDS}")
    if errs:
        raise LearnError("NARRATION needs fixing:\n- " + "\n- ".join(errs))


def _content_words(text):
    return [w for w in re.findall(r"[a-z]+", text.lower()) if len(w) > 3]


def align_narration(lines, marks):
    """Mark time per line (numbered captions 1..n), or None for whole-clip sync. Rejects label-reading."""
    if not marks:
        return None
    nums = sorted(marks)
    if nums != list(range(1, len(nums) + 1)):
        return None
    if len(nums) != len(lines):
        raise LearnError(f"The scene shows numbered captions 1-{len(nums)} but NARRATION has {len(lines)} "
                         "line(s). Write exactly one narration line per numbered caption, in the same order.")
    for i, line in enumerate(lines, 1):
        cap = set(_content_words(re.sub(r"^\s*\d+[\s.):]+", "", marks[i][1])))
        words = _content_words(line)
        if words and len(words) <= len(cap) + 2 and sum(w in cap for w in words) >= 0.8 * len(words):
            raise LearnError(f"Narration line {i} only reads its caption ({marks[i][1]!r}). Say what the "
                             "learner should notice on screen and why it matters.")
    return [marks[i][0] for i in nums]


def schedule(marks, durations, video_len, exact=False):
    """Place each line on the output timeline. Where a line would still be talking when the next step's visuals
    start, freeze the video at that step until the voice catches up. Returns (starts, holds, total_len);
    holds are (original_time, seconds)."""
    holds, starts = {}, []
    shift, prev_end = 0.0, 0.0
    if exact:   # audio-first: each voice block already lasts its line + gap, so a line starts on its block
        starts = list(marks)
        need = starts[-1] + durations[-1] + NARR_TAIL
        if need > video_len:
            holds[round(video_len, 3)] = need - video_len
        return starts, sorted(holds.items()), max(video_len, need)
    for i, d in enumerate(durations):
        if marks and (i == 0 or marks[i] > marks[i - 1] + 0.05):
            t = max(marks[i], 0.05)
            want = t + shift + (NARR_LEAD if i == 0 else 0.1)
            if prev_end > want:   # previous line still talking when this step's visuals begin: freeze here
                holds[round(t, 3)] = holds.get(round(t, 3), 0) + prev_end - want
                shift += prev_end - want
                want = prev_end
            start = want
        else:   # no captions, or this caption appeared together with the previous one: speak right after it
            start = max(NARR_LEAD, prev_end)
        starts.append(start)
        prev_end = start + d + NARR_GAP
    total = video_len + shift
    need = prev_end - NARR_GAP + NARR_TAIL
    if need > total:
        holds[round(video_len, 3)] = holds.get(round(video_len, 3), 0) + need - total
        total = need
    return starts, sorted(holds.items()), total


def probe_duration(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
                       capture_output=True, text=True)
    try:
        return float(r.stdout.strip())
    except ValueError:
        raise LearnError(f"Could not read the length of {path.name}.")


def compose(video, clips, starts, holds, total, video_len, out):
    """Mux narration into the video: freeze frames where `holds` says, loudness-normalise the voice (EBU R128,
    -16 LUFS). The video stream is copied unless a freeze is needed."""
    cmd = ["ffmpeg", "-v", "error", "-y", "-i", str(video)] + [x for c, _ in clips for x in ("-i", str(c))]
    graph = []
    if holds:
        cuts = [0.0] + [t for t, _ in holds if t < video_len - 1e-3] + [video_len]
        pad = dict(holds)
        pieces = []
        for j in range(len(cuts) - 1):
            a, b = cuts[j], cuts[j + 1]
            h = pad.get(round(b, 3), 0)
            graph.append(f"[0:v]trim=start={a:.3f}:end={b:.3f},setpts=PTS-STARTPTS"
                         + (f",tpad=stop_mode=clone:stop_duration={h:.3f}" if h else "") + f"[v{j}]")
            pieces.append(f"[v{j}]")
        graph.append("".join(pieces) + f"concat=n={len(pieces)}:v=1:a=0[v]")
    for i, st in enumerate(starts, 1):
        graph.append(f"[{i}:a]silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.03,"
                     f"aresample=48000,adelay=delays={int(st * 1000)}:all=1[a{i}]")
    mix = "".join(f"[a{i}]" for i in range(1, len(starts) + 1))
    graph.append((f"{mix}amix=inputs={len(starts)}:normalize=0:dropout_transition=0," if len(starts) > 1
                  else f"{mix}") + "loudnorm=I=-16:TP=-1.5:LRA=11,aresample=48000,apad[a]")
    cmd += ["-filter_complex", ";".join(graph), "-map", "[v]" if holds else "0:v", "-map", "[a]"]
    cmd += (["-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p"] if holds else ["-c:v", "copy"])
    cmd += ["-c:a", "aac", "-b:a", "160k", "-t", f"{total:.3f}", "-movflags", "+faststart", str(out)]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=900)
    if r.returncode != 0 or not out.exists():
        raise LearnError("ffmpeg could not mix the narration: " + (r.stderr.strip().splitlines() or ["?"])[-1])


def _voicebox(method, path, body=None, timeout=30):
    req = urllib.request.Request(VOICEBOX_URL + path, method=method,
                                 data=json.dumps(body).encode() if body is not None else None,
                                 headers={"Content-Type": "application/json"})
    return urllib.request.urlopen(req, timeout=timeout)


def voicebox_ready():
    """Make sure the local Voicebox server answers; start it from the install dir if needed."""
    try:
        _voicebox("GET", "/health", timeout=3).read()
        return
    except (urllib.error.URLError, OSError):
        pass
    py = VOICEBOX_DIR / ".venv/bin/python"
    if not py.exists():
        raise TTSError(f"Voicebox is not installed at {VOICEBOX_DIR} (run scripts/install.sh)")
    if os.environ.get("LEARN_VOICEBOX_AUTOSTART", "1") == "0":
        raise TTSError(f"Voicebox server is not running at {VOICEBOX_URL}")
    VOICEBOX_DATA.mkdir(parents=True, exist_ok=True)
    port = str(urllib.parse.urlparse(VOICEBOX_URL).port or 17493)
    with open(VOICEBOX_DATA / "server.log", "a") as log:
        subprocess.Popen([str(py), "-m", "backend.main", "--port", port, "--data-dir", str(VOICEBOX_DATA)],
                         cwd=VOICEBOX_DIR, stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
    for _ in range(90):
        time.sleep(1)
        try:
            _voicebox("GET", "/health", timeout=3).read()
            return
        except (urllib.error.URLError, OSError):
            continue
    raise TTSError(f"Voicebox server did not start within 90 s (see {VOICEBOX_DATA / 'server.log'})")


def voicebox_profile(voice):
    name = f"learn-narrator-{voice}"
    for p in json.loads(_voicebox("GET", "/profiles").read()):
        if p.get("name") == name:
            return p["id"]
    return json.loads(_voicebox("POST", "/profiles", {
        "name": name, "language": "en", "voice_type": "preset", "preset_engine": "kokoro",
        "preset_voice_id": voice, "default_engine": "kokoro"}).read())["id"]


def tts_lines(lines, voice, outdir):
    """Speak each line to a WAV. Returns [(path, seconds)]. Raises TTSError on any failure."""
    backend = os.environ.get("LEARN_TTS", "voicebox")
    clips = []
    if backend == "none":
        raise TTSError("narration is turned off (LEARN_TTS=none)")
    if backend == "fake":   # tests: silent WAVs at a speaking rate of ~2.6 words/s
        for i, line in enumerate(lines):
            secs = max(1.0, len(line.split()) / 2.6)
            path = outdir / f"line{i}.wav"
            with wave.open(str(path), "wb") as w:
                w.setnchannels(1), w.setsampwidth(2), w.setframerate(24000)
                w.writeframes(b"\0\0" * int(secs * 24000))
            clips.append((path, secs))
        return clips
    try:
        voicebox_ready()
        pid = voicebox_profile(voice)
        for i, line in enumerate(lines):
            gid = json.loads(_voicebox("POST", "/generate", {"profile_id": pid, "text": line, "language": "en",
                                                             "engine": "kokoro"}).read())["id"]
            last = {}
            with _voicebox("GET", f"/generate/{gid}/status", timeout=TTS_LINE_TIMEOUT) as stream:
                for raw in stream:
                    row = raw.decode().strip()
                    if row.startswith("data:"):
                        last = json.loads(row[5:])
            if last.get("status") != "completed":
                raise TTSError(f"line {i + 1}: {last.get('status', 'no status')} {last.get('error') or ''}".strip())
            path = outdir / f"line{i}.wav"
            path.write_bytes(_voicebox("GET", f"/audio/{gid}", timeout=60).read())
            clips.append((path, float(last.get("duration") or probe_duration(path))))
    except TTSError:
        raise
    except (urllib.error.URLError, OSError, ValueError, KeyError) as e:
        raise TTSError(f"{type(e).__name__}: {e}")
    return clips


def tts_warning(e):
    return (f"WARNING: narration failed ({e}). Saved the silent video so the lesson can continue. "
            f"Fix later: `bash scripts/install.sh`, or see {VOICEBOX_DATA / 'server.log'}.")


def narrate(s, video, lines, marks, tmp, clips=None, audio_first=False):
    """Return (video_to_save, message). Never raises for TTS problems: the silent video is kept instead."""
    voice = s["profile"].get("voice", DEFAULT_VOICE)
    if clips is None:
        try:
            clips = tts_lines(lines, voice, tmp)
        except TTSError as e:
            return video, tts_warning(e)
    video_len = probe_duration(video)
    starts, holds, total = schedule(marks, [d for _, d in clips], video_len, exact=audio_first)
    if os.environ.get("LEARN_DEBUG_SYNC"):
        print(f"SYNC marks={marks} durations={[round(d, 2) for _, d in clips]} starts={[round(x, 2) for x in starts]} "
              f"holds={holds} total={total:.2f}")
    out = tmp / "narrated.mp4"
    try:
        compose(video, clips, starts, holds, total, video_len, out)
    except (LearnError, subprocess.TimeoutExpired) as e:
        return video, f"WARNING: could not mix the narration ({e}). Saved the silent video."
    held = sum(h for _, h in holds)
    sync = ("audio-first: every line starts on its own visual event" if audio_first else
            "step-synced to the numbered captions" if marks else "played as one block (no numbered captions found)")
    return out, (f"Narration: {len(lines)} line(s), voice {voice}, {sum(d for _, d in clips):.1f}s of speech, {sync}"
                 + (f"; picture held {held:.1f}s in total so it waits for the voice" if held else "") + ".")


def save_figure(s, name, out, kind):
    sess = need_session(s)
    rel = f"{FIG_DIR}/{sess['topic']}/{name}{out.suffix}"
    dest = VAULT / rel
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(out.read_bytes())
    s.setdefault("figures", {})[rel] = kind
    s.setdefault("narrations", {}).pop(rel, None)
    print(f"Figure saved: {rel} ({kind})")
    print(f"EMBED: ![[{rel}]]")
    print("NEXT: Put the EMBED line under its segment heading in the block (or in a question's \"figure\" field). "
          "The notes beside it add steps or a table, not the narration. Make the next segment's scene, or run "
          "`learn block <unit>` when all segments are ready.")
    return rel


def strip_ansi(text):
    return re.sub(r"\x1b\[[0-9;]*[A-Za-z]", "", text)


def render_manim(s, name, script, still, tmp, durations=None):
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
               LEARN_VOICE_DUR=json.dumps({str(i + 1): d for i, d in enumerate(durations or [])}),
               PATH=f"{TEX_BIN}{os.pathsep}{os.environ.get('PATH', '')}")
    quality = os.environ.get("LEARN_MANIM_QUALITY", "-qm")      # 720p30 for lessons; tests use -ql
    cmd = [str(MANIM), "-s" if still else quality, "--disable_caching", "--media_dir", str(tmp / "media"),
           "-o", "out", str(tmp / "harness.py"), "LearnChecked"]
    if still:
        cmd.insert(2, quality)
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
    rep = json.loads(report.read_text()) if report.exists() else {}
    problems = rep.get("problems", [])
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
    return out, {int(k): v for k, v in rep.get("marks", {}).items()}, {int(k): v for k, v in rep.get("voice", {}).items()}


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
    if is_manim:   # old 3b1b/ManimGL code is the first thing to fix, and counts as a failed Manim attempt
        old = [fix for pat, fix in OLD_MANIM_API if re.search(pat, script)]
        if old:
            sess["manim_failures"] = fails + 1
            save(s)
            raise LearnError("This is old 3Blue1Brown/ManimGL code. Rewrite it for Manim Community "
                             "(references/visuals.md):\n- " + "\n- ".join(old)
                             + f"\n(Manim attempt failed {sess['manim_failures']} time(s) in a row)")
    lines = None
    if is_manim and not a.still and not a.silent:
        lines = narration_of(script)
        if lines is None:
            raise LearnError(NARRATION_MISSING)
        validate_narration(lines)
    audio_first = bool(lines) and "self.voice(" in script
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        clips, tts_note = None, None
        if audio_first:   # speak first, then render the scene to the real line lengths
            try:
                clips = tts_lines(lines, s["profile"].get("voice", DEFAULT_VOICE), tmp)
            except TTSError as e:
                tts_note = tts_warning(e)
        if is_manim:
            try:
                out, marks, vmarks = render_manim(s, name, script, a.still, tmp,
                                                  durations=[d + NARR_GAP for _, d in clips] if clips else None)
            except LearnError:
                sess["manim_failures"] = fails + 1
                left = MANIM_FALLBACK_AFTER - sess["manim_failures"]
                print(f"(Manim attempt failed {sess['manim_failures']} time(s) in a row"
                      + (f"; matplotlib fallback unlocks after {left} more)" if left > 0 else
                         "; matplotlib fallback is now unlocked if you need it)"))
                save(s)
                raise
            sess["manim_failures"] = 0
            note = None
            if audio_first:
                if sorted(vmarks) != list(range(1, len(lines) + 1)):
                    raise LearnError(f"NARRATION has {len(lines)} line(s) but the scene opened voice blocks "
                                     f"{sorted(vmarks) or 'none'}. Use `with self.voice(1):` ... `with self.voice("
                                     f"{len(lines)}):`, one per line, in order.")
                note = tts_note or None
                if clips:
                    out, note = narrate(s, out, lines, [vmarks[i] for i in range(1, len(lines) + 1)], tmp,
                                        clips=clips, audio_first=True)
            elif lines:
                out, note = narrate(s, out, lines, align_narration(lines, marks), tmp)
            rel = save_figure(s, name, out, "manim")
            if lines and note and not note.startswith("WARNING"):
                s["narrations"][rel] = lines
            if note:
                print(note)
        else:
            out = render_matplotlib(script, tmp)
            save_figure(s, name, out, "matplotlib")


def block_structure_problems(md, unit_size):
    """Notes must be structured: short paragraphs, and for a unit: big idea, key terms, segments with visuals."""
    errs = []
    body = re.sub(r"```.*?```|\$\$.*?\$\$", "", md, flags=re.S)
    para = []
    for line in body.split("\n") + [""]:
        st = line.strip()
        prose = st and not re.match(r"^(#|>|-|\*\*Big idea|\*\*Key terms|\||!\[\[|\d+[.)]\s|\$)", st)
        if prose:
            para.append(st)
        elif para:
            n = len(" ".join(para).split())
            if n > MAX_PARAGRAPH_WORDS:
                errs.append(f"a {n}-word paragraph (\"{' '.join(para)[:50]}...\"): over {MAX_PARAGRAPH_WORDS} words; "
                            "turn it into numbered steps, a list or a table")
            para = []
    segs = re.split(r"(?m)^### ", md)
    if unit_size > 1:
        if not re.search(r"(?m)^\*\*Big idea:\*\*", md):
            errs.append("start with '**Big idea:** <one sentence>'")
        if not re.search(r"(?m)^\*\*Key terms", md):
            errs.append("add '**Key terms:**' with a '- **term**: one-line meaning' list before the first video")
        parts = segs[1:]
        if not 1 <= len(parts) <= MAX_SEGMENTS:
            errs.append(f"a unit block needs 1-{MAX_SEGMENTS} segments, each starting with '### <sub-idea>' "
                        f"(found {len(parts)})")
        for p in parts:
            title = p.split("\n", 1)[0].strip()
            if not (FIG_EMBED.search(p) or MERMAID.search(p)):
                errs.append(f"segment '{title}' has no visual (its own short `learn figure` scene)")
            if not re.search(r"(?m)^\s*(- |\d+[.)] |\|)", p):
                errs.append(f"segment '{title}' needs a structured element: numbered steps, a list or a table")
            if len(re.sub(r"```.*?```", " ", p, flags=re.S).split()) > MAX_BLOCK_WORDS:
                errs.append(f"segment '{title}' is over {MAX_BLOCK_WORDS} words; cut it or split the segment")
    return errs


def cmd_block(s, a):
    sess = need_session(s)
    t = topic_of(s)
    target = slug(a.concept)
    if target in t.get("units", {}) and target not in t["concepts"]:
        unit = units_of(t)[target]
        cids = list(unit["concepts"])
        title = unit["title"]
    else:
        cids = [target]
        concept(s, target)
        title = t["concepts"][target]["title"]
    cid = cids[0]
    c = t["concepts"][cid]
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
    limit = MAX_BLOCK_WORDS * (MAX_SEGMENTS if len(cids) > 1 else 1)
    if words > limit:
        raise LearnError(f"Block is {words} words; the limit is {limit}. Cut it and re-run.")
    shape = block_structure_problems(md, len(cids))
    if shape:
        raise LearnError("The notes need structure (unit recipe in the skill):\n- " + "\n- ".join(shape))
    for f in figs:   # folded transcript under each narrated video
        said = s.get("narrations", {}).get(f)
        if said:
            md = re.sub(r"(!\[\[" + re.escape(f) + r"(?:\|[^\]]*)?\]\])",
                        lambda m: m.group(1) + "\n\n> [!quote]- Narration (what the voice says)\n"
                        + "\n".join(f"> {i}. {x}" for i, x in enumerate(said, 1)), md, count=1)
    sess["blocks"] += 1
    for x in cids:
        cx = t["concepts"][x]
        cx["taught"] = True
        if len(cids) > 1:
            cx["checked"] = False
        if cx["status"] == "new":
            cx["status"] = "learning"
        key = f"{sess['topic']}/{x}"
        sess["touched"].setdefault(key, sess["start_status"].get(key, "new"))
    sess["followups"] = [f for f in sess.get("followups", []) if f["concept"] not in cids]
    refs = "\n".join(f"> {x}: {brief['sources'][x]['source']} ({brief['sources'][x]['type']})" for x in cited)
    append(s, f"## {sess['blocks']}. {title}\n\n{md}\n\n> [!quote]- Sources\n{refs}")
    prev = sess["step"]
    if len(cids) > 1:
        sess["step"] = None      # current_step now asks for the unit check
    else:
        lvl = 1 if (prev and prev["action"] == "reteach") else max(2, c["level"])
        sess["step"] = step("ask", cid, f"Theory for '{c['title']}' is in the note. Now one application question.", lvl)
    render_canvas(s, sess["topic"])
    print_next(s, "Block written to the note." + (f" ({unchecked} mermaid diagram(s) not checked: Obsidian not "
                                                    "reachable; open the note to confirm it renders.)" if unchecked else ""))


def _words(text):
    return {w for w in re.findall(r"[a-z]{4,}", text.lower()) if w not in STOPWORDS}


def item_problems(stem, opts, note_text="", level=1):
    """Item-writing flaws an engine can see (Haladyna, Downing & Rodriguez 2002; NBME guide)."""
    errs = []
    key = next(o["text"] for o in opts if o.get("correct"))
    dis = [o["text"] for o in opts if not o.get("correct")]
    if not stem.rstrip().endswith("?"):
        errs.append("the stem must be a closed question ending in '?': an expert should be able to answer it "
                    "before seeing the options")
    if re.search(r"\b(NOT|EXCEPT)\b|\bwhich\b.{0,40}\b(false|incorrect|not true)\b", stem):
        errs.append("negative stem (NOT/EXCEPT/false): ask for the correct idea instead")
    texts = [o["text"].strip().lower() for o in opts]
    if len(set(texts)) < len(texts):
        errs.append("two options are identical")
    if any(re.search(r"\b(all|none|both) of the above\b", x) for x in texts):
        errs.append("no 'all/none/both of the above'")
    mean = sum(len(d) for d in dis) / len(dis)
    if len(key) >= 20 and len(key) > KEY_LENGTH_RATIO * mean:
        errs.append(f"the right option is {len(key) / mean:.1f}x longer than the others: a length cue. Make all "
                    "options the same length and detail")
    sw = _words(stem)
    leak = (sw & _words(key)) - set().union(*[_words(d) for d in dis])
    if len(leak) >= 2:
        errs.append(f"only the right option repeats stem words ({', '.join(sorted(leak))}): a wording cue")
    for d in dis:
        if ABSOLUTES.search(d) and not ABSOLUTES.search(key):
            errs.append(f"'{d[:40]}' uses an absolute word (always/never/only...) the right option lacks: a cue")
            break
    if level >= 2 and note_text:
        # a copied sentence shares a long run of words; a topic's own name ("the chance of at least one") does not
        grams = lambda x: {tuple(w[i:i + 8]) for w in [re.findall(r"[a-z0-9]+", x.lower())] for i in range(len(w) - 7)}
        if grams(stem) & grams(note_text):
            errs.append("the stem copies text already in the note (the lesson or an earlier question); level 2+ "
                        "needs a new scenario")
    return errs


def _check_options(opts, label):
    if len(opts) != 3:
        raise LearnError(f"{label}: use exactly 3 options (1 right + 2 plausible distractors; Rodriguez 2005). "
                         "'I don't know' is added automatically.")
    if sum(bool(o.get("correct")) for o in opts) != 1:
        raise LearnError(f"{label}: exactly one option must have \"correct\": true.")
    for o in opts:
        if not o.get("correct") and not str(o.get("misconception", "")).strip():
            raise LearnError(f"Wrong option {o.get('text')!r} needs a \"misconception\": the wrong belief that leads to it.")


def cmd_ask(s, a):
    cid = slug(a.concept)
    c = concept(s, cid)
    sess = need_session(s)
    if not c["taught"] and c["status"] != "claimed":
        raise LearnError(f"'{c['title']}' has not been taught yet. Teach it first with `learn block {cid}`. "
                         "Learner rule: questions only on what was taught.")
    if len(sess["pending"]) >= MAX_PENDING:
        raise LearnError(f"{MAX_PENDING} questions are already waiting. Run `learn check` after the learner answers.")
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
    t = topic_of(s)
    uid, unit = unit_of(t, cid)
    _, todo = unit_check_needed(s)
    in_check = len(unit["concepts"]) > 1 and cid in todo
    if in_check:
        level = max(level, 2)
        others = [p for p in sess["pending"].values() if p["concept"] in unit["concepts"]]
        open_item = any(p["type"] in ("typed", "two-tier") or not p.get("source", "pattern:").startswith("pattern:")
                        for p in others)
        real = topic_profile(t) and not str(q.get("source") or "pattern:").startswith("pattern:")
        if kind == "choice" and not open_item and not real and len(todo) == 1:
            raise LearnError("A unit check needs at least one two-tier (answer + reason) or typed question with a "
                             "rubric. Make this last one two-tier or typed (references/questions.md).")
    note_text = note_file(s).read_text()
    prof = topic_profile(t)
    authentic = False
    if prof:
        src, marks = str(q.get("source") or "").strip(), q.get("marks")
        if not isinstance(marks, int) or not 1 <= marks <= 20:
            raise LearnError("Exam mode: add \"marks\": the question's mark total (a whole number).")
        if src.lower().startswith("pattern:"):
            pid = src.split(":", 1)[1].strip()
            if pid not in brief_of(s)["patterns"]:
                raise LearnError(f"Exam mode: pattern {pid!r} is not in the brief's Paper patterns.")
        elif prof["re"].fullmatch(src):
            paper = src.split(" Q")[0]
            if paper not in note_text and paper not in (VAULT / t["research"]["note"]).read_text():
                raise LearnError(f"Exam mode: {paper} is not among the brief's real questions/sources. Add it to "
                                 "the brief (with its source row) before using it.")
            authentic = True
        else:
            raise LearnError(f"Exam mode: \"source\" must be a real question cited like {prof['citation_example']} "
                             "(quoted word for word), or \"pattern:P1\" for a generated question that follows a "
                             "verified pattern.")
        p_exam = {"source": src, "marks": marks}
    if kind in ("choice", "two-tier") and authentic:   # official items are kept as printed (often 4 options)
        opts_ = q.get("options") or []
        if not 2 <= len(opts_) <= 5 or sum(bool(o.get("correct")) for o in opts_) != 1:
            raise LearnError("Past-paper MCQ: copy its options exactly (2-5), mark the one right answer.")
        for o in opts_:
            if not o.get("correct") and not str(o.get("misconception", "")).strip():
                raise LearnError(f"Wrong option {o.get('text')!r} needs a \"misconception\" (the examiner report or "
                                 "the error that leads to it).")
    elif kind in ("choice", "two-tier"):
        _check_options(q.get("options") or [], "Answer options")
        if kind == "two-tier":
            _check_options(q.get("reasons") or [], "Reason options")
        flaws = item_problems(q["question"], q["options"], note_text, level)
        if kind == "two-tier":
            flaws += [f"reason tier: {f}" for f in item_problems("Why?", q["reasons"]) if "stem" not in f]
        if flaws:
            raise LearnError("This question can be answered without understanding. Fix it (references/questions.md):"
                             "\n- " + "\n- ".join(flaws))
    sess["qn"] += 1
    qid = f"Q{sess['qn']}"
    p = {"concept": cid, "type": kind, "level": level, "why": q["why"].strip(), "question": q["question"].strip()}
    tag = {"two-tier": " · two-tier", "typed": " · write it"}.get(kind, "")
    if prof:
        p.update(p_exam)
        tag += (f" · {p_exam['source']}" if authentic else f" · generated, follows {p_exam['source'].split(':')[1].strip()}")
        tag += f" · [{p_exam['marks']} mark{'s' if p_exam['marks'] > 1 else ''}]"
    out = [f"### {qid} · level {level}{tag}", "", q["question"].strip(), ""]
    fig = str(q.get("figure") or "").strip()
    if fig:
        m = FIG_EMBED.fullmatch(fig) or FIG_EMBED.fullmatch(f"![[{fig}]]")
        if not m or not (VAULT / m.group(1)).exists():
            raise LearnError(f"\"figure\" must be an embed printed by `learn figure`, got {fig!r}.")
        out[3:3] = ["", f"![[{m.group(1)}]]"]
        p["figure"] = m.group(1)
    if kind in ("choice", "two-tier"):
        opts = list(q["options"])
        if not authentic:   # past-paper keys refer to the printed letters
            random.Random(f"{sess['date']}{qid}{cid}").shuffle(opts)
        letters = "ABCDEF"
        p["options"] = {letters[i]: o["text"].strip() for i, o in enumerate(opts)}
        p["misconceptions"] = {letters[i]: o.get("misconception", "") for i, o in enumerate(opts)}
        p["correct"] = next(letters[i] for i, o in enumerate(opts) if o.get("correct"))
        p["idk"] = letters[len(opts)]
        if kind == "two-tier":
            out.append("**Answer**")
        out += [f"- [ ] {L}. {txt}" for L, txt in p["options"].items()]
        if kind == "two-tier":
            reasons = list(q["reasons"])
            random.Random(f"{sess['date']}{qid}{cid}r").shuffle(reasons)
            p["reasons"] = {str(i + 1): r["text"].strip() for i, r in enumerate(reasons)}
            p["reason_misconceptions"] = {str(i + 1): r.get("misconception", "") for i, r in enumerate(reasons)}
            p["reason_correct"] = next(str(i + 1) for i, r in enumerate(reasons) if r.get("correct"))
            out += ["", "**Because**"] + [f"- [ ] {k}. {txt}" for k, txt in p["reasons"].items()]
            out.append("")
        out.append(f"- [ ] {p['idk']}. I don't know")
    elif kind == "typed":
        if not str(q.get("answer", "")).strip():
            raise LearnError("A typed question needs \"answer\": a model answer.")
        rubric = [str(x).strip() for x in (q.get("rubric") or []) if str(x).strip()]
        top = max(4, p.get("marks", 0))
        if not 2 <= len(rubric) <= top and not (prof and len(rubric) == 1 == p.get("marks")):
            raise LearnError(f"A typed question needs \"rubric\": 2-{top} key points a correct answer must contain "
                             "(graded point by point; in exam mode, the mark-scheme points with their codes).")
        p["answer"], p["rubric"] = q["answer"].strip(), rubric
        out += ["**Your answer** (type below this line):", ""]
    else:
        raise LearnError("\"type\" must be \"choice\", \"two-tier\" or \"typed\".")
    out.append(f"%% {qid} end %%")
    prev = current_step(s)
    label = {"review": f"> [!question] Review: '{c['title']}', last seen {c['last_seen']}. No theory first: this checks memory.",
             "check": f"> [!question] Quick check: you said you know '{c['title']}'. Right answer = we skip the lesson."
             }.get(prev.get("action") if prev.get("concept") == cid else None)
    if label:
        out = [label, ""] + out
    if label and "Review" in label:
        p["review"] = True
    if prev.get("action") == "practice" and cid in units_of(t).get(prev["concept"], {}).get("concepts", []):
        p["practice"] = prev["concept"]
    sess["pending"][qid] = p
    sess["step"] = None
    sess["followups"] = [f for f in sess.get("followups", []) if f["concept"] != cid]
    append(s, "\n".join(out))
    notice(f"{qid} is ready in your session note")
    print(f"{qid} written to the note.")
    print("WHY: " + ("Spaced review: remembering on a later day is what makes it stick." if label and "Review" in label
                      else "A quick check instead of a lesson." if label else "Active recall right after the theory."))
    _, todo = unit_check_needed(s)
    if todo:
        print(f"NEXT: Unit check not finished: also ask about {', '.join(todo)} (`learn ask <concept>`), then tell the "
              "learner in ONE line that the questions are in the note and STOP.")
        return
    waiting = list(sess["pending"])
    qs = f"{waiting[0]}-{waiting[-1]} are" if len(waiting) > 1 else f"{qid} is"
    print(f"NEXT: Tell the learner in ONE line: \"{qs} in the note. Answer there, then send any message.\" "
          "Then STOP and wait. When they reply, run `learn check`.")


def read_answer(s, qid, p):
    lines = note_lines(s)
    head, end = q_span(lines, qid)
    if p["type"] in ("choice", "two-tier"):
        letters = [m.group(2) for l in lines[head:end] if (m := re.match(r"^\s*- \[(?!\s\])(.)\] ([A-F])\.", l))]
        if p["type"] == "choice":
            return letters
        digits = [m.group(2) for l in lines[head:end] if (m := re.match(r"^\s*- \[(?!\s\])(.)\] ([1-6])\.", l))]
        return letters, digits
    start = next((i for i in range(head, end) if lines[i].startswith("**Your answer**")), None)
    return "\n".join(lines[start + 1:end]).strip() if start is not None else ""

def cmd_check(s, a):
    sess = need_session(s)
    if not sess["pending"]:
        print_next(s, "Nothing is waiting for an answer.")
        return
    for qid, p in list(sess["pending"].items()):
        ans = read_answer(s, qid, p)
        if p["type"] == "two-tier":
            letters, digits = ans
            if p["idk"] in letters:
                print(f"{qid}: I don't know -> idk. " + grade(s, qid, "idk", picked=p["idk"]))
                continue
            if len(letters) != 1 or len(digits) != 1:
                print(f"{qid}: tick exactly one answer (A-C) and one reason (1-3).")
                continue
            ok_a, ok_r = letters[0] == p["correct"], digits[0] == p["reason_correct"]
            result = "correct" if ok_a and ok_r else "wrong"
            kind = None if result == "correct" else ("misconception" if not ok_r else "error")
            what = (p["reason_misconceptions"].get(digits[0]) if not ok_r else p["misconceptions"].get(letters[0], ""))
            reason = grade(s, qid, result, kind=kind, what=what, picked=f"{letters[0]}{digits[0]}")
            print(f"{qid}: learner picked {letters[0]} because {digits[0]} -> {result}. {reason}")
            continue
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
            rub = p.get("rubric") or [p["answer"]]
            print(f"{qid} (typed) learner wrote: {ans!r}\n  Rubric (one mark each):\n" +
                  "\n".join(f"   {i}. {r}" for i, r in enumerate(rub, 1)))
            print(f"NEXT: Mark each rubric point present or absent by meaning, not wording. All points -> "
                  f"`learn grade {qid} correct --marks {len(rub)}/{len(rub)}`; otherwise `learn grade {qid} wrong "
                  f"--marks <got>/{len(rub)} --kind slip|gap|misconception --what \"<what was missing or wrong>\"`; "
                  f"\"don't know\" -> `learn grade {qid} idk`.")
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
    if p["type"] == "two-tier":
        raw = (a.choice or "").strip().upper()
        if raw in ("IDK", "?") or "DON" in raw:
            raw = p["idk"]
        m = re.fullmatch(r"([A-F])\W*([1-6])?", raw)
        if not m or (m.group(1) != p["idk"] and not m.group(2)):
            raise LearnError(f"Two-tier answer looks like 'B2' (answer letter + reason number), or 'idk'.")
        for i in range(head, end):
            if re.match(rf"^\s*- \[.\] {m.group(1)}\.", lines[i]) or (m.group(2) and re.match(rf"^\s*- \[.\] {m.group(2)}\.", lines[i])):
                lines[i] = re.sub(r"\[.\]", "[x]", lines[i], count=1)
    elif p["type"] == "choice":
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
    if a.marks:
        m = re.fullmatch(r"(\d+)/(\d+)", a.marks.strip())
        if not m:
            raise LearnError("--marks looks like 2/3")
        sess["pending"][qid]["marks_got"] = a.marks.strip()
    reason = grade(s, qid, a.result, kind=a.kind, what=a.what or "")
    print(f"{qid}: {a.result}" + (f" ({a.marks} marks)" if a.marks else "") + f". {reason}")
    if sess["pending"]:
        print("NEXT: Run `learn check` for the other waiting question.")
        return
    print_next(s)


def cmd_next(s, a):
    print_next(s)


def cmd_voice(s, a):
    cur = s["profile"].get("voice", DEFAULT_VOICE)
    if not a.voice:
        print(f"Narrator voice: {cur}. English Kokoro voices: {', '.join(KOKORO_EN)}")
        return
    v = a.voice.strip().lower()
    if v not in KOKORO_EN:
        raise LearnError(f"Unknown voice {v!r}. Choose one of: {', '.join(KOKORO_EN)}")
    s["profile"]["voice"] = v
    print(f"Narrator voice set to {v}. New animations use it; existing videos keep their voice.")


def cmd_pref(s, a):
    text = " ".join(a.text).strip()
    if a.topic:
        t = topic_of(s)
        prefs = t.setdefault("prefs", [])
        if text and text not in prefs:
            prefs.append(text)
        print(f"Saved for '{t['title']}' only. {len(prefs)} topic preference(s).")
        return
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
    p = sub.add_parser("start"); p.add_argument("topic", nargs="+"); p.add_argument("--exam")
    p = sub.add_parser("research"); p.add_argument("--save", action="store_true")
    p = sub.add_parser("lit"); p.add_argument("action", choices=["search", "db", "resolve", "text", "guide"])
    p.add_argument("args", nargs="*"); p.add_argument("--sources"); p.add_argument("--max", type=int, default=6)
    p.add_argument("--chars", type=int, default=6000); p.add_argument("--objective")
    p = sub.add_parser("plan"); p.add_argument("--goal"); p.add_argument("--concept", action="append", default=[])
    p.add_argument("--unit", action="append", default=[])
    p.add_argument("--known")
    p = sub.add_parser("known"); p.add_argument("concept")
    p = sub.add_parser("add"); p.add_argument("id"); p.add_argument("title", nargs="+")
    p.add_argument("--prereqs"); p.add_argument("--before")
    p = sub.add_parser("figure"); p.add_argument("name"); p.add_argument("--still", action="store_true")
    p.add_argument("--silent", action="store_true")
    p = sub.add_parser("voice"); p.add_argument("voice", nargs="?")
    p = sub.add_parser("block"); p.add_argument("concept")
    p = sub.add_parser("ask"); p.add_argument("concept")
    sub.add_parser("check")
    p = sub.add_parser("answer"); p.add_argument("qid"); p.add_argument("choice", nargs="?"); p.add_argument("--text")
    p = sub.add_parser("grade"); p.add_argument("qid"); p.add_argument("result", choices=["correct", "wrong", "idk"])
    p.add_argument("--kind", choices=["slip", "gap", "misconception", "error"]); p.add_argument("--what")
    p.add_argument("--marks")
    sub.add_parser("next")
    p = sub.add_parser("pref"); p.add_argument("text", nargs="+"); p.add_argument("--topic", action="store_true")
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
