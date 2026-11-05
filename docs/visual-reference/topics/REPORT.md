# Topic-neutral kit: test on four non-computer topics (2026-11-04)

Question: was the BX kit overfitted to DRAM / computers? Yes: the materials were metals only, the colour rules spoke of
1/0, charge and signals, the gauge showed volts, `board` was a circuit board, and every example was a chip.

## What changed (decision-log 2026-11-04)
- Core helpers for any subject: `shape` and `part` lit from any `"#rrggbb"` with `finish` lit / matte / flat; `pipe`;
  `arrow` (curve, dash; labels keep off the line itself); `axis` (timelines, scales); `liquid`; `move`, `turn`, `pulse`;
  `obstacle`; `gauge` with `min/max/unit/dp/label/bar`; `label(..., {hud})`; `bg: "studio"`; colour roles `C.good/bad/move/energy/label/structure`.
- Fixes found by the tests: labels are sized for the zoom after the running camera move (they came out a third of
  their size during pull-outs); `label(null).hide()` works; the basis footer has a dark backing; the audit's fix hint
  depends on the error.
- Docs: rules without electronics, a colour-role table with rows for biology, mechanics, history and software, the API
  split into a core and an electronics pack, a second worked example (the heart).
- Tests: every public helper is in the docs; the heart example has no electronics and passes the real render. 127 passed, 1 skipped.
- Back-compatible: all 9 DRAM scenes, the gallery, the DRAM example and agent-loop still pass the checks unchanged.

## The four scenes (real narrated MP4s, frames checked from the video)

| Scene | Written by | Engine runs | Notes |
|---|---|---|---|
| `heart/` | Opus fork, then refactored onto the new helpers | 4 renders | Now the worked example `hyperframes-example-heart.html` |
| `canal-lock/` | Opus fork | 3 renders | Cut-away stone, water and boat rising; gate states in green/red |
| `silk-road/` | Opus fork | 4 renders | Map, routes, caravans, timeline. Weakest: flat map, wide shot thin |
| `photosynthesis/` | **Claude Haiku from the docs only** | 2 (passed the checks on run 1) | Drew a leaf cross-section, not a circuit. Leaders cross the stalk in places |

## Still open
- Depth: all four are flat 2.5D (as with DRAM, see `branch-dram/comparison/REPORT.md` §7 on R12).
- Maps: no map helpers (coastline, city marker); about 15 lines of SVG per scene. Add a pack only if map topics recur.
- The checks cannot see meaning (a label crossing a shape, an empty frame); frame review stays part of the job.
