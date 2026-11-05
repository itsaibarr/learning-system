# HyperFrames scenes: the picture for every topic that is not maths

A scene is one HTML file. The engine renders it to a narrated MP4 with HyperFrames (HeyGen, Apache-2.0, pinned
version in `learn.py`): headless Chromium captures frames from a paused GSAP timeline, ffmpeg adds the voice.
Use it for anything with parts, steps, places or change over time: machines, organs, cells, buildings, processes,
protocols, routes, history, economies, ecosystems, software. Maths with a formula in it stays in Manim
(`references/visuals.md`).

```bash
learn figure <short-name> <<'EOF'
<!doctype html> ... one scene ...
EOF
```

The engine speaks your narration first, measures every line, then gives the page its real timing, writes the
`<audio>` tags itself and renders. You never set a duration by hand.

**The style is Branch Education's** (decision-log 2026-11-03), and it works for any subject: the **voice explains**,
the picture shows the real thing, and text is **short labels attached to parts**. There are no sentence captions. The
learner reads the full narration in the folded transcript under each video.

## Start from the worked example closest to your topic

Both are finished, passing scenes. Copy one, keep the page skeleton as it is (head, `#root`, `#stage`, and the three
timeline lines at the top and bottom of the script), and rewrite the narration, `BX.init` options and the `{ ... }`
scene block.

| Example | Topic | Shows how to |
|---|---|---|
| `references/hyperframes-example-heart.html` | How the heart pumps blood (biology), 8 lines, ~60 s | draw organic shapes (`shape`, `pipe`), choose topic colours, hinge valves (`turn`), beats (`pulse`), a named gauge, camera moves between places |
| `references/hyperframes-example.html` | Reading one DRAM cell (electronics), 6 lines, ~45 s | use the electronics pack: wires, symbols, voltages, a digit badge |

**Do not draw a circuit unless the topic is electronics.** A heart is drawn as a heart, a lock as stone and water, a
trade route as a map. The electronics pack exists only for chips, circuits and signals.

## What the engine gives your page

- `<script type="application/json" id="narration">["line one", "line two"]</script>` is YOUR input: the spoken lines
  (4-40 words each, spoken words only, no markdown or citations). One line = one clause group of visual events.
- Optional `<script type="application/json" id="pauses">{"2": 1.0}</script>`: extra seconds of silence after line 2
  (0.5-4 s). Use one at a segment boundary so the learner can take in the picture.
- `LEARN.start[i]`, `LEARN.dur[i]`, `LEARN.total` (seconds) and `T(i, f)`: the moment fraction `f` (0 to 1) of
  spoken line `i` is said. Estimate `f` from where the word sits in the line (by word count; commas are pauses).
- The token `LEARN_TOTAL` in `data-duration` of the root and the stage. Do not write a number there.
- Local files next to the page: `gsap.min.js`, and the **BX kit** `bx.js` + `bx.css` (with the Saira font).
  Link them as in the examples. Nothing else is available offline.

## The teaching rules

1. **Each visual event starts on the word it belongs to**: `T(i, f)` where the word is spoken. One event per clause:
   a callout appears, a valve opens, the camera moves, a number ticks, a route draws. **No still stretch longer than
   ~6 s** (the engine warns at more than 6.0 s: `BX hold`). Aim for a change every 3-5 s. Scenes run 45-120 s.
2. **Labels, not captions.** 1-3 words, cyan, on a leader line that points at the part (`BX.callout`), shown when
   the word is spoken and hidden when the part stops mattering. Numbers live on instruments (`readout`, `gauge`,
   `figure`, `axis`). At most one title card per scene (`BX.title`), for the name of the whole thing.
3. **Colour = meaning, never decoration.** Six roles are the same in every topic:

   | Role | Token | Means | Heart | Canal lock | History / trade | Software |
   |---|---|---|---|---|---|---|
   | good / active | `C.good` (green) | on, open, healthy, success, done | valve open | gate open | route open | final answer, test passes |
   | bad / failure | `C.bad` (red) | off, shut, danger, loss, error | valve shut, backflow | gate shut, pressure | route closed, war | error, limit hit |
   | what moves | `C.move` (orange) | flow of anything: matter, goods, data, people | blood flow arrows | water flowing in | caravans, goods | requests, tool calls |
   | energy | `C.energy` (yellow) | power, heat, force, hazard | | gravity | | |
   | labels | `C.label` (cyan) | text on leader lines, nothing else | | | | |
   | structure | `C.structure` (grey), `C.plate` | parts that just exist | | | | |

   **Topic colours:** a topic often has its own things to tell apart (oxygen-poor vs oxygen-rich blood, two
   armies, two chemicals). Choose those colours once at the top of the scene, name them (`const POOR = "#4f74c4"`),
   and keep them for the whole scene. Never use cyan for them (cyan is for labels), and avoid green and red unless
   the thing really is good or bad. A second kind of moving thing may get its own colour, as long as a label says
   which is which.
4. **The thing → how it works → how it connects.** Show what the thing *is* (the object, place or organism), then
   what it *does* (its moving parts and states), then, if useful, how it connects to the rest (grey `plate`s joined
   by arrows). Keep the same place and colour through each change.
5. **Fill the frame.** Frame the subject close (`BX.cam.frame`, zoom 1.2-3): 2-3 parts fill the screen, as in a
   close-up. Empty background around a small drawing is the most common failure. Move the camera between levels of
   scale instead of cutting (whole heart → valve → lungs; whole map → one city). Show `BX.inset` for deep zooms.
6. **Draw the real thing**: organs, machines, buildings, landscapes, maps, people, vehicles, chips. Simple SVG paths
   you write yourself, made solid with `BX.shape(d, "#colour")`. Never a box with only a name in it, except a
   functional `plate` in a block diagram. For an abstract topic (an algorithm, an economy), draw the concrete things
   it acts on (the list being sorted, the coins and shops) and say in `basis` that it is illustrative.
7. **Dates, numbers, names and directions come only from the research brief.** Anything drawn only to help (layout,
   distances, positions, shapes) is illustrative: say so in the `basis` line (`BX.init(tl, {basis: "..."})`). Never
   present an illustration as what the source shows.
8. **A real scale where there is one**: dimension lines with units (`dimline`), bars in proportion (`bar`,
   `compare`), timelines with gaps to scale (`axis`).
9. Text is 24 px or more on screen. Defaults: callouts 72 px, readouts 56 px, headline figures 100 px.

## The BX kit (`bx.js`)

`BX.init(tl, {bg, section, basis})` builds the layers:
- `bg: "studio"`: a plain dark backdrop lit from above. **The default choice for any topic.**
- `bg: "floor"`: a charcoal perspective grid floor, for objects standing on the ground and wide shots.
- `bg: "board"`: a dark circuit board, **only** for electronics close-ups.

`section` is a small grey tag top-left, shown during the first narration line only. `basis` is the footer.

**Coordinates.** Shapes are in *world* pixels (1920×1080 at zoom 1); the camera moves the world. Text `size` is in
*screen* pixels, so a label reads the same size at any zoom (it is sized for the zoom after any camera move running at
that moment has finished). Every animated helper takes its start time first. `const C = BX.C` holds the colours.

### Core: every topic

| Helper | One-line example | What it does |
|---|---|---|
| `BX.cam.set(cx, cy, z)` | `BX.cam.set(900, 560, 1.4)` | Start with world point (cx, cy) at screen centre, zoom z |
| `BX.cam.move(t, cx, cy, z, dur)` | `BX.cam.move(T(2, 0), 960, 540, 0.6, 3)` | Camera leg (2-4 s, ease in-out) |
| `BX.cam.frame(t, rect, {pad})` | `BX.cam.frame(T(1, 0), [700, 400, 500, 300])` | Fill the screen with a world rect or an element (`t = null`: set now) |
| `BX.inset(t, area, {draw, label})` | `BX.inset(T(2, 0), [0, 0, 3840, 2160], {label: "Lungs"})` | "You are here" mini-map; its outline follows the camera |
| `BX.shape(d, colour, {finish})` | `const heart = BX.shape("M650 420 C640 330 ... Z", "#a3424a", {finish: "matte"})` | Any SVG path as a solid, shaded object. `finish`: `"lit"` (default: metal, plastic, wet), `"matte"` (skin, stone, wood, cloth), `"flat"` (maps, big areas) |
| `BX.part(x, y, w, h, colour, {finish})` | `BX.part(300, 400, 220, 90, "#8a5a32", {finish: "matte"})` | The same for a rounded rectangle. Presets: copper, silver, steel, beige, green, plate |
| `BX.prism(x, y, w, h, depth, colour)` | `BX.prism(400, 500, 300, 200, 60, "#7a6a55")` | A 2.5D box with lit top and side and a floor shadow (buildings, crates, blocks) |
| `BX.pipe(d, {w, color})` | `const vein = BX.pipe("M770 400 V-320", {w: 60, color: POOR})` | A lit round tube: pipes, blood vessels, ropes, rivers, roads. `vein.color(t, col)` |
| `BX.arrow(t, pts, {color, w, curve, dash})` | `BX.arrow(T(2, 0.1), [[300, 760], [700, 700], [1100, 760]], {curve: true})` | A line that draws itself and ends in a head: flow, movement, cause → effect. `dash: true` for planned or possible paths. Labels keep off it |
| `BX.flow(t, d, col, dur)` | `BX.flow(T(2, 0), "M1180 650 V520 H560", C.move, 4)` | Travelling dashes along a path: something moving through a pipe or along a route |
| `BX.packet(t, pts, col, dur)` | `BX.packet(T(1, 0), [[100, 500], [900, 500]], C.move, 2)` | One dot travelling the points (a caravan, a parcel, a message) |
| `BX.particles(t, a, b, dur, {n, color})` | `BX.particles(T(1, 0), [300, 500], [1500, 500], 4, {n: 60})` | Seeded stream of dots from a to b (blood cells, water, crowds, gas) |
| `BX.liquid(x, yBottom, w, hMax, col, {level})` | `const w = BX.liquid(400, 900, 600, 300, "#2f6ea3", {level: 0.2}); w.to(T(3, 0.2), 0.9, 4)` | Contents of a container in cut-away that fill or drain (water, blood, fuel). `w.surface(0.9)` = y of the top |
| `BX.move(t, el, dx, dy, dur)` | `BX.move(T(4, 0), boat, 0, -220, 4)` | Slide a shape by (dx, dy) from where it was drawn (a boat rising, a piston, a person walking) |
| `BX.turn(t, el, deg, [ox, oy], dur)` | `BX.turn(T(3, 0), flap, 65, [765, 583], 0.35)` | Rotate about a hinge or pivot (valve, gate, lever, door). `deg` is absolute: 0 = as drawn |
| `BX.pulse(t, el, k, dur, n)` | `BX.pulse(T(0, 0.3), heart, 1.04, 0.3, 2)` | Grow to scale k and back, n times (heartbeat, squeeze, emphasis) |
| `BX.callout(t, ax, ay, text, {avoid})` | `const k = BX.callout(T(0, 0.5), 900, 520, "Left atrium"); k.hide(T(1, 0))` | Dot → leader → underline → label; picks a free side by itself. Or pin the elbow: `BX.callout(t, ax, ay, lx, ly, text)`: the leader runs from the part (ax, ay) to the elbow (lx, ly), then the underline and text run away from the part (right of the elbow if lx ≥ ax, else left), text sitting on the underline |
| `BX.obstacle(els or rects)` | `BX.obstacle([heart, [640, 290, 700, 700]])` | Tell label placement about shapes you drew yourself, so callouts keep off them |
| `BX.label(t, x, y, text, {anchor, size, color, cls, hud})` | `BX.label(T(1, 0), 600, 200, "Right pump", {anchor: "right"})` | Plain label; (x, y) is its baseline. `size` 60 px default, `anchor` left / center / right, `cls` bx-lbl / bx-big / bx-num / bx-small, `hud: true` = screen position. `t = null`: shown from the start |
| `BX.lens(t, cx, cy, r, col)` | `BX.lens(T(0, 0.5), 790, 455, 125, "#7fb6d6")` | Translucent disc over the part being named |
| `BX.box(t, x, y, w, h, col, {dash})` | `BX.box(T(2, 0), 200, 380, 1500, 90, C.good)` | Glowing outline around a region |
| `BX.readout(x, y, v0, fmt)` | `const v = BX.readout(600, 700, 0, (x) => "+" + x.toFixed(1) + " m"); v.to(t, 4, 3)` | Live number that ticks to new values |
| `BX.gauge(x, y, h, {min, max, unit, dp, label, bar, v})` | `const g = BX.gauge(1640, 300, 400, {min: 0, max: 100, unit: "%", dp: 0, label: "Oxygen"}); g.set(t, 98, 1.5)` | Vertical gauge in screen space for any quantity. Default bar runs green (top) to red (bottom); `bar: C.move` for one colour |
| `BX.figure(t, x, y, to, {unit})` | `BX.figure(T(3, 0.2), 1200, 160, 100000, {unit: "beats a day"})` | Headline number counting up |
| `BX.axis(t, x, y, len, {from, to, step, fmt})` | `const ax = BX.axis(T(0, 0.5), 200, 950, 1500, {from: -200, to: 1500, step: 300, fmt: (v) => v < 0 ? -v + " BC" : v + " AD"}); ax.mark(T(1, 0.3), -130, "Routes open")` | A scale for timelines, distances or any quantity. `ax.at(v)` = x of a value |
| `BX.bar(t, x, y, w, h, col, {label})` | `BX.bar(T(4, 0), 200, 700, 39 * 12, 60, C.move, {label: "39"})` | Bar growing to its length. `y` is the top edge |
| `BX.compare(t, x, baseY, items)` | `BX.compare(T(0, 0.3), 400, 800, [{label: "Walk", value: "5 km/h", h: 40}, {label: "Camel", value: "4 km/h", h: 32}])` | Blocks on one baseline with big values |
| `BX.dimline(t, x1, y1, x2, y2, text)` | `BX.dimline(T(1, 0), 1600, 400, 1600, 620, "4 m")` | Dimension line with units |
| `BX.plate(x, y, w, h, text)` | `const p = BX.plate(1300, 560, 380, 160, "Web search")` | Grey functional block (block diagrams only) |
| `BX.chain(x, y, steps)` | `const ch = BX.chain(150, 620, ["Collect", "Pump", "Return"]); ch.on(t, 1); ch.arc(t, 2, 0, "Repeat", C.move)` | Numbered process steps; skip arcs |
| `BX.progress(x, y, items, {row})` | `const p = BX.progress(80, 820, ["Fill", "Open", "Exit"]); p.at(t, 0); p.done(t, 0)` | Checklist or "1 2 3 4" HUD |
| `BX.title(t, text, {sub})` | `const tt = BX.title(T(0, 0), "The Human Heart"); tt.hide(T(0, 0.3))` | One title card per scene |
| `BX.show / hide / dim(t, els)` | `BX.show(T(1, 0), el, {pop: true}); BX.dim(T(2, 0), others, 0.25)` | `show` keeps `els` **hidden until t**, then fades in (`pop`, `rise`). `hide` fades out. `dim` fades to any opacity (also back up: `BX.dim(t, els, 1)`) without hiding first |
| `BX.color(t, els, col, dur, attr)` | `BX.color(T(1, 0), label.el, C.good)` · `BX.color(T(1, 0), chamber, POOR, 0.8, "fill")` | Text colour; for SVG pass `"fill"` or `"stroke"` as the 5th argument (a chamber filling with blood, a gate rim turning green) |
| `BX.draw(t, path, dur)` | `BX.draw(T(0, 0), BX.S("path", {d: "M0 0 L500 0", stroke: C.move}))` | A line that draws itself |
| `BX.S(tag, attrs)` / `BX.D(cls, css, html)` | `BX.S("circle", {cx: 600, cy: 400, r: 20, fill: "#f2f5f7"})` | Raw SVG shape / HTML element in the world |
| `BX.rand(seed)` | `const R = BX.rand(7); R()` | Seeded random numbers (`Math.random` is banned) |

### Electronics pack: chips, circuits and signals only

| Helper | One-line example | What it does |
|---|---|---|
| `BX.wire(x1, y1, x2, y2, {w, color})` / `BX.tube(d, ...)` | `const wl = BX.wire(0, 300, 1920, 300, {w: 16})` | Glowing copper wire; `wl.color(t, C.good)` |
| `BX.fetSym(x, y, {w})` | `const f = BX.fetSym(900, 520, {w: 200})` | Transistor symbol; `f.chTube.color(t, C.good)` |
| `BX.capSym(x, y, {w, charged})` | `const c = BX.capSym(1180, 660, {charged: true})` | Capacitor symbol; `c.fill` is the charge bar |
| `BX.ground(x, y)` | `BX.ground(1180, 750)` | Ground symbol |
| `BX.badge(x, y, {size, value})` | `const b = BX.badge(1300, 600, {value: "1"}); b.set(t, "0")` | Digit plate (green 1 / red 0); `size` wide, 1.5×`size` tall |
| `BX.bits(x, y, str, {size})` | `const b = BX.bits(300, 120, "0110"); b.field(t, 0, 2, C.move); b.bracket(t, 0, 2, "Bank", C.move)` | Binary string; colour and bracket fields |
| `BX.bus(t, pts, {width, n})` | `BX.bus(T(2, 0.5), [[840, 640], [1290, 640]], {width: "x16"})` | Orange bundle of signal wires with a width label |
| `BX.stripes(t, tube, dur)` | `const s = BX.stripes(T(2, 0.3), bitline, 8); s.off(T(4, 0))` | Moving yellow/black hazard stripes on an energised line |

**Return values.** Helpers that animate return an object you can keep: callouts, labels, titles, figures, insets,
arrows, axes and stripes have `.hide(t)`; pipes, wires and arrows have `.color(t, col)`; `readout` has `.to(t, value, dur)`;
`gauge` has `.set(t, value, dur)`; `liquid` has `.to(t, level, dur)`; `badge` has `.set(t, "1"|"0")`; anything with
`.el` or `.g` is the element to pass to `BX.show/hide/dim` (a pipe: `BX.hideNow(vein.g); BX.show(t, vein.g)`). Path strings may hold several pieces (`"M0 0 V100 M50 0 V100"`). `box`, `lens`, `plate`, `shape`, `part`, `flow` and `packet`
return the element itself.

**Contrast.** Cyan, green and red text needs a dark background behind it. Do not put a label on a light shape; place
it beside the shape. When the engine reports `contrast_aa_failure`, the error names the text and its colours. A light
ground under the footer (stone, sand) fails too: keep a dark band at the bottom of the picture.

**Kit files.** You only link `gsap.min.js`, `bx.js` and `bx.css` by name; the engine copies them next to the page
when it renders. Write the scene anywhere.

Items that should appear later must start hidden: helpers with a `t` do this for you; for your own shapes call
`BX.hideNow(el)` and then `BX.show(t, el)`. To move several shapes as one object, put them in a group
(`const boat = BX.S("g", {}); BX.shape(..., {parent: boat})`) and move, turn or pulse the group.

## HyperFrames rules the engine checks (it prints the exact failure)

- One paused GSAP timeline, built synchronously, stored in `window.__timelines["main"]`; the root has
  `data-composition-id="main"`.
- Animate only opacity, x, y, scale, rotation, colours, SVG attributes. Never `display` or `visibility`.
- No `Math.random`, `Date.now`, timers, `requestAnimationFrame`, endless repeats, `<br>`, external URLs, downloaded
  fonts or images.
- **Labels must not overlap other labels or plates at any moment, and must stay inside the frame.** The engine steps
  the whole timeline and fails with `BX label overlap at 12.4s "A" overlaps "B"` or `... "A" is cut off by the frame
  edge`. Fix: hide the first label before the second appears, or let `BX.callout` place it (leave out the elbow point
  and pass the part in `avoid`, or register your shapes with `BX.obstacle`).
- Text contrast must pass WCAG AA; text must stay inside its box.
- Warnings are printed, not fatal: `BX hold` (a still stretch over 6 s). Fix them anyway.
- The checks cannot see meaning: a label that crosses an arrow, a shape hidden behind another, a camera that shows
  empty space. Look at frames of the rendered video before you call a scene done.

## Minimal skeleton (one line, two events)

```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1920, height=1080" />
    <script src="gsap.min.js"></script>
    <script src="bx.js"></script>
    <link rel="stylesheet" href="bx.css" />
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="LEARN_TOTAL" data-width="1920" data-height="1080">
      <div id="stage" class="clip" data-start="0" data-duration="LEARN_TOTAL" data-track-index="0">
        <script type="application/json" id="narration">["Water always runs downhill, so the river carries the boat towards the sea without any engine."]</script>
      </div>
    </div>
    <script>
      window.__timelines = window.__timelines || {};
      const tl = gsap.timeline({ paused: true });
      BX.init(tl, { bg: "studio", basis: "Illustrative" });
      const C = BX.C;
      {
        BX.cam.set(960, 540, 1.2);
        BX.pipe("M300 600 C 700 520, 1200 680, 1620 560", { w: 70, color: "#2f6ea3" });
        BX.packet(T(0, 0.1), [[300, 600], [960, 600], [1620, 560]], C.move, LEARN.dur[0] * 0.8, 18);
        BX.callout(T(0, 0.25), 700, 570, "River");
      }
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
```

## Scenes without the kit

A plain page that only loads `gsap.min.js` still renders (older lessons use it). New scenes use the kit.
