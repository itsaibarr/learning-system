# Paper teaching plan (2026-10-15)

Status: approved 2026-10-15 and built (see 'Build status' at the end). Depth D3 (harness category 5): recon, spec, plan, approval gate, build, review.
Source request: "Teach this paper to me" with an arXiv URL, concept-first, visual, with a standalone report.
Rule from the request: extend the existing `learn` engine. No second pipeline, no second knowledge graph.

## What the repo does today (read from source)

- `scripts/learn.py` (2447 lines) owns state and every teaching decision. Pipeline: `start`, `research`, `plan`, `figure`, `block`, `ask`, `check`, `end`.
- The research brief already models a concept map: a Concepts table with prerequisites and units, plus sources typed primary, textbook, review, secondary or vendor. `learn lit` already searches arXiv and fetches open-access text.
- `exam` mode already shows how to add a profile: a topic mode, extra required brief sections, and checks in `parse_brief`. Paper mode copies that pattern.
- Visuals: `cmd_figure` takes a script on stdin and renders Manim to a narrated MP4 or a still. `cmd_block` refuses a block without a Manim figure.
- Baseline: 90 tests pass, 1 skipped (`python3 -m pytest scripts`, 24 s).

## Where the bottleneck actually is

| Limit | Root cause | Evidence |
| --- | --- | --- |
| Non-technical topics get text in boxes | The Manim gate forces a scene for every segment, and for history the only fitting template is System or Process: labelled boxes and arrows. The 2026-10-08 Kazakh history session shows it: `dzungar-unity.mp4` is two text boxes and an arrow, `seasonal-cycle.mp4` is three text boxes. No map, no document, no dated timeline, no image of the thing. | frames from the two videos in `Attachments/learn/kazakh-history-.../` |
| Every concept becomes a Manim scene | Engine policy, not Manim. `cmd_figure` rejects non-Manim until 3 Manim failures, then allows only matplotlib. `cmd_block` requires a Manim embed. | `learn.py:1772-1778`, `learn.py:1906-1913` |
| No way to pick a representation by concept type | `visuals.md` has five templates, all Manim. No routing table, no comparison template, no simulation template. | `references/visuals.md` |
| Moving systems look hard | They are not. A car, a road, an obstacle and a perceive, plan, act strip rendered in Manim in 2.4 s on the first attempt. | spike in `/tmp/spikeA/car.py` |
| Nothing the learner can change | Outputs are MP4, PNG and GIF. "Change an input and watch the result" needs a live page. | `FIG_DIR` kinds in `save_figure` |
| Visuals do not say what they are based on | No label separating "from the paper", "illustrative model" and "hypothetical example". | none in code |
| No paper entry point | Nothing turns a URL into a paper id, picks HTML or PDF, or records whether full text was read. | `cmd_start` takes a topic string only |
| No standalone report | One session note per session. The vault has five folders by decision. | `AGENTS.md`, decision-log 2026-09-08 |

Manim stays the renderer for math, geometry, derivations, algorithms and technical architectures. It is the right tool there. The gap is topic fit: a history or social-science paper needs timelines, maps, source documents and argument maps, which a box-and-arrow scene cannot carry. Interactivity (HTML sims) is a smaller, optional gap for technical papers.

## Verified facts that shape the design

- Obsidian runs a note-embedded `<iframe>` pointing at a vault HTML file, JavaScript included. Its sandbox allows scripts. The URL is `app.vault.adapter.getResourcePath(path)`, read through the CLI the engine already calls (`cli_eval`). Spike files are deleted.
- arXiv serves `/html/<id>`, `/abs/<id>` and `/pdf/<id>` (all 200 for 1706.03762). `pymupdf`, `pdfminer` and `markitdown` can read PDFs. `pdftotext` is not installed, so it is not used.
- Playwright and Chromium are installed, so a sim can be checked headless.

## Design: the smallest change that works

1. `learn paper <url>` is a new command that calls the existing start path. It parses arXiv abs, pdf and html links, DOIs and direct PDF links. It fetches the best text in this order: arXiv HTML, open-access text through `learn lit`, PDF through pymupdf, abstract only. It records `fidelity` as `full`, `partial` or `abstract-only`, caches text outside the vault, and creates a topic with mode `paper`.
2. Paper brief profile, same mechanism as exam mode. Extra required sections: `Access` (fidelity and what was not read), `Claims` (each tagged `author-claim`, `evidence` or `interpretation`, with a source id), `Authors` (affiliation and role only with a source; otherwise "collective"), `Novelty` (existed before, changed, shown). Abstract-only fidelity blocks `learn plan` unless the learner passes `--accept-abstract-only`.
3. Teaching reuses units, `learn block`, `learn ask` and `learn check` unchanged. A paper is taught and checked like any topic, so a report never replaces learning.
4. Pick the visual from the kind of knowledge, not from the renderer. Paper mode (and any topic the brief marks as humanities or social science) gets a router table in `visuals.md`:
   - Dated events: a timeline drawn on a real time axis, with gaps to scale. Not equal boxes.
   - Places and movement: a real historical map from a public-domain source as the base, with sourced overlays (routes, regions, labels). No invented borders.
   - What someone said or wrote: the primary source on screen, with the key phrases highlighted and who, when and to whom stated.
   - Who argued what: an argument map (claim, evidence, counterclaim, who holds it). This is also how the brief's typed claims get shown.
   - Cause and effect: a causal chain where each link says whether the paper argues it, the evidence shows it, or it is interpretation.
   - Math, algorithms, technical architecture: Manim as today.
   - Results data: matplotlib chart.
   Everything except math, algorithms, architecture and charts is drawn by us as HTML, SVG and CSS. No image libraries, no stock photos, no AI-generated images.
5. Second renderer: HyperFrames (HeyGen, Apache-2.0), already installed as a skill. A composition is one HTML file; headless Chromium captures frames and ffmpeg makes the MP4. `learn figure <name> --hf` takes the composition on stdin, runs `hyperframes check`, renders, then applies the same narration step as Manim (speak lines first, measure, write each line's length into the composition). Output is an MP4 saved and embedded like any Manim figure. Needs Node 22 or newer (Node 24 present), ffmpeg (present), and Chromium (cached in `~/.cache/hyperframes`). Maps are drawn from public-domain Natural Earth coastline data as vector shapes. Historical borders are schematic and labelled "schematic". Nothing is invented as exact.
6. Basis labels. `learn figure --basis` is required in paper mode: `sourced` (a document, map or data the paper cites), `argued` (the author's claim drawn as a picture), `illustrative` (a diagram that helps, not evidence), `hypothetical`. The label is inserted under each embed. The engine rejects a scene that is only text in boxes when the topic is not technical, because that is the failure the Kazakh frames show.
7. The block gate in paper and humanities topics accepts any engine-checked visual: Manim, a HyperFrames video, a chart, or an HTML sim. Technical topics keep the current Manim gate exactly.
8. HTML sims stay, but optional and last. Use them only for a technical paper where changing an input is the lesson. Checks: no external URLs, size limit, loads headless with no errors, canvas not blank, moving a control changes the canvas.
9. `learn report` prints a 10-part template (parts 1 to 10 of the request) and validates the filled report. Rules: all ten parts present, facts cite brief ids, every embed file exists, every non-text visual has a basis label, the `Access` line matches recorded fidelity, the Authors part names only people from the brief. It saves to the vault.
10. Entry: `/learn <url>` runs `learn paper`. `AGENTS.md` and `teach-understanding` get one paper route. "Teach this paper to me" with a URL in this repo reaches the same command.

New dependencies: HyperFrames, run through `npx` and pinned in the repo. Playwright, pymupdf, Chromium, Node and ffmpeg are already on the machine. Maintenance cost: one new renderer (about 150 lines) and its tests, plus a pin bump when HyperFrames releases.

## Tasks (build order, each with its proof)

1. Paper ingestion. `learn paper`, URL parser, fetch chain, fidelity. Proof: tests for arXiv abs, pdf and html with version suffix, DOI, direct PDF, unsupported host, each fetch fallback with a mocked network.
2. Paper brief profile and the abstract-only gate. Proof: tests reject a brief with a missing section, an untyped claim, or an Authors row without a source.
3. Basis labels, the topic-fit gate and the text-in-boxes check. Proof: a technical non-paper topic still needs Manim (regression test); a paper topic accepts other checked visuals; a missing basis is rejected; the two Kazakh scenes are rejected for a history topic.
4. SPIKE DONE 2026-10-15, go. Source: `tasks/spike-hyperframes/dzungar-timeline.html` (GSAP vendored beside it, audio from `learn.tts_lines`). Measured: HyperFrames 0.8.161 `check` passes, render 17.4 s for 31 s of 1080p (54 s wall with `npx`), 2.0 MB, h264+aac. Voice starts 0.3 s after each scheduled start (lead silence in the clip) and phrase beats from word counts land within about 0.5 s of the comma pauses. Loads and plays in Obsidian reading view. Not yet judged: how it looks to you, and whether a free model writes this HTML. Next: `learn figure --hf`.
   Original task text: Spike first, then `learn figure --hf`. Spike: one history scene (a 1763 to 1776 timeline, 3 narration lines) as a HyperFrames composition, rendered on this Mac with a Voicebox line length written in. Go or stop on three numbers: render time, whether the voice stays in sync, whether it looks better than the Kazakh box frames. Then the engine path with `hyperframes check` and the narration step.
5. `visuals.md` router table and templates: Timeline, Map, Source close reading, Argument map and Causal chain as HyperFrames compositions, Compare as Manim. Proof: a test renders each template, and the existing template-renders test still passes.
5b. Optional, last: HTML sim renderer and checks (good sim passes, external URL fails, ignored control fails).
6. `learn report`. Proof: tests for every validation rule above.
7. Entry points, `references/papers.md` (concept-first rules, what to skip, source hierarchy), decision-log rows, README line.
8. Evaluation (below).

Order matters: 1, 2 and 3 first (end-to-end skeleton), then 4 to 6, then 7 and 8. Tasks 4 and 6 are the largest.

## Evaluation

- Existing suite: 90 pass, 1 skipped, before and after.
- Visual eval, five concepts rendered through the engine, scored on first-try success, render time, file size and whether you can say what the picture claims:
  1. Math in Manim: scaled dot-product attention as vectors and a softmax.
  2. Technical architecture: the transformer encoder-decoder, Manim System template.
  3. History, events and causes: the road to the American Declaration of Independence, 1763 to 1776, on a dated timeline with a causal chain.
  4. History, a primary source: the grievance list in the Declaration of Independence, close reading.
  5. History, a place: the thirteen colonies as a schematic map drawn from Natural Earth coastline.
  The same history concepts are also rendered with the old System template as the baseline, so the comparison is visible.
- End-to-end, two papers through `/learn <url>` in OpenCode, each ending with a report in the vault: "Attention Is All You Need" (arXiv 1706.03762) for the technical path, and one open-access paper on the American Revolution for the history path. Checks: Access line matches what was read, claims are typed, authors section matches the paper, report has all ten parts, every image has a credit and a basis label.
- Learning-quality read of the report against section 11.3 of the request (missing prerequisites, unexplained terms, visuals that do not help, unsupported claims, needless derivations).

## Failure points and guards

| Failure | Guard |
| --- | --- |
| Unsupported or paywalled source | Named error with the reason; no silent fallback |
| No full text | `abstract-only` fidelity blocks planning unless the learner accepts it, and the report carries the limit |
| Dead reference | Brief rule already says disclose in Open questions; the paper profile adds it to `Access` |
| Visual fails to render | Manim retry path unchanged; sim checks print the exact failure; after 3 failures the existing fallback applies |
| Incomplete report | `learn report` rejects until all ten parts pass |
| Misattributed claim or author role | Typed claims, a source on every author row, "collective" as the default |

## Out of scope

- Author deep-dives beyond affiliation, group, topic and prior work tied to the paper.
- Paywalled publisher scraping, supplementary datasets, running author code.
- A second knowledge graph, a new frontend, a bundled JS library, PDF output.
- Changing the Manim-only rule for non-paper topics.

## Assumptions I will build on unless you veto them

1. The report lives in a new vault folder `Papers/` (a decision-log row supersedes the five-folder rule for reports only).
2. Paper mode relaxes the Manim-only gate. All other topics keep it.
3. No image libraries and no AI-generated images (your call on 2026-10-15; the 2026-10-03 rule stands). History visuals are drawn as HTML and SVG and rendered by HyperFrames.
4. Technical end-to-end paper is arXiv 1706.03762. For the history path I pick an open-access paper on the American Revolution and tell you which before running it.
4b. HTML sims are optional, single-file vanilla JS, built last.
5. Your global `~/.claude/CLAUDE.md` stays untouched. The routing lives in this repo and OpenCode.

## Build setup

Work in a git worktree of `learning-system` on branch `itsaibarr/paper-teaching`, based on `origin/master`. The main checkout has an uncommitted `state/learner.json` and two unpushed session commits, and the build leaves them alone. Merge by PR, as with PRs #1 to #5.

## Build status (2026-10-15, uncommitted in the worktree)

Built and tested (123 pass, 1 skipped as before): `learn figure` for HyperFrames scenes (HTML) with Manim limited to formula-driven maths;
`learn paper <url>` (arXiv HTML/PDF, DOI, direct PDF, open article page) with recorded fidelity and the abstract-only gate; the paper brief
profile (Access, typed Claims, Authors, Novelty); `--basis` labels under every figure; `learn report` (10 parts, validated, saved to vault
`Papers/`); `/learn <url>` entry in the OpenCode command, AGENTS.md and the skill; `references/papers.md`, `hyperframes.md` and the worked example.

Evidence: end-to-end on arXiv 1706.03762 with an isolated state and vault: brief accepted first time, 6 scenes (5 HyperFrames, 1 Manim),
2 unit blocks, 6 questions answered, report accepted first time; all six videos load in Obsidian. Live fetch also checked on a direct PDF, a
paywalled Nature DOI (stops at abstract-only) and an open article page (partial). Defects found by running it: no CA certificates for urllib
(fixed with certifi), duplicate ids in a scene (caught by the engine), label overlaps in three scenes (found only by looking at frames).

Not done: the history paper end to end (only ingestion tested on a web article); muse 1.3 driving the whole loop (it passed the HyperFrames
check once, picture was plainer); a check for "at most 4 text items" and "one caption per beat"; the four-concept comparison table;
nothing committed or pushed.
