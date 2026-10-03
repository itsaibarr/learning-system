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
| Steps of a process or an algorithm | Process | `learn figure <name>` |
| A system of parts and what flows between them | System | `learn figure <name> --still` |

`--still` renders the last frame as a PNG (for static diagrams and picture answers).
Without it you get an MP4 that plays inside the note.

## How to make one

1. Copy the closest template below. Change only the part under `--- edit`.
2. `learn figure <short-name> <<'EOF'` ... `EOF` (add `--still` for a picture).
3. If it is rejected, read the reason, fix that one thing, re-run with the same name.
   The engine checks, in this order: old-Manim code, the render itself (Python and
   LaTeX errors, with LaTeX's own message), text that overlaps other text or is cut off
   at the frame edge (checked after EVERY play/wait), length 2-90 s, size.
4. Paste the printed `EMBED:` line into the theory block, right after "Why we need this".

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
- **One idea, 5-20 seconds.** End with `self.wait(1)` so the last frame can be read.
- **Numbered captions.** One caption at the top, changed with
  `Transform(caption, Text("2  ...").to_edge(UP))`; the block text uses the same numbers.
- **Layout with relations, never raw coordinates for text:** `.to_edge(UP)`,
  `.next_to(obj, DOWN, buff=0.3)`, `VGroup(...).arrange(RIGHT, buff=0.6)`.
  `FadeOut` old text before new text takes its place.
- **Colour means something:** BLUE = the main object, YELLOW = what to look at,
  GREEN = the result, RED = the wrong idea or the thing to follow.
- **Words in `Text`, maths in `MathTex`.** Use raw strings: `MathTex(r"\frac{1}{f}")`.
  Units with `\,\mathrm{m/s}`. Font size 24 or more.
- **Numbers come from the research brief.** If a number only shows the shape of the
  idea, say "illustrative" in a caption.
- **Motion from a formula** (`ValueTracker` + updaters), so it is physically right. Check
  any marker you place ("the squeeze is here") against the formula, not by eye.

## Template: Physical

```python
# TEMPLATE: the physical thing itself, moving (particles, waves, objects). Motion comes from a formula.
from manim import *

class Physical(Scene):
    def construct(self):
        # --- edit below: rest positions and the motion rule ---
        xs, ys = np.linspace(-6, 6, 36), np.linspace(-1.6, 1.0, 6)
        rest = [(x, y) for x in xs for y in ys]
        k, A = 2 * PI / 4, 0.35                    # wavelength 4 units, wobble size
        t = ValueTracker(0)
        def pos(x, y):
            return [x + A * np.sin(k * x - t.get_value()), y, 0]
        dots = VGroup(*[Dot(pos(x, y), radius=0.05, color=BLUE) for x, y in rest])
        watch = 6 * 17                              # one molecule to follow
        dots[watch].set_color(RED).scale(1.8)
        dots.add_updater(lambda g: [d.move_to(pos(x, y)) for d, (x, y) in zip(g, rest)])
        # compressions sit where k*x - t = pi (mod 2*pi): mark them with arrows that move with the wave
        def squeezes():
            c0 = ((PI + t.get_value()) / k) % 4 - 6
            return VGroup(*[Arrow([c - 0.4, 1.55, 0], [c + 0.4, 1.55, 0], buff=0, color=YELLOW)
                            for c in np.arange(c0, 6, 4)])
        arrows = always_redraw(squeezes)
        rest_line = DashedLine([xs[17], -2.0, 0], [xs[17], 1.2, 0], color=RED)
        note1 = Text("1  the squeeze travels", font_size=26, color=YELLOW).to_corner(UL)
        note2 = Text("2  the red molecule only wobbles", font_size=26, color=RED).to_edge(DOWN)
        self.add(dots, rest_line, arrows, note1, note2)
        self.play(t.animate.set_value(4 * PI), run_time=6, rate_func=linear)
```

## Template: Derivation

```python
# TEMPLATE: a formula built step by step (LaTeX). Matching pieces glide into place.
from manim import *

class Derivation(Scene):
    def construct(self):
        # --- edit below: the steps; one argument per piece, so equal pieces glide into place ---
        steps = [
            MathTex(r"v", r"=", r"f", r"\lambda"),
            MathTex(r"\lambda", r"=", r"\frac{v}{f}"),
            MathTex(r"\lambda", r"=", r"\frac{343\,\mathrm{m/s}}{343\,\mathrm{Hz}}"),
            MathTex(r"\lambda", r"=", r"1\,\mathrm{m}"),
        ]
        why = ["1  speed = waves per second x length of one wave",
               "2  divide both sides by f",
               "3  put in the numbers",
               "4  one wave is one metre long"]
        for s in steps:
            s.scale(1.4)
        caption = Text(why[0], font_size=28).to_edge(UP)
        self.play(Write(steps[0]), FadeIn(caption))
        self.wait(1)
        for i in range(1, len(steps)):
            self.play(TransformMatchingTex(steps[i - 1], steps[i]),
                      Transform(caption, Text(why[i], font_size=28).to_edge(UP)))
            self.wait(1)
        self.play(Circumscribe(steps[-1], color=YELLOW))
        self.wait(1)
```

## Template: Graph

```python
# TEMPLATE: a curve with what matters marked (LaTeX labels). Draw it, then point at the features.
from manim import *

class Graph(Scene):
    def construct(self):
        # --- edit below: the function and its features (values from the research brief) ---
        A, f = 1.0, 2
        axes = Axes(x_range=[0, 1, 0.25], y_range=[-1.5, 1.5, 0.5], x_length=9, y_length=4.2,
                    y_axis_config={"include_numbers": True, "font_size": 24}).shift(0.4 * DOWN)
        labels = axes.get_axis_labels(Tex("time (s)", font_size=28), Tex("pressure", font_size=28))
        wave = axes.plot(lambda t: A * np.sin(2 * PI * f * t), color=BLUE)
        title = MathTex(r"p(t) = A \sin(2\pi f t)", font_size=40).to_edge(UP)
        self.play(Write(title), Create(axes), Write(labels))
        self.play(Create(wave), run_time=2)
        amp = DoubleArrow(axes.c2p(0.125, 0), axes.c2p(0.125, A), buff=0, color=YELLOW)
        amp_t = MathTex(r"A", color=YELLOW).next_to(amp, LEFT, buff=0.15)
        per = DoubleArrow(axes.c2p(0.125, 1.25), axes.c2p(0.625, 1.25), buff=0, color=GREEN)  # peak to peak
        per_t = MathTex(r"T = \tfrac{1}{f} = 0.5\,\mathrm{s}", color=GREEN, font_size=34).next_to(per, UP, buff=0.1)
        self.play(GrowFromCenter(amp), Write(amp_t))
        self.play(GrowFromCenter(per), Write(per_t))
        self.wait(1.5)
```

## Template: Process

```python
# TEMPLATE: a process step by step. Something travels through stages; each stage lights up while the caption explains it.
from manim import *

class Process(Scene):
    def construct(self):
        # --- edit below: the stages and what happens at each ---
        stages = ["sound", "microphone", "converter", "numbers"]
        says = ["1  sound reaches the microphone",
                "2  the diaphragm turns it into a voltage",
                "3  the converter measures the voltage 16,000 times a second",
                "4  the computer now holds a list of numbers"]
        boxes = VGroup(*[VGroup(RoundedRectangle(corner_radius=0.15, width=2.6, height=1.1, color=GREY),
                                Text(n, font_size=26)) for n in stages]).arrange(RIGHT, buff=0.7)
        links = VGroup(*[Arrow(a.get_right(), b.get_left(), buff=0.08, color=GREY)
                         for a, b in zip(boxes[:-1], boxes[1:])])
        token = Dot(boxes[0].get_center() + 0.9 * DOWN, color=YELLOW, radius=0.14)
        caption = Text(says[0], font_size=28).to_edge(UP)
        self.play(FadeIn(boxes), FadeIn(links), Write(caption), FadeIn(token))
        for i, box in enumerate(boxes):
            if i:
                self.play(token.animate.move_to(box.get_center() + 0.9 * DOWN),
                          Transform(caption, Text(says[i], font_size=28).to_edge(UP)))
            self.play(box[0].animate.set_color(YELLOW), run_time=0.5)
            self.play(Indicate(box[1], color=YELLOW))
            self.play(box[0].animate.set_color(GREEN), run_time=0.4)
        self.wait(1)
```

## Template: System (render with --still)

```python
# TEMPLATE: system of parts (use --still for a picture). Parts, what flows between them, numbered steps.
from manim import *

class SystemDiagram(Scene):
    def construct(self):
        # --- edit below: the parts, left to right ---
        names = ["voice:\nair pressure", "microphone:\ndiaphragm moves", "signal:\nvoltage over time"]
        steps = ["1  sound pushes air", "2  air pushes diaphragm", "3  motion becomes voltage"]
        colors = [BLUE, YELLOW, GREEN]
        parts = VGroup(*[
            VGroup(RoundedRectangle(corner_radius=0.2, width=3.4, height=1.6, color=c),
                   Text(n, font_size=26, line_spacing=0.8))
            for n, c in zip(names, colors)
        ]).arrange(RIGHT, buff=1.0)
        arrows = VGroup(*[Arrow(a.get_right(), b.get_left(), buff=0.1, color=GREY)
                          for a, b in zip(parts[:-1], parts[1:])])
        labels = VGroup(*[Text(s, font_size=24, color=c).next_to(p, UP, buff=0.35)
                          for s, c, p in zip(steps, colors, parts)])
        title = Text("How a microphone hears you", font_size=36).to_edge(UP)
        self.add(title, parts, arrows, labels)
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
object, one change, one caption. Not the same scene again.

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
