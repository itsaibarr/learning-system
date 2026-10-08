---
id: cambridge-as-a-level
board: Cambridge International AS & A Level
citation_regex: \b\d{4}/\d{2}/(?:M/J|O/N|F/M)/\d{2} Q\d+[a-z0-9()]*
citation_example: 9702/21/M/J/24 Q2(b)(iii)
---

# Exam profile: Cambridge International AS & A Level

Facts below were checked against the real documents on 2026-10-07/08
(`docs/research/teaching-quality/exam-mode.md` has every URL and page reference).

## Codes and citations

- File names: `9702_s23_qp_22` = syllabus, series + year (`m` Feb/March, `s` May/June, `w` Oct/Nov),
  `qp` question paper / `ms` mark scheme / `er` examiner report / `gt` grade thresholds, then
  paper + variant (`22` = Paper 2, variant 2). Examiner reports have no component number.
- Cite a question with the code printed in the paper's own footer: **`9702/21/M/J/24 Q2(b)(iii)`**,
  `9702/22/F/M/24 Q1(b)`, `9618/11/M/J/24 Q2(e)(i)`. The engine checks this format.
- Computer Science: **9618** applies. 9608 was last examined in 2021 (legacy notice). An old 9608 item
  may be used only when it maps to a 9618 learning outcome, and is still cited as 9608. A coursebook
  chapter "Communication and networking technologies" maps to 9618 section 2.1 (Paper 1).

## Papers

| Syllabus | Paper | Time | Marks | What |
| --- | --- | --- | --- | --- |
| 9702 | 1 | 1 h 15 | 40 | forty four-choice multiple-choice items, AS content |
| 9702 | 2 | 1 h 15 | 60 | structured questions, AS content |
| 9702 | 3 | 2 h | 40 | practical, two 20-mark questions |
| 9702 | 4 | 2 h | 100 | A Level structured (A + AS content) |
| 9702 | 5 | 1 h 15 | 30 | planning, analysis and evaluation |
| 9618 | 1 | 1 h 30 | 75 | theory fundamentals, sections 1-8, no calculator |
| 9618 | 2 | 2 h | 75 | problem-solving and programming (pseudocode), no calculator |

## Command words (quoted from the syllabus)

9702 (syllabus 2025-2027 p.41): **Calculate** "work out from given facts, figures or information";
**Comment** "give an informed opinion"; **Compare** "identify/comment on similarities and/or differences";
**Define** "give precise meaning"; **Describe** "state the points of a topic / give characteristics and
main features"; **Determine** "establish an answer using the information available"; **Explain** "set out
purposes or reasons / make the relationships between things evident / provide why and/or how and support
with relevant evidence"; **Give** "produce an answer from a given source or recall/memory"; **Identify**
"name/select/recognise"; **Justify** "support a case with evidence/argument"; **Predict** "suggest what may
happen based on available information"; **Show (that)** "provide structured evidence that leads to a given
result"; **Sketch** "make a simple freehand drawing showing the key features"; **State** "express in clear
terms"; **Suggest** "apply knowledge and understanding to situations where there are a range of valid
responses in order to make proposals".

9618 (syllabus 2026 pp.41-42) adds, among others: **Outline** "set out the main points"; **Describe**,
**Explain** "...make the relationships between things clear / say why and/or how..."; **Evaluate** "judge or
calculate the quality, importance, amount, or value of something"; **Complete** "add information to an
incomplete diagram or table"; **Contrast** "identify/comment on differences". 9618 has no "Determine".

## Mark schemes

- 9702: **B** independent marks; **M** method marks that later A marks depend on; **C** compensatory marks
  ("If a correct answer is given to a numerical question, all of the preceding C marks are awarded
  automatically"); **A** answer marks. `ecf` = error carried forward. A missing or wrong unit normally loses
  the final mark. List rule: for "State two ...", wrong answers still count towards the two.
- 9618: points-based, "1 mark each to max 2", `//` separates alternatives; no B/M/A letters.
- Rubric points for typed questions copy these codes: `C1: base units of F are kg m s^-2`, `A1: kg m^-3`.

## Examiner reports

Principal Examiner Report for Teachers: key messages, general comments, then comments per question part.
Use each common error as a misconception (distractor, grading trap). Rank by the report's wording:
"majority" > "significant number" > "small minority". Example (9702/21/M/J/24 Q2(b)(iii)): "A significant
number of candidates ... substituted a value of a = 9.81 m s-2 rather than a = -9.81 m s-2."

## Sources (learner-approved)

| Site | Use | Watch out |
| --- | --- | --- |
| cambridgeinternational.org | syllabus PDFs, June 2024 variant-1 QP/MS/ER only | everything else is School Support Hub (login); file URLs are numeric IDs, take them from the subject's past-papers page |
| pastpapers.papacambridge.com | all variants to May/June 2026; ERs to Oct/Nov 2023 | `.../CAIE/CAIE-pastpapers/upload/9702_s23_qp_22.pdf`. A missing file returns HTTP 200 with an HTML page: check it is really a PDF |
| physicsandmathstutor.com | QP + MS by paper and variant | no examiner reports; "PMT" watermark |
| GCE Guide | **never** | its domains redirect to a gambling site / ad domain (2026-10-07) |

## Building a pattern (for generated questions)

1. One syllabus learning outcome. 2. At least 4 real questions from at least 2 series, with mark schemes.
3. Record stem shape, data given, command word, marks, mark-scheme points, examiner-report errors.
4. Keep features shared by 3+ questions; the rest are allowed variations. 5. A generated question stays
inside those features and is labelled "generated, follows pattern P#".

Worked example (9702 1.2 SI base units, from 9702/21/M/J/23 Q1(b), 9702/22/M/J/23 Q1(b), 9702/22/F/M/24
Q1(b), 9702/21/M/J/24 Q1(a), 9702/23/M/J/24 Q1(a), 9702/22/F/M/26 Q1(c)): Q1 of Paper 2; an unfamiliar
equation with every symbol defined and one unknown constant; "Determine the SI base units of k" [3] or
"Show that ..." [2]; MS C1 base units of the given quantities, A1 final units; traps: hertz used as a base
unit, (p2 - p1) treated as unitless, symbol equation written without substituting base units.
