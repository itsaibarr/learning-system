# Teaching a paper ("Teach this paper to me")

Entry: the learner gives a link (arXiv, DOI, direct PDF, open-access article page) or attaches a file (PDF, HTML, text; the
chat shows its path) and says "teach me this paper". Run `learn paper <url-or-file-path>`. For an attached PDF the engine reads
the arXiv id or DOI printed on the first page and fetches the real title, authors and date. If the file carries no id, cite it in
the brief as the `file://` path `learn paper` prints, and pass `--title` if the title it guessed is wrong. It fetches the paper, tells you how much was really read (`FIDELITY: full|partial|abstract-only`),
caches the text, and opens a paper topic. Then the normal loop runs: research brief, plan, units, checks. When every
idea is solid, `learn report` produces the visual report. This is teaching, not summarising: the learner is
asked questions on every unit, and the report is the reference they keep.

## The goal

Remove the friction between finding an interesting paper and understanding its ideas. The learner understands
visual explanations far better than text, finds long linear reading hard to start, and cares about ideas,
mechanisms, trade-offs and practical use more than derivations. Papers can be from any field: machine learning,
history, social science. Pick the picture by the kind of idea (`references/visuals.md`, `references/hyperframes.md`).

## Before anything else

- `FIDELITY: abstract-only` or no text: stop and tell the learner in one line what is missing. Continue only if they
  accept it (`learn paper <url> --accept-abstract-only`), and then say in the report what could not be checked.
  Never present an abstract summary as a study of the paper.
- `partial`: say what was not read in the brief's `Access` section.
- A link the engine refuses (not a paper, paywalled page): ask for another copy. Do not guess a paper from a title.

## Research (what goes into the brief)

1. Read the cached text in chunks (the path is printed). The paper is source S1, type `primary`.
2. Fill the paper sections the template adds:
   - **Access**: fidelity (must match what the engine recorded) and what you did not read.
   - **Claims**: what the paper claims, each typed `author-claim` (they say it), `evidence` (an experiment or source
     shows it) or `interpretation` (your reading). Do not assume a claim is right because the paper states it.
   - **Authors**: affiliation at paper time, and an individual role only when a source states it. Otherwise the role
     is `collective`. Never invent roles or backgrounds.
   - **Novelty**: `Existed`, `Changed`, `Shown`.
3. Resolve gaps with the shortest path to a correct mental model: a term or method the paper assumes and the learner
   may lack gets one good source (`learn lit resolve|search|text`, the cited foundational paper, official docs,
   an author project page). Do not turn every unfamiliar word into a literature review.
4. Source order: the paper and its supplement, then author pages and implementations, then foundational papers it
   cites, then official documentation, then reliable independent explanations. Keep every important claim traceable
   to a source id, and keep three things apart: what the paper says, what an external source says, what you explain.
5. Author research: only public, verifiable facts tied to the topic (affiliation, group, relevant earlier work).
   No personal details.

## Teaching it (concept first)

- The concept map is the brief's Concepts table. It already holds prerequisites and units. Put what the learner must
  know first at the root, the central contribution in the middle, supplementary detail last or out.
- Teach: the problem and why it matters, what existing approaches fail at, the central insight, how the method works
  (each component: what it does, why it exists, what goes in and out, how it connects), what makes it different,
  what the experiments show and do not show, when it is useful, what remains open.
- Explain what a loss function or key equation does and why. Do not reproduce derivations, algebra or proofs
  unless the equation is the contribution. Skip implementation detail that does not change understanding.
- If the paper rests on a technique it does not explain, teach that technique before the contribution.
- Label every picture with `--basis`: `sourced` (from the paper or its sources), `argued` (the authors' claim drawn),
  `illustrative` (a helper diagram, not evidence), `hypothetical` (an invented example). An illustrative model is
  never presented as the authors' implementation. Do not draw a causal link the source does not support.

## The report (`learn report`)

Ten parts: at a glance, problem and motivation, central idea, how it works, what is actually new, experiments and
results, authors, practical applications, limitations and open questions, the mental model to retain. The engine
checks: all ten in order, real content in each, brief citations where facts are stated, an `Access:` line that matches
the fidelity, a basis on every figure, at least 3 visuals (a visual in parts 4 and 10), authors only from the brief's
table, and part 9 keeping "Authors acknowledge" apart from "Our analysis". The report goes to the vault folder
`Papers/` and must make sense without the chat.

Separate results from conclusions: say which conclusions the evidence does not justify, and keep the evaluation
conditions. A narrow result is not a general one.
