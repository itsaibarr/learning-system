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

## 2. Research, then plan

Follow `references/research.md`: `learn lit guide generic`, a few `learn lit search`
queries, web search for a textbook chapter, read the best sources. Then save the brief
(source rows below are illustrative; real ones are what you actually read):

```bash
learn research --save <<'EOF'
# Research brief: probability basics

Goal: solve "at least one" chance questions
Domain: generic
Date: 2026-10-03

## Concepts
| Id | Concept | Builds on | Sources |
| --- | --- | --- | --- |
| total | All chances add up to 1 | - | S1, S2 |
| none | Chance that something never happens | total | S1 |
| atleast | At least one = 1 minus none | none | S1, S3 |

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
| S1 | OpenStax Introductory Statistics 2e, ch. 3, https://openstax.org/... | textbook | high | definitions, complement rule | 2026-10-03 |
| S2 | ... | secondary | med | at-least-one method | 2026-10-03 |
| S3 | Grinstead & Snell, Introduction to Probability, https://math.dartmouth.edu/... | textbook | high | overlap error | 2026-10-03 |

## Open questions
- none
EOF
```
```
Brief saved to Sources/probability basics research brief.md: 3 concepts, 3 sources.
WHY: 'probability basics' has a research brief but no plan yet.
```

```bash
learn plan --concept total --concept none --concept atleast \
  --known none      # the learner said "I know nothing"
```
```
WHY: Next new idea: 'All chances add up to 1', because it needs nothing else, so it is a starting point.
NEXT: Write the theory block for 'All chances add up to 1' from the research brief (cite its sources as [S1]) ...
```

## 3. Picture, theory, then the question

```bash
learn figure all-chances <<'EOF'
from manim import *

NARRATION = [
    "A die can land in six ways, and every face is just as likely, so each one gets a chance of one sixth.",
    "Now add all six chances together: six times one sixth makes exactly one. One is the whole, every way the throw can go.",
]

class AllChances(Scene):
    def construct(self):
        faces = VGroup(*[VGroup(Square(1.1, color=BLUE), Text(str(i), font_size=36)) for i in range(1, 7)])
        faces.arrange(RIGHT, buff=0.25)
        sixths = VGroup(*[MathTex(r"\tfrac{1}{6}", font_size=40).next_to(f, DOWN) for f in faces])
        caption = Text("1  each face has chance 1/6", font_size=30).to_edge(UP)
        self.play(Write(caption), FadeIn(faces))
        self.play(LaggedStart(*[Write(x) for x in sixths], lag_ratio=0.2))
        total = MathTex(r"6 \times \tfrac{1}{6} = 1", font_size=48, color=GREEN).next_to(sixths, DOWN, buff=0.7)
        self.play(Transform(caption, Text("2  all six together make one whole", font_size=30).to_edge(UP)),
                  TransformFromCopy(sixths, total))
        self.wait(1.5)
EOF
```
```
Figure saved: Attachments/learn/probability-basics/all-chances.mp4 (manim)
EMBED: ![[Attachments/learn/probability-basics/all-chances.mp4]]
Narration: 2 line(s), voice af_heart, 15.7s of speech, step-synced to the numbered captions; picture held 10.4s in total so it waits for the voice.
```

```bash
learn block total <<'EOF'
**Why we need this:** To find a chance, we first need to know what "all of it" is.

![[Attachments/learn/probability-basics/all-chances.mp4]]

Something can turn out in a few ways. ① Each way has its own chance. ② The chances of
all the ways add up to 1. One whole [S1].

> [!example] Example
> A coin lands heads or tails. Heads $= 0.5$, tails $= 0.5$. Together $0.5 + 0.5 = 1$.

**Remember:** all the ways together $= 1$.
EOF

learn ask total <<'EOF'
{"type":"choice","level":1,
 "question":"A die shows 1 to 6. The chance of a six is $1/6$. What is the chance of NOT a six?",
 "options":[{"text":"$5/6$","correct":true},
            {"text":"$1/6$","misconception":"Gave the chance of the six itself"},
            {"text":"$1/5$","misconception":"Divided by the five other faces only"},
            {"text":"$6/6$","misconception":"Thinks every face counts as not-six"}],
 "why":"All chances add to 1, so not six $= 1 - 1/6 = 5/6$."}
EOF
```
```
Q1 written to the note.
NEXT: Tell the learner in ONE line: "Q1 is in the note. Answer there, then send any message." Then STOP and wait.
```

Chat (you): `Q1 is in the note. Answer there, then send any message.` Then stop.

## 4. The learner answers in Obsidian, then says "done"

```bash
learn check
```
```
Q1: learner picked B -> wrong. Missed once. The feedback explains the fix. Now a new question on the same idea.
NEXT: Write 1 NEW question on 'All chances add up to 1' at level 1 ... Pipe it to `learn ask total`.
```

The note now shows, under Q1:

```markdown
> [!failure] Q1: you picked B. Right answer: C. $5/6$
> All chances add to 1, so not six $= 1 - 1/6 = 5/6$.
> Why B is tempting: Gave the chance of the six itself
>
> **Next:** Missed once. The feedback explains the fix. Now a new question on the same idea.
```

Chat (you): `Not quite. The fix is under Q1. Q2 is coming with new numbers.` Then run
`learn ask total` with a new question (for example a spinner with 4 colours).

## What NOT to do

- Do not teach a fact that is not in the research brief. Add it with a source and re-save first.
- Do not paste the theory into chat as well. It lives in the note.
- Do not ask Q2 in chat. Use `learn ask`.
- Do not write "Correct answer: C" under the question yourself. `check` does it.
- Do not jump to the next concept because you think they got it. NEXT decides.
