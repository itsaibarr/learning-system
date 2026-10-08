"""Tests for learn.py: the mastery rules and the seven learner scenarios.

Run: python3 -m unittest discover scripts
"""

import io
import json
import os
import re
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import learn  # noqa: E402

CHOICE = {"type": "choice", "question": "Coin, 2 flips. Chance of at least one head?",
          "why": "None = 1/4, so at least one = 1 - 1/4 = 3/4.",
          "options": [{"text": "0.75", "correct": True},
                      {"text": "0.25", "misconception": "stopped at the none-case and forgot 1 -"},
                      {"text": "0.5", "misconception": "thinks one flip decides it"}]}


VIS = "\n\n```mermaid\nflowchart LR\n  A --> B\n```"
PROB = [("total", "All chances add to 1", "-"), ("none", "Chance of none", "total"),
        ("atleast", "At least one = 1 - none", "none")]
PY = [("for", "For loop", "-"), ("acc", "Running total", "for"), ("sum", "Sum a list", "acc")]


def make_brief(concepts, goal="solve at-least-one problems", sources=3, strong=True):
    rows = "\n".join(f"| {i} | {t} | {b} | S1 |" for i, t, b in concepts)
    src = "\n".join(f"| S{n} | Source {n}, https://example.org/{n} | {'textbook' if strong and n == 1 else 'secondary'} "
                    f"| high | definitions | 2026-10-03 |" for n in range(1, sources + 1))
    return f"""# Research brief: X

Goal: {goal}
Domain: generic

## Concepts
| Id | Concept | Builds on | Sources |
| --- | --- | --- | --- |
{rows}

## Definitions
- **chance**: a number from 0 to 1 [S1]

## Misconceptions
- adding chances of overlapping events -> they overlap [S1]
- stopping at the none-case -> flip with 1 minus [S2]

## Worked examples
- total: coin, 0.5 + 0.5 = 1 [S1]

## Sources
| Id | Source | Type | Reliability | Supports | Retrieved |
| --- | --- | --- | --- | --- | --- |
{src}

## Open questions
- none
"""


_QN = [0]


def fresh_choice(**extra):
    """CHOICE with a stem that shares no 6-word run with earlier questions (the engine rejects copies)."""
    _QN[0] += 1
    n = _QN[0]
    return dict(CHOICE, question=f"Toss {n + 1} coins; is the chance of {n} heads above {n}0 percent?", **extra)


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        learn.STATE = root / "state" / "learner.json"
        learn.VAULT = root / "vault"
        os.environ.update(LEARN_NO_CLI="1", LEARN_NO_GIT="1", LEARN_TODAY="2026-10-03", LEARN_REQUIRE_MANIM="0",
                          LEARN_TTS="fake", LEARN_MANIM_QUALITY="-ql")

    def tearDown(self):
        self.tmp.cleanup()
        os.environ.pop("LEARN_TODAY", None)

    def day(self, d):
        os.environ["LEARN_TODAY"] = d

    def run_cmd(self, *args, stdin="", ok=True):
        out, err = io.StringIO(), io.StringIO()
        old = sys.stdin
        sys.stdin = io.StringIO(stdin)
        try:
            with redirect_stdout(out), redirect_stderr(err):
                code = learn.main(list(args))
        finally:
            sys.stdin = old
        if ok:
            self.assertEqual(code, 0, err.getvalue())
        else:
            self.assertEqual(code, 1, "expected an error")
        return out.getvalue() + err.getvalue()

    def state(self):
        return json.loads(learn.STATE.read_text())

    def note(self):
        return (learn.VAULT / self.state()["session"]["note"]).read_text()

    def concept(self, cid, topic=None):
        s = self.state()
        return s["topics"][topic or s["session"]["topic"]]["concepts"][cid]

    def tick(self, qid, which):
        """Tick a box in the note the way the learner does in Obsidian. which: correct|wrong|idk."""
        p = self.state()["session"]["pending"][qid]
        letter = {"correct": p["correct"], "idk": p["idk"],
                  "wrong": next(L for L in p["options"] if L != p["correct"])}[which]
        path = learn.VAULT / self.state()["session"]["note"]
        lines = path.read_text().split("\n")
        head, end = learn.q_span(lines, qid)
        for i in range(head, end):
            lines[i] = lines[i].replace(f"- [ ] {letter}.", f"- [x] {letter}.")
        path.write_text("\n".join(lines))
        return self.run_cmd("check")

    def research(self, concepts=PROB):
        return self.run_cmd("research", "--save", stdin=make_brief(concepts))

    def start_topic(self, *words, concepts=PROB):
        self.run_cmd("start", *words)
        self.research(concepts)

    def teach_and_ask(self, cid, block="Short theory. [S1]" + VIS, q=None):
        q = q or fresh_choice()
        self.run_cmd("block", cid, stdin=block)
        out = self.run_cmd("ask", cid, stdin=json.dumps(q))
        return re.search(r"(Q\d+) written", out).group(1)

    def answer(self, cid, which, teach=False, level=2):
        if teach:
            self.run_cmd("block", cid, stdin="Theory again. [S1]" + VIS)
        q = fresh_choice(level=level)
        qid = re.search(r"(Q\d+) written", self.run_cmd("ask", cid, stdin=json.dumps(q))).group(1)
        return self.tick(qid, which)

    def start_planned(self):
        self.start_topic("Probability", "basics")
        self.run_cmd("plan", "--goal", "solve at-least-one problems",
                     "--concept", "total|All chances add to 1",
                     "--concept", "none|Chance of none|total",
                     "--concept", "atleast|At least one = 1 - none|none", "--known", "none")


class TestNewLearner(Base):
    def test_new_topic_asks_for_goal_then_teaches_roots_first(self):
        out = self.run_cmd("start", "Probability", "basics")
        self.assertIn("no research brief yet", out)
        self.assertIn("ask ONE plain question", out)
        self.assertIn("Theory first, then questions", out)  # preferences are in every briefing
        self.assertTrue((learn.VAULT / "Sessions" / "Sessions.base").exists())
        self.start_planned()
        out = self.run_cmd("next")
        self.assertIn("'All chances add to 1'", out)
        self.assertIn("starting point", out)
        self.assertIn("```mermaid", self.note())

    def test_cannot_ask_before_teaching(self):
        self.start_planned()
        out = self.run_cmd("ask", "total", stdin=json.dumps(fresh_choice()), ok=False)
        self.assertIn("has not been taught yet", out)

    def test_answer_key_not_in_note_until_graded(self):
        self.start_planned()
        qid = self.teach_and_ask("total")
        self.assertNotIn("1 - 1/4 = 3/4", self.note())
        self.assertIn("I don't know", self.note())
        self.tick(qid, "correct")
        self.assertIn("1 - 1/4 = 3/4", self.note())

    def test_one_application_answer_makes_solid_and_unlocks_next(self):
        self.start_planned()
        out = self.answer("total", "correct", teach=True, level=1)
        self.assertIn("recall only", out)
        out = self.answer("total", "correct", level=2)
        self.assertIn("applied to a new scenario", out)
        c = self.concept("total")
        self.assertEqual((c["status"], c["box"], c["next_review"]), ("solid", 1, "2026-10-04"))
        self.assertIn("'Chance of none'", out)

    def test_block_word_limit(self):
        self.start_planned()
        self.assertIn("limit is", self.run_cmd("block", "total", stdin="word " * 300 + "[S1]" + VIS, ok=False))

    def test_bad_question_json_is_rejected(self):
        self.start_planned()
        self.run_cmd("block", "total", stdin="x [S1]" + VIS)
        bad = fresh_choice(options=[{"text": "a", "correct": True}, {"text": "b"}, {"text": "c", "misconception": "x"}])
        self.assertIn("needs a \"misconception\"", self.run_cmd("ask", "total", stdin=json.dumps(bad), ok=False))


    def test_recall_only_is_not_solid(self):
        self.start_planned()
        self.answer("total", "correct", teach=True, level=1)
        out = self.answer("total", "correct", level=1)
        self.assertIn("applies it to a new scenario (level 2)", out)
        self.assertEqual(self.concept("total")["status"], "learning")
        self.answer("total", "correct", level=2)
        self.assertEqual(self.concept("total")["status"], "solid")


class TestResearchGate(Base):
    def test_cannot_plan_before_research(self):
        self.run_cmd("start", "Quantum", "tunnelling")
        out = self.run_cmd("plan", "--concept", "total", "--known", "none", ok=False)
        self.assertIn("no research brief", out)

    def test_brief_validation_lists_every_problem(self):
        self.run_cmd("start", "Quantum", "tunnelling")
        bad = make_brief(PROB, sources=2, strong=False).replace("## Open questions\n- none\n", "") + "\nSee [S9]."
        out = self.run_cmd("research", "--save", stdin=bad, ok=False)
        for msg in ("at least 3 sources", "primary, textbook or review", "Open questions", "S9 is cited"):
            self.assertIn(msg, out)

    def test_brief_lands_in_vault_and_sets_goal(self):
        self.start_topic("Probability", "basics")
        s = self.state()
        self.assertTrue((learn.VAULT / "Sources" / "Probability basics research brief.md").exists())
        self.assertEqual(s["topics"]["probability-basics"]["goal"], "solve at-least-one problems")
        self.assertIn("[!info] Research brief", self.note())

    def test_plan_uses_brief_ids_titles_and_prereqs(self):
        self.start_topic("Probability", "basics")
        out = self.run_cmd("plan", "--concept", "magic", "--known", "none", ok=False)
        self.assertIn("not in the research brief", out)
        self.assertIn("not in the plan", self.run_cmd("plan", "--concept", "none", "--known", "none", ok=False))
        self.run_cmd("plan", "--concept", "none", "--concept", "total", "--known", "none")
        self.assertEqual(self.concept("none")["prereqs"], ["total"])
        self.assertEqual(self.concept("total")["title"], "All chances add to 1")

    def test_block_must_cite_brief_sources(self):
        self.start_planned()
        self.assertIn("Cite the research brief", self.run_cmd("block", "total", stdin="No source.", ok=False))
        self.assertIn("S7 not in the research brief", self.run_cmd("block", "total", stdin="x [S7]", ok=False))
        self.run_cmd("block", "total", stdin="All ways add to 1 [S1]." + VIS)
        self.assertIn("> [!quote]- Sources\n> S1: Source 1, https://example.org/1 (textbook)", self.note())

    def test_lit_without_praxist_explains_fallback(self):
        import builtins
        real = builtins.__import__

        def fake(name, *a, **k):
            if name.startswith("praxist"):
                raise ImportError(name)
            return real(name, *a, **k)
        builtins.__import__ = fake
        try:
            self.assertIn("PRAXIST is not installed", self.run_cmd("lit", "search", "x", ok=False))
        finally:
            builtins.__import__ = real


PNG_OK = """
import matplotlib.pyplot as plt
fig, ax = plt.subplots(figsize=(3, 2))
ax.plot([0, 1, 2], [0, 1, 0])
ax.text(0.2, 0.5, "1 rise"); ax.text(1.5, 0.5, "2 fall")
fig.savefig(OUT_PNG, dpi=60)
"""
GIF_OK = """
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
fig, ax = plt.subplots(figsize=(2, 2))
dot, = ax.plot([0], [0], "o"); ax.set_xlim(0, 3)
anim = FuncAnimation(fig, lambda k: dot.set_data([k], [0]), frames=3)
anim.save(OUT_GIF, writer=PillowWriter(fps=2), dpi=40)
"""


class TestVisuals(Base):
    def test_block_needs_a_visual(self):
        self.start_planned()
        out = self.run_cmd("block", "total", stdin="Plain text only [S1].", ok=False)
        self.assertIn("needs a Manim visual", out)

    def test_figure_png_lands_in_vault_and_embeds(self):
        self.start_planned()
        out = self.run_cmd("figure", "Rise and fall", stdin=PNG_OK)
        embed = re.search(r"EMBED: (!\[\[.+\]\])", out).group(1)
        self.assertEqual(embed, "![[Attachments/learn/probability-basics/rise-and-fall.png]]")
        self.assertTrue((learn.VAULT / "Attachments/learn/probability-basics/rise-and-fall.png").exists())
        self.run_cmd("block", "total", stdin=f"{embed}\n\nThe curve rises then falls [S1].")
        self.assertIn(embed, self.note())

    def test_figure_gif_animation(self):
        self.start_planned()
        out = self.run_cmd("figure", "dot", stdin=GIF_OK)
        self.assertIn("dot.gif", out)

    def test_figure_errors_are_explained(self):
        self.start_planned()
        self.assertIn("Figure script failed", self.run_cmd("figure", "x", stdin="raise ValueError('boom')", ok=False))
        self.assertIn("save exactly one file", self.run_cmd("figure", "x", stdin="import matplotlib.pyplot as plt\nplt.figure()", ok=False))
        overlap = PNG_OK.replace('ax.text(1.5, 0.5, "2 fall")', 'ax.text(0.2, 0.5, "2 fall")')
        self.assertIn("Labels collide", self.run_cmd("figure", "x", stdin=overlap, ok=False))
        on_line = PNG_OK.replace('ax.text(1.5, 0.5, "2 fall")', 'ax.text(0.9, 0.95, "2 fall")')
        self.assertIn("sits on top of a plotted line", self.run_cmd("figure", "x", stdin=on_line, ok=False))

    def test_missing_figure_embed_rejected(self):
        self.start_planned()
        out = self.run_cmd("block", "total", stdin="![[Attachments/learn/nope.png]] [S1]", ok=False)
        self.assertIn("Embedded figure not found", out)

    def test_broken_mermaid_rejected_when_obsidian_says_so(self):
        self.start_planned()
        real = learn.cli_eval
        learn.cli_eval = lambda js: "ERR Parse error on line 2"
        try:
            out = self.run_cmd("block", "total", stdin="x [S1]" + VIS, ok=False)
        finally:
            learn.cli_eval = real
        self.assertIn("Mermaid would not render", out)

    def test_canvas_map_follows_progress(self):
        self.start_planned()
        path = learn.VAULT / "Maps" / "Probability basics map.canvas"
        self.assertIn("![[Maps/Probability basics map.canvas]]", self.note())
        nodes = {n["id"]: n for n in json.loads(path.read_text())["nodes"]}
        self.assertNotIn("color", nodes["total"])
        self.assertEqual(nodes["none"]["x"], 340)  # one column right of its prerequisite
        self.run_cmd("block", "total", stdin="t [S1]" + VIS)
        nodes = {n["id"]: n for n in json.loads(path.read_text())["nodes"]}
        self.assertEqual(nodes["total"]["color"], "3")  # yellow = learning, right after the block
        self.answer("total", "correct")
        self.answer("total", "correct")
        nodes = {n["id"]: n for n in json.loads(path.read_text())["nodes"]}
        self.assertEqual(nodes["total"]["color"], "4")  # green = solid

    def test_question_can_show_a_figure(self):
        self.start_planned()
        embed = re.search(r"EMBED: (!\[\[.+\]\])", self.run_cmd("figure", "q1", stdin=PNG_OK)).group(1)
        self.run_cmd("block", "total", stdin=embed + " [S1]")
        self.run_cmd("ask", "total", stdin=json.dumps(fresh_choice(figure=embed)))
        head = self.note().split("### Q1")[1]
        self.assertIn(embed, head.split("- [ ]")[0])
        bad = fresh_choice(figure="![[nope.png]]")
        self.assertIn('"figure" must be', self.run_cmd("ask", "total", stdin=json.dumps(bad), ok=False))

    @unittest.skipUnless(learn.MANIM.exists(), "Manim not installed (scripts/install.sh)")
    def test_every_template_in_visuals_guide_renders(self):
        guide = Path(__file__).resolve().parent.parent / "skills/teach-understanding/references/visuals.md"
        templates = [t for t in re.findall(r"```python\n(.*?)```", guide.read_text(), re.S) if "TEMPLATE" in t or "OUT_PNG" in t]
        self.assertGreaterEqual(sum("from manim import" in t for t in templates), 5)
        self.start_planned()
        for n, code in enumerate(templates, 1):
            args = ["--still"] if "--still" in code.splitlines()[0] else []
            out = self.run_cmd("figure", f"template-{n}", *args, stdin=code)
            self.assertIn("EMBED:", out, f"template {n} failed")

    def test_new_default_preferences_reach_existing_learners(self):
        self.start_planned()
        st = self.state()
        st["profile"]["preferences"] = st["profile"]["preferences"][:2]
        learn.STATE.write_text(json.dumps(st))
        self.assertIn("Visual learner", self.run_cmd("start", "Probability", "basics"))


MANIM_OK = """
from manim import *
NARRATION = ["The squeeze of air moves along the tube while each bit of air only rocks in place."]
class Ok(Scene):
    def construct(self):
        self.play(Write(Text("pressure wave", font_size=32).to_edge(UP)))
        self.wait(1.5)
"""
MANIM_OVERLAP = """
from manim import *
NARRATION = ["Two labels sit on top of each other here, which the engine must catch."]
class Bad(Scene):
    def construct(self):
        self.play(Write(Text("pressure wave")), Write(Text("air stays").shift(0.1 * RIGHT)))
        self.wait(1.5)
"""
MPL_OK = "import matplotlib.pyplot as plt\nfig, ax = plt.subplots()\nax.plot([0, 1])\nfig.savefig(OUT_PNG, dpi=40)\n"


class TestManim(Base):
    def setUp(self):
        super().setUp()
        os.environ["LEARN_REQUIRE_MANIM"] = "1"

    def test_old_manimgl_code_is_rejected_before_rendering(self):
        self.start_planned()
        out = self.run_cmd("figure", "x", stdin="from manimlib import *\nclass A(Scene):\n    def construct(self):\n"
                                                  "        self.play(ShowCreation(Circle()))\n", ok=False)
        self.assertIn("ShowCreation -> Create", out)
        self.assertEqual(self.state()["session"]["manim_failures"], 1)

    def test_matplotlib_is_locked_until_three_manim_failures(self):
        self.start_planned()
        self.assertIn("matplotlib unlocks only after 3", self.run_cmd("figure", "m", stdin=MPL_OK, ok=False))
        for _ in range(3):
            self.run_cmd("figure", "x", stdin="from manimlib import *\n", ok=False)
        self.assertIn("(matplotlib)", self.run_cmd("figure", "m", stdin=MPL_OK))

    def test_block_requires_a_manim_figure(self):
        self.start_planned()
        out = self.run_cmd("block", "total", stdin="x [S1]" + VIS, ok=False)
        self.assertIn("needs a Manim visual", out)

    @unittest.skipUnless(learn.MANIM.exists(), "Manim not installed")
    def test_manim_video_and_still_render_and_unlock_the_block(self):
        self.start_planned()
        self.run_cmd("figure", "x", stdin="from manimlib import *\n", ok=False)
        out = self.run_cmd("figure", "wave", stdin=MANIM_OK)
        self.assertIn("wave.mp4 (manim)", out)
        self.assertEqual(self.state()["session"]["manim_failures"], 0)
        self.assertIn("still.png (manim)", self.run_cmd("figure", "still", "--still", stdin=MANIM_OK))
        embed = re.search(r"EMBED: (!\[\[.+\]\])", out).group(1)
        self.run_cmd("block", "total", stdin=f"{embed}\n\nThe push travels [S1].")
        self.assertIn(embed, self.note())

    @unittest.skipUnless(learn.MANIM.exists(), "Manim not installed")
    def test_overlapping_text_is_caught_during_the_animation(self):
        self.start_planned()
        out = self.run_cmd("figure", "bad", stdin=MANIM_OVERLAP, ok=False)
        self.assertIn("'pressure wave' overlaps 'air stays'", out)

    def test_old_visual_preference_is_replaced(self):
        self.start_planned()
        st = self.state()
        old = next(iter(learn.SUPERSEDED_PREFS))
        st["profile"]["preferences"].append(old)
        learn.STATE.write_text(json.dumps(st))
        out = self.run_cmd("start", "Probability", "basics")
        self.assertNotIn(old, out)
        self.assertEqual(out.count("Visual learner"), 1)


MANIM_STEPS = """
from manim import *
NARRATION = ["First the client asks the server whether it may open a connection.",
             "Then the server agrees and asks for a connection in the other direction too."]
class Steps(Scene):
    def construct(self):
        cap = Text("1  client asks", font_size=30).to_edge(UP)
        self.play(Write(cap))
        self.wait(0.5)
        self.play(Transform(cap, Text("2  server answers", font_size=30).to_edge(UP)))
        self.wait(1)
"""


def has_audio(path):
    import subprocess
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries", "stream=codec_name",
                        "-of", "csv=p=0", str(path)], capture_output=True, text=True)
    return bool(r.stdout.strip())


class TestNarrationRules(Base):
    def test_schedule_fits_without_holds(self):
        starts, holds, total = learn.schedule([0.0, 5.0], [2.0, 2.0], 10.0)
        self.assertEqual(holds, [])
        self.assertAlmostEqual(starts[1], 5.1)
        self.assertEqual(total, 10.0)

    def test_schedule_freezes_the_next_step_until_the_voice_finishes(self):
        starts, holds, total = learn.schedule([0.0, 2.0], [5.0, 1.0], 4.0)
        self.assertEqual(holds[0][0], 2.0)               # frozen right where step 2 would start
        self.assertAlmostEqual(starts[1], 0.30 + 5.0 + 0.35)  # first mark clamps to 0.05
        self.assertAlmostEqual(total, 4.0 + sum(h for _, h in holds))

    def test_captions_shown_together_are_spoken_back_to_back(self):
        starts, holds, _ = learn.schedule([0.0, 0.0], [3.0, 3.0], 10.0)
        self.assertEqual(holds, [])
        self.assertAlmostEqual(starts[1], 0.30 + 3.0 + 0.35)

    def test_schedule_holds_the_end_when_speech_is_longer(self):
        _, holds, total = learn.schedule(None, [6.0, 6.0], 5.0)
        self.assertEqual(holds[0][0], 5.0)
        self.assertGreater(total, 12.0)

    def test_narration_parsing_and_rules(self):
        self.assertEqual(learn.narration_of('NARRATION = ["a b c d", "e f g h"]\n'), ["a b c d", "e f g h"])
        self.assertIsNone(learn.narration_of("x = 1\n"))
        with self.assertRaises(learn.LearnError):
            learn.narration_of("NARRATION = [f'{x}']\n")
        for bad, msg in [(r"lambda equals \\frac v f here now", "spoken words"),
                         ("this sentence cites the brief [S1] for sure", "citation"),
                         ("word " * 80, "4-40 words"), ("**bold** words are not speech", "markdown")]:
            with self.assertRaises(learn.LearnError) as e:
                learn.validate_narration([bad])
            self.assertIn(msg, str(e.exception))

    def test_alignment_needs_one_line_per_caption_and_no_label_reading(self):
        marks = {1: [0.0, "1  the squeeze travels"], 2: [3.0, "2  the molecule wobbles"]}
        with self.assertRaises(learn.LearnError) as e:
            learn.align_narration(["only one line here for two captions"], marks)
        self.assertIn("one narration line per numbered caption", str(e.exception))
        with self.assertRaises(learn.LearnError) as e:
            learn.align_narration(["The squeeze travels.", "Follow the red dot: it only rocks around its spot."], marks)
        self.assertIn("only reads its caption", str(e.exception))
        self.assertEqual(learn.align_narration(["Watch the crowded air move right: that is sound.",
                                                "The red dot only rocks back and forth in place."], marks), [0.0, 3.0])
        self.assertIsNone(learn.align_narration(["x y z w"], {}))

    def test_missing_narration_is_rejected_before_rendering(self):
        os.environ["LEARN_REQUIRE_MANIM"] = "1"
        self.start_planned()
        out = self.run_cmd("figure", "x", stdin=MANIM_OK.replace("NARRATION", "_UNUSED"), ok=False)
        self.assertIn("no NARRATION", out)
        self.assertEqual(self.state()["session"].get("manim_failures", 0), 0)

    def test_voice_setting(self):
        self.start_planned()
        self.assertIn("af_heart", self.run_cmd("voice"))
        self.run_cmd("voice", "bm_george")
        self.assertEqual(self.state()["profile"]["voice"], "bm_george")
        self.assertIn("Unknown voice", self.run_cmd("voice", "darth", ok=False))


@unittest.skipUnless(learn.MANIM.exists(), "Manim not installed")
class TestNarratedVideo(Base):
    def test_narrated_video_has_audio_synced_to_captions_and_a_transcript(self):
        self.start_planned()
        os.environ["LEARN_DEBUG_SYNC"] = "1"
        try:
            out = self.run_cmd("figure", "steps", stdin=MANIM_STEPS)
        finally:
            os.environ.pop("LEARN_DEBUG_SYNC")
        self.assertIn("step-synced to the numbered captions", out)
        marks = re.search(r"marks=\[([0-9.]+), ([0-9.]+)\]", out)
        self.assertLess(float(marks.group(1)), float(marks.group(2)))
        rel = "Attachments/learn/probability-basics/steps.mp4"
        self.assertTrue(has_audio(learn.VAULT / rel))
        self.assertEqual(len(self.state()["narrations"][rel]), 2)
        self.run_cmd("block", "total", stdin=f"![[{rel}]]\n\nThe client asks first [S1].")
        self.assertIn("> [!quote]- Narration (what the voice says)\n> 1. First the client asks", self.note())

    def test_silent_flag_and_still_have_no_voice(self):
        self.start_planned()
        self.run_cmd("figure", "quiet", "--silent", stdin=MANIM_STEPS)
        self.assertFalse(has_audio(learn.VAULT / "Attachments/learn/probability-basics/quiet.mp4"))
        self.assertIn("still.png", self.run_cmd("figure", "still", "--still", stdin=MANIM_STEPS))

    def test_tts_down_keeps_the_silent_video_and_warns(self):
        self.start_planned()
        os.environ.update(LEARN_TTS="voicebox", LEARN_VOICEBOX_AUTOSTART="0")
        real = learn.VOICEBOX_URL
        learn.VOICEBOX_URL = "http://127.0.0.1:9"
        try:
            out = self.run_cmd("figure", "steps", stdin=MANIM_STEPS)
        finally:
            learn.VOICEBOX_URL = real
            os.environ.update(LEARN_TTS="fake")
            os.environ.pop("LEARN_VOICEBOX_AUTOSTART")
        self.assertIn("WARNING: narration failed", out)
        rel = "Attachments/learn/probability-basics/steps.mp4"
        self.assertTrue((learn.VAULT / rel).exists())
        self.assertFalse(has_audio(learn.VAULT / rel))
        self.assertNotIn(rel, self.state().get("narrations", {}))

    @unittest.skipUnless(os.environ.get("LEARN_TEST_VOICEBOX"), "set LEARN_TEST_VOICEBOX=1 to use the real voice")
    def test_real_voicebox_voice(self):
        self.start_planned()
        os.environ["LEARN_TTS"] = "voicebox"
        out = self.run_cmd("figure", "real", stdin=MANIM_STEPS)
        self.assertIn("voice af_heart", out)
        self.assertTrue(has_audio(learn.VAULT / "Attachments/learn/probability-basics/real.mp4"))


UNIT_BLOCK = """**Big idea:** every chance is a share of one whole, so 'none' and 'at least one' split it.

**Key terms:**
- **total**: all the ways together make 1 [S1]
- **complement**: the ways an event does not happen [S1]

### All the ways make one
```mermaid
flowchart LR
  A --> B
```
1. List every way it can turn out.
2. Their chances add to 1.

### None and at least one
![[FIG]]
| case | chance |
| --- | --- |
| none | (5/6)^3 |
| at least one | 1 - (5/6)^3 |
"""

TWO_TIER = {"type": "two-tier", "level": 2,
            "question": "A bag has 3 red and 5 blue beads; what is P(not red) for one draw?",
            "options": [{"text": "5/8", "correct": True},
                        {"text": "3/8", "misconception": "gives P(red)"},
                        {"text": "5/3", "misconception": "divides blue by red"}],
            "reasons": [{"text": "All outcomes add to 1", "correct": True},
                        {"text": "Blue beads outnumber red", "misconception": "compares counts, not shares"},
                        {"text": "Each colour is half", "misconception": "treats colours as equally likely"}],
            "why": "P(not red) = 1 - 3/8 = 5/8 because all outcomes add to 1."}


MANIM_VOICE = """
from manim import *
NARRATION = ["First the client asks the server whether it may open a connection.",
             "Then the server agrees and asks for a connection back."]
class Voiced(Scene):
    def construct(self):
        a = Circle(); b = Square().shift(2 * RIGHT)
        with self.voice(1):
            self.play(Create(a), run_time=0.5)
        with self.voice(2) as d:
            self.play(Create(b), run_time=d)
"""


@unittest.skipUnless(learn.MANIM.exists(), "Manim not installed")
class TestAudioFirst(Base):
    def test_voice_blocks_follow_the_real_line_lengths(self):
        self.start_planned()
        os.environ["LEARN_DEBUG_SYNC"] = "1"
        try:
            out = self.run_cmd("figure", "voiced", stdin=MANIM_VOICE)
        finally:
            os.environ.pop("LEARN_DEBUG_SYNC")
        self.assertIn("audio-first", out)
        marks = [float(x) for x in re.search(r"marks=\[([^\]]*)\]", out).group(1).split(",")]
        durs = [float(x) for x in re.search(r"durations=\[([^\]]*)\]", out).group(1).split(",")]
        self.assertAlmostEqual(marks[1] - marks[0], durs[0] + learn.NARR_GAP, delta=0.1)   # block 1 = line 1 + gap
        rel = "Attachments/learn/probability-basics/voiced.mp4"
        self.assertTrue(has_audio(learn.VAULT / rel))

    def test_voice_blocks_must_match_narration(self):
        self.start_planned()
        bad = MANIM_VOICE.replace("with self.voice(2) as d:", "with self.voice(1) as d:")
        out = self.run_cmd("figure", "voiced", stdin=bad, ok=False)
        self.assertIn("voice blocks", out)
        self.assertEqual(self.state()["session"].get("manim_failures", 0), 0)


class TestUnits(Base):
    def plan_unit(self):
        self.start_topic("Probability", "basics")
        return self.run_cmd("plan", "--unit", "basics|Chance basics|total,none", "--concept", "atleast",
                            "--known", "none")

    def test_plan_groups_concepts_into_units_and_teaches_the_unit_first(self):
        out = self.plan_unit()
        self.assertIn("3 concepts in 2 unit(s)", out)
        self.assertIn("Teach the whole unit 'Chance basics' in ONE block", out)
        self.assertIn("No questions until the block is in the note", out)

    def test_unit_size_is_bounded(self):
        self.start_topic("Probability", "basics")
        out = self.run_cmd("plan", "--unit", "big|Big|total,none,atleast,total,none,atleast", "--known", "none", ok=False)
        self.assertIn("a unit holds 1-5", out)

    def test_unit_block_needs_structure(self):
        self.plan_unit()
        out = self.run_cmd("block", "basics", stdin="Some words [S1]." + VIS, ok=False)
        for msg in ("Big idea", "Key terms", "segments"):
            self.assertIn(msg, out)
        long_para = UNIT_BLOCK.replace("FIG", "x") + "\n" + "word " * 70 + "[S1]\n"
        self.assertIn("-word paragraph", self.run_cmd("block", "basics", stdin=long_para, ok=False))

    def test_unit_check_one_question_per_concept_with_an_open_item(self):
        self.plan_unit()
        self.run_cmd("block", "basics", stdin=UNIT_BLOCK.replace("![[FIG]]", VIS))
        self.assertTrue(all(self.concept(c)["taught"] for c in ("total", "none")))
        out = self.run_cmd("next")
        self.assertIn("Unit check for 'Chance basics'", out)
        q1 = re.search(r"(Q\d+) written", self.run_cmd("ask", "total", stdin=json.dumps(fresh_choice(level=2)))).group(1)
        out = self.run_cmd("ask", "none", stdin=json.dumps(fresh_choice(level=2)), ok=False)
        self.assertIn("at least one two-tier", out)
        out = self.run_cmd("ask", "none", stdin=json.dumps(TWO_TIER))
        q2 = re.search(r"(Q\d+) written", out).group(1)
        self.assertIn("Answer there", out)
        self.tick(q1, "correct")
        self.run_cmd("answer", q2, "A1")
        st = self.state()
        self.assertIn(self.concept("total")["status"], learn.SOLID)

    def test_two_tier_wrong_reason_is_a_misconception(self):
        self.start_planned()
        self.run_cmd("block", "total", stdin="t [S1]" + VIS)
        qid = re.search(r"(Q\d+) written", self.run_cmd("ask", "total", stdin=json.dumps(TWO_TIER))).group(1)
        p = self.state()["session"]["pending"][qid]
        wrong_reason = next(k for k in p["reasons"] if k != p["reason_correct"])
        out = self.run_cmd("answer", qid, p["correct"] + wrong_reason)
        self.assertIn("-> wrong", out)
        self.assertEqual(self.state()["mistakes"][-1]["kind"], "misconception")
        self.assertIn("reason " + wrong_reason + " is the belief", self.note())

    def test_wrong_answers_in_a_unit_check_queue_followups(self):
        self.plan_unit()
        self.run_cmd("block", "basics", stdin=UNIT_BLOCK.replace("![[FIG]]", VIS))
        q1 = re.search(r"(Q\d+) written", self.run_cmd("ask", "total", stdin=json.dumps(fresh_choice(level=2)))).group(1)
        q2 = re.search(r"(Q\d+) written", self.run_cmd("ask", "none", stdin=json.dumps(TWO_TIER))).group(1)
        self.tick(q1, "wrong")
        out = self.run_cmd("answer", q2, "idk")
        self.assertIn("Re-teach", out)   # followups take over once the whole check is graded

    def test_difficulty_band(self):
        self.start_planned()
        s = self.state(); s["session"]["recent"] = ["correct"] * 10; learn.STATE.write_text(json.dumps(s))
        self.assertIn("too easy", learn.band_note(learn.load()))
        s["session"]["recent"] = ["wrong"] * 6 + ["correct"] * 4; learn.STATE.write_text(json.dumps(s))
        self.assertIn("too hard", learn.band_note(learn.load()))


class TestItemFlaws(Base):
    def opts(self, key, *dis):
        return [{"text": key, "correct": True}] + [{"text": d, "misconception": "m"} for d in dis]

    def test_each_flaw_is_caught(self):
        f = learn.item_problems
        self.assertIn("longer", " ".join(f("Which is right?", self.opts(
            "It is owned by a provider for general access by anyone", "It is a hard drive", "It is local"))))
        self.assertIn("ending in '?'", " ".join(f("Pick the right one", self.opts("aa", "bb", "cc"))))
        self.assertIn("negative stem", " ".join(f("Which is NOT a LAN device?", self.opts("aa", "bb", "cc"))))
        self.assertIn("of the above", " ".join(f("Which?", self.opts("aa", "all of the above", "cc"))))
        self.assertIn("absolute word", " ".join(f("Which?", self.opts("it can vary", "it never varies", "it varies"))))
        self.assertIn("wording cue", " ".join(f("Why does packet switching share bandwidth?", self.opts(
            "packets share bandwidth links", "circuits reserve a line", "routers store calls"))))
        self.assertEqual(f("What is P(not six) for one roll?", self.opts("5/6", "1/6", "6/5")), [])


EXAM_EXTRA = """
## Syllabus points
- 1.2.2: express derived units as products or quotients of the SI base units [S4]

## Paper patterns
| Id | Syllabus point | Pattern | Command words | Marks | Real questions | Mark scheme |
| --- | --- | --- | --- | --- | --- | --- |
| P1 | 1.2.2 | equation with one unknown constant | Determine | 3 | 9702/21/M/J/23 Q1(b); 9702/22/M/J/23 Q1(b) | C1 base units, A1 answer |

## Examiner-report errors
- 9702/21/M/J/23 Q1(b): "hertz used as a base unit" (significant number) [S4]
"""
EXAM_SOURCES = """| S4 | 9702 syllabus 2025-2027, https://www.cambridgeinternational.org/Images/664565-2025-2027-syllabus.pdf | syllabus | high | outcomes | 2026-10-08 |
| S5 | 9702_s23_qp_21, https://pastpapers.papacambridge.com/directories/CAIE/CAIE-pastpapers/upload/9702_s23_qp_21.pdf | past-paper | high | questions | 2026-10-08 |
| S6 | 9702_s23_ms_21, https://pastpapers.papacambridge.com/directories/CAIE/CAIE-pastpapers/upload/9702_s23_ms_21.pdf | mark-scheme | high | marking | 2026-10-08 |
"""


def exam_brief():
    b = make_brief(PROB)
    b = b.replace("\n## Open questions", EXAM_EXTRA + "\n## Open questions")
    return b.replace("\n\n## Open questions", "\n" + EXAM_SOURCES + "\n## Open questions", 1) \
        if False else b.replace("| 2026-10-03 |\n\n## Syllabus", "| 2026-10-03 |\n" + EXAM_SOURCES + "\n## Syllabus", 1)


class TestExamMode(Base):
    def start_exam(self):
        self.run_cmd("start", "Physics", "units", "--exam", "cambridge-as-a-level")
        brief = exam_brief()
        self.assertIn("9702_s23_ms_21", brief)
        self.run_cmd("research", "--save", stdin=brief)
        self.run_cmd("plan", "--concept", "total", "--concept", "none", "--concept", "atleast", "--known", "none")

    def test_start_refuses_a_sentence_as_topic(self):
        out = self.run_cmd("start", "probability basics. Teach the next unit and ask its unit check, then stop.", ok=False)
        self.assertIn("looks like a message", out)
        self.assertFalse(learn.STATE.exists())

    def test_profile_and_mode(self):
        prof = learn.exam_profile("cambridge-as-a-level")
        self.assertTrue(prof["re"].fullmatch("9702/21/M/J/24 Q2(b)(iii)"))
        self.assertTrue(learn.exam_profile("pearson-edexcel-ial")["re"].fullmatch("WMA11/01 June 2024 Q2(ii)"))
        self.assertIn("No exam profile", self.run_cmd("start", "x", "--exam", "nope", ok=False))

    def test_exam_brief_needs_patterns_from_real_questions(self):
        self.run_cmd("start", "Physics", "units", "--exam", "cambridge-as-a-level")
        out = self.run_cmd("research", "--save", stdin=make_brief(PROB), ok=False)
        for msg in ("Syllabus points", "Paper patterns", "past-paper"):
            self.assertIn(msg, out)
        one_ref = exam_brief().replace("; 9702/22/M/J/23 Q1(b)", "")
        self.assertIn("needs 2+ real past-paper questions", self.run_cmd("research", "--save", stdin=one_ref, ok=False))

    def test_existing_topic_switched_to_exam_mode_must_upgrade_its_brief(self):
        self.start_planned()
        out = self.run_cmd("start", "Probability", "basics", "--exam", "cambridge-as-a-level")
        self.assertIn("exam mode", out)
        self.assertIn("Never invent a question pattern", out)

    def test_exam_questions_need_a_real_source_and_marks(self):
        self.start_exam()
        self.run_cmd("block", "total", stdin="t [S1]" + VIS)
        q = fresh_choice(level=2)
        self.assertIn("\"marks\"", self.run_cmd("ask", "total", stdin=json.dumps(q), ok=False))
        self.assertIn("must be a real question", self.run_cmd("ask", "total", stdin=json.dumps(dict(q, marks=1, source="my own")), ok=False))
        self.assertIn("not among the brief", self.run_cmd("ask", "total", stdin=json.dumps(dict(q, marks=1, source="9702/11/O/N/19 Q4")), ok=False))
        four = dict(q, marks=1, source="9702/21/M/J/23 Q1(b)", question="Which quantity is a base quantity",
                    options=[{"text": "mass", "correct": True}, {"text": "force", "misconception": "derived"},
                             {"text": "speed", "misconception": "derived"}, {"text": "charge", "misconception": "derived"}])
        out = self.run_cmd("ask", "total", stdin=json.dumps(four))   # authentic item: kept as printed
        self.assertIn("9702/21/M/J/23 Q1(b) · [1 mark]", self.note())
        self.assertIn("- [ ] A. mass\n- [ ] B. force\n- [ ] C. speed\n- [ ] D. charge", self.note())  # printed order

    def test_exam_unit_check_accepts_authentic_choice_items(self):
        self.run_cmd("start", "Physics", "units", "--exam", "cambridge-as-a-level")
        self.run_cmd("research", "--save", stdin=exam_brief())
        self.run_cmd("plan", "--unit", "u|Units|total,none", "--known", "none")
        self.assertIn("AUTHENTIC", self.run_cmd("block", "u", stdin=UNIT_BLOCK.replace("![[FIG]]", VIS)))
        for cid, n in (("total", 1), ("none", 2)):
            q = dict(fresh_choice(level=2), marks=1, source=f"9702/21/M/J/23 Q{n}(b)")
            self.run_cmd("ask", cid, stdin=json.dumps(q))
        self.assertEqual(len(self.state()["session"]["pending"]), 2)
        wrong = next(L for L, t in self.state()["session"]["pending"]["Q1"]["options"].items()
                     if L != self.state()["session"]["pending"]["Q1"]["correct"])
        self.run_cmd("answer", "Q1", wrong)
        self.run_cmd("answer", "Q2", self.state()["session"]["pending"]["Q2"]["correct"])
        self.assertIn("EXAM MODE: 1 NEW question", self.run_cmd("next"))

    def test_typed_exam_question_graded_by_mark_points(self):
        self.start_exam()
        self.run_cmd("block", "total", stdin="t [S1]" + VIS)
        q = {"type": "typed", "level": 2, "question": "Determine the SI base units of k.", "marks": 3,
             "source": "pattern:P1", "answer": "kg m^-3",
             "rubric": ["C1: base units of F", "C1: base units of v", "A1: kg m^-3"], "why": "k = F / (A v^2)."}
        qid = re.search(r"(Q\d+) written", self.run_cmd("ask", "total", stdin=json.dumps(q))).group(1)
        self.assertIn("generated, follows P1 · [3 marks]", self.note())
        self.run_cmd("answer", qid, "--text", "kg m-3 from F over A v squared")
        out = self.run_cmd("grade", qid, "wrong", "--marks", "2/3", "--kind", "slip", "--what", "missed C1 for v")
        self.assertIn("2/3 marks", out)
        self.assertEqual(self.concept("total")["history"][-1]["marks"], "2/3")

    def test_practice_share_after_a_unit_is_solid(self):
        self.start_exam()
        s = self.state()
        for c in s["topics"]["physics-units"]["concepts"].values():
            c.update(status="solid", taught=True, box=1, next_review="2099-01-01")
        learn.STATE.write_text(json.dumps(s))
        out = self.run_cmd("next")
        self.assertIn("Exam practice", out)
        self.assertIn("AUTHENTIC past-paper questions", out)

    def test_topic_prefs_stay_in_their_topic_and_9702_prefs_migrate(self):
        self.start_planned()
        self.run_cmd("pref", "--topic", "Only", "past-paper", "questions")
        self.assertIn("FOR THIS TOPIC ONLY", self.run_cmd("start", "Probability", "basics"))
        self.assertNotIn("Only past-paper questions", self.run_cmd("start", "Python", "loops"))
        s = self.state()
        s["topics"]["phys-9702"] = {"title": "9702", "goal": "", "created": "2026-10-03", "concepts": {}}
        s["profile"]["preferences"].append("Exam-prep: use only past papers")
        learn.STATE.write_text(json.dumps(s))
        s2 = learn.load()
        self.assertNotIn("Exam-prep: use only past papers", s2["profile"]["preferences"])
        self.assertIn("Exam-prep: use only past papers", s2["topics"]["phys-9702"]["prefs"])


class TestGuides(Base):
    def test_question_guide_examples_pass_the_engine(self):
        guide = (Path(__file__).resolve().parent.parent / "skills/teach-understanding/references/questions.md").read_text()
        blocks = [json.loads(b) for b in re.findall(r"```json\n(.*?)```", guide, re.S) if '"source"' not in b]
        self.assertGreaterEqual(len(blocks), 3)
        for q in blocks:
            if q["type"] in ("choice", "two-tier"):
                learn._check_options(q["options"], "x")
                self.assertEqual(learn.item_problems(q["question"], q["options"], level=q["level"]), [], q["question"])
                if q["type"] == "two-tier":
                    learn._check_options(q["reasons"], "x")
            else:
                self.assertTrue(2 <= len(q["rubric"]) <= 4)


class TestExistingKnowledge(Base):
    def test_claimed_concepts_get_a_quick_check(self):
        self.start_topic("Probability")
        self.run_cmd("plan", "--concept", "total|Total is 1", "--concept", "none|None|total",
                     "--concept", "atleast|At least one|none", "--known", "total,none")
        out = self.run_cmd("next")
        self.assertIn("quick check", out)
        self.assertIn("'Total is 1'", out)
        out = self.answer("total", "correct")
        self.assertEqual(self.concept("total")["status"], "solid")
        self.assertIn("'None'", out)

    def test_failed_claim_turns_into_teaching(self):
        self.start_topic("Probability")
        self.run_cmd("plan", "--concept", "total|Total is 1", "--known", "total")
        out = self.answer("total", "wrong")
        self.assertIn("check says not yet", out)
        self.assertFalse(self.concept("total")["taught"])
        self.run_cmd("ask", "total", stdin=json.dumps(fresh_choice()), ok=False)


    def test_plan_requires_explicit_known(self):
        self.start_topic("Probability")
        self.assertIn("Pass --known", self.run_cmd("plan", "--concept", "total|Total", ok=False))

    def test_learner_says_known_mid_session(self):
        self.start_planned()
        out = self.run_cmd("known", "total")
        self.assertIn("quick check", out)
        self.assertEqual(self.concept("total")["status"], "claimed")
        self.answer("total", "correct")
        self.assertEqual(self.concept("total")["status"], "solid")

    def test_known_after_a_correct_answer_is_solid_at_once(self):
        self.start_planned()
        self.answer("total", "correct", teach=True, level=1)
        self.assertIn("so it is solid", self.run_cmd("known", "total"))
        self.assertEqual(self.concept("total")["status"], "solid")

    def test_known_with_pending_question_uses_it_as_the_check(self):
        self.start_planned()
        qid = self.teach_and_ask("total")
        self.assertIn("should be quick", self.run_cmd("known", "total"))
        self.tick(qid, "correct")
        self.assertEqual(self.concept("total")["status"], "solid")


class TestMistake(Base):
    def test_wrong_answer_logs_misconception_and_asks_again(self):
        self.start_planned()
        out = self.tick(self.teach_and_ask("total"), "wrong")
        self.assertIn("Missed once", out)
        m = self.state()["mistakes"][0]
        self.assertEqual(m["kind"], "error")   # one wrong pick shows an error, not yet a misconception
        self.assertTrue(m["what"])
        self.assertIn("[!failure]", self.note())
        self.assertIn("Why", self.note())
        self.assertIn("Write 1 NEW question", out)

    def test_idk_reteaches_instead_of_reasking(self):
        self.start_planned()
        out = self.tick(self.teach_and_ask("total"), "idk")
        self.assertIn("Re-teach", out)
        self.assertEqual(self.state()["mistakes"][0]["kind"], "gap")


class TestRepeatedStruggle(Base):
    def test_two_misses_revisit_weak_prerequisite_then_return(self):
        self.start_planned()
        self.answer("total", "correct", teach=True, level=1)  # recall only: total stays learning
        self.run_cmd("block", "none", stdin="none theory [S1]" + VIS)
        self.answer("none", "wrong")
        out = self.answer("none", "wrong")
        self.assertIn("rests on 'All chances add to 1'", out)
        self.assertEqual(self.state()["session"]["stack"], ["none"])
        out = self.answer("total", "correct", teach=True)  # 2nd in a row: solid
        self.assertIn("back to 'Chance of none'", out)
        self.assertEqual(self.state()["session"]["stack"], [])

    def test_three_misses_stop_quizzing(self):
        self.start_planned()
        self.run_cmd("block", "total", stdin="t [S1]" + VIS)
        for _ in range(2):
            self.answer("total", "wrong")
        out = self.answer("total", "wrong", teach=True)
        self.assertIn("Stop quizzing", out)
        out = self.run_cmd("add", "split", "Count", "the", "cases", "--before", "total")
        self.assertIn("smaller step", out)
        self.assertIn("split", self.concept("total")["prereqs"])


class TestMasteryOverTime(Base):
    def test_later_day_review_promotes_and_closes_old_mistake(self):
        self.start_planned()
        self.tick(self.teach_and_ask("total"), "wrong")
        self.answer("total", "correct")
        self.answer("total", "correct")
        self.assertIn("Correct again. Same day", self.answer("total", "correct"))
        self.run_cmd("end")
        self.day("2026-10-04")
        out = self.run_cmd("start", "Probability", "basics")
        self.assertIn("due for review", out)
        out = self.answer("total", "correct")
        self.assertIn("box 2 (mastered)", out)
        self.assertIn("[!question] Review:", self.note())
        c = self.concept("total")
        self.assertEqual(c["next_review"], "2026-10-07")
        self.assertTrue(all(m["closed"] for m in self.state()["mistakes"]))

    def test_forgotten_review_drops_back(self):
        self.start_planned()
        self.answer("total", "correct", teach=True)
        self.answer("total", "correct")
        self.run_cmd("end")
        self.day("2026-10-05")
        self.run_cmd("start", "Probability", "basics")
        out = self.answer("total", "wrong")
        self.assertIn("forgotten since last time", out)
        self.assertEqual(self.concept("total")["status"], "learning")


class TestTopicChange(Base):
    def test_switch_keeps_one_note_and_old_state(self):
        self.start_planned()
        self.answer("total", "correct", teach=True)
        note = self.state()["session"]["note"]
        out = self.run_cmd("start", "Python", "loops")
        self.assertIn("Switched", out)
        self.research(PY)
        s = self.state()
        self.assertEqual(s["session"]["note"], note)
        self.assertEqual(s["topics"]["probability-basics"]["concepts"]["total"]["streak"], 1)
        self.assertIn("## Switched topic: Python loops", self.note())
        self.run_cmd("plan", "--concept", "for|For loop", "--known", "none")
        self.answer("for", "correct", teach=True)
        self.run_cmd("end")
        self.assertIn("| For loop |", (learn.VAULT / note).read_text())
        self.assertIn("| All chances add to 1 |", (learn.VAULT / note).read_text())


class TestReturningLearner(Base):
    def test_next_session_continues_from_state(self):
        self.start_planned()
        qid = self.teach_and_ask("total")
        self.run_cmd("end", "--next-time", "Finish 'All chances add to 1', then 'Chance of none'.")
        first = (learn.VAULT / self.state()["history"][-1]["note"]).read_text()
        self.assertIn(f"{qid}: not answered", first)
        self.assertIn("status: done", first)
        self.assertTrue((learn.VAULT / learn.DASHBOARD).exists())
        self.day("2026-10-06")
        out = self.run_cmd("start", "Probability", "basics")
        self.assertIn("LAST SESSION 2026-10-03", out)
        self.assertIn("Last time (2026-10-03)", self.note())
        self.assertIn("2026-10-06 Probability basics", self.state()["session"]["note"])

    def test_unclosed_session_is_closed_automatically(self):
        self.start_planned()
        self.day("2026-10-04")
        self.run_cmd("start", "Probability", "basics")
        s = self.state()
        self.assertEqual(len(s["history"]), 1)
        self.assertEqual(s["session"]["date"], "2026-10-04")


    def test_last_time_line_is_per_topic(self):
        self.start_planned()
        self.answer("total", "correct", teach=True)
        self.start_topic("Python", "loops", concepts=PY)
        self.run_cmd("plan", "--concept", "for|For loop", "--known", "none")
        self.run_cmd("end", "--next-time", "Teach the for loop.")
        self.day("2026-10-04")
        self.run_cmd("start", "Probability", "basics")
        self.assertNotIn("Teach the for loop", self.note())
        self.assertIn("All chances add to 1", self.note().split("Last time")[1])


class TestChatAndTyped(Base):
    def test_chat_answer_ticks_the_note(self):
        self.start_planned()
        qid = self.teach_and_ask("total")
        letter = self.state()["session"]["pending"][qid]["correct"]
        self.run_cmd("answer", qid, f"{letter})")
        self.assertIn(f"- [x] {letter}.", self.note())
        self.assertEqual(self.concept("total")["streak"], 1)

    def test_typed_question_needs_model_grade(self):
        self.start_planned()
        q = {"type": "typed", "question": "Why 1 - none?", "answer": "the two cases fill the whole pie",
             "rubric": ["none and at-least-one are the only two cases", "together they make the whole pie, 1"],
             "why": "None and at-least-one cover everything."}
        qid = self.teach_and_ask("total", q=q)
        self.assertIn("nothing typed", self.run_cmd("check"))
        out = self.run_cmd("answer", qid, "--text", "because it's everything else")
        self.assertIn("learn grade", out)
        out = self.run_cmd("grade", qid, "correct", "--marks", "2/2")
        self.assertIn("2/2 marks", out)
        self.assertIn("[!success]", self.note())

    def test_preference_persists(self):
        self.start_topic("x")
        self.run_cmd("pref", "Use", "Russian", "for", "terms")
        self.assertIn("Use Russian for terms", self.run_cmd("next") + self.run_cmd("start", "x"))


if __name__ == "__main__":
    unittest.main()
