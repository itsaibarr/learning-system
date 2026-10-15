# HyperFrames scenes: the picture for every topic that is not maths

A scene is one HTML file. The engine renders it to a narrated MP4 with HyperFrames (HeyGen, Apache-2.0, pinned
version in `learn.py`): headless Chromium captures frames from a paused GSAP timeline, ffmpeg adds the voice.
Use it for history, people, places, events and their causes, arguments, systems, architectures, processes,
protocols, comparisons, mechanisms. Maths with a formula in it stays in Manim (`references/visuals.md`).

```bash
learn figure <short-name> <<'EOF'
<!doctype html> ... one scene ...
EOF
```

The engine speaks your narration first, measures every line, then gives the page its real timing, writes the
`<audio>` tags itself and renders. You never set a duration by hand.

## What the engine gives your page

- `<script type="application/json" id="narration">["line one", "line two"]</script>` is YOUR input: the spoken lines
  (4-40 words each, spoken words only, no markdown or citations), one per beat group.
- `LEARN.start[i]`, `LEARN.dur[i]`, `LEARN.total` (seconds) and `T(i, f)`: the moment fraction `f` (0 to 1) of
  spoken line `i` is said. Estimate `f` from where the phrase sits in the line (by word count; commas are pauses).
- The token `LEARN_TOTAL` in `data-duration` of the root and the stage. Do not write a number there.
- `gsap.min.js` in the same folder: `<script src="gsap.min.js"></script>`. Nothing else is available offline.

## Start from the worked example

`references/hyperframes-example.html` is a finished, passing scene (history, three lines of narration, a timeline
drawn to scale, a camp that fights off an attack). Copy it, keep the two `ENGINE` sections as they are, and rewrite
the `CONTENT` sections: the items, the captions, the `BEATS` list and the motion.

## The teaching rules (the learner asked for these after watching a first version)

1. **One beat per narration phrase. One focus per beat.** The focused things are at full brightness and move or pop.
   Everything else dims to 30% or disappears. The learner must always know where to look. If two things matter,
   make two beats.
2. **One caption per beat, at most 12 words, saying what happened or why it matters** ("The auls are far apart.
   Nobody can help."). The caption carries the meaning for someone who is not listening closely. Never a vague
   word on its own ("held", "result", "ok").
3. **Show cause and effect with the drawing**: things move, stop, merge, change colour, a ring closes. Not with labels.
4. **At most 4 text items on screen at once**, including the caption and the title. A label belongs to its beat and
   leaves with it.
5. **Draw the real thing**: places, routes, animals, tents, water, people, machines, packets, servers. Simple CSS
   shapes or inline SVG you write yourself. Never a box with only a name in it.
6. **Dates, numbers, names and directions come only from the research brief.** Anything drawn only to help (layout,
   distances, positions) is illustrative: say so in the footer line. Never present an illustration as what the
   source shows.
7. **A real scale where there is one**: a timeline with gaps to scale, a map with true relative positions if the
   brief gives them.
8. Dark background `#12161b`, text `#eef1f4`, accents `#5ec8f0 #ffd166 #6ee7a0 #ff6b5e #b69cff`, muted `#8892a0`.
   Colour means something and keeps its meaning across the scene. Text 24px or more; captions 56px.
9. 2 to 4 beat groups per scene, 25 to 60 seconds. One scene per segment of the unit.

## HyperFrames rules the engine checks (it prints the exact failure)

- One paused GSAP timeline, built synchronously, stored in `window.__timelines["main"]`; the root has
  `data-composition-id="main"`.
- Animate only opacity, x, y, scale, rotation, color, backgroundColor, borderRadius. Never `display` or `visibility`.
- No `Math.random`, `Date.now`, timers, `requestAnimationFrame`, endless repeats, `<br>`, external URLs, downloaded
  fonts or images.
- Set starting states with `gsap.set` (the `item()` helper does), not `tl.set` at time 0.
- Text must stay inside the frame and not sit on other text. The engine runs `hyperframes check` and rejects
  errors. Overlapping text is reported as info: fix those too, a viewer cannot read overlaps.

## Minimal skeleton (one line, one beat)

```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1920, height=1080" />
    <script src="gsap.min.js"></script>
    <style>
      * { margin: 0; padding: 0; box-sizing: border-box; }
      html, body { width: 1920px; height: 1080px; overflow: hidden; background: #12161b; }
      #root { position: relative; width: 1920px; height: 1080px; overflow: hidden; font-family: Inter, system-ui, sans-serif; color: #eef1f4; }
      #stage { position: absolute; inset: 0; }
      #caption { position: absolute; left: 160px; top: 110px; width: 1600px; font-size: 56px; font-weight: 700; }
      #ball { position: absolute; left: 200px; top: 560px; width: 90px; height: 90px; border-radius: 45px; background: #ffd166; }
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="LEARN_TOTAL" data-width="1920" data-height="1080">
      <div id="stage" class="clip" data-start="0" data-duration="LEARN_TOTAL" data-track-index="0">
        <script type="application/json" id="narration">["Watch the yellow ball roll to the right, because nothing pushes back on it."]</script>
        <div id="caption">The ball rolls on. Nothing slows it.</div>
        <div id="ball"></div>
      </div>
    </div>
    <script>
      window.__timelines = window.__timelines || {};
      const tl = gsap.timeline({ paused: true });
      gsap.set("#caption", { opacity: 0 });
      tl.to("#caption", { opacity: 1, duration: 0.4 }, T(0, 0));
      tl.to("#ball", { x: 1400, duration: LEARN.dur[0], ease: "none" }, T(0, 0));
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
```
