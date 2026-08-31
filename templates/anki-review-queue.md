# Anki queue

Drafted cards wait here until the user approves a batch; `scripts/anki_push.py` pushes
only batches whose status is `approved`, then moves them to `anki/pushed.md`.

Card-writing rules (from the audit; enforced at draft time, not fixed later):
- One testable idea per card. If the answer has an "and", split it.
- Clear wording, minimal ambiguity; include context in the question where needed
  ("In AS Physics, ..."), never in the answer.
- No overly broad cards ("Explain X"), no cards for things easily re-derived.
- Link back: every card carries `Src:` (vault note or source).

Format (parsed by the script — keep the key lines exact):

```
## Batch: <name> | deck: <Deck::Subdeck> | status: draft

Q: <front — basic card>
A: <back>
Tags: <space-separated>
Src: <[[vault note]] or url>

Text: <cloze card with {{c1::hidden part}}>
Tags: <space-separated>
Src: <...>
```

A card block starts at `Q:` (basic) or `Text:` (cloze) and ends at the next blank line.
Change `status: draft` → `status: approved` by hand after reviewing — that is the gate.
