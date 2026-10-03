# Visuals: a picture of how it works, for every idea

The learner understands pictures far better than text. Every theory block needs at
least one visual (the engine refuses blocks without one). The visual shows HOW the
thing works: parts, what moves between them, and the order of steps. Decoration,
stock photos and AI-generated images don't count: they are not drawn for the
explanation and their labels don't match the text.

All tools here are free and local: matplotlib (pictures, plots, animations) and
mermaid (structure), both rendered natively by Obsidian.

## Pick the visual

| The idea is about | Make | How |
| --- | --- | --- |
| Physical things: particles, waves, objects, forces, motion | the things themselves, animated | Template 4, `learn figure` |
| How a system works: parts and what flows between them | labelled diagram | Template 1, `learn figure` |
| A process that changes over time, or steps of an algorithm | step animation (GIF) | Template 2, `learn figure` |
| Numbers, a formula, a curve, a distribution, geometry | annotated plot | Template 3, `learn figure` |
| Pure structure: a hierarchy, a decision, a sequence of messages | mermaid | ```mermaid``` block in the text |

Mermaid types that render in this Obsidian: `flowchart`, `sequenceDiagram`,
`stateDiagram-v2`, `mindmap`, `timeline`, `xychart-beta`, `quadrantChart`. The engine
parses every mermaid block with Obsidian's own mermaid and rejects broken ones.

## How to make a figure

1. Copy the closest template below. Change only the part under `--- edit`.
2. Pipe it to the engine: `learn figure <short-name> <<'EOF' ... EOF`.
3. If it is rejected, read the reason (crash, labels colliding, no file, too big), fix
   that one thing, re-run with the same name.
4. Paste the printed `EMBED:` line into the theory block, near the top.

The script gets `OUT_PNG` and `OUT_GIF` paths. Save exactly one: a picture with
`fig.savefig(OUT_PNG, dpi=110, bbox_inches="tight")`, an animation with
`anim.save(OUT_GIF, writer=PillowWriter(fps=...), dpi=80)`.

## Rules for a picture that teaches

- **Draw the thing, not a box with its name.** If the idea is physical (air molecules,
  a wave, a robot arm, a ball, a force), draw those objects and how they move. Boxes
  and arrows are for systems made of parts (a microphone pipeline, a training loop).
  A box labelled "air: molecules wobble" explains less than 200 dots that wobble.
- **Show the misconception being wrong.** If the brief lists a misconception, make the
  picture show why it is wrong (Template 4 follows one molecule to show the air stays).
- **Numbered marks.** Put ① ② ③ on the parts or steps, and use the same marks in the
  text: "① sound pushes the air...". This is how the text walks through the picture.
- **Few labels, big enough.** At most about 6 labels, font size 9 or more, plain words.
- **One idea per picture.** If it needs more than 3-4 parts, split it into two figures
  or an animation.
- **Real numbers come from the research brief.** If a number is made up to show the
  shape of the idea, label the figure "illustrative".
- **Colour means something.** Same colour for the same kind of thing in every figure of
  the session (blue = main object, orange = what changes, green = result, grey = context).
- **Animations:** 3-8 frames, a title on every frame saying what changed, 0.5-1 frame
  per second so the learner can read it. Call `fig.tight_layout()` in each frame.

## Template 1: mechanism diagram (PNG)

```python
# TEMPLATE 1: mechanism diagram. Parts as boxes, arrows for what flows, numbered steps.
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

fig, ax = plt.subplots(figsize=(10, 3.6))
ax.set_xlim(0, 10); ax.set_ylim(0, 3.6); ax.axis("off")
C = {"main": "#3b6fb6", "accent": "#e08a2e", "good": "#2e9d62", "muted": "#9aa5b1"}

def part(x, y, w, h, label, color):            # one component of the mechanism
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.04", fc="white", ec=color, lw=2))
    ax.text(x + w / 2, y + h / 2, label, ha="center", va="center", fontsize=10)

def flow(x1, y1, x2, y2, color):               # what moves from one part to the next
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=16, color=color, lw=2))

def step(x, y, n, text, color):                # numbered mark the text refers to
    ax.text(x, y, f"{n} {text}", ha="center", fontsize=10, weight="bold", color=color)

# --- edit below: the mechanism ---
part(0.3, 1.2, 2.0, 1.0, "voice:\nair pressure waves", C["main"])
part(4.0, 1.2, 2.0, 1.0, "microphone:\ndiaphragm moves", C["accent"])
part(7.7, 1.2, 2.0, 1.0, "electrical signal:\nvoltage over time", C["good"])
flow(2.35, 1.7, 3.95, 1.7, C["muted"])
flow(6.05, 1.7, 7.65, 1.7, C["muted"])
step(1.3, 2.6, "①", "sound pushes air", C["main"])
step(5.0, 2.6, "②", "air pushes the diaphragm", C["accent"])
step(8.7, 2.6, "③", "motion becomes voltage", C["good"])
ax.text(5.0, 0.5, "illustrative: one sound wave at a time", ha="center", fontsize=8, color=C["muted"])
fig.savefig(OUT_PNG, dpi=110, bbox_inches="tight")
```

## Template 2: step animation (GIF)

```python
# TEMPLATE 2: step animation. One frame per state; a caption says what changed.
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter

# --- edit below: the states of the process, one per frame (frequency in Hz, caption) ---
states = [(1, "① 1 wave per second: low pitch"), (2, "② 2 waves per second: higher pitch"),
          (4, "③ 4 waves per second: higher again"), (4, "③ same height = same loudness")]
t = np.linspace(0, 1, 400)

fig, ax = plt.subplots(figsize=(6, 3))
def frame(k):
    f, caption = states[k]
    ax.clear()
    ax.plot(t, np.sin(2 * np.pi * f * t), color="#3b6fb6", lw=2)
    ax.set_ylim(-1.5, 1.5); ax.set_xlabel("time (s)"); ax.set_ylabel("air pressure")
    ax.set_title(caption, fontsize=11, weight="bold")
    fig.tight_layout()
anim = FuncAnimation(fig, frame, frames=len(states))
anim.save(OUT_GIF, writer=PillowWriter(fps=0.7), dpi=80)
```

## Template 3: annotated plot (PNG)

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

## Template 4: the physical thing, animated (GIF)

Every moving object is computed from its rest position plus a formula, so the motion is
physically right. Check any marker you place (like "the squeeze is here") against the
formula, not by eye.

```python
# TEMPLATE 4: the physical thing itself, animated (particles, waves, objects, forces).
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter

# --- edit below: the objects and how each one moves over time ---
rng = np.random.default_rng(1)
x0 = np.repeat(np.linspace(0.3, 9.7, 40), 6)            # rest positions of air molecules
y = np.tile(np.linspace(0.4, 2.6, 6), 40) + rng.uniform(-0.08, 0.08, 240)
k, w, A = 2 * np.pi / 3.0, 2 * np.pi / 8, 0.35            # wavelength 3, 8 frames per cycle, wobble size
watch = 6 * 20                                           # one molecule to follow
frames = 16

fig, ax = plt.subplots(figsize=(7, 3.2))
def frame(n):
    ax.clear(); ax.set_xlim(0, 10); ax.set_ylim(-0.2, 3.6); ax.axis("off")
    x = x0 + A * np.sin(k * x0 - w * n)                  # each molecule wobbles around its rest spot
    ax.scatter(x, y, s=10, color="#3b6fb6")
    ax.scatter(x[watch], y[watch], s=60, color="#c0392b", zorder=3)
    ax.axvline(x0[watch], color="#c0392b", lw=0.8, ls="--")
    crest = (np.pi + w * n) / k % 3.0                     # densest air: where k*x - w*t = pi (compression)
    for c in np.arange(crest, 10, 3.0):
        ax.annotate("", xy=(c + 0.35, 3.05), xytext=(c - 0.35, 3.05), arrowprops=dict(arrowstyle="-|>", color="#e08a2e", lw=2))
    ax.text(0.2, 3.35, "① orange: the squeeze moves right", fontsize=9, color="#e08a2e", weight="bold")
    ax.text(5.6, 3.35, "② red molecule only wobbles", fontsize=9, color="#c0392b", weight="bold")
    fig.tight_layout()
anim = FuncAnimation(fig, frame, frames=frames)
anim.save(OUT_GIF, writer=PillowWriter(fps=3), dpi=80)
```

## Questions about a picture

A question can show a figure above its options. Make a NEW figure for the question
(not the one from the theory), so the learner has to read it:

```json
{"type": "choice", "level": 2,
 "figure": "![[Attachments/learn/sound-basics/q-wave.png]]",
 "question": "In the picture, which wave has the higher pitch?",
 "options": [{"text": "B, it has more waves per second", "correct": true},
             {"text": "A, it is taller", "misconception": "Confuses height (loudness) with pitch"}],
 "why": "Pitch is frequency: more waves per second. Height is amplitude, which is loudness."}
```

Pictures can also BE the options (they render inside the checkboxes). Make one small
figure per option (`figsize=(3, 2)`), same axes and scale, and put each embed with a
width as the option text:

```json
{"type": "choice", "level": 2,
 "question": "Which picture shows the louder sound?",
 "options": [{"text": "![[Attachments/learn/sound-basics/opt-tall.png|220]]", "correct": true},
             {"text": "![[Attachments/learn/sound-basics/opt-dense.png|220]]",
              "misconception": "Thinks more waves per second means louder"}],
 "why": "Loudness is amplitude, the height of the wave. More waves per second is pitch."}
```

## Re-teach visuals

When NEXT says re-teach, draw the step the learner got wrong, bigger and alone: one
part, one arrow, one mark. Not the same picture again.
