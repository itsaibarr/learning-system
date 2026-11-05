# Report: Branch Education visual style as an engine feature (2026-11-04)

Task: `docs/handoff-branch-visual-style.md`. Plan: `docs/visual-reference/branch-dram/PLAN.md`.
Nothing is committed. The learner's own uncommitted work in `scripts/learn.py` (`reassess`), `scripts/test_learn.py` and
`state/learner.json` is untouched apart from the additions listed here; `state/learner.json` was not edited.

## 1. What changed

**Engine (`scripts/learn.py`)**
- **R1 kit shipped by the engine:** `scripts/vendor/bx/` (`bx.js`, `bx.css`, `fonts/` Saira Semi Condensed 400/600 + OFL).
  - `hf_prepare` copies it into every HyperFrames project whose page links `bx.js` or `bx.css`.
  - Scenes without the kit are unchanged.
- **R2 typography:** Saira loads from local files (`url("fonts/…woff2")`); this passes lint and renders (seen in frames). Inter stays the fallback. The Manim path is untouched.
- **R5 / R10 checks:** `scripts/vendor/learn-audit.js` is injected into every scene. It steps the timeline every 0.2 s:
  - two visible kit labels or plates that overlap → **error**;
  - a label cut off by the frame edge → **error**;
  - more than 6 s of narration with no new timeline event → **warning**, which the engine prints.
- **Clearer errors:** HyperFrames errors now name the failing text and its colours, not only a page-structure path.
- **R15 narration pace:**
  - `learn voice --speed 0.75–1.25` is saved in the profile. The Voicebox API has no speed or tempo option (checked against its OpenAPI schema), so the engine stretches each line with ffmpeg `atempo`, which keeps the pitch.
  - Optional `<script id="pauses">{"2": 1.0}</script>` adds 0.5–4 s of silence after a line. It is validated before any voice is generated.
- **R13 tests:** 7 new tests:
  - kit copy and fonts;
  - local paths allowed;
  - audit injected;
  - overlap error and hold warning through the engine;
  - a real HyperFrames run that catches a real overlap;
  - pauses;
  - voice speed.

  `LEARN_TTS=fake python3 -m pytest scripts/test_learn.py -q`: **125 passed, 1 skipped**.

**Kit (`bx.js`, about 380 lines)**
- **R3 two worlds:** `BX.init(tl, {bg: "board"|"floor", section, basis})` builds every layer, with the vignette under the content. The floor is a flat SVG drawn in perspective (see §4).
- **R4 camera:**
  - `cam.set/move` remember every move, so helpers know the zoom at any moment.
  - `cam.frame(t, rect|element)` frames an element.
  - `inset(...)` is a "you are here" mini-map whose outline follows the camera.
- **R5 labels:**
  - `callout(t, ax, ay, "Label", {avoid})` picks a free side automatically. Obstacles are stored in world space, so camera moves are accounted for.
  - Text sizes are screen pixels (callouts 72 px by default).
  - `lens`, `label`, `title`.
- **R6 colour grammar:** `C.*` tokens and CSS variables, `badge` (green 1 / red 0), `hatch`, moving hazard `stripes`.
- **Material:**
  - `tube`/`wire` draw lit round wires with a glow;
  - `part` gives gradient metals;
  - `prism` draws lit 2.5D boxes with a floor shadow;
  - `beam` draws translucent light beams.
- **R7 instruments:** `readout`, `counter`, `gauge` (beveled, tick bars), `figure` count-up, `bar`.
- **R8 flows:** `flow`, `packet`, seeded `particles`.
- **R9 vocabulary:**
  - `bits` with `field` and `bracket`;
  - `plate`;
  - `bus` with mitred parallel wires and a cyan width label;
  - `chain` with `on`/`arc`;
  - `dimline`, `compare`, `progress`.

**Docs (R11, R14)**
- `skills/teach-understanding/references/hyperframes.md` is rewritten for the labels-only style: teaching rules, the colour rule, physical → symbol → block, and an API table with a one-line example per helper.
- New worked example `hyperframes-example.html`: a DRAM cell read, 6 lines, ~45 s.
- `decision-log.md` has a row dated 2026-11-03 that supersedes the 2026-10-15 caption rules and keeps rules 5–7 and `basis`.
- `SKILL.md` and two engine hints no longer ask for captions.

**Scenes:** `dram-memory/scenes/` reworked for round 2:
- `u2-cell-switch`, `u1-prefetch`, `u4-sense`, `u3-decoder-mux`, `u7-hit-miss`, `u7-timings`, `u6-die-banks`, `u6-address`, `u2-cell-anatomy`.
- Round-1 versions are in `dram-memory/build/*.round1.scene.bak`.
- `dram-memory/kit/build.py` now links the engine kit and builds previews with the engine's own `hf_prepare`.

**Tooling:** `tools/render.py` runs voice → engine checks → render without a learn session, so nothing goes to the vault or state. `tools/pairs.py` builds reference/ours pairs at `T(line, f)` of the real timing.

## 2. Final scores (round 2, `round-2/scorecard.md`)

Scores are 0–3. Every pair is ≥ 2 on every dimension except depth/material, which is ≥ 1 everywhere. No dimension regressed from round 1. Typical row:

| | Frm | Typ | Col | Lbl | Dep | Mot | Den | Syn |
|---|---|---|---|---|---|---|---|---|
| Round 1 (9 pairs, range) | 0–2 | 1–2 | 2–3 | 2–3 | 0–2 | – | 1–2 | – |
| Round 2 (14 pairs, range) | 2–3 | 2–3 | 2–3 | 2–3 | 1–2 | 2 | 2–3 | 2 |

**Caveats on these scores:**
- They are a self-assessment by the agent that built the scenes.
- Motion and sync were judged from 1-fps strips and the hold check, not by watching every video with sound.
- The handoff's last done criterion, **"the learner has seen the final pairs"**, is still open.

Note on numbering: round 1 scored cell anatomy as "V7". Round 2 adds the handoff's real V7, the block diagram with buses (`u6-address`), and keeps cell anatomy as V8. The catalogued reference for V6b (3:52) shows the physical cell, not the particle flow, so that pair compares style only.

## 3. Remaining gaps, stated plainly

1. **Depth and material (all pairs).** Branch is rendered 3D: lit cylinders, textured metal, bloom, and arrays and diagrams tilted in perspective. We draw flat or 2.5D: glowing tubes, gradient parts, shaded prisms. V3a (active row) and V7a (block diagram) look clearly flatter than the reference.
2. **Label size in close-ups:** about 1.3–1.5× smaller than Branch (V1, V2a).
3. **Chain + bars in one picture (V4):** the narration splits them into two scenes.
4. **No exploded 3D object:** reference 0:04 and 7:58 need R12.

## 4. Things found along the way

- **Snapshots lie about 3D compositing.** The CSS `perspective() rotateX()` floor passed `hyperframes check` and looked right in `hyperframes snapshot`. In the final MP4, though, it covered everything in the world layer: V6 lost its SSD, DIMM and CPU.
  - Fix: the floor is now a flat SVG with the same perspective geometry.
  - Rule: judge only from frames of the real MP4 (`tools/pairs.py` does).
- **The audit found real defects in existing lessons** that `hyperframes check` passed: overlapping labels in `u5-refresh-timing`, `u6-address` and `u9-diff-amp`. The scenes not reworked here (`u5-refresh-timing`, `u9-diff-amp`, and the other 15 not in the comparison set) were not re-checked against the final kit; re-run `kit/build.py <name> --preview` plus `check` before re-rendering any of them.
- **Kokoro speaks at 2.6–3.2 words/s** (measured on 10 scenes), faster than the 2.6 words/s planning figure. `learn voice --speed 0.9` brings it to about 2.35–2.85.

## 5. Render-time impact

Measured on the 9 round-2 scenes, each 44–57 s long, on this Mac (GPU, HyperFrames draft quality):

| Step | Time |
|---|---|
| Voice (Voicebox/Kokoro) | 9–15 s |
| Check + render | 37–81 s |

The in-page audit runs once per page load. It steps about 250–290 positions. Its cost was not measured separately; the totals above include it. Scenes with many SVG elements and glow layers (`u7-timings`, `u2-cell-switch`) sit at the slow end.

## 6. Can a fresh, weaker model write a passing scene from the docs alone? (R14)

Tested twice with Claude Haiku (the cheapest model available here, standing in for free OpenCode models), reading only `hyperframes.md` and the example:

| Run | Topic | Result | What it showed |
|---|---|---|---|
| 1 (before fixes) | Cache hit vs miss | Passed on attempt 6 | Five blind failures on one contrast error that named only a page-structure path. |
| 2 (after fixes) | SSD flash cell | **Passed on the first run** | Clean after 3 small edits: two to clear hold warnings, one for a badge glyph overflow (a kit bug, now fixed). |

Fixes made between the runs: errors name the text and its colours, and the docs gained return values, contrast advice and where the kit files come from. The remaining doc gaps it named are now covered too: label options, the `color` arguments, badge size, and the exact 6.0 s hold threshold.

**Answer: yes, with the current docs.** The engine's error messages are what make this work for a weak model.

## 7. Recommendation on R12 (Three.js)

**Recommendation: do the R12 spike, scoped to one scene (the DDR5 stick exploding into its chips), and keep 2.5D as the default.**

The evidence:

- **Depth is the one dimension that stays at 1.** It scores 1 in 9 of the 14 pairs and 2 in the other five (V4a, V4b, V6a, V8a, V8b), while every other dimension is at 2–3. The gaps named in those pairs are things 2D cannot fake convincingly: lit cylinders and textured metal (V8), perspective-tilted arrays and diagrams (V3a, V7a), and an exploded 3D object (reference 0:04). Further 2.5D work brought diminishing returns. Prisms, gradients and glow lifted V6a and V8 to 2, but not the arrays.
- **What argues for keeping the scope small:**
  1. CSS 3D has already shown one renderer-only compositing bug (§4). A WebGL canvas avoids DOM compositing but must also be verified on real MP4 frames, not snapshots.
  2. Labels and callouts, colour grammar, instruments and the diagram vocabulary already score 2–3 in 2D and do not need 3D.
  3. Every 3D scene raises the bar for free models: the docs and API would need to stay as small as the 2D kit's.
- **Success test for the spike:** the exploded-stick scene scores ≥ 2 on depth against reference 0:04, renders in under ~2× the time of a 2.5D scene of the same length, passes the engine checks, and keeps callouts in 2D screen space over the 3D canvas.

## 8. What the learner should look at

- **The pairs:** `comparison/round-2/*-pair.jpg`, 14 images, reference left and ours right. Start with V1, V6a, V7a and V8b; then V3a and V7a for the flatness gap.
- **The videos:** `comparison/round-2/renders/*.mp4`, 9 lesson scenes plus the kit gallery.
- **The scores and evidence:** `comparison/round-2/scorecard.md`.
