# Questions that need understanding

A question earns its place only if its answer changes what happens next and a learner who did
not understand would get it wrong. Evidence: `docs/research/teaching-quality/assessment.md`
(Haladyna, Downing & Rodriguez 2002; NBME item-writing guide; Rodriguez 2005; Gierl et al. 2017;
Treagust 1988; Butler 2018).

## When and how many

- After a unit's block: **one question per concept** of the unit (3-5), all waiting together.
- At least one of them **two-tier or typed** (the engine insists).
- All at **level 2+**: a scenario the lesson never used. Level 3 = predict, explain why, combine.
- No questions after each segment, none on isolated facts, never two in a row on the same idea.
- Spaced reviews open the next sessions; the engine schedules them.

## Pick the format by what you are testing

| Testing | Format |
| --- | --- |
| Can apply it | 3-option single-best-answer with a short scenario stem and a closed question ("Which device forwards the frame?") |
| Understands why | two-tier: answer + reason (both must be right) |
| A suspected misconception | two-tier whose wrong reasons ARE the misconceptions |
| Can explain or produce | typed, with a 2-4 point rubric |
| Exam technique | exam mode: a real past-paper question, marked on the mark scheme |

## Writing a multiple-choice item (the engine checks what it can)

1. **Stem first.** A short scenario + a closed question ending in "?". Cover the options: an
   expert must be able to answer from the stem alone.
2. **Key next.** One correct, short claim. No hedges or extra detail that only the key has.
3. **Two distractors**, each the answer someone with ONE specific wrong belief would give. Take
   the beliefs from the brief's Misconceptions and the examiner reports. Write the belief in
   `misconception`. Same length, grammar and detail as the key.
4. **Never**: "all/none of the above", NOT/EXCEPT stems, absolute words (always, never, only)
   just in the distractors, stem words repeated only in the key, text copied from the lesson,
   absurd options nobody would pick.
5. **Check**: solve it yourself; read only the options and ask "could I guess?". If yes, rewrite.

```json
{"type": "choice", "level": 2,
 "question": "A school links 40 PCs with one switch. PC 7 sends a frame to PC 12. Where does the switch send it?",
 "options": [
   {"text": "Only out of the port PC 12 is on", "correct": true},
   {"text": "Out of every port except the one it came in on", "misconception": "Treats a switch like a hub that floods every frame"},
   {"text": "Out of the port that leads to the router", "misconception": "Thinks every frame goes to the router first"}],
 "why": "A switch learns which port each MAC address is on and forwards a frame only to that port [S2]."}
```

## Two-tier (answer + reason)

```json
{"type": "two-tier", "level": 3,
 "question": "A ball is thrown straight up. At its highest point, what is its acceleration?",
 "options": [
   {"text": "9.8 m/s^2 downward", "correct": true},
   {"text": "Zero", "misconception": "Confuses zero velocity with zero acceleration"},
   {"text": "9.8 m/s^2 upward", "misconception": "Thinks the push of the throw still acts"}],
 "reasons": [
   {"text": "Gravity acts the whole time", "correct": true},
   {"text": "The ball has stopped moving", "misconception": "v = 0 so a = 0"},
   {"text": "The throw's force is still on it", "misconception": "Impetus: force stays in the object"}],
 "why": "Velocity is zero for an instant, but gravity still changes it at 9.8 m/s^2 downward [S1]."}
```

Both tiers follow the rules above. Right answer + wrong reason = a misconception: the engine
logs it and schedules a contrast re-teach. The learner answers in the note or in chat as "A1".

## Typed with a rubric

```json
{"type": "typed", "level": 3,
 "question": "Explain why a switch is faster than a hub when many computers send at once.",
 "answer": "A switch sends each frame only to its destination port, so other links stay free; a hub repeats every frame to all ports, so frames collide.",
 "rubric": ["switch forwards a frame only to the destination port", "hub broadcasts to all ports",
            "so with a hub frames collide / bandwidth is shared, and with a switch they do not"],
 "why": "Switching separates traffic; hubs share one collision domain [S2]."}
```

Grading: mark each rubric point present or absent **by meaning**, not wording or spelling.
All points: `learn grade Q correct --marks 3/3`. Otherwise
`learn grade Q wrong --marks 1/3 --kind slip|gap|misconception --what "<what was missing or wrong>"`.
- `slip`: knows it, slipped on arithmetic or reading
- `gap`: never learned this part
- `misconception`: believes something false (say what)

## Exam mode

- **Authentic**: copy the question word for word, give its citation and marks. Its options stay as
  printed (often 4, same letters as the mark scheme). Add each wrong option's misconception from the
  examiner report. Use only questions whose text is complete without the diagram, unless you describe
  it in the note. An authentic item counts as the unit check's "not a lucky pick" item.
  `{"type": "choice", "source": "9702/21/M/J/24 Q2(b)(iii)", "marks": 1, ...}`
- **Generated**: only from a brief pattern, inside its features, with all the rules above.
  `{"type": "typed", "source": "pattern:P1", "marks": 3, "rubric": ["C1: ...", "C1: ...", "A1: ..."], ...}`
- Typed exam answers: the rubric is the mark scheme's points with their codes; grade with
  `--marks got/total`, following the mark scheme's rules (ecf, units, list rule, cso, awrt).
- Use the board's command words exactly as defined in the profile.

## Feedback (the engine writes it from your fields)

`why`: the reason the key is right, 1-3 sentences, cited. Each `misconception`: why someone picks
that option. No praise. After a miss, the next step is a new, differently worded question or a
short contrast re-teach, never the same question again.
