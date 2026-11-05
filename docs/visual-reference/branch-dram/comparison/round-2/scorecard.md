# Round 2 scorecard: engine kit + reworked scenes vs the reference (2026-11-04)

**Inputs.** Real narrated MP4s (Kokoro `af_heart`, engine pipeline via `tools/render.py`, HyperFrames draft quality) in `renders/`. Pairs are made by `tools/pairs.py` from `pairs.json`: reference left, our frame right, each 960×540, our frame taken at `T(line, f)` of the real timing.

**Scale.** 0 = clearly different · 1 = weak · 2 = comparable · 3 = close.
**Dimensions.** Frm composition/framing · Typ typography · Col colour grammar · Lbl labels/callouts · Dep depth/material · Mot motion/transitions · Den information density · Syn narration sync.

**How Mot and Syn were judged.** From 1-frame-per-second strips of the real MP4s (e.g. `u4-sense`: readouts, stripes and amplifier colours change every 1-2 s, two camera pans) and the engine's hold check (no scene has a still stretch over 6 s). I did not watch every video with sound. The scenes place every event with `T(line, fraction)` on its word, but the fractions are word-count estimates, so sync is scored 2, not 3, everywhere.

**Who scored.** The same agent that built the scenes. Treat the scores as a self-assessment until the learner has looked at the pairs.

| Pair | Frm | Typ | Col | Lbl | Dep | Mot | Den | Syn | Evidence (visible in the pair image) |
|---|---|---|---|---|---|---|---|---|---|
| V1 labels + lens (`u2-cell-switch` 7.1 s) | 3 | 2 | 3 | 3 | 1 | 2 | 2 | 2 | Same glowing copper grid with 2½ cells across, blue lens on the transistor, peach lens on the capacitor, dot-leader-underline callouts. Ref labels are ~1.5× taller (≈110 px vs ≈72 px). Our neighbour cells are dimmed and their "1" badges barely show; the ref shows them bright. Wires are flat glowing tubes, the ref's are lit 3D bars. |
| V2a read + gauge (`u4-sense` 26.3 s) | 2 | 2 | 3 | 2 | 1 | 2 | 2 | 2 | Green wordline, yellow/black stripes on the bitline, vertical bitline voltage (0.60 V), 0.90 V cell readout, green 1 / red 0 badges, gauge. The ref is a tighter close-up with gauge numbers ~2× ours, and a "Bitline" label we do not show here. |
| V2b sense amps (`u4-sense` 35.3 s) | 3 | 3 | 3 | 2 | 1 | 2 | 3 | 2 | Same layout: green "Sense Amplifier" hexagon beside a grey one, vertical 0.99 V readout, 0.90 V, 1/0 badges, gauge top right. Ref text ~95 px vs ours ~78 px. No row number / wordline driver arrow (belongs to the decoder scene). |
| V3a active row (`u3-decoder-mux` 23.2 s) | 2 | 2 | 3 | 2 | 1 | 2 | 2 | 2 | Same idea: array of cells, green "Active row" box, decoder arrows. The ref array is tilted in perspective on the floor with "Showing 16 of 8 192 Columns" dimension brackets; ours is a flat front view with the decoder plate. |
| V3b decoder close-up (`u3-decoder-mux` 14.1 s) | 2 | 2 | 2 | 2 | 1 | 2 | 2 | 2 | Same parts: 16-bit row address with bracket and label, x16 bus with slash, white decoder arrows. Ref digits are white with green 1s; ours are all cyan. "65,536 choices" sits over wires (readable thanks to the halo, but busier than the ref). |
| V4a row-miss chain (`u7-hit-miss` 34.4 s) | 2 | 2 | 3 | 2 | 2 | 2 | 2 | 2 | Same five numbered steps with a big "Row miss" arc back to step 1 and a "Row hit" arc to step 4. Our steps are boxed plates (ref: bare text with chevrons and sub-notes); our "Row hit" label is dim at this moment. Ref adds the DIMM and cycle boxes at the top. |
| V4b timing bars (`u7-timings` 46.3 s) | 2 | 3 | 3 | 2 | 2 | 2 | 2 | 2 | Bars in proportion to cycles with tick rulers and ns totals, "≈ 3×" headline: large and readable. The ref stacks the bars on the chain with cycle boxes above each segment; ours is a separate chart (the narration splits chain and bars into two scenes). |
| V5 die (`u6-die-banks` 16.8 s) | 3 | 2 | 2 | 2 | 1 | 2 | 2 | 2 | Same composition: "2 GB DRAM Die" title at the top, die lying on the perspective floor with the grey centre strip. Ref title is cyan, ours white with a cyan underline; our die is a flat tilted plane with no thickness and blue banks (ref: dark navy with a cyan bank highlight). |
| V6a prefetch (`u1-prefetch` 4.7 s) | 3 | 3 | 3 | 2 | 2 | 2 | 2 | 2 | Same shot: big cyan "Data", rows of cyan cubes, a translucent cyan beam down to the SSD, grid floor. Our cubes and SSD are flat-shaded 2.5D boxes with a floor shadow; the ref has a photoreal motherboard and SSD. |
| V6b data flow (`u1-prefetch` 27.5 s) | 2 | 2 | 2 | 2 | 1 | 2 | 2 | 2 | **Reference mismatch:** the catalogued 3:52 frame shows the physical cell + DIMM, not the CPU/SSD/DRAM particle flow, so this pair compares style only. Ours: processor, DIMM and SSD on the floor with cubes hopping into DRAM slots, "Save file" callout, loading bar. |
| V7a block diagram (`u6-address` 26.9 s) | 2 | 3 | 3 | 3 | 1 | 2 | 3 | 2 | Same blocks (Address Input, Row Decoder, Bank with orange plate, Sense Amplifier, Column Multiplexer, Read Driver, Bank Group and Bank Control) joined by orange bundles with slashes and cyan x16 / x5 / x10 / x65,536 / x8,192 / x8 labels. The ref is in perspective on the floor; ours is a flat front view on the board. |
| V7b address fields (`u6-address` 30.0 s) | 2 | 3 | 3 | 3 | 1 | 2 | 2 | 2 | 31-bit address, white 0s and green 1s, green "[RAS] Row Address Strobe" bracket over 21 bits, column bits dimmed: the same treatment as the ref. Ref digits are underlined and sit on the floor next to an enlarged Address Input; ours sit above the whole diagram. |
| V8a cell anatomy (`u2-cell-anatomy` 12.9 s) | 3 | 3 | 2 | 3 | 2 | 2 | 2 | 2 | Same "1T1C DRAM Memory Cell" stacked title card, beige block, silver cylinder, cyan 64.0 nm and 360.0 nm dimension lines. Ref has lit metal texture, a 32 nm dimension and the copper array behind; ours is flat 2.5D with a dark copper backdrop. |
| V8b capacitor charge (`u2-cell-anatomy` 22.2 s) | 3 | 2 | 3 | 3 | 2 | 2 | 2 | 2 | Hatched green charge inside the capacitor, "1" badge above, "Capacitor" callout: the same three elements. Ref also shows a "0.92 Volts" vertical readout that we do not. |

## Verdict

- **Done criteria for this round: met on the self-assessment.** Every pair scores ≥ 2 on every dimension except depth/material, which is ≥ 1 everywhere.
- **Compared with round 1, no dimension regressed.** For example, V1 framing went from 1 to 3, V2b typography from 1 to 3, V6 framing from 0 to 3, V4a typography from 1 to 2. Round 1 had no Mot/Syn columns.
- **The remaining gap is the same in nearly every pair: depth and material.** The reference is rendered 3D: lit cylinders, textured metal, arrays and diagrams tilted in perspective. Ours is flat or 2.5D. This is what R12 (Three.js) would address.
- **Still clearly different:**
  1. Perspective-tilted arrays and diagrams (V3a, V7a).
  2. Label size about 1.3–1.5× smaller than Branch in close-ups (V1, V2a).
  3. Process chain and bars are not combined in one picture (V4).

## Found and fixed during this round

- **The CSS-3D grid floor rendered on top of the whole world in the final MP4.** HyperFrames' `snapshot` composited it correctly, so every preview looked fine. V6 lost its SSD, DIMM and CPU. The floor is now a flat SVG drawn in perspective. **Rule: judge from frames of the real MP4, never from snapshots alone.**
- **The section tag collided with plates during camera moves (V3, V4).** It now shows only during the first narration line.
- **Bracket labels could leave the frame (V7b).** They are now kept inside the frame.

## Fixes for round 3 (if the learner wants a closer match)

1. Perspective-tilted array / diagram helper (a `BX.plane` that maps local points to world, so callouts can still be placed).
2. Close-up label size 90 px for one-word callouts; gauge text 1.5×.
3. Address digits: white with green 1s by default in `BX.bits`, with underlines.
4. Bright neighbours with badges in cell close-ups (V1).
