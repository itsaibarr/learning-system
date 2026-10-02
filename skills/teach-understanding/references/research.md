# Research step (PRAXIST method, adapted for teaching)

Runs once per topic, before anything is taught. `learn plan` and `learn block` refuse to
run until a validated brief exists. Facts in lessons come from the brief, not from your
memory. This matters most for academic or niche topics, where a model's memory is
weakest and errors are hardest to spot.

The method is PRAXIST's `praxist-scientific-research` skill (sapientinc/PRAXIST, Fair
Source License 1.0, used internally under the free tier). Load that skill too: its
source priority, note shape and evidence language apply here. Its literature tools are
available as `learn lit ...` commands (the PRAXIST no-key lookup: OpenAlex, arXiv,
Crossref, Semantic Scholar, PubMed, Europe PMC). PRAXIST's own run commands
(`praxist`, takeover, peers) are NOT used: we are not running an experiment.

## Evidence language (from PRAXIST, mapped to learning)

- **Literature signal**: what a source says. Goes into the brief with its source id.
- **Provenance**: URL or DOI/arXiv id plus retrieval date. Every source row has both.
- **Measured learner fact**: what the learner got right or wrong. Only `learn` records
  these, and only they drive mastery. A source never proves the learner knows something.

## Pipeline

1. **Goal first.** If the learner hasn't said what they want to be able to do and what
   they already know, ask that ONE question and wait. The research targets that goal.
2. **Local material first** (PRAXIST priority 1): anything the learner gave you (PDFs,
   syllabus, notes), and existing vault notes: `obsidian search query="<topic>"`.
3. **Pick the domain and source families:** `learn lit guide <domain>`. Domains:
   machine_learning, biology, chemistry, medicine, robotics_control, physics_materials,
   generic.
4. **Search** (priority 2), 2-4 queries from different angles:
   ```bash
   learn lit search "<core concept> introduction review" --max 6
   learn lit search "<concept> tutorial survey" --sources openalex,crossref
   learn lit db "<term>" --sources europepmc        # biology/medicine databases
   ```
   Results are signals, not truth. Screen them: drop off-topic hits, prefer reviews,
   surveys and textbooks, and prefer the original paper over re-uploads (check with
   `learn lit resolve <arXiv:id | doi:...>`).
5. **Web search** (priority 3) for what paper indexes don't cover: textbooks, official
   syllabi or exam specifications, university lecture notes, standards bodies,
   official documentation. For school and undergraduate topics this is usually the
   best source of definitions and worked examples.
6. **Read before you write.** Open the best 3-6 sources: `learn lit text <id>` for open
   access, otherwise web fetch, otherwise the abstract from `learn lit resolve`. A
   source you only saw as a search hit cannot support a definition.
7. **Write the brief.** Run `learn research` to print the template, fill every section,
   then save:
   ```bash
   learn research --save <<'EOF'
   # Research brief: ...
   EOF
   ```
   The engine rejects it with a list of problems if anything is missing. Fix all of
   them and re-save.

## What a good brief has

- **Concepts**: 4-10 rows, each a single teachable idea with what it builds on. Roots
  are definitions or facts with no "usually". This table becomes the plan, so the
  order of ideas comes from the sources, not from you.
- **Definitions**: exact wording from the best source, cited. Simplify later, in the
  lesson, never here.
- **Misconceptions**: errors the sources say learners actually make. These become the
  wrong options in questions.
- **Worked examples**: one per root concept, with numbers, from or checked against a source.
- **Sources**: at least 3, at least one primary, textbook or review. Type honestly.
  `vendor` means documentation from whoever sells the thing.
- **Open questions**: where sources disagree, or what you could not verify. Teach
  those as open, never as settled.

## Rules

- No source, no fact. If it isn't in the brief, either add it (with a source) and re-save,
  or don't teach it.
- Every theory block cites brief sources as `[S1]` after the facts they support. The
  engine refuses blocks without valid citations and shows the learner a folded
  source list under each block.
- Don't download datasets, install packages or sign up for anything a source mentions
  (PRAXIST resource policy). Note it as an open question if it matters.
- If `learn lit` fails (no network, PRAXIST missing), continue with web search and say so
  in Open questions.
