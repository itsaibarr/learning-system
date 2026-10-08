# Assessment and question design

Problem: in 148 LLM-written MCQs, the key was the uniquely longest option 47% of the time (chance is 25%). Learners scored 90-98% by picking the most sensible-sounding option, and the distractors were often absurd. This file sets out rules for the question writer and the checks the engine can run.

## Sources

1. Haladyna, Downing & Rodriguez (2002). A review of multiple-choice item-writing guidelines for classroom assessment. *Applied Measurement in Education* 15(3), 309-333. https://doi.org/10.1207/S15324818AME1503_5. **Full text** (course copy: lesn.appstate.edu/olson/RES5560/...Haladyna_Downing_Rodrequez_2002.pdf).
2. NBME (2016). *Constructing Written Test Questions for the Basic and Clinical Sciences*, 4th ed., eds. Paniagua & Swygert. **Full text** (copy at health.uconn.edu/.../constructing_written_test_questions.pdf). The current 6th edition (2020, nbme.org/item-writing-guide) sits behind a form, so I did not read it.
3. Gierl, Bulut, Guo & Zhang (2017). Developing, analyzing, and using distractors for multiple-choice tests in education: A comprehensive review. *Review of Educational Research* 87(6), 1082-1116. https://doi.org/10.3102/0034654317726529. **Full text** (third-party upload of the published PDF at tipsforteachers.co.uk).
4. Treagust (1988). Development and use of diagnostic tests to evaluate students' misconceptions in science. *Int. J. Science Education* 10(2), 159-169. **Abstract only** (ERIC EJ380815). Method details come from the **full text** of Treagust & Haslam (1986), the NARST paper that underlies it (ERIC ED283713). Three-tier: Pesman & Eryilmaz (2010), *J. Educational Research* 103(3), **abstract only**. Hasan, Bagayoko & Kelley (1999), Certainty of Response Index, *Physics Education* 34(5), **abstract only**. Chu, Chandrasegaran & Treagust (2018), ERIC EJ1174745, **abstract only**.
5. Butler (2018). Multiple-choice testing in education: Are the best practices for assessment also good for learning? *JARMAC* 7(3), 323-331. https://doi.org/10.1016/j.jarmac.2018.07.002. **Abstract only** (paywalled), plus Butler's own **full** summary post (learningscientists.org/blog/2017/10/10-1).
6. Rodriguez (2005). Three options are optimal for multiple-choice items: A meta-analysis of 80 years of research. *EM:IP* 24(2), 3-13. **Full text** (author's course site, edmeasurement.net).
7. Krathwohl (2002). A revision of Bloom's taxonomy: An overview. *Theory Into Practice* 41(4). **Full text**. I used it as a stand-in for Anderson & Krathwohl (2001), the book, which I did not read.
8. Supporting sources: Butler & Roediger (2008), *Memory & Cognition* 36(3), **full text**. Shute (2008), Focus on formative feedback, *RER* 78(1), **full text**. Kang, McDermott & Roediger (2007), *Eur. J. Cog. Psych.* 19, **abstract only**. Yang et al. (2021), *Psych. Bulletin* 147(4), **abstract only**. Agarwal, Nunes & Blunt (2021), *Educ. Psych. Review*, **abstract only**. Jonsson & Svingby (2007), *Educ. Research Review* 2, **abstract only**.

## Item-writing flaws an engine can detect automatically

NBME sorts flaws into two kinds. "Testwiseness" flaws let savvy test-takers guess without knowing the content. "Irrelevant difficulty" flaws confuse everyone (NBME ch. 3). Haladyna guideline 28 lists the same cues. The numeric thresholds below are mine (inference). No source gives a number.

| Flaw | Rule (source) | Detection heuristic |
|---|---|---|
| Longest key | "Keep the length of choices about equal" (H 24, 85% of textbooks). NBME: the correct option is often "longer, more specific, or more complete" because writers add teaching caveats to it. | Flag the item if len(key) / mean(len(distractors)) > 1.25, or if the key is the uniquely longest option. Batch check: across a lesson, the key should be uniquely longest in no more than about 1/k of items (k = number of options). |
| Clang clue | Stem words repeated in the key (NBME; H 28b). | Compare content-word stems (lemmatised) between the stem and each option. Flag if the key shares a stem word that no distractor shares. |
| Absolute words | "always, never, completely, absolutely" mark options that testwise students rule out (NBME; H 28a). | Regex for absolute words. Flag if they appear only in distractors. Also flag hedges ("may", "can", "often") that appear only in the key. |
| All / none of the above | Avoid AOTA (H 26). NBME lists NOTA as a flaw. Butler: avoid both. | String match. Reject the item. |
| Negative stem | Avoid NOT/EXCEPT (H 17; NBME). | Regex `\b(not|except|least|false)\b` in the stem. Reject, or require caps and a stated justification. |
| Grammatical cue | Distractors that don't follow grammatically from the stem (NBME; H 28c). | Require a closed question stem ending in "?". That prevents the flaw at the source (NBME). Optionally, check a/an and singular/plural agreement for completion stems. |
| Overlap / exhaustive set | Options must not overlap (H 22). NBME: numeric ranges that contain other options; option subsets that cover every outcome. | For numbers, parse values and ranges and flag containment or mixed formats. For text, flag high embedding similarity between options, or one option containing another. |
| Convergence | The key shares the most elements with the other options because distractors were written as variations of it (NBME). | For each option, count the tokens it shares with the other options. Flag if the key has the strict maximum. |
| Heterogeneous options | Options must be homogeneous and fall on a single dimension (H 23; NBME). | Flag if option lengths have a coefficient of variation above 0.35, or if the options mix syntactic types (noun phrase vs full sentence). |
| Cover-the-options failure | A knowledgeable learner should be able to answer from the stem alone (NBME rule 3). | LLM check: answer the stem without the options, then compare with the key. |
| Answer guessable without stem | (Inference from the flaws above.) | Ask an LLM to pick the answer from the options only. If it is right much more often than 1/k across a batch, the set leaks cues. |
| Position bias | Vary where the key appears (H 20). Gierl: randomise, except for ordered series. | Shuffle in code. Sort numeric options. |

## Distractor construction

- **Source of distractors.** Write distractors from typical learner errors (H 30). Gierl's first and most common recommendation is to use "common misconceptions or errors in thinking, reasoning, and problem solving". You find these in learners' answers to open-ended versions of the same item, in think-alouds, or by asking an expert "What do students usually confuse this with?" The second strategy is similarity: same category as the key, similar length, complexity and grammar. For numeric items, recompute the answer with a step left out or reversed. The engine already sees the learner's typed answers, so wrong typed answers should feed the next round of distractors (inference, following Gierl/Tamir).
- **Plausibility.** All distractors must be plausible. Guideline 29 and "avoid giving clues" each had 96% textbook support. H 28f says to avoid blatantly absurd options. NBME: distractors may be partly correct, but each must be "less correct" than the key along one dimension, and filler options added only to reach five are "not an improvement". Gierl, citing Little & Bjork: competitive distractors improve later retention, while unrelated ones add misinformation.
- **How many.** Rodriguez (56 trials, 27 studies) found that going from 5 to 3 options left discrimination and reliability unchanged on average. Going from 4 to 3 raised discrimination by .03 and reliability by .02. Going to 2 options hurt all three measures. He concludes that items "should consist of three options, one correct option and two plausible distractors". The modal number of functioning distractors per item in real tests is about one (Haladyna & Downing 1993, cited in H and Rodriguez). Rodriguez notes an exception: diagnostic items whose distractors map to misconceptions may need more options. Butler: three or four, depending on how many plausible wrong answers exist. Gierl reaches the same conclusion.
- **Functional distractor.** A distractor is functional if more than 5% of learners choose it, and if low scorers choose it more often than high scorers (negative point-biserial, falling trace line) (Haladyna & Downing, cited in Rodriguez, Gierl, NBME ch. 4). If an item is answered correctly more than 90% of the time, its distractors will naturally be rarely picked (Gierl). NBME treats p > .95 as uninformative.
- **Homogeneity.** Use the same grammatical form, a similar length and the same category for every option. Use a logical or numerical order for numbers (H 21-23).

## Question types by learning objective

Level definitions follow Krathwohl (2002). Remember = recognizing or recalling. Understand = interpreting, classifying, comparing, inferring, explaining. Apply = executing or implementing a procedure in a given situation. Analyze = differentiating, organizing, attributing. "Transfer" is not a Krathwohl category. Here it means applying knowledge to material that is new to the learner (H 3; NBME, inference).

| Objective | Best format | Evidence |
|---|---|---|
| Recognition | Single-best-answer (SBA) MCQ, 3 options | NBME fig. 1: recall items suit formative "rapid fire" checks. Rodriguez on option count. |
| Recall | Typed short answer, with feedback | Kang 2007: with feedback, a short-answer quiz gave the best 3-day retention. Without feedback, MC did better. |
| Conceptual understanding | SBA with a novel example; "explain why" typed answer | H 3: use novel material and paraphrase the teaching text. |
| Application | SBA with a scenario/vignette stem and a closed lead-in ("What is the next step?") | NBME rule 2. In NBME's own data, low scorers fell from 90% correct (no vignette) to 66% (long vignette). |
| Transfer | Vignette in a context not used in teaching; prediction items | NBME: a vignette identical to one taught becomes recall. |
| Reasoning | Two-tier (answer + reason), or answer + typed justification | Treagust: tier 2 offers reasons drawn from learner misconceptions. Chu et al. 2018: Year 8 learners showed their understanding better on two-tier items than on MC with open justification. |
| Misconception diagnosis | Two-tier or three-tier (add confidence) | Pesman & Eryilmaz; Hasan CRI. Confidence separates a misconception (wrong and confident) from a knowledge gap (wrong and unsure). |
| Exam procedure | Worked problem, error-spotting, ordering steps | Context-dependent item sets test multistep thinking (H). Ordering and error-spotting are inferences from Krathwohl's "organizing" and "checking". |

## When open-ended beats MCQ

Use open-ended items when the goal is recall or explanation, or when MCQ cueing inflates scores. Kang 2007: short answer plus feedback beat MC. NBME/H: an MCQ the learner can solve from the options alone measures testwiseness, not knowledge. Yang 2021 and Agarwal 2021 found benefits from both formats in classrooms. Matching the quiz format to the final test format moderated the effect in Yang. Default rule (inference): use MCQ for quick checks and typed answers for core concepts.

**Grading typed answers.** Jonsson & Svingby (75 studies): rubrics make scoring more reliable "especially if they are analytic, topic-specific, and complemented with exemplars". Use a key-point rubric (inference, built on that finding):
- Each answer gets 2 to 4 required key points. Each point is a single checkable proposition.
- List known misconceptions that cancel credit.
- Provide one exemplar answer.
- The grader (LLM) returns which points were present, with a supporting quote from the learner's answer for each, plus any misconception detected.
- Score = points present / points required. Do not award credit for length or wording.

## Question density and feedback

- Testing beats restudy. Yang 2021: g = 0.50 across 222 classroom studies. The effect grew with corrective feedback and with more test repetitions (moderators named in the abstract; direction per the abstract). Adesope 2017 found the same.
- Target difficulty: Butler recommends tests that "challenge students but allow them to succeed often", with a mean around 80%. Super-easy items "undermine learning". 90-98% is too easy (inference from Butler). Butler & Roediger 2008: with no prior study and no feedback, MC testing left learners with more false answers (.32) than correct ones (.18).
- Density (inference; no source fixes a number): about 1 retrieval item per key idea, at least 3 per unit, more spaced repetitions for the core ideas. Stop adding items in a unit once rolling accuracy stays above 90% on items that pass the flaw checks.
- Feedback after a wrong answer: always show the correct answer and why it is correct (Butler & Roediger: feedback reduced lure intrusions). Shute: give elaborated "what, how, why" feedback, in small units, focused on the task, only after the learner has attempted the item, and without praise or comparison with others. For hard tasks or weak learners, give feedback immediately.
- Feedback after a right answer: still confirm it and briefly give the reason. Butler & Roediger found that delayed feedback helped even initially correct items, and that feedback improved learners' calibration (inference: this targets lucky guesses). If the engine collects confidence, explain right answers that were given with low confidence.

## Decision rules for the engine

1. Every MCQ has exactly 3 options (1 key + 2 distractors). The writer may use 4 only if each distractor is tagged with a distinct misconception. (Rodriguez, Butler)
2. Each distractor must carry a `misconception` or `common_error` tag. Reject untagged distractors. (H 30, Gierl)
3. Reject if len(key)/mean(len(distractors)) > 1.25, or if the key is the uniquely longest option in more than 40% of a batch. (H 24, NBME)
4. Reject if a stem content word appears in the key but in no distractor. (NBME clang)
5. Reject if absolute words appear only in distractors, or hedges only in the key. (NBME, H 28a)
6. Reject "all/none of the above", "both A and B", and negative stems. (H 17, 26; NBME; Butler)
7. Stems must be closed questions ending in "?" that pass the cover-the-options check: an LLM answering without options must reach the key. (NBME)
8. Run an options-only blind test with an LLM. If its accuracy across the batch is more than 1.5/k, regenerate. (inference)
9. Reject overlapping or exhaustive option sets and numeric ranges that contain other options. Sort numeric options. Shuffle all other options in code. (H 20-22, NBME, Gierl)
10. At least half of a unit's items must use a scenario that did not appear in the lesson text (application/transfer). Check that the scenario's n-gram overlap with the lesson is low. (H 3, NBME)
11. Core concepts get at least one typed item graded by a key-point rubric (2 to 4 points, misconception list, exemplar). (Kang, Jonsson & Svingby)
12. Reasoning and misconception items use a two-tier format (answer + reason drawn from misconceptions) with an optional confidence rating. Treat "wrong + confident" as a misconception and schedule it for remediation. (Treagust, Pesman, Hasan)
13. Log choice frequencies. After 20 or more responses, flag distractors chosen by fewer than 5% of learners and items with p > .90 for rewrite. (Haladyna & Downing via Gierl, NBME)
14. Target 70-85% rolling accuracy. Above 90% on a unit, raise the difficulty (scenario or typed items). Below 60%, re-teach before testing again. (Butler; thresholds inference)
15. Feedback: after every answer, give a verdict plus a one-to-three-sentence reason for the key. After a wrong answer, also say why the chosen distractor is wrong, using its misconception tag. No praise. (Butler & Roediger, Shute)
