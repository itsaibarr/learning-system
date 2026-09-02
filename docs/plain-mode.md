# Plain mode — no Obsidian, no LaTeX

For machines without the Obsidian vault (e.g. the iMac). Everything the vault would
hold lives in the repo instead, and math is written so it renders in *any* markdown
viewer — GitHub, VS Code preview, Quick Look, plain `cat`.

## Where notes go

| Vault folder | Plain-mode location |
| --- | --- |
| `Maps/<subject>` | `subjects/<subject>/map.md` |
| `Concepts/<name>` | `subjects/<subject>/notes/<name>.md` |
| `Sources/<name>` | `subjects/<subject>/sources/<name>.md` |
| `Reviews/<date>` | `subjects/<subject>/reviews/<date>.md` |

Repo-native artifacts (brief, study cycle, mistake log, decision log) do not move —
they were already in `subjects/<subject>/`. Wiki-links `[[Concepts/x]]` become relative
markdown links `[x](notes/x.md)`, so they stay clickable without Obsidian.

## Math: Unicode, not LaTeX

`$...$` renders as literal dollar signs in most plain markdown viewers, so plain mode
bans it. Write math with Unicode characters inline, and put display math in a fenced
code block — which every viewer renders as monospace, aligned, and unmangled.

Inline: the energy E(x, y) is low when y is compatible with x; the encoder gives sₓ = Enc(x).

Display:

```
  L(x, y) = ‖ Pred(sₓ, z) − s_y ‖²        prediction loss, in embedding space
     sₓ = Enc(x),  s_y = Enc(y)           encoders map inputs to representations
      z                                    latent variable — the part of y that x cannot predict
```

Symbol crib (copy from here rather than reaching for LaTeX):

| Need | Use | Need | Use |
| --- | --- | --- | --- |
| minus | `−` (U+2212, not a hyphen) | norm | `‖x‖` |
| times / dot | `×` `·` | sum / product | `Σ` `Π` |
| approx / prop / equiv | `≈` `∝` `≡` | integral | `∫` |
| ≤ ≥ ≠ | `≤` `≥` `≠` | partial / nabla | `∂` `∇` |
| element / subset | `∈` `⊂` | expectation | `𝔼` |
| arrow / maps-to | `→` `↦` | infinity | `∞` |
| square root | `√` | degrees | `°` |
| Greek | `α β γ δ ε θ λ μ σ τ φ ψ ω Δ Λ Σ Φ Ω` | | |
| superscripts | `⁰¹²³⁴⁵⁶⁷⁸⁹ ⁿ ⁻` (e.g. `10⁻³`, `n²`) | | |
| subscripts | `₀₁₂₃₄₅₆₇₈₉ ₓ ₜ ₙ ᵢ ⱼ ₖ` (e.g. `sₓ`, `xₜ`) | | |

No Unicode subscript exists for most letters (there is no `_y` subscript). Write `s_y`
with a plain underscore in those cases and keep it consistent inside one document —
mixing `sₓ` and `s_y` in the same line is fine and still reads correctly.

## Diagrams

Mermaid blocks stay as they are: GitHub renders them natively, and in a plain viewer the
fenced source is still readable. Keep them ≤ ~7 nodes as the `visualize` skill requires.

## Anki

Unaffected — `anki/queue.md` keeps `$...$`, because `scripts/anki_push.py` converts it to
Anki's MathJax delimiters and Anki renders it properly. Plain mode is about files a human
reads directly.
