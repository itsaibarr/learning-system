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


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        learn.STATE = root / "state" / "learner.json"
        learn.VAULT = root / "vault"
        os.environ.update(LEARN_NO_CLI="1", LEARN_NO_GIT="1", LEARN_TODAY="2026-10-03")

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

    def teach_and_ask(self, cid, block="Short theory. [S1]" + VIS, q=CHOICE):
        self.run_cmd("block", cid, stdin=block)
        out = self.run_cmd("ask", cid, stdin=json.dumps(q))
        return re.search(r"(Q\d+) written", out).group(1)

    def answer(self, cid, which, teach=False, level=2):
        if teach:
            self.run_cmd("block", cid, stdin="Theory again. [S1]" + VIS)
        q = dict(CHOICE, level=level)
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
        out = self.run_cmd("ask", "total", stdin=json.dumps(CHOICE), ok=False)
        self.assertIn("has not been taught yet", out)

    def test_answer_key_not_in_note_until_graded(self):
        self.start_planned()
        qid = self.teach_and_ask("total")
        self.assertNotIn("1 - 1/4 = 3/4", self.note())
        self.assertIn("I don't know", self.note())
        self.tick(qid, "correct")
        self.assertIn("1 - 1/4 = 3/4", self.note())

    def test_two_in_a_row_makes_solid_and_unlocks_next(self):
        self.start_planned()
        self.assertIn("1 of 2", self.tick(self.teach_and_ask("total"), "correct"))
        out = self.answer("total", "correct")
        self.assertIn("is solid", out)
        c = self.concept("total")
        self.assertEqual((c["status"], c["box"], c["next_review"], c["level"]), ("solid", 1, "2026-10-04", 2))
        self.assertIn("'Chance of none'", out)

    def test_block_word_limit(self):
        self.start_planned()
        self.assertIn("limit is", self.run_cmd("block", "total", stdin="word " * 300 + "[S1]" + VIS, ok=False))

    def test_bad_question_json_is_rejected(self):
        self.start_planned()
        self.run_cmd("block", "total", stdin="x [S1]" + VIS)
        bad = dict(CHOICE, options=[{"text": "a", "correct": True}, {"text": "b"}])
        self.assertIn("needs a \"misconception\"", self.run_cmd("ask", "total", stdin=json.dumps(bad), ok=False))


    def test_recall_only_is_not_solid(self):
        self.start_planned()
        self.answer("total", "correct", teach=True, level=1)
        out = self.answer("total", "correct", level=1)
        self.assertIn("applies it to a new example (level 2)", out)
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
        self.assertIn("needs a visual", out)

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
        self.run_cmd("ask", "total", stdin=json.dumps(dict(CHOICE, figure=embed)))
        head = self.note().split("### Q1")[1]
        self.assertIn(embed, head.split("- [ ]")[0])
        bad = dict(CHOICE, figure="![[nope.png]]")
        self.assertIn('"figure" must be', self.run_cmd("ask", "total", stdin=json.dumps(bad), ok=False))

    def test_every_template_in_visuals_guide_renders(self):
        guide = Path(__file__).resolve().parent.parent / "skills/teach-understanding/references/visuals.md"
        templates = re.findall(r"```python\n(.*?)```", guide.read_text(), re.S)
        self.assertGreaterEqual(len(templates), 4)
        self.start_planned()
        for n, code in enumerate(templates, 1):
            out = self.run_cmd("figure", f"template-{n}", stdin=code)
            self.assertIn("EMBED:", out, f"template {n} failed")

    def test_new_default_preferences_reach_existing_learners(self):
        self.start_planned()
        st = self.state()
        st["profile"]["preferences"] = st["profile"]["preferences"][:2]
        learn.STATE.write_text(json.dumps(st))
        self.assertIn("Visual learner", self.run_cmd("start", "Probability", "basics"))


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
        self.run_cmd("ask", "total", stdin=json.dumps(CHOICE), ok=False)


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
        self.answer("total", "correct", teach=True)
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
        self.assertEqual(m["kind"], "misconception")
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
        self.answer("total", "correct", teach=True)  # total: learning, 1 of 2
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
             "why": "None and at-least-one cover everything."}
        qid = self.teach_and_ask("total", q=q)
        self.assertIn("nothing typed", self.run_cmd("check"))
        out = self.run_cmd("answer", qid, "--text", "because it's everything else")
        self.assertIn("learn grade", out)
        out = self.run_cmd("grade", qid, "correct")
        self.assertIn("1 of 2", out)
        self.assertIn("[!success]", self.note())

    def test_preference_persists(self):
        self.start_topic("x")
        self.run_cmd("pref", "Use", "Russian", "for", "terms")
        self.assertIn("Use Russian for terms", self.run_cmd("next") + self.run_cmd("start", "x"))


if __name__ == "__main__":
    unittest.main()
