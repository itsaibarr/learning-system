# Visual reference analysis: Branch Education, "How does Computer Memory Work?"

- **Video:** https://www.youtube.com/watch?v=7J7X7aZvMXQ (35:32, 2022-11-04, 5.4M views when retrieved on 2026-11-03).
- **How it was made (from the video description):** script, modelling and animation by Teddy Tablante, with Mike Radjabov (animation) and Prakash Kakadiya (modelling). It was animated in **Blender 3.1.2** (a 3D program), edited in Adobe Premiere Pro, with a professional voice-over (Phil Lee) and separate sound design.
- **What this means for us:** the reference is rendered 3D CGI. The Learning Harness draws 2D HTML scenes with HyperFrames. Some of the look carries over directly (layout, colour code, labels, timing, diagram language). Some can only be approximated (lit 3D models, materials, a free 3D camera). Section 9 lists both honestly.

**How it was studied:**
- A frame every 4 s, 533 frames on 18 contact sheets. These are not saved here; regenerate them with the command in the README.
- 28 full-resolution key frames in `frames/`.
- 6 one-frame-per-second filmstrips of transitions in `strips/`.
- Colours sampled from pixels.
- Pace measured against the creator's caption track (`dram-memory/transcript/`).
- Opinions are marked "(judgement)". Everything else was observed in frames.

---

## 1. The system in one paragraph

Every idea sits in one physical world, shown on two backgrounds.
- **Wide shots:** objects stand on a lit charcoal floor with a perspective grid.
- **Close-ups:** circuits sit on a near-black board.

The camera moves through scale without cutting:
- PC → motherboard → memory stick → chip package → die → bank → cell array → one cell → the transistor's gate.
- Then it pulls back out again.

On the way the model changes form. It is a realistic object while the video explains what a thing *is*. It becomes a schematic symbol or block diagram while the video explains what it *does*. The same position and colour carry through each change, so the viewer never loses track.

Text is rare and short:
- 1–3 word cyan labels on leader lines.
- Numbers that update live.
- A few large "headline" figures.

The narration does the explaining. Colour has fixed meanings that hold for 35 minutes: green = on, active or 1; red = off or 0; orange = signal wiring; yellow = power or charge flowing. Every narrated clause triggers one visible change. Everything else dims.

## 2. Techniques (T1–T16)

Each technique gives timestamps where you can see it, why it works, and how to build it in HyperFrames (HTML, SVG, CSS 3D transforms, one GSAP timeline).

### T1. Two worlds: grid floor for objects, dark board for circuits
- **Seen:** 0:56–6:00, 6:10–12:00, 27:50 onwards (floor). 12:09–24:00 and 25:00 onwards (board).
- **What:**
  - **Wide shots:** a charcoal floor with a perspective grid that recedes to a horizon. The centre is brighter (#46494b) and the edges darker (#1e2225), a radial vignette. Objects cast soft shadows on it.
  - **Close-ups:** circuit close-ups switch to a near-black field (#101417) with a faint flat grid.
- **Why it works:** the floor gives scale and depth without decoration. The board says "we are now inside the chip", so the change of background marks a change of scale.
- **HyperFrames:** a large `div` with two `linear-gradient` grid layers, a fixed `transform: perspective() rotateX(64deg)`, and a radial-gradient vignette *behind* the content. The vignette must sit behind the content: HyperFrames' layout check treats a full-screen overlay above text as covering it. The board is a flat grid on #111518. (Built in the kit: `.bx-floor`, `.bx-board`.)

### T2. One continuous scale journey
- **Seen:** the computer to the memory stick to the chip (0:00–8:30). Strip `0600s-array-to-die-pullback.jpg`: a 3D cell array pulls back into the die, then the die's banks light up one by one. Frames `0904s`/`0932s`: zoom from one cell's schematic to a whole row.
- **What:** the camera moves between levels of scale instead of cutting. Each level keeps a reminder of where we are, for example the small text "Showing 16 of 8 192 Columns · Showing 8 of 65 536 Rows" and a miniature of the bank with the current area outlined.
- **Why it works:** the viewer builds a mental map of the hierarchy (judgement; this matches Mayer's signalling principle). Nothing appears from nowhere.
- **HyperFrames:** put everything in a `.world` wrapper and tween one camera state (`x`, `y`, `scale`). `scale` and `x` are allowed properties. Draw the next level *inside* the current one at small scale, so zooming in reveals it. Cross-fade detail as the camera reaches it. Keep a small screen-space "you are here" inset that does not move with the camera. (Kit: `BX.cam.set/move`. Blueprint: HyperFrames `camera-journey`, rules `viewport-change` and `coordinate-target-zoom`.)

### T3. Exploded views
- **Seen:** 0:04, the PC case panels fly apart. About 7:58–8:20, the chip package lifts into layers: case, interconnection matrix, ball grid array, die.
- **What:** layers separate along one axis with a short stagger. Then one layer is named and the others fade out.
- **Why it works:** it shows that the inside exists and how it is stacked, before showing what it does.
- **HyperFrames:** stacked SVG or `div` layers with a fixed isometric skew (`rotateX(55deg) rotateZ(-45deg)` set once on a wrapper). Tween each layer's `y` with a stagger. Labels go in screen space, not inside the skewed wrapper.

### T4. Representation shift: real object → symbol → block
- **Seen:**
  - 14:53, "Let's simplify the visual and use symbols": the 3D cell becomes transistor and capacitor symbols on a copper grid.
  - 15:04, translucent lenses over the transistor and capacitor link the two pictures.
  - 8:53, "we're going to transition to a functional diagram": the die becomes grey blocks joined by orange wire bundles.
- **What:** the same object keeps its place and colour while its drawing style changes.
- **Why it works:** the physical picture answers "what is it". The symbol answers "what does it do". The lens bridges the two. (Judgement: this is the single most important technique to copy.)
- **HyperFrames:** draw both versions at the same coordinates. Cross-fade (opacity) and add a lens circle over the part that changes. Never move the camera during the swap.

### T5. Callout labels: dot, leader line, underline, label
- **Seen:** everywhere. Clearest at 12:20–13:30 ("Capacitor", "Conductive Surfaces", "Dielectric Insulator") and in strip `0905s` ("Wordline" → "Gate" → "Bitline", each appearing as it is spoken).
- **What:**
  - A small dot sits *on* the part. A thin cyan line runs out at an angle, then turns horizontal as an underline.
  - The label (1–3 words) sits on the underline.
  - The line draws itself in about 0.4 s, then the label fades in.
  - Labels stay while the part matters, then leave together.
  - Small grey sub-notes can hang under a label ("⇒ 20–30 atoms thick").
- **Why it works:** the word sits next to the thing (spatial contiguity, Mayer d = 0.82 in our own research file). It appears when the word is spoken (temporal contiguity).
- **HyperFrames:** an SVG `path` (dot → elbow → underline) drawn by tweening `stroke-dashoffset` (passes `hyperframes check`), plus an HTML label with a dark text halo. (Kit: `BX.callout`.)

### T6. Highlight lens
- **Seen:** 15:00–15:10 (blue lens on the transistor, peach lens on the capacitor), 32:05.
- **What:** a translucent tinted disc pops over the part being named. Each part gets its own tint, which then stays with it.
- **HyperFrames:** an SVG circle with fill-opacity about 0.26 and a stroke at about 0.7, popped with `scale` and `back.out`. (Kit: `BX.lens`.)

### T7. A fixed colour code (measured)
| Meaning | Colour seen | Sampled | Where |
|---|---|---|---|
| Label / interface text | cyan | #30d8d8–#38d6e6 | all labels |
| On, active, binary 1, open row, row hit | green | #48f030 / #60f060 | active wordline, sense amp "1" |
| Off, binary 0, wrong, row miss, "interference" | red | ~#ff4d4d | passive bitline, failed sense amp |
| Signal and data wiring, warnings | orange | #f09000 / #f0a830 | block-diagram wire bundles, "Row Miss" |
| Power, charge, hazard stripes | yellow | #f0f030 | lightning, striped charged bitlines |
| Metal wires (physical) | copper | ~#c8825a | wordlines and bitlines in the array |
| Background, wide | charcoal | #1e2225 (edge) → #46494b (centre) | grid floor |
| Background, close | near-black | #101417 | circuit board |

- **Why it works:** after a few minutes the viewer reads state from colour alone. Green and red are never used for decoration.
- **HyperFrames:** CSS variables, and a rule in the scene docs: "colour = state".

### T8. Live instruments: gauges, readouts, timers, counters
- **Seen:**
  - 18:00–18:30 (strip `1090s`): a voltage gauge (green → yellow → red, 1.0/0.5/0.0 V) beside the cell. The capacitor readout ticks 1.00 → 0.90 V while the bitline readout ticks 0.50 → 0.65 V.
  - 22:56: a "64.00 ms" timer counts while the capacitor's charge drains.
  - 8:40: a cell count ticks up to 65,536.
  - 23:17: "4800 Million Requests".
- **Why it works:** an abstract quantity (voltage, time, count) becomes something you watch change, at the moment the narration says it changes.
- **HyperFrames:** a GSAP tween on a proxy object with `onUpdate` writing `textContent` (seek-safe), and a gauge marker moved with `y`. (Kit: `BX.counter`, `BX.gauge`.)

### T9. Flow: charge, data and signals moving
- **Seen:**
  - 2:30: cyan data blocks hop from SSD to DRAM ("Prefetching").
  - 3:52: particle streams run between CPU, SSD and DRAM.
  - 18:00: green arrows crawl along the transistor channel.
  - 22:20: bitlines get moving yellow/black hazard stripes when charged.
  - 32:40: chevrons stream along the bitlines.
- **Why it works:** direction and cause become visible: where the charge goes, and what pushes what.
- **HyperFrames:** dashed SVG strokes with an animated `stroke-dashoffset`, and dots moved along the points of a path. Particle fields use a *seeded* random generator, because `Math.random` is banned. (Kit: `BX.flow`, `BX.packet`, `BX.rand`.)

### T10. Binary as a segmented, coloured string
- **Seen:** 9:00–9:40 and 15:31–16:10. A 31-bit address appears, then is bracketed into fields (Bank group | Bank | Row | Column), each field labelled ("RAS Row Address Strobe", "CAS Column Address Strobe"). One field then travels to the decoder it drives.
- **HyperFrames:** one `span` per bit, so a field can change colour, get a bracket, or move. (Kit: `BX.bits`.)

### T11. Functional block diagram
- **Seen:** 8:53–9:40, 16:00–17:40, 26:00 onwards.
- **What:** grey rounded blocks (Row Decoder, Column Multiplexer, Sense Amplifier, Read/Write Driver, Address Input) joined by thick orange wire bundles. Each bundle carries a slash and a width label ("x16", "x8 192"). The active path lights up while the rest stays grey.
- **HyperFrames:** `.bx-plate` blocks plus SVG bundles (several parallel strokes) with width labels. (Kit: `BX.plate`.)

### T12. A process chain with a skip arc, plus timing bars
- **Seen:** 25:40–27:00 (frames `1584s`, `1616s`).
  - "1) Row Close → 2) Precharge Bitlines → 3) Row Open → 4) Column Address → 5) Access 1T1C Cells", with a big curved arrow labelled "Row Miss" returning to step 1.
  - A short arc labelled "Row Hit" loops only steps 4–5.
  - Then each step gets a bar whose length is its clock cycles (39, 39, 40) and "Data Out".
- **Why it works:** the viewer sees the time saved, the skipped bars, rather than being told it.
- **HyperFrames:** an HTML row of steps, SVG arcs drawn with `stroke-dashoffset`, and bars scaled with `scaleX` from 0, in proportion to their cycles.

### T13. Progress markers
- **Seen:**
  - 4:07–6:00 "Quick Notes: 1 2 3 4 5 6": the current number is bright and the others are grey.
  - 17:40 onwards "DRAM Control ☐ Reading ☐ Writing ☐ Refreshing": the current operation is ticked green.
- **Why it works:** the viewer always knows where they are in a long explanation (signalling).
- **HyperFrames:** a small fixed HUD element, updated by colour tweens.

### T14. Comparisons and analogies at true ratios
- **Seen:**
  - 0:47–1:40: a DRAM stick and an SSD side by side, each with "Billion memory cells" / "Trillion memory cells". "17 nanoseconds" vs "50 microseconds", then "x3000".
  - 1:30: a jet ("Mach 3") vs a tortoise.
  - 12:20: dimension lines in nanometres on the cell ("64.0 nm", "360.0 nm").
  - 5:40: "1 foot / ns".
- **HyperFrames:** two objects on one baseline, with dimension lines drawn as SVG and arrowheads.

### T15. Headline figures
- **Seen:** "17 billion memory cells" (8:54), "4800 Million Requests" (23:17), "16 Refreshes / Second", "16 Gigabytes · 4 800 Million Transfers per Second · 38 400 Peak Megabytes per Second" (28:45).
- **What:** a large light-weight cyan number with a small unit or label under it, often counted up. No more than 3 on screen.
- **HyperFrames:** `.bx-big` plus `BX.counter`.

### T16. Honest footnotes
- **Seen:**
  - 13:20 "Note: The shown design is technically closer to a substrate plate capacitor."
  - 23:56 "Note: Video game data is stored in both DRAM and VRAM ..."
  - 0:48 a footnote on SSD latency.
- **What:** tiny grey text at the bottom-left that corrects or qualifies the picture.
- **Why it matters:** the harness already needs this. Its `basis` line ("illustrative, not to scale") is the same idea; keep it.

## 3. Typography
- **Typeface:** one narrow, squarish technical sans with rounded corners, used at two or three weights. The exact font is not named in the credits, so the match is a judgement. **Saira Semi Condensed** (SIL OFL) is close and is used in the kit. Inter (the harness's current font) reads as a UI font and is visibly different.
- **Sizes:** at 1080p, labels are about 40–48 px, headline numbers 70–110 px, and sub-notes and scale reminders 20–28 px.
- **Text on screen:** no sentence captions anywhere in the teaching sections. The longest text is a process chain step ("Column Address Select") or a footnote.

## 4. Composition and spacing
- **Placement:** one subject, slightly off-centre, takes up about 40–60% of the frame. Labels go into the empty side. Labels never cover the subject; they sit at the end of a leader line in free space.
- **Context:** context objects stay in frame but dim to about 25–35% (for example the other cells in the array), or blur with distance on the floor.
- **Dense frames:** dense diagrams (the block diagram, the sense amplifier) are introduced part by part, and the camera frames only the part being discussed.

## 5. Motion and timing (measured)
- **Narration pace:** 5,216 words in about 33 minutes of narrated time, about **2.45 words/s**. That is close to the harness voice (Kokoro, about 2.6 words/s).
- **Visual changes:** something meaningful changes in nearly every 4-second sample; static holds longer than about 6 s are rare (contact sheets).
- **Camera moves:** usually 2–4 s with smooth ease-in-out. Push-ins end slowly. The camera keeps drifting slightly during holds.
- **Labels:** draw in 0.3–0.5 s. New parts pop with a small overshoot. State changes (colour) take about 0.2–0.3 s and land on the word.

## 6. Narration ↔ picture sync
- Sync is per clause, not per sentence. In strip `0905s`, "Wordline", "Gate" and "Bitline" each appear at the moment the voice names them.
- In the sense-amplifier read (strip `1090s`), the voltage numbers start moving on "some charge flows", and the gauge settles on "pushes the voltage all the way up to 1 volt".
- The harness's audio-first timing (`T(i, f)`, measured line lengths) already supports this. Scenes should place events at the word's fraction of the line.

## 7. Why it engages without overloading (judgement, based on the observations above)
1. **One focus at a time.** Everything else dims; the camera frames only the focus.
2. **Persistence.** The same model (the stick, the bank, the cell) returns again and again, so viewers re-use a picture they already understand.
3. **A predictable colour grammar.** No colour needs decoding twice.
4. **Physical first, abstract second.** Each abstraction is introduced as a simplification of something already seen.
5. **Live change instead of text.** Numbers, gauges and flows move as they are spoken about.
6. **Very little reading.**

## 8. Screenshot catalogue

All frames are 1280×720, from the 720p stream. Files are in `frames/`.

| # | Time | File | What is happening | Technique | Worth copying because | How the harness could do it |
|---|---|---|---|---|---|---|
| 1 | 0:04 | `0004s-01-exploded-pc.jpg` | PC case panels fly apart around the motherboard | T3 exploded view | Opens the "inside the box" journey | Staggered `y`/`x` tweens of panel layers in an isometric wrapper |
| 2 | 1:04 | `0064s-02-dram-vs-ssd-cells.jpg` | DRAM vs SSD, cell grids above each with "Billion" / "Trillion memory cells" | T14 comparison, T15 | Two quantities compared on one baseline | Two SVG blocks on the floor; labels below; counters |
| 3 | 1:32 | `0092s-03-analogy-jet-turtle.jpg` | Jet (Mach 3) vs tortoise, "x3000" | T14 analogy | Makes a ratio feel physical | Simple SVG silhouettes moving at a speed ratio |
| 4 | 2:36 | `0156s-04-data-prefetch-blocks.jpg` | Cyan blocks hop from SSD toward DRAM, "Data" | T9 packets | Shows prefetching as motion | `BX.packet` along a curved path, staggered |
| 5 | 3:52 | `0232s-05-particle-flow-cpu-ssd-dram.jpg` | Particle streams between CPU, SSD, DRAM | T9 particles | Shows who talks to whom | Seeded particle dots on SVG paths |
| 6 | 5:04 | `0304s-06-quick-notes-counter.jpg` | "Quick Notes: 1 2 3 4" with the current number lit; CPU and "Speed / Capacity" | T13 progress | Orients the viewer in a list | HUD row of numbers, colour tween |
| 7 | 7:28 | `0448s-07-channels-a-b.jpg` | DIMM slots lit cyan "A" and green "B", "32 bits ↓ 32 data wires" | T7, T11 | Abstract channels drawn onto the real board | Coloured translucent overlays on the drawn DIMM |
| 8 | 7:44 | `0464s-08-wire-count-callouts.jpg` | Boxed callouts "21 wires read/write address", "7 control signal wires" | T5 variant (boxed note) | Numbers attached to the physical thing | `.bx-plate` notes with leader lines |
| 9 | 8:32 | `0512s-09-die-32-banks.jpg` | The 2 GB die with its banks outlined, "32 Banks" | T2, T15 | A scale step with its count | Grid of rectangles, outline tween, counter |
| 10 | 9:20 | `0560s-10-bank-block-diagram.jpg` | Functional diagram: banks, row decoder, sense amps, orange buses | T4, T11 | Physical → functional switch | Plates + bundled SVG strokes |
| 11 | 9:48 | `0588s-11-address-bit-fields.jpg` | 31-bit address split into Bank / Row address / Column address | T10 | Binary made structural | `BX.bits` + field colours + brackets |
| 12 | 12:24 | `0744s-12-cell-dimensions.jpg` | 1T1C cell with "64.0 nm", "360.0 nm" dimension lines | T14 dimensions | Real scale on a tiny thing | SVG dimension lines with end ticks |
| 13 | 12:56 | `0776s-13-capacitor-charge-1.jpg` | Capacitor filled with green hatching, "1", "1.00 Volts" | T7, T8 | State shown as fill + digit + value | Hatched SVG pattern fill, digit swap |
| 14 | 13:56 | `0836s-14-wordline-bitline-labels.jpg` | Bitline, Wordline, Gate, Channel labelled on the 3D cell | T5 | Each part named where it is | `BX.callout` ×4, staggered by narration |
| 15 | 15:04 | `0904s-15-schematic-lens.jpg` | Schematic cell, blue lens on transistor, peach lens on capacitor | T4, T6 | Bridges real cell → symbol | `BX.lens` + cross-fade of two drawings |
| 16 | 15:32 | `0932s-16-active-row.jpg` | One wordline green across the array, "Active Row" | T7 | One row on, the rest off, visibly | Stroke colour tween on one line |
| 17 | 16:12 | `0972s-17-row-decoder-zoom.jpg` | Row decoder arrows, row 27 524 lit green "Active Row" | T2, T10 | Address → physical row | Arrows + bits + camera push |
| 18 | 18:08 | `1088s-18-voltage-gauge.jpg` | Close-up: bitline 0.50 V, cell 1.00 V, gauge | T8 | Voltage becomes visible | `BX.gauge` + `BX.counter` |
| 19 | 18:24 | `1104s-19-sense-amp-states.jpg` | Sense amplifiers turn green (1) / grey, bitline arrows | T7, T9 | The sensing step as colour | Hexagon plates with colour tweens |
| 20 | 22:36 | `1356s-20-refresh-cycle-chain.jpg` | "Row Closing → Bitline Precharging → Next Row Opening → Sense Amplifier Refreshing" over the bank | T12 | A loop shown as a cycle | HTML chain + SVG return arrow |
| 21 | 22:56 | `1376s-21-leak-timer.jpg` | Capacitor draining, "64.00 Milliseconds" timer | T8 | Time-dependence made visible | Counter + fill `scaleY` tween |
| 22 | 25:40 | `1540s-28-already-open-row.jpg` | "Already OPEN Row", the active cells highlighted | T7 | Names a state the narration relies on | Box highlight + label |
| 23 | 26:24 | `1584s-22-row-miss-chain.jpg` | Steps 1–5, big "Row Miss" arc, small "Row Hit" arc | T12 | Skipped work made visible | Steps + two SVG arcs |
| 24 | 26:56 | `1616s-23-timing-bars.jpg` | Timing bars 39 / 39 / 40 clock cycles, "Data Out" | T12, T14 | Latency maths as lengths | `scaleX` bars proportional to cycles |
| 25 | 28:48 | `1728s-24-dimension-callout.jpg` | 32 banks side by side, "8192 x 32 = 262144", "65536" | T14, T15 | Explains why banks are tall | Rectangles + dimension line + counter |
| 26 | 30:16 | `1816s-25-burst-buffer-bits.jpg` | Burst buffer grid of red/green bits feeding the read driver | T7, T11 | Bits as a grid you can watch | SVG grid of cells, colour per bit |
| 27 | 32:36 | `1956s-26-sense-amp-inverters.jpg` | Sense amplifier: cross-coupled inverters, "Active/Passive Bitline" | T4, T5 | A circuit explained by its inputs | Symbols + coloured bitlines + callouts |
| 28 | 33:12 | `1992s-27-numbered-list-gauge.jpg` | "Differential Pair", list "1. Precharge 2. 3.", gauge | T13, T8 | List progress + live state | HUD list + gauge |

**Filmstrips** (`strips/`, 8 frames at 1 frame/s from the start time):
- `0480s-data-lanes-to-power.jpg`: 8-bit data lanes as dotted columns. They hand over to a yellow lightning bolt and crackle for "power", and a callout lands on "Power Management Chips". Shows a topic handover inside one shot.
- `0600s-array-to-die-pullback.jpg`: the copper cell array pulls back and becomes the die. Then banks light up left to right in cyan. This is the scale-journey transition (T2).
- `0905s-cell-to-array-pullback.jpg`: "Transistor", "Capacitor", then "Wordline", "Gate", "Bitline" appear one per spoken word, with lenses fixed on the parts (T5, T6, sync).
- `1090s-sense-amp-read.jpg`: capacitor 1.00 → 0.90 V while the bitline goes 0.50 → 0.65 V; green arrows travel the channel; gauge on the right (T8, T9).
- `1350s-refresh-wave.jpg`: a refresh moves down the bank row by row (T9, T12).
- `1576s-row-hit-skip.jpg`: the row-miss loop and the row-hit shortcut being drawn (T12).

## 9. What HTML can and cannot match

| Aspect | Can match in HyperFrames | Only approximate | Not realistic without 3D |
|---|---|---|---|
| Colour grammar, labels, typography, pacing | ✔ | | |
| Block diagrams, schematics, address bits, timing bars | ✔ | | |
| Gauges, counters, flows, particles | ✔ | | |
| Camera push/pull through scale (2D) | ✔ | | |
| Grid floor with perspective | ✔ (CSS 3D transform) | | |
| Exploded views, isometric parts | | ✔ (fixed isometric CSS 3D, flat-shaded SVG) | |
| Lit 3D models (DIMM, chip package, 3D cell cutaway), soft shadows, depth of field | | partly (gradients, blur on far layers) | ✔ needs Three.js/WebGL |
| Orbiting the camera around a 3D object | | | ✔ needs Three.js |

Plan agreed with the learner (2026-11-03):
1. Build the 2.5D kit first.
2. Add a locally vendored Three.js layer later, only for scenes that need solid 3D objects.

HyperFrames 0.8.161 has a `three` runtime adapter that renders on `hf-seek`. The harness bans external URLs, so `three.module.js` must be vendored the way `gsap.min.js` is.

## 10. Regenerating this material
```bash
# needs a recent yt-dlp; the pip copy was 403'd by YouTube on 2026-11-03, a fresh venv install worked
python3 -m venv /tmp/ytvenv && /tmp/ytvenv/bin/pip install -U --pre "yt-dlp[default]"
/tmp/ytvenv/bin/yt-dlp -f "136/398/247/18" -o video720.mp4 https://www.youtube.com/watch?v=7J7X7aZvMXQ
ffmpeg -i video720.mp4 -vf "fps=1/4,scale=384:-2,tile=6x5:padding=4:color=white" -q:v 4 sheet_%02d.jpg   # contact sheets
ffmpeg -ss <t> -i video720.mp4 -frames:v 1 -q:v 3 frame.jpg                                             # one key frame
```
The reference video is copyrighted. These frames are kept in this private repository only as design reference and are not redistributed.
