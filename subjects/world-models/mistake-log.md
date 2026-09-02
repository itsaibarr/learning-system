# Mistake Log: world models

One row per confirmed miss. Feeds Anki drafting and the weekly review.

| Date | What I got wrong | Kind | Root cause | Fixed by | Card? |
| --- | --- | --- | --- | --- | --- |
| 2026-09-02 | Could not say how violation detection is measured (answered "I don't know") | gap | Never met the violation-of-expectation paradigm or its import from infant cognition into ML | Taught 2026-09-02: matched possible/impossible pairs, compared within-pair on prediction error | queued |
| 2026-09-02 | Did not hold that prediction error is the free test-time signal — derived it, then disowned the derivation | gap | Self-supervision not yet a possessed concept; reasoning outran vocabulary | Ratified the derivation and stated it as a foundation: reality supplies the target, so the signal needs no labels | queued |
| 2026-09-02 | Chose "train a linear probe on the frozen representation" as the control for the novelty confound | **misconception** | Equated sophistication with rigour — a deeper measurement felt like a better control. But a probe separates the clips using the disputed novelty signal itself, so both hypotheses predict the same result | Gave the criterion: an experiment is a control only if the competing explanations predict *different* outcomes. Applied it to all four options; only "legal-but-unfamiliar clips" splits them | queued |
| 2026-09-02 | Recurring: answers reasoned correctly, then disowned ("logically A, but really I don't know") — twice | pattern | Evaluating options by plausibility rather than by a criterion, which never yields confidence | Replaced plausibility-matching with the discrimination test, which can be applied without domain knowledge | no |

Rules:
- **Kind matters.** Slips need no card. Gaps need teaching. Misconceptions need dislodging —
  probe their extent before marking fixed.
- A row is closed only after a later retrieval succeeds (quiz, practice, or Anki).
- Recurring root causes get surfaced in the weekly review.
