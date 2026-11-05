# Plan: Branch visual style as an engine feature (round 2 onward)

Source: `docs/handoff-branch-visual-style.md`. Written 2026-11-03.
Baseline: 120 passed / 1 skipped (`LEARN_TTS=fake python3 -m pytest scripts/test_learn.py -q`). Voicebox is up.
Learner WIP in `scripts/learn.py` (`reassess`, grading text), `scripts/test_learn.py` and `state/learner.json` stays untouched. All edits go around it. No commits unless asked; branch first if asked.

## Stage 1: Kit ships with the engine (R1, R2, R3, R6 tokens)
- Move `dram-memory/kit/{bx.js,bx.css,fonts/}` to `scripts/vendor/bx/`. The prototype stays importable.
- `hf_prepare`: when the page references `bx.js` or `bx.css`, copy the kit and its fonts into the project, next to `gsap.min.js`.
- Font: first try `@font-face src: url(fonts/saira-*.woff2)`. If `hyperframes check` rejects it, inline a data URI at prepare time.
- `BX.init(tl, {bg: "floor"|"board", section, basis})` builds the background, world, HUD and vignette layers, so a scene is a short HTML page. The vignette always sits below the content.
- `dram-memory/kit/build.py` emits `<script src="bx.js">` instead of inlining. The existing 27 scenes still build.
- **Acceptance:** a kit scene and a non-kit scene both pass `check` through `hf_prepare`. Tests cover the copy and font injection.

## Stage 2: Engine checks (R5 failure, R10 warning)
- Overlap: read the `hyperframes check --json` overlap/occlusion `info` finding format. Promote it to an error when either element is a kit label (`.bx-lbl`, `.bx-big`, `.bx-num`). If the finding does not name the elements, fall back to a bounding-box check that the kit runs in the page.
- Hold gap: the kit records tween start times on `window.__bx`. The engine computes the largest gap and **warns** when it is over 6 s. Method chosen after confirming what can be read without a browser; the fallback is a static scan of `T(i, f)` calls.
- **Acceptance:** tests show the overlap error and the gap warning.

## Stage 3: Kit upgrades from round-1 fixes (R4, R5, R7, R8, R9)
- Defaults scale up: callout 56 px, plate text 36 px or more, headline figures 90 px.
- `BX.frame(t, el, pad)` frames a measured element. Add the "you are here" inset and nested-level reveal.
- `BX.callout` auto-placement: picks the free side and avoids other labels and the subject's bounding box.
- Material: gradient helper (copper, silver, beige), wire glow, cylindrical wire shading by default, beveled gauge with tick bars.
- Vocabulary: `bits` brackets, `bus` with an "x16" slash label, `chain` with skip arcs, timing `bars`, progress `hud`, `dim` lines, `compare` on one baseline, `figure` count-up, `title` card.
- **Acceptance:** each helper has a one-line example and its probe passes `check`.

## Stage 4: Docs and authorability (R11, R14)
- Rewrite `references/hyperframes.md` and the worked example for the labels-only style: API table, colour rule, and the physical → symbol → block progression.
- Add a decision-log row dated 2026-11-03 that supersedes the 2026-10-15 caption rules. Keep rules 5–7 and `basis`.
- A fresh subagent writes one scene from the docs alone. Its scene must pass `learn figure` checks.

## Stage 5: Narration pace (R15)
- Check whether the Voicebox/Kokoro API accepts a speed setting. If it does, add `learn voice --speed 0.9` as a profile preference.
- Add an optional per-scene pause: `data-pause` JSON or `{"pause": s}` entries in the narration list. The timing model inserts silent holds.

## Stage 6: Visual rounds 2…N (Section D)
- Render V1–V7 with real narration through the engine pipeline. Use a dev script that calls `tts_lines`, `hf_prepare` and render directly, so the learner's vault and `state/learner.json` are not written. Scenes come from `dram-memory/scenes/`; `u1-prefetch` is redone at close-up scale.
- Make pairs with ffmpeg and save them in `comparison/round-N/`. Score 8 dimensions with visible evidence for each. Fix, re-render, and repeat until every score is ≥ 2 (≥ 1 for depth) with no regressions.

## Stage 7: Report and R12
- Write `comparison/REPORT.md`: changes, final scores, honest gaps, render-time impact, and the authorability result.
- Recommend for or against R12 (Three.js) from the evidence. The spike happens only after R1–R11 pass.
