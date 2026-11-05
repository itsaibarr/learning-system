# Round 1 scorecard: real lesson renders vs the reference (2026-11-03)

**Inputs:** narrated MP4s from `learn figure`, rendered at HyperFrames draft quality. Each pair is the reference on the left and ours on the right, at a comparable beat.

**Scores:** 0 = clearly different, 1 = weak, 2 = comparable, 3 = close.

**Dimensions:**
- **Frm:** composition and framing.
- **Typ:** typography.
- **Col:** colour grammar.
- **Lbl:** labels and callouts.
- **Dep:** depth and material.
- **Den:** information density.

Motion and narration sync were judged from 12-frame sheets per scene, not frame by frame.

| Pair | Frm | Typ | Col | Lbl | Dep | Den | Evidence |
|---|---|---|---|---|---|---|---|
| V1 labels + lens (`u2-cell-switch` 5 s) | 1 | 2 | 3 | 3 | 1 | 1 | Same callout build, same tinted lenses on transistor and capacitor. The reference fills the frame with 3–4 cells; ours shows one small cell in mostly empty board. |
| V2a read + gauge (`u4-sense` 26.5 s) | 1 | 2 | 3 | 2 | 1 | 2 | Same gauge, green wordline, live 0.61 V / 0.90 V readouts, "1" badge. The reference is an extreme close-up with 2× larger numbers and glowing wires; ours is medium-wide and flat. |
| V2b sense amp (`u4-sense` 31 s) | 1 | 1 | 3 | 2 | 1 | 2 | Same hexagon sense amp turning green. The reference label "Sense Amplifier" is about 70 px; ours is about 20 px inside the hexagon. |
| V3 active row (`u3-decoder-mux` 19 s) | 1 | 2 | 2 | 2 | 1 | 2 | Same vocabulary: decoder plate, arrows, 16-bit row address, "Active row" box. The reference pushes in on the row; ours keeps the whole grid at small scale. |
| V4a row-miss chain (`u7-hit-miss` 33 s) | 2 | 1 | 2 | 2 | 2 | 2 | Same five-step chain with a big "Row miss" arc and a "Row hit" shortcut. Our step text (~22 px) is small for 1080p. |
| V4b timing bars (`u7-timings` 30 s) | 1 | 1 | 2 | 2 | 2 | 1 | Both show cycles as bar lengths. The reference stacks bars on the chain; ours is a cleaner chart, but small and sparse. |
| V5 die → banks (`u6-die-banks` 28 s) | 2 | 2 | 2 | 2 | 1 | 2 | Same scale step and bank numbering, with "32 banks" and a bank-group highlight. Ours is a flat top view at this moment (the isometric exploded package comes earlier in the scene). |
| V6 prefetch (`u1-prefetch` 25 s) | 0 | 1 | 2 | 2 | 0 | 1 | Same idea (blocks hopping SSD → DRAM, a loading bar), but our objects fill about 30% of the frame and are flat icons. Clearly different. **Weakest scene.** |
| V7 cell anatomy (`u2-cell-anatomy` 9.5 s) | 2 | 1 | 2 | 2 | 2 | 2 | Shaded silver capacitor, beige transistor block, copper wordline and dimension lines, as in the reference. Missing the large "1T1C DRAM Memory Cell" title card, and dimension labels are small. |

## Verdict
**Not yet visually comparable overall.** The done criteria (≥ 2 on every dimension except depth) are not met.

**What already matches:** colour grammar, callout and lens technique, gauges and readouts, process chains, bank layouts, the font, and the dark board / grid floor. A viewer would recognise the same diagram language.

**What does not match**, consistently:
1. **Scale and framing.** Branch shoots extreme close-ups that fill the frame. Ours are medium-wide with empty board around the subject.
2. **Text size.** Branch labels are about 60–80 px at 1080p; ours are often 20–40 px.
3. **Material and depth.** Glow, cylindrical shading and lighting are mostly absent outside the anatomy scene.

## Fixes for round 2 (in order of impact)
1. Push every camera 1.4–2× closer. Make the callout default 56 px and plate text ≥ 36 px.
2. Use dead space for the subject, not for room around it.
3. Add a kit gradient helper (copper, silver, beige) and a wire glow, and use them in all scenes.
4. Redo `u1-prefetch` at stick/SSD close-up scale.
5. Add a title-card moment ("1T1C DRAM memory cell") where the reference has one.
