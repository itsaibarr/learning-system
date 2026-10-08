# Example: one full teaching turn (real output, trimmed)

Copy this pattern. Output lines come from an actual run of `learn`.

## 1. Start

```bash
learn start probability basics
```
```
New session note: Sessions/2026-10-03 probability basics.md
LEARNER PREFERENCES (apply to every block and every reply): ...
WHY: 'probability basics' has no research brief yet. Research comes before any teaching.
NEXT: 1) If you don't know the learner's goal yet, ask ONE plain question in chat ... 2) Run the research pipeline in references/research.md ...
```

Chat (you): `Your note is open in Obsidian. What do you want to be able to do with probability, and what do you already know about it?`

Learner: `I want to solve the "at least one" questions. I know nothing.`

## 2. Research, then plan in units

Follow `references/research.md`. The brief's Concepts table has a `Unit` column: these three
ideas only make sense together, so they are ONE unit (source rows below are illustrative;
real ones are what you actually read):

```bash
learn research --save <<'EOF'
# Research brief: probability basics

Goal: solve "at least one" chance questions
Domain: generic
Date: 2026-10-08

## Concepts
| Id | Concept | Builds on | Sources | Unit |
| --- | --- | --- | --- | --- |
| total | All chances add up to 1 | - | S1 | at-least-one |
| none | Chance that something never happens | total | S1 | at-least-one |
| atleast | At least one = 1 minus none | none | S1, S3 | at-least-one |

## Definitions
- **complement**: the event "not A"; P(not A) = 1 - P(A) [S1]

## Misconceptions
- adding the chances of each trial to get "at least one" (2 x 1/6 for two dice) -> events overlap [S3]
- stopping at P(none) and giving it as the answer -> the question asks for the complement [S2]

## Worked examples
- atleast: at least one six in 3 rolls = 1 - (5/6)^3 = 0.4213 [S1]

## Sources
| Id | Source | Type | Reliability | Supports | Retrieved |
| --- | --- | --- | --- | --- | --- |
| S1 | OpenStax Introductory Statistics 2e, ch. 3, https://openstax.org/books/introductory-statistics-2e/pages/3-1-terminology | textbook | high | definitions, complement rule | 2026-10-08 |
| S2 | Khan Academy, probability of at least one, https://www.khanacademy.org/math/statistics-probability | secondary | med | at-least-one method | 2026-10-08 |
| S3 | Grinstead and Snell, Introduction to Probability, https://math.dartmouth.edu/~prob/prob/prob.pdf | textbook | high | overlap error | 2026-10-08 |

## Open questions
- none
EOF
learn plan --unit 'at-least-one|At least one|total,none,atleast' --known none
```
```
WHY: Next unit: 'At least one' (3 linked ideas taught together), because it needs nothing else, so it is a starting point.
NEXT: Teach the whole unit 'At least one' in ONE block: one segment per sub-idea (2-4) ... For each segment make one short narrated Manim scene ... No questions until the block is in the note.
```

## 3. One scene per segment (audio-first), then one block

```bash
learn figure all-ways <<'EOF'
from manim import *

NARRATION = [
    "A die can land in six ways, and every face is just as likely, so each face gets a chance of one sixth.",
    "Add all six chances together and you get exactly one. One means every way the throw can go.",
]

class AllWays(Scene):
    def construct(self):
        faces = VGroup(*[VGroup(Square(1.1, color=BLUE), Text(str(i), font_size=36)) for i in range(1, 7)]).arrange(RIGHT, buff=0.25)
        sixths = VGroup(*[MathTex(r"\tfrac{1}{6}", font_size=40).next_to(f, DOWN) for f in faces])
        self.add(Text("All the ways make one", font_size=30).to_edge(UP))
        with self.voice(1):
            self.play(FadeIn(faces), LaggedStart(*[Write(x) for x in sixths], lag_ratio=0.2))
        with self.voice(2):
            total = MathTex(r"6 \times \tfrac{1}{6} = 1", font_size=48, color=GREEN).next_to(sixths, DOWN, buff=0.7)
            self.play(TransformFromCopy(sixths, total))
EOF
```
```
Figure saved: Attachments/learn/probability-basics/all-ways.mp4 (manim)
EMBED: ![[Attachments/learn/probability-basics/all-ways.mp4]]
Narration: 2 line(s), voice af_heart, 15.8s of speech, audio-first: every line starts on its own visual event; picture held 1.7s in total so it waits for the voice.
```

```bash
learn figure none-flip <<'EOF'
from manim import *

NARRATION = [
    "Roll three times. The chance of no six on one roll is five sixths, so no six at all is five sixths cubed.",
    "None and at least one are the only two boxes, and together they make one. So at least one six is one minus none.",
]

class NoneFlip(Scene):
    def construct(self):
        self.add(Text("Count none, then flip it", font_size=30).to_edge(UP))
        bar = Rectangle(width=10, height=1, color=WHITE).shift(0.5 * DOWN)
        cut = 10 * (5 / 6) ** 3
        none = Rectangle(width=cut, height=1, color=RED, fill_opacity=0.5).align_to(bar, LEFT).shift(0.5 * DOWN)
        rest = Rectangle(width=10 - cut, height=1, color=GREEN, fill_opacity=0.5).align_to(bar, RIGHT).shift(0.5 * DOWN)
        with self.voice(1):
            self.play(Create(bar))
            self.play(FadeIn(none), Write(MathTex(r"\left(\tfrac{5}{6}\right)^3 \approx 0.58", color=RED).next_to(none, UP)))
        with self.voice(2):
            self.play(FadeIn(rest), Write(MathTex(r"1 - 0.58 = 0.42", color=GREEN).next_to(rest, DOWN)))
EOF
```

```bash
learn block at-least-one <<'EOF'
**Big idea:** to find the chance of "at least one", count the chance of none, then take it away from 1.

**Key terms:**
- **outcome**: one way something can turn out [S1]
- **complement**: everything that is not the event; P(not A) = 1 - P(A) [S1]

### All the ways make one
![[Attachments/learn/probability-basics/all-ways.mp4]]
1. List every way it can turn out.
2. Their chances add up to exactly 1.

### Count none, then flip it
![[Attachments/learn/probability-basics/none-flip.mp4]]
| step | three rolls of a die |
| --- | --- |
| none | (5/6)^3 = 0.579 |
| at least one | 1 - 0.579 = 0.421 |

> [!example] Worked example
> 1. Two coins: P(no heads) = (1/2)^2 = 0.25 [S1]
> 2. P(at least one head) = 1 - 0.25 = 0.75

**Check yourself:** why can't you just add 1/6 three times? [S3]
EOF
```
```
WHY: Unit 'At least one' is taught. Still to check: 'All chances add up to 1', 'Chance that something never happens', 'At least one = 1 minus none'.
NEXT: Unit check for 'At least one': write ONE question for each of total, none, atleast at level 2+ (a scenario the lesson did not use) ... at least one of them two-tier or typed with a rubric ...
```

## 4. The unit check: one question per concept, all waiting together

```bash
learn ask total <<'EOF'
{"type": "choice", "level": 2,
 "question": "A spinner has red, blue and green sectors with P(red) = 0.2 and P(blue) = 0.5. What is P(green)?",
 "options": [{"text": "0.3", "correct": true},
             {"text": "0.7", "misconception": "Adds the two given chances instead of taking them from 1"},
             {"text": "0.5", "misconception": "Assumes the missing colour equals the largest one"}],
 "why": "All the chances add to 1, so P(green) = 1 - 0.2 - 0.5 = 0.3 [S1]."}
EOF
learn ask none <<'EOF'
{"type": "choice", "level": 2,
 "question": "A light fails on 10% of nights. Nights are independent. What is the chance it never fails across 2 nights?",
 "options": [{"text": "0.81", "correct": true},
             {"text": "0.80", "misconception": "Subtracts 10% twice instead of multiplying"},
             {"text": "0.01", "misconception": "Multiplies the failure chances instead of the no-failure chances"}],
 "why": "No failure on one night is 0.9, so on both nights it is 0.9 x 0.9 = 0.81 [S1]."}
EOF
learn ask atleast <<'EOF'
{"type": "two-tier", "level": 3,
 "question": "You roll two dice. What is the chance of at least one six?",
 "options": [{"text": "11/36", "correct": true},
             {"text": "12/36", "misconception": "Adds 1/6 + 1/6 and counts double-six twice"},
             {"text": "25/36", "misconception": "Stops at P(no six) and gives it as the answer"}],
 "reasons": [{"text": "It is 1 minus the chance of no six", "correct": true},
             {"text": "Each die adds its own 1/6", "misconception": "Treats overlapping events as separate"},
             {"text": "No six on both dice is the case asked", "misconception": "Answers the complement"}],
 "why": "P(no six) = (5/6)^2 = 25/36, so P(at least one) = 1 - 25/36 = 11/36 [S1]."}
EOF
```

Chat (you): `Three questions are in the note. Answer there, then send any message.` Then stop.

## 5. The learner answers, then says "done"

```bash
learn check
```
```
Q1: learner picked B -> correct. applied to a new scenario: 'All chances add up to 1' is solid. Review tomorrow.
Q2: learner picked B -> wrong. Missed once (error). The feedback explains the fix. Now a new, differently worded question on the same idea.
Q3: learner picked C because 1 -> wrong. Misconception on 'At least one = 1 minus none': a short contrast re-teach of that step, then a differently-worded question.
NEXT: Re-teach 'At least one = 1 minus none': ... a NEW Manim visual that shows the step they got wrong ...
```

The right answer with the wrong reason (Q3) is exactly what a plain multiple-choice question
would have missed. The note shows, under Q3:

```markdown
> [!failure] Q3: you picked C because 1. Right answer: C. 11/36, because 3. It is 1 minus the chance of no six
> P(no six) = (5/6)^2 = 25/36, so P(at least one) = 1 - 25/36 = 11/36 [S1].
> reason 1 is the belief: Answers the complement
```

After the re-teach, the queued follow-up for Q2 comes next: one new question on "none".

## What NOT to do

- Do not split the unit into one block per concept, or ask after each segment.
- Do not teach a fact that is not in the research brief. Add it with a source and re-save first.
- Do not paste the theory into chat as well. It lives in the note.
- Do not write prose paragraphs: steps, tables and a worked example (the engine rejects long paragraphs).
- Do not write "Correct answer: C" under a question yourself. `check` does it.
- Do not jump ahead because you think they got it. NEXT decides.
