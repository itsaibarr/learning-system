"""Tests for the anki queue parser and payload builder. Run: python3 -m unittest discover scripts"""

import unittest

from anki_push import parse_queue, build_notes, to_anki_html

QUEUE = """# Anki queue

Some prose that must be ignored.

## Batch: kinematics-1 | deck: AS-Physics::Kinematics | status: approved

Q: What quantity is the gradient of a displacement-time graph?
A: Velocity
Tags: kinematics graphs
Src: [[Concepts/motion-graphs]]

Text: For uniform acceleration, $v = u + {{c1::at}}$
Tags: kinematics suvat
Src: [[Concepts/suvat]]

## Batch: drafts | deck: AS-Physics | status: draft

Q: Unreviewed question
A: Unreviewed answer
Tags: t
Src: x
"""


class ParseQueueTest(unittest.TestCase):
    def test_parses_batches_with_name_deck_and_status(self):
        batches = parse_queue(QUEUE)
        self.assertEqual(len(batches), 2)
        self.assertEqual(batches[0]["name"], "kinematics-1")
        self.assertEqual(batches[0]["deck"], "AS-Physics::Kinematics")
        self.assertEqual(batches[0]["status"], "approved")
        self.assertEqual(batches[1]["status"], "draft")

    def test_parses_basic_and_cloze_cards(self):
        cards = parse_queue(QUEUE)[0]["cards"]
        self.assertEqual(len(cards), 2)
        basic, cloze = cards
        self.assertEqual(basic["type"], "basic")
        self.assertEqual(basic["front"], "What quantity is the gradient of a displacement-time graph?")
        self.assertEqual(basic["back"], "Velocity")
        self.assertEqual(basic["tags"], ["kinematics", "graphs"])
        self.assertEqual(basic["src"], "[[Concepts/motion-graphs]]")
        self.assertEqual(cloze["type"], "cloze")
        self.assertIn("{{c1::at}}", cloze["text"])

    def test_records_line_spans_covering_each_batch(self):
        lines = QUEUE.splitlines()
        first, second = parse_queue(QUEUE)
        self.assertTrue(lines[first["start"]].startswith("## Batch: kinematics-1"))
        self.assertEqual(first["end"], second["start"])
        self.assertTrue(lines[second["start"]].startswith("## Batch: drafts"))
        self.assertEqual(second["end"], len(lines))

    def test_rejects_basic_card_missing_answer(self):
        broken = "## Batch: b | deck: D | status: approved\n\nQ: front only\nTags: t\nSrc: x\n"
        with self.assertRaises(ValueError):
            parse_queue(broken)

    def test_rejects_batch_header_missing_deck(self):
        broken = "## Batch: b | status: approved\n\nQ: q\nA: a\n"
        with self.assertRaises(ValueError):
            parse_queue(broken)

    def test_rejects_cloze_without_cloze_deletion(self):
        broken = "## Batch: b | deck: D | status: approved\n\nText: no braces here\nTags: t\nSrc: x\n"
        with self.assertRaises(ValueError):
            parse_queue(broken)

    def test_rejects_unrecognized_line_inside_card_block(self):
        # A wrapped/continuation line would otherwise be silently dropped from the card.
        broken = ("## Batch: b | deck: D | status: approved\n\n"
                  "Q: derive it\nA: start from v = u + at,\n   then integrate over t\nTags: t\n")
        with self.assertRaises(ValueError):
            parse_queue(broken)


class AnkiHtmlTest(unittest.TestCase):
    def test_escapes_html_special_characters(self):
        self.assertEqual(to_anki_html("v < 0 and a > 0"), "v &lt; 0 and a &gt; 0")

    def test_converts_dollar_math_to_anki_mathjax_delimiters(self):
        self.assertEqual(to_anki_html(r"speed is $9.8\ \mathrm{m/s^2}$"),
                         r"speed is \(9.8\ \mathrm{m/s^2}\)")
        self.assertEqual(to_anki_html("$$E = mc^2$$"), r"\[E = mc^2\]")

    def test_preserves_cloze_markers(self):
        self.assertEqual(to_anki_html("$s = {{c1::ut}}$"), r"\(s = {{c1::ut}}\)")


class BuildNotesTest(unittest.TestCase):
    def test_builds_anki_connect_payloads_with_source_in_back(self):
        batch = parse_queue(QUEUE)[0]
        notes = build_notes(batch)
        self.assertEqual(len(notes), 2)
        basic, cloze = notes
        self.assertEqual(basic["deckName"], "AS-Physics::Kinematics")
        self.assertEqual(basic["modelName"], "Basic")
        self.assertEqual(basic["fields"]["Front"], "What quantity is the gradient of a displacement-time graph?")
        self.assertIn("Velocity", basic["fields"]["Back"])
        self.assertIn("[[Concepts/motion-graphs]]", basic["fields"]["Back"])
        self.assertEqual(basic["tags"], ["kinematics", "graphs"])
        self.assertFalse(basic["options"]["allowDuplicate"])
        self.assertEqual(cloze["modelName"], "Cloze")
        self.assertIn("{{c1::at}}", cloze["fields"]["Text"])
        self.assertIn(r"\(v = u + {{c1::at}}\)", cloze["fields"]["Text"])
        self.assertIn("[[Concepts/suvat]]", cloze["fields"]["Back Extra"])


if __name__ == "__main__":
    unittest.main()
