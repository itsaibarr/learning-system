# Rules for writing index.html (HyperFrames composition, one narrated teaching scene)

You write ONE file, `index.html`, in this folder. It renders to a 1920x1080 video with the narration audio.
Start from `example.html` (a finished, passing scene about a different topic). Keep its structure:
`<head>` styles, the `<svg>` symbols idea, `#root` with `data-composition-id="main"`, one `#stage` clip, the
`<audio>` tags as direct children of `#root`, and the single paused GSAP timeline registered on `window.__timelines["main"]`.
Keep the `item()` helper and the BEATS loop exactly as in example.html. Rewrite the content: items, captions, BEATS, motion.

## HyperFrames contract (breaking these fails the check or renders wrong)
- Timeline: exactly one `gsap.timeline({paused:true})`, built synchronously at load, stored in `window.__timelines["main"]`.
- Animate only: opacity, x, y, scale, rotation, color, backgroundColor, borderRadius. Never animate `display` or `visibility`.
- No `Math.random()`, `Date.now()`, network fetches, `repeat:-1`, `<br>`, setTimeout, requestAnimationFrame.
- Set initial hidden states with `gsap.set(...)` (the `item()` helper does), not `tl.set(...)` at time 0.
- Root `data-duration` = total seconds (see BRIEF.md). `<audio>` tags: `src`, `data-start`, `data-duration`, `data-track-index`, `data-volume="1"`.
- Text must fit inside the 1920x1080 frame and not overlap other text at the same moment. Minimum text size 24px.
- Load GSAP with `<script src="gsap.min.js"></script>` (the file is in this folder). Use no other library, no images, no fonts to download.

## Teaching rules (the learner said the first version was overwhelming and "just writing 'held' does not explain what happened")
1. One beat per narration phrase. At each beat exactly ONE thing is the focus (full brightness, it moves or pops). Everything else dims to 30% or disappears. The viewer must always know where to look.
2. One caption per beat: a plain sentence of at most 12 words stating what happened or why it matters ("The auls are far apart. Nobody can help."). The caption says the meaning. Never write single vague words like "held", "ok", "result".
3. Show cause and effect with the drawing itself (things move, stop, merge, change color), not with labels.
4. At most 4 text items visible at any moment, including the caption and the title. Labels belong to the beat that explains them and disappear after.
5. Draw the real thing (places, routes, animals, tents, water, hay), not boxes with words. Use simple CSS shapes or inline SVG you write yourself.
6. Use only facts in BRIEF.md. Do not add dates, numbers, names or compass directions that are not there. Anything drawn only to help understanding (layout, distances, positions) is illustrative: keep the footer line saying so.
7. Scene titles are short ("Part 1: ..."), never repeating the caption.
8. Colors: background dark (#12161b), text #eef1f4, accents #5ec8f0 #ffd166 #6ee7a0 #ff6b5e #b69cff, muted grey #8892a0.

## Done means
`npx --yes hyperframes@0.8.161 check` prints "Check passed" with 0 errors. Do not render. Do not edit other files.
