# Exam mode: sources, codes, marking and patterns

Researched 2026-10-07/08. Every URL below was fetched (HTTP 200, `application/pdf`) and its text read unless marked (unverified).

## 1. Sources

| Site | Provides | Reliability |
|---|---|---|
| cambridgeinternational.org | Syllabuses, specimen papers, and only one public session: June 2024, variant 1 of each paper, plus the whole-syllabus examiner report | Authoritative. File URLs use opaque numeric IDs (`/Images/567868-...pdf`), so get them by scraping the subject's `/past-papers/` page, not by guessing |
| pastpapers.papacambridge.com | All variants, sessions up to May/June 2026 (QP, MS, ER, grade thresholds, confidential instructions) | Mirror. The 9702/21 June 2024 QP and MS were text-identical to the official copies. Recent files have a "Trace ID: PC-..." stamp. **A missing file returns HTTP 200 with an HTML page**, so check Content-Type. ERs found only up to Oct/Nov 2023 |
| physicsandmathstutor.com (PMT) | CAIE QP and MS by paper and variant; WMA11 QP and MS up to June 2025 | Mirror with a "PMT" watermark on each page. Content matched the official copy. No examiner reports found |
| qualifications.pearson.com | WMA11 spec, QP, MS, examiners' report | Authoritative. Predictable URLs |
| GCE Guide | **Do not use.** On 2026-10-07 gceguide.com and papers.gceguide.com redirected to an online slot-gambling site, papers.gceguide.net redirected to an ad domain, papers.gceguide.cc did not resolve, and gceguide.xyz is a non-working Wayback-downloader demo. Remove it from the allow-list |

**9702 Physics (verified)**
- Syllabus 2025-2027: https://www.cambridgeinternational.org/Images/664565-2025-2027-syllabus.pdf (2028-2030: `/Images/744626-2028-2030-syllabus.pdf`)
- QP: https://www.cambridgeinternational.org/Images/567868-june-2024-question-paper-21.pdf
- MS: https://www.cambridgeinternational.org/Images/567863-june-2024-mark-scheme-paper-21.pdf
- ER: https://www.cambridgeinternational.org/Images/567861-june-2024-examiner-report.pdf
- Mirrors: https://pastpapers.papacambridge.com/directories/CAIE/CAIE-pastpapers/upload/9702_s23_qp_22.pdf (also `_ms_22`, `9702_s23_er.pdf`, `9702_s23_gt.pdf`); https://pmt.physicsandmathstutor.com/download/Physics/A-level/Past-Papers/CAIE/Paper-2/QP/June%202024%20(v1)%20QP.pdf
- Quirk: the official link labelled "June 2023 Mark Scheme Paper 31" (`567864`) is actually the May/June 2024 9702/31 scheme.

**9618 Computer Science (verified).** 9618 is the code that applies. The 9608 legacy notice (https://www.cambridgeinternational.org/Images/596760-2021-syllabus-legacy-notice.pdf) says 9618 was first examined in June 2021 and that 9608 "will not be available for examination after 2021". The last 9608 paper on PapaCambridge is 9608_w21_qp_11. The 9608 page on the Cambridge site returns HTTP 500. The label "Chapter 2 Communication and networking technologies" looks like a coursebook chapter title (unverified which edition). The matching 9618 content is section 2 "Communication", 2.1 "Networks including the internet" (2026 syllabus pp.16-17), which is tested in Paper 1. Section 14 "Communication and internet technologies" is A Level only and is tested in Paper 3. Old 9608 items, such as 9608/11/O/N/21 Q11(b) "Describe the format of an IP address.", can be used only when they map to a 9618 2.1 learning outcome. They must still be cited as 9608.
- Syllabus 2026: https://www.cambridgeinternational.org/Images/697372-2026-syllabus.pdf (2027-2029: `/Images/721397-2027-2029-syllabus.pdf`, which states "no significant changes which affect teaching")
- QP: https://www.cambridgeinternational.org/Images/673628-june-2024-question-paper-11.pdf
- MS: https://www.cambridgeinternational.org/Images/673620-june-2024-mark-scheme-paper-11.pdf
- ER: https://www.cambridgeinternational.org/Images/673617-june-2024-examiner-report.pdf
- Mirrors: `.../upload/9618_s24_qp_11.pdf`; https://pmt.physicsandmathstutor.com/download/Computer-Science/A-level/Past-Papers/CAIE/Spec-2021/Paper-1/QP/June%202024%20(v1)%20QP.pdf

**WMA11 (verified)**
- Spec (Issue 3): https://qualifications.pearson.com/content/dam/pdf/International%20Advanced%20Level/Mathematics/2018/Specification-and-Sample-Assessment/international-a-level-maths-spec.pdf
- QP: https://qualifications.pearson.com/content/dam/pdf/International-Advanced-Level/Mathematics/2018/Exam-materials/wma11-01-que-20240510.pdf
- MS: `.../Exam-materials/wma11-01-rms-20240815.pdf`
- Examiners' report: `.../Exam-materials/wma11-01-pef-20240815.pdf`
- June 2025 (`rms-20250814`, `pef-20250814`) and January 2025 (`rms-20250306`) are also public. I did not locate anything later (unverified).
- PMT: https://pmt.physicsandmathstutor.com/download/Maths/A-level/Papers/Edexcel-IAL/Pure/P1/QP/June%202024%20QP.pdf (and `/MS/June%202024%20MS.pdf`)

**Behind a login.** The Cambridge past-papers page says: "This is only a selection of our papers. Registered Cambridge International Schools can access a wide range of teaching and learning materials and examination resources through our School Support Hub." So everything on the Cambridge site beyond the June 2024 variant-1 set is Hub-only there. Examiner reports after June 2024 were not found in any public source. Presumably they are on the Hub (unverified: I could not log in). Pearson says: "Question papers, mark schemes and examiner reports for the most recent exam sessions (within the last 12 months) can be accessed only by registered centres."

## 2. Paper code anatomy

**Cambridge:** `9702_s23_qp_22` = syllabus, then series and year, then document type, then component.
- Series: `m` = Feb/March (footer `F/M`), `s` = May/June (`M/J`), `w` = Oct/Nov (`O/N`).
- Document type: `qp` question paper, `ms` mark scheme, `er` examiner report (one per syllabus per series, so no component number), `gt` grade thresholds, `ci` confidential instructions for the practical paper.
- Component: the first digit is the paper and the second is the variant (`22` = Paper 2, variant 2). Variants exist because "All Cambridge schools are allocated to an administrative zone. Each zone has a specific timetable." (9702 syllabus p.63). Which variant goes to which zone is (unverified).
- March is offered only to schools in India (9702 p.63). Only variant 2 was seen in March (`9702_m24_qp_22`). 9618 runs in June and November only.

**Citation.** Use the code printed in the paper's own footer, then the question number: **"9702/21/M/J/24 Q2(b)(iii)"**, "9702/22/F/M/24 Q1(b)", "9618/11/M/J/24 Q2(e)(i)".

**Pearson:** the paper reference is `WMA11/01` (unit P1, paper 01). Series are January, June and October (spec p.7). In official file names, `que` is followed by the exam date, and `rms` (mark scheme) and `pef` (examiners' report) are followed by the results date. Inside each document there is a publications code (`WMA11_01_2406_MS`, `WMA11_01_2406_ER`) and a question-paper log number (`P75707A`). Pearson calls the June series "Summer". Citation: **"WMA11/01 June 2024 Q2(ii)"**. Add the log number if two documents could be confused.

## 3. Paper structure

**9702** (2025-2027 syllabus pp.11, 40, 42; timings and marks are the same in 2028-2030)

| Paper | Time | Marks | Content | Weighting |
|---|---|---|---|---|
| 1 Multiple Choice | 1 h 15 | 40 | "Forty multiple-choice items of the four-choice type", AS content | 31% AS / 15.5% A |
| 2 AS Structured | 1 h 15 | 60 | Structured questions, AS content | 46% / 23% |
| 3 Advanced Practical Skills | 2 h | 40 | "two questions, each of 1 hour and each of 20 marks" | 23% / 11.5% |
| 4 A Level Structured | 2 h | 100 | A Level content plus AS content | 38.5% A |
| 5 Planning, Analysis and Evaluation | 1 h 15 | 30 | Two compulsory questions | 11.5% A |

The data and formulae sheet is page 2 of Papers 1 and 2 (p.15). Question papers say "You may use a calculator."

**9618 AS** (2026 syllabus pp.11, 40). Paper 1 Theory Fundamentals: 1 h 30, 75 marks, sections 1-8. Paper 2 Fundamental Problem-solving and Programming Skills: 2 h, 75 marks, sections 9-12, answers in pseudocode, with an Insert listing built-in functions. Each paper is 50% of the AS. "Calculators must not be used in any paper."

**WMA11** (spec p.7 and p.12). One paper: 1 h 30, 75 marks, all questions compulsory, calculator and formula booklet allowed. It is 33⅓% of the IAS and 16⅔% of the IAL. The June 2024 paper had 11 questions and the instruction "Inexact answers should be given to three significant figures unless otherwise stated." Some questions are headed "In this question you must show all stages of your working. Solutions relying on calculator technology are not acceptable."

## 4. Command words

**9702** (syllabus p.41), quoted exactly:
- Calculate: "work out from given facts, figures or information"
- Comment: "give an informed opinion"
- Compare: "identify/comment on similarities and/or differences"
- Define: "give precise meaning"
- Describe: "state the points of a topic / give characteristics and main features"
- Determine: "establish an answer using the information available"
- Explain: "set out purposes or reasons / make the relationships between things evident / provide why and/or how and support with relevant evidence"
- Give: "produce an answer from a given source or recall/memory"
- Identify: "name/select/recognise"
- Justify: "support a case with evidence/argument"
- Predict: "suggest what may happen based on available information"
- Show (that): "provide structured evidence that leads to a given result"
- Sketch: "make a simple freehand drawing showing the key features"
- State: "express in clear terms"
- Suggest: "apply knowledge and understanding to situations where there are a range of valid responses in order to make proposals"

**9618** (2026 syllabus pp.41-42). The list has 26 words. These differ from 9702:
- Explain: "...make the relationships between things clear / say why and/or how..."
- Sketch adds "taking care over proportions"
- Suggest adds "/ put forward considerations"
- 9618 has no "Determine" and no "Show (that)"

Words added in 9618:
- Analyse: "examine in detail to show meaning, identify elements and the relationship between them"
- Assess: "make an informed judgement"
- Complete: "add information to an incomplete diagram or table"
- Consider: "review and respond to given information"
- Contrast: "identify/comment on differences"
- Demonstrate: "show how or give an example"
- Develop: "take forward to a more advanced stage or build upon given information"
- Discuss: "write about issue(s) or topic(s) in depth in a structured way"
- Draw: "draw a line to match a term with a description"
- Evaluate: "judge or calculate the quality, importance, amount, or value of something"
- Examine: "investigate closely, in detail"
- Outline: "set out the main points"
- Summarise: "select and present the main points, without detail"
- Write: "write an answer in a specific way"

**Pearson.** The IAL maths spec has no command-word list. Pearson's poster for the UK A level (Dec 2025, https://qualifications.pearson.com/content/dam/pdf/A%20Level/Mathematics/2017/Teaching%20and%20learning%20materials/a-level-maths-and-a-level-further-maths-command-words.pdf) defines:
- Show that: "All steps need to be shown to get the given answer, followed by a conclusion."
- Hence: "Use the result or information from a previous part of the question to help solve the current part."
- State / Write down: "Provide an answer concisely, without needing to show the working or explanation."
- Prove: "More formal than 'show', all steps must be present..."
- Also covered: Find, Determine, Sketch, Interpret, Estimate, Comment on, Verify, Deduce

Applying this poster to IAL is (unverified). Treat the in-paper instructions above as binding.

## 5. Mark scheme conventions

**9702** (MS 9702/21 May/June 2024, p.5):
- "B marks ... independent marks, which do not depend on other marks."
- "M marks ... method marks upon which A marks later depend."
- "C marks ... compensatory marks which can be awarded even if the points to which they refer are not written down ... If a correct answer is given to a numerical question, all of the preceding C marks are awarded automatically."
- "A marks ... answer marks."
- Notation: `/` means alternatives, `( )` is context that need not be seen, underlined words must be present.
- Principle 4: "The error carried forward (ecf) principle should be applied".
- Units: "a missing or incorrect unit will normally mean that the final calculation mark is not awarded."
- "List rule": for "State two ...", incorrect responses "still count towards n".
- **"owtte" did not appear** in any 9702 scheme I checked (s15, s19, s23, s24, s25, m26). Use "allow" and "ignore" as written in each scheme.

**9618** (MS 9618/11 May/June 2024) is points-based and has no B/M/A letters:
- Marks are given as "1 mark each to max 2:" or "1 mark for each row".
- `//` separates alternatives.
- A bullet starting with "…" is a follow-on that expands the point before it.
- Some parts have explicit exclusions, e.g. "No mark for identification of monitoring or control".

**WMA11** (MS June 2024, p.4):
- "M marks: Method marks are awarded for 'knowing a method and attempting to apply it'"
- "A marks: Accuracy marks can only be awarded if the relevant method (M) marks have been earned."
- "B marks are unconditional accuracy marks"
- Abbreviations: bod, ft, cao, cso ("There must be no errors in this part of the question to obtain this mark"), isw, awrt ("answers which round to"), SC, oe, "d… or dep – dependent", dp, sf, ag.
- "All A marks are 'correct answer only' (cao), unless shown ... as A1 ft"
- A misread costs "deduct two from any A or B marks gained".
- Differentiation M mark: "Power of at least one term decreased by 1".
- `dM1` (dependent method mark) appears in the scheme bodies: 4 in June 2024, 24 in January 2024.

## 6. Examiner reports

Cambridge's "Principal Examiner Report for Teachers" covers every variant of every paper. For each one it gives Key messages, General comments (including which parts candidates found easy or hard), then comments on each question part. Pearson's "Principal Examiner Feedback" gives General Comments, then comments per question.

How the tutor should use them:
- Store each error as a misconception record: {ER code, question ref, quoted error, frequency phrase}.
- Rank records by the frequency phrase: "majority" > "significant number" > "small minority".
- Use them as MCQ distractors, as hint triggers during grading, and as "trap" fields in patterns (section 7).

Verified examples:
- **9702/21/M/J/24 Q2(b)(iii)** (ER 567861): "A significant number of candidates used s = ut + ½at2 ... but substituted a value of a = 9.81 m s–2 rather than a = –9.81 m s–2. Many of those who successfully calculated the height reached above the launch position then did not add the value of 1.2 m".
- **WMA11/01 June 2024 Q2(ii)** (WMA11_01_2406_ER): "A significant number of candidates did not show the working for rationalising the denominator and hence lost the final two marks. The question specifically said that all stages of working should be shown."
- **9618/11/M/J/24 Q2(e)(i)** (ER 673617), on bit streaming: "many candidates need to improve their understanding of what is meant by bit streaming."

## 7. Extracting a question pattern

Procedure:
1. Pick one syllabus learning outcome.
2. Collect at least 4 real questions on it, from at least 2 series, with their mark schemes.
3. For each question, record: stem shape, data given, command word, marks, the mark-scheme points with their letters, and the ER errors.
4. Keep only the features shared by at least 3 of the questions. Everything else becomes an allowed variation.
5. When generating a question, stay inside those features, label it "generated, follows pattern X", and grade it with the pattern's mark-scheme template.

**Worked example: 9702 learning outcome 1.2.2/1.2.3** ("express derived units as products or quotients of the SI base units"; "use SI base units to check the homogeneity of physical equations", syllabus p.16). Questions read:
- 9702/21/M/J/23 Q1(a)(ii) [1] and Q1(b) [3]: "Determine the SI base units of k." MS: C1, C1, A1, answer kg m⁻³
- 9702/22/M/J/23 Q1(a)(ii) [1] and Q1(b) [3]: answer kg m⁻¹ s⁻¹ (C1, C1, A1)
- 9702/22/F/M/24 Q1(b) [2]: "Use the definition of power to determine its SI base units." (C1, A1)
- 9702/21/M/J/24 Q1(a) [3]: "Use SI base units to show that the drag coefficient has no units." (M1, M1, A1)
- 9702/23/M/J/24 Q1(a) [2]: "Show that the SI base units of viscosity are kg m–1 s–1." (C1, A1)
- 9702/22/F/M/26 Q1(c) [2]: "state and explain whether this equation is homogeneous" (C1, A1: "not homogeneous")

Resulting pattern:

| Field | Observed |
|---|---|
| Position | Q1 of Paper 2, usually after a 1-mark "Define X" (power, pressure, force) |
| Stem | An unfamiliar equation, every symbol defined ("where ... is"), with one unknown constant (k, C, η) |
| Command | Determine [3], Show (that) [1-2], "Use SI base units to show" [3], "state and explain whether homogeneous" [2] |
| MS template | C1: base units of the given quantities (several quantities can share one mark). A1: final combined units, or a conclusion with a comment |
| Traps (from ERs) | Using hertz as a base unit and using ampere for intensity I (s23 ER, 9702/21 Q1(b)). Treating (p2 – p1) as having no units (9702/22 Q1(b)). Making C the subject and getting "1 or 2", or cancelling wrongly (June 2024 ER, 9702/21 Q1(a)). Writing the symbol equation without substituting base units (9702/21/M/J/23 Q1(a)(ii)). |

## 8. Exam profile template fields

```yaml
board: cambridge | pearson
qualification: AS & A Level | IAL
syllabus_code: 9702          # with legacy_codes: [9608] for CS
syllabus_version: 2025-2027  # plus pdf_url and page refs
series: [{code: m, label: F/M}, {code: s, label: M/J}, {code: w, label: O/N}]
papers: [{id: 2, name, duration_min, marks, question_types, calculator, weighting, content_sections, inserts}]
file_naming: "{syl}_{series}{yy}_{type}_{paper}{variant}"
citation_format: "{syl}/{paper}{variant}/{series_label}/{yy} Q{n}{parts}"
sources: [{site, url_template, doc_types, coverage_to, trust, login_required, verify_rule: content-type==application/pdf}]
command_words: [{word, definition, source_page}]
mark_scheme: {mark_types: {B, M, C, A}, abbreviations: {...}, dependency_rules, list_rule, unit_rule}
examiner_reports: {available, url_template, structure}
syllabus_map: [{lo_id, text, papers}]
patterns: [{lo_id, source_questions: [...], stem, data, command, marks, ms_template, traps: [{text, er_ref}]}]
misconceptions: [{lo_id, error_quote, er_ref, frequency}]
```
