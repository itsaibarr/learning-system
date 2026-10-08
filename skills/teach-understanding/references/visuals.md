# Visuals: Manim, the 3Blue1Brown way

The learner understands pictures far better than text. Every theory block needs a
**Manim** visual of how the idea works (the engine refuses blocks without one). Manim is
the animation engine behind 3Blue1Brown: things move, formulas transform, the eye
follows the idea. Stock photos and AI-generated images are never used.

Installed locally and free: Manim Community 0.21 in its own environment, plus TinyTeX
for LaTeX (`MathTex`, `Tex`). `learn figure` finds both itself.

## Pick the template

| The idea is about | Template | Command |
| --- | --- | --- |
| Physical things moving: particles, waves, objects, forces | Physical | `learn figure <name>` |
| A formula, an equation to solve, a derivation | Derivation | `learn figure <name>` |
| A curve, a function, numbers changing | Graph | `learn figure <name>` |
| Steps of a process, a protocol, an algorithm | Process | `learn figure <name>` |
| A system of parts and what flows between them | System | `learn figure <name>` (or `--still` for a picture) |

Without flags you get a **narrated MP4** that plays inside the note: the scene's `NARRATION`
is spoken by a local voice (Kokoro, via Voicebox) first, and each `self.voice(i)` block is timed to its line.
`--still` renders the last frame as a PNG (static diagrams, picture answers; no voice).
`--silent` makes an animation without a voice; use it only when speech would add nothing.

## How to make one

1. Copy the closest template below. Change only the part under `--- edit`.
2. `learn figure <short-name> <<'EOF'` ... `EOF` (add `--still` for a picture).
3. If it is rejected, read the reason, fix that one thing, re-run with the same name.
   The engine checks, in this order: old-Manim code, the render itself (Python and
   LaTeX errors, with LaTeX's own message), text that overlaps other text or is cut off
   at the frame edge (checked after EVERY play/wait), length 2-90 s, size.
4. Paste the printed `EMBED:` line into the theory block, right after "Why we need this".
   `learn block` adds a folded transcript of the narration under the video by itself.

After 3 failed Manim attempts in a row the engine also accepts the matplotlib fallback
at the end of this file. Use it only then.

## Manim Community only (your training data has old code)

Write `from manim import *` and one `class Name(Scene)` with `construct(self)`.
3Blue1Brown's own videos use ManimGL, a different library. Its code does not run here,
and the engine rejects it before rendering:

| Old (ManimGL / legacy) | Manim Community |
| --- | --- |
| `from manimlib import *` | `from manim import *` |
| `ShowCreation(x)` | `Create(x)` |
| `TextMobject("...")` | `Text("...")` or `Tex("...")` |
| `TexMobject("...")` | `MathTex("...")` |
| `GraphScene`, `self.setup_axes()`, `get_graph` | `axes = Axes(...)`, `axes.plot(f)` |
| `CONFIG = {...}` | arguments in `construct()` |
| `FadeInFrom(x, DOWN)` | `FadeIn(x, shift=DOWN)` |
| `InteractiveScene`, `self.embed()` | `Scene`, remove it |

## Rules for a scene that teaches

- **Draw the thing, not a box with its name.** Molecules, a wave, a robot arm, a vector:
  draw them and move them. Boxes are only for systems of parts.
- **Show the misconception being wrong.** If the brief lists one, make the scene
  disprove it (Physical follows one molecule to show the air stays).
- **One sub-idea per scene, 60-120 s**, paced by its voice blocks (see Narration).
- **Short title, not captions.** One title at the top (1-5 words) and short labels on objects;
  the voice does the explaining.
- **Layout with relations, never raw coordinates for text:** `.to_edge(UP)`,
  `.next_to(obj, DOWN, buff=0.3)`, `VGroup(...).arrange(RIGHT, buff=0.6)`.
  `FadeOut` old text before new text takes its place.
- **Colour means something:** BLUE = the main object, YELLOW = what to look at,
  GREEN = the result, RED = the wrong idea or the thing to follow.
- **Words in `Text`, maths in `MathTex`.** Use raw strings: `MathTex(r"\frac{1}{f}")`.
  Units with `\,\mathrm{m/s}`. Font size 24 or more.
- **Numbers come from the research brief.** If a number only shows the shape of the
  idea, say "illustrative" in a label or in the narration.
- **Motion from a formula** (`ValueTracker` + updaters), so it is physically right. Check
  any marker you place ("the squeeze is here") against the formula, not by eye.

## Narration (every animation): audio-first

Each scene has a module-level `NARRATION` list, one spoken phrase per visual event, and wraps
each event in `with self.voice(i):` (1-based, in order). `learn figure` speaks the lines FIRST,
measures them, then renders: each voice block lasts exactly as long as its line (plus a short
gap), so the words and the picture they describe happen together (Mayer: temporal contiguity,
the largest effect in multimedia learning). The video ends on a 2 s hold.

```python
NARRATION = [
    "Before any data moves, the client asks to open a connection ...",
    "The server agrees and answers with SYN ACK ...",
]
...
        with self.voice(1) as d:          # d = the line's real length in seconds
            self.play(GrowArrow(syn), run_time=1.5)     # shorter is fine: the block waits for the voice
        with self.voice(2) as d:
            self.play(Create(curve), run_time=d)        # or stretch one animation over the whole line
```

Rules (research: `docs/research/teaching-quality/multimedia.md`):

- **One phrase, one visual event.** A line describes exactly what animates inside its block.
  4-40 words (8-15 s). Long explanation = more lines and more blocks, not longer lines.
- **One scene = one segment = one sub-idea, 60-120 s** (hard cap 3 min). A unit uses 2-4 scenes
  with notes between them, never one long video.
- **No on-screen sentences that repeat the narration.** Keep a short title, 1-4 word labels next to
  the object they name, formulas, and arrows or highlights at the moment the voice names them.
- **Animate only what changes over time** (processes, motion, transformations). Structures,
  classifications and comparisons can be a still (`--still`) or a build-up with few moves.
- **Spoken words only**: "lambda equals v over f", "three hundred forty three metres per second".
  No LaTeX, citations or markdown in NARRATION.
- **Explain what to notice and why**, introduce a term the first time it appears, say "you".
- If the voice engine is down, the silent video is saved with a WARNING and the lesson continues.
- Older scenes with numbered captions ("1  ...") and no voice blocks still work (caption sync).

## Template: Physical

```python
# TEMPLATE: the physical thing itself, moving (particles, waves, objects). Motion comes from a formula.
from manim import *

NARRATION = [
    "Each dot is a bit of air. Watch the yellow arrows: a squeeze of crowded air travels to the right, and that moving squeeze is the sound.",
    "Now follow the red dot. It only rocks back and forth around the dashed line. It never travels with the wave.",
    "So the push moves forward while the air stays put. That is why sound needs a material to travel through.",
]

class Physical(Scene):
    def construct(self):
        # --- edit below: rest positions and the motion rule ---
        xs, ys = np.linspace(-6, 6, 36), np.linspace(-1.6, 1.0, 6)
        rest = [(x, y) for x in xs for y in ys]
        k, A, speed = 2 * PI / 4, 0.35, PI     # wavelength 4 units, wobble size, phase per second
        t = ValueTracker(0)
        def pos(x, y):
            return [x + A * np.sin(k * x - t.get_value()), y, 0]
        dots = VGroup(*[Dot(pos(x, y), radius=0.05, color=BLUE) for x, y in rest])
        watch = 6 * 17                              # one bit of air to follow
        dots[watch].set_color(RED).scale(1.8)
        dots.add_updater(lambda g: [d.move_to(pos(x, y)) for d, (x, y) in zip(g, rest)])
        def squeezes():                             # compressions sit where k*x - t = pi (mod 2*pi)
            c0 = ((PI + t.get_value()) / k) % 4 - 6
            return VGroup(*[Arrow([c - 0.4, 1.55, 0], [c + 0.4, 1.55, 0], buff=0, color=YELLOW)
                            for c in np.arange(c0, 6, 4)])
        arrows = always_redraw(squeezes)
        self.add(dots, arrows, Text("Sound in air", font_size=30).to_edge(UP))
        with self.voice(1) as d:                    # the voice block lasts exactly as long as line 1
            self.play(t.animate.increment_value(speed * d), run_time=d, rate_func=linear)
        with self.voice(2) as d:
            line = DashedLine([xs[17], -2.0, 0], [xs[17], 1.2, 0], color=RED)
            tag = Text("one bit of air", font_size=24, color=RED).next_to(line, DOWN, buff=0.1)
            self.play(Create(line), FadeIn(tag), run_time=1)
            self.play(t.animate.increment_value(speed * (d - 1)), run_time=max(0.5, d - 1), rate_func=linear)
        with self.voice(3) as d:
            self.play(t.animate.increment_value(speed * d), run_time=d, rate_func=linear)
```

## Template: Derivation

```python
# TEMPLATE: a formula built step by step (LaTeX). Matching pieces glide into place while the voice explains each move.
from manim import *

NARRATION = [
    "Speed equals frequency times wavelength: how many waves pass each second, times the length of one wave.",
    "We want the wavelength on its own, so we divide both sides by the frequency.",
    "Sound in air travels at about three hundred forty three metres per second. Put that in, with a frequency of three hundred forty three hertz.",
    "The units cancel to metres. One wave of this sound is exactly one metre long.",
]

class Derivation(Scene):
    def construct(self):
        # --- edit below: the steps (one argument per piece, so equal pieces glide) and a 1-3 word tag each ---
        steps = [MathTex(r"v", r"=", r"f", r"\lambda"),
                 MathTex(r"\lambda", r"=", r"\frac{v}{f}"),
                 MathTex(r"\lambda", r"=", r"\frac{343\,\mathrm{m/s}}{343\,\mathrm{Hz}}"),
                 MathTex(r"\lambda", r"=", r"1\,\mathrm{m}")]
        tags = ["the wave equation", "divide by f", "put in numbers", "result"]
        for s in steps:
            s.scale(1.4)
        self.add(Text("Wavelength from speed", font_size=30).to_edge(UP))
        tag = Text(tags[0], font_size=26, color=YELLOW).to_edge(DOWN)
        with self.voice(1):
            self.play(Write(steps[0]), FadeIn(tag))
        for i in range(1, len(steps)):
            with self.voice(i + 1):
                new_tag = Text(tags[i], font_size=26, color=YELLOW).to_edge(DOWN)
                self.play(TransformMatchingTex(steps[i - 1], steps[i]), Transform(tag, new_tag), run_time=1.5)
                if i == len(steps) - 1:
                    self.play(Circumscribe(steps[i], color=YELLOW))
```

## Template: Graph

```python
# TEMPLATE: a curve with what matters marked (LaTeX labels). Each feature appears as the voice names it.
from manim import *

NARRATION = [
    "This curve is the air pressure at your ear over one second: it rises above normal, falls below, and repeats.",
    "The yellow arrow is the amplitude, the height of each swing. A bigger swing means a louder sound.",
    "The green arrow spans one period, half a second here. So two waves arrive every second: a frequency of two hertz, which we hear as pitch.",
]

class Graph(Scene):
    def construct(self):
        # --- edit below: the function and its features (values from the research brief) ---
        A, f = 1.0, 2
        axes = Axes(x_range=[0, 1, 0.25], y_range=[-1.5, 1.5, 0.5], x_length=9, y_length=4.2,
                    y_axis_config={"include_numbers": True, "font_size": 24}).shift(0.4 * DOWN)
        labels = axes.get_axis_labels(Tex("time (s)", font_size=28), Tex("pressure", font_size=28))
        wave = axes.plot(lambda t: A * np.sin(2 * PI * f * t), color=BLUE)
        self.add(MathTex(r"p(t) = A \sin(2\pi f t)", font_size=40).to_edge(UP))
        with self.voice(1) as d:
            self.play(Create(axes), Write(labels), run_time=1)
            self.play(Create(wave), run_time=max(1, d - 1))
        with self.voice(2):
            amp = DoubleArrow(axes.c2p(0.125, 0), axes.c2p(0.125, A), buff=0, color=YELLOW)
            self.play(GrowFromCenter(amp), Write(MathTex(r"A", color=YELLOW).next_to(amp, LEFT, buff=0.15)))
        with self.voice(3):
            per = DoubleArrow(axes.c2p(0.125, 1.25), axes.c2p(0.625, 1.25), buff=0, color=GREEN)  # peak to peak
            self.play(GrowFromCenter(per), Write(MathTex(r"T = \tfrac{1}{f} = 0.5\,\mathrm{s}", color=GREEN,
                                                          font_size=34).next_to(per, UP, buff=0.1)))
```

## Template: Process

```python
# TEMPLATE: a process step by step. Each message travels while the voice explains that step.
from manim import *

NARRATION = [
    "Before any data moves, the client asks to open a connection. It sends a SYN message carrying its own starting number.",
    "The server agrees and answers with SYN ACK: it confirms the client's number and sends a starting number of its own.",
    "Finally the client confirms the server's number with an ACK. Both sides now know where counting starts, so data can flow in order.",
]

class Process(Scene):
    def construct(self):
        # --- edit below: the two parties and the messages, in order ---
        client = VGroup(RoundedRectangle(corner_radius=0.15, width=2.4, height=1.0, color=BLUE),
                        Text("client", font_size=28)).to_edge(LEFT, buff=1.0)
        server = VGroup(RoundedRectangle(corner_radius=0.15, width=2.4, height=1.0, color=GREEN),
                        Text("server", font_size=28)).to_edge(RIGHT, buff=1.0)
        self.add(Text("TCP three-way handshake", font_size=30).to_edge(UP), client, server)
        steps = [("SYN  seq=100", client, server, 1.2), ("SYN-ACK  seq=300 ack=101", server, client, 0.0),
                 ("ACK  ack=301", client, server, -1.2)]
        for i, (label, src, dst, y) in enumerate(steps, 1):
            with self.voice(i):
                start = [src.get_center()[0] + (1.3 if src is client else -1.3), y, 0]
                end = [dst.get_center()[0] + (1.3 if dst is client else -1.3), y - 0.5, 0]
                arrow = Arrow(start, end, buff=0, color=YELLOW)
                self.play(GrowArrow(arrow), FadeIn(Text(label, font_size=24, color=YELLOW).next_to(arrow, UP, buff=0.1)),
                          run_time=1.5)
        self.play(Indicate(client), Indicate(server))
```

## Template: System (animated; `--still` gives a picture)

```python
# TEMPLATE: a system of parts, built up one part at a time (also works with --still for a picture).
from manim import *

NARRATION = [
    "It starts with your voice: tiny ups and downs in air pressure travel out from your mouth.",
    "Those pressure changes push the microphone's thin diaphragm back and forth, copying the wave.",
    "The moving diaphragm makes a changing voltage, so the sound has become an electrical signal a computer can measure.",
]

class SystemDiagram(Scene):
    def construct(self):
        # --- edit below: the parts, left to right, and a 1-3 word label each ---
        names = ["voice:\nair pressure", "microphone:\ndiaphragm moves", "signal:\nvoltage over time"]
        tags = ["1  air pushes", "2  diaphragm moves", "3  voltage"]
        colors = [BLUE, YELLOW, GREEN]
        parts = VGroup(*[VGroup(RoundedRectangle(corner_radius=0.2, width=3.4, height=1.6, color=c),
                                Text(n, font_size=26, line_spacing=0.8)) for n, c in zip(names, colors)]
                       ).arrange(RIGHT, buff=1.0)
        arrows = [Arrow(a.get_right(), b.get_left(), buff=0.1, color=GREY) for a, b in zip(parts[:-1], parts[1:])]
        labels = [Text(s, font_size=24, color=c).next_to(p, UP, buff=0.35) for s, c, p in zip(tags, colors, parts)]
        self.add(Text("How a microphone hears you", font_size=36).to_edge(UP))
        for i, (part, label) in enumerate(zip(parts, labels)):
            with self.voice(i + 1):
                if i:
                    self.play(GrowArrow(arrows[i - 1]), run_time=0.6)
                self.play(Create(part[0]), Write(part[1]), FadeIn(label))
```

## Questions about a picture

A question can show a figure above its options. Make a NEW figure for the question (not
the one from the theory), so the learner has to read it:

```json
{"type": "choice", "level": 2,
 "figure": "![[Attachments/learn/sound-basics/q-wave.mp4]]",
 "question": "In the animation, which wave has the higher pitch?",
 "options": [{"text": "The lower one, it has more waves per second", "correct": true},
             {"text": "The upper one, it is taller", "misconception": "Confuses height (loudness) with pitch"}],
 "why": "Pitch is frequency: more waves per second. Height is amplitude, which is loudness."}
```

Pictures can also BE the options (they render inside the checkboxes). Render one small
still per option with `--still`, same axes and scale, and use the embed with a width:

```json
{"type": "choice", "level": 2,
 "question": "Which picture shows the louder sound?",
 "options": [{"text": "![[Attachments/learn/sound-basics/opt-tall.png|220]]", "correct": true},
             {"text": "![[Attachments/learn/sound-basics/opt-dense.png|220]]",
              "misconception": "Thinks more waves per second means louder"}],
 "why": "Loudness is amplitude, the height of the wave. More waves per second is pitch."}
```

## Re-teach visuals

When NEXT says re-teach, animate the step the learner got wrong, alone and slower: one
object, one change, one voice line. Not the same scene again.

## Fallback only: matplotlib (after 3 failed Manim attempts in a row)

The script gets `OUT_PNG` / `OUT_GIF` and must save exactly one.

```python
# TEMPLATE 3: annotated plot. Draw the real curve, then point at what matters.
import numpy as np
import matplotlib.pyplot as plt

t = np.linspace(0, 2, 800)
A, f = 1.0, 2                                   # --- edit: values from the research brief
y = A * np.sin(2 * np.pi * f * t)
fig, ax = plt.subplots(figsize=(7, 3.4))
ax.plot(t, y, color="#3b6fb6", lw=2)
ax.axhline(0, color="#9aa5b1", lw=1)
ax.set_xlabel("time (s)"); ax.set_ylabel("air pressure"); ax.set_ylim(-1.7, 2.3)
ax.annotate("", xy=(0.125, A), xytext=(0.125, 0), arrowprops=dict(arrowstyle="<->", color="#e08a2e", lw=2))
ax.text(0.02, 1.75, "① amplitude = height (loudness)", color="#e08a2e", fontsize=9, weight="bold")
ax.annotate("", xy=(1.125, 1.25), xytext=(1.625, 1.25), arrowprops=dict(arrowstyle="<->", color="#2e9d62", lw=2))
ax.text(1.375, 1.75, "② one period = 0.5 s", ha="center", color="#2e9d62", fontsize=9, weight="bold")
ax.text(1.0, -1.55, "③ frequency = 1 / period = 2 waves per second (pitch)", ha="center", fontsize=9, weight="bold")
fig.savefig(OUT_PNG, dpi=110, bbox_inches="tight")
```
