# Multimedia learning: rules for narrated animations and their notes

Researched 2026-10-07. "(inference)" marks extrapolation beyond what a source tested. Mayer's effects come from short lab lessons scored on transfer tests; Guo measures engagement, not learning.

## Sources

| ID | Citation | URL | Read |
|---|---|---|---|
| S1 | Mayer, R. E., & Moreno, R. (2003). Nine ways to reduce cognitive load in multimedia learning. *Educational Psychologist, 38*(1), 43-52. | https://www.uky.edu/~gmswan3/575/9_ways_to_reduce_CL.pdf | Full text |
| S2 | Mayer, R. E. (2023). Research-based principles for designing multimedia instruction. In Overson et al. (Eds.), *In Their Own Words* (pp. 143-157). APA Div. 2. Effect sizes summarize Mayer (2021), *Multimedia Learning* (3rd ed.). | https://www.unh.edu/teaching-learning-resource-hub/sites/default/files/media/2023-06/itow-research-based-principles-for-designing-multimedia-instruction-mayer.pdf | Full text |
| S3 | Mayer, R. E., & Pilegard, C. (2014). Principles for managing essential processing: segmenting, pre-training, and modality. *Cambridge Handbook of Multimedia Learning* (2nd ed.), 316-344. | https://www.cambridge.org/core/books/cambridge-handbook-of-multimedia-learning/principles-for-managing-essential-processing-in-multimedia-learning-segmenting-pretraining-and-modality-principles/DD24C2F48B9B1277CE59F78276110258 | Abstract only |
| S4 | Tversky, B., Morrison, J. B., & Betrancourt, M. (2002). Animation: can it facilitate? *IJHCS, 57*, 247-262. | https://hci.stanford.edu/courses/cs448b/papers/Tversky_AnimationFacilitate_IJHCS02.pdf | Full text |
| S5 | Höffler, T. N., & Leutner, D. (2007). Instructional animation versus static pictures: a meta-analysis. *Learning and Instruction, 17*(6), 722-738. | https://doi.org/10.1016/j.learninstruc.2007.09.013 | Abstract only (paywalled) |
| S6 | Spanjers, I. A. E., van Gog, T., & van Merriënboer, J. J. G. (2010). A theoretical analysis of how segmentation of dynamic visualizations optimizes students' learning. *Educational Psychology Review, 22*(4), 411-423. | https://repub.eur.nl/pub/19682/201020040109.pdf | Full text |
| S7 | Rey, G. D., Beege, M., Nebel, S., Wirzberger, M., Schmitt, T. H., & Schneider, S. (2019). A meta-analysis of the segmenting effect. *Educational Psychology Review, 31*, 389-419. | https://doi.org/10.1007/s10648-018-9456-4 | Abstract only (paywalled) |
| S8 | Guo, P. J., Kim, J., & Rubin, R. (2014). How video production affects student engagement: an empirical study of MOOC videos. *Proc. ACM Learning@Scale*, 41-50. | https://www.cs.rochester.edu/hci/pubs/pdfs/edX-MOOC-video-production-and-engagement_LAS-2014.pdf | Full text |
| S9 | Ainsworth, S. (2006). DeFT: a conceptual framework for considering learning with multiple representations. *Learning and Instruction, 16*(3), 183-198. | https://doi.org/10.1016/j.learninstruc.2006.03.001 | Abstract only; function names from secondary summaries |

## Segmenting

- Mayer & Chandler (2001, reported in S1, S2) cut a lightning lesson into 16 segments, each 1-2 sentences of narration and about 8-10 s of animation, with a Continue button. Transfer improved (d = 1.36, one study).
- Segmenting principle: 7 of 7 tests, d = 0.67 (S2); 10 of 10, d = 0.79 (S3). Meta-analysis of 56 studies: small to medium gains in retention and transfer, lower cognitive load, and the effect also holds for system-paced pauses (S7).
- Why it works (S6): pauses give time to process one unit before the next arrives, and pauses at event boundaries cue the structure. Breaks at event boundaries improved recall; breaks between boundaries hurt (Boltz 1992, in S6). Spanjers et al. used an automatic 2 s pause. No tested rule for segment length exists (S6).
- Guo (S8, 6.9M sessions): median watch time was at most 6 min whatever the length; viewers got under halfway through videos over 9 min; 0-3 min videos engaged best.

**Rule.** One segment = one event, 1-2 narrated sentences, 8-15 s (8-10 s is the tested value; 15 s is inference), never over 20 s (inference). Split today's 12-27 s steps at their internal event boundaries. One video = one sub-idea, target 3 min or less, hard cap 6 min. A bigger lesson becomes several videos with notes between them, so the learner paces the lesson at the video level.

## Narration-animation synchronization

- Temporal contiguity: 8 of 8 tests, d = 1.31 (S2). When words and their picture are separated, the learner must hold one in working memory until the other arrives (S1). The effect is strongest for long, system-paced lessons (S2), which describes our videos.
- Granularity: the tested contrast was whole narration before or after the whole animation. But the advantage disappears when the material alternates in bites of a few seconds of narration and the matching animation (S1). So the unit that matters is the phrase and its visual event, not the section.
- Drift inside a step is worse than plain lag: the voice names event B while the screen shows A, so the learner links the wrong word to the wrong picture (inference).
- Animations are often too fast or too complex to perceive, so they must be slow and clear enough for viewers to see each change and when it happens (S4). Visual cues (arrows, flashing, spotlights) work (11 of 12 tests, d = 0.71, S2) only if they fire when the word is spoken (inference).

**Implication: audio first.** Synthesize each phrase, measure its real duration (word timestamps if available), then derive every animation's start time and run_time from the audio. Each phrase gets one visual event that starts at the phrase onset (within about 0.3 s, inference) and settles before the next phrase. Freeze frames are allowed only at segment boundaries, never mid-segment (inference).

## On-screen text and redundancy

- Redundancy: narration plus identical on-screen text did worse than narration alone (3 studies, d = 0.69, S1). The later tally is weaker (8 of 12 tests, d = 0.10, S2): small harm, no benefit. It shrinks or reverses for short or reworded text, technical terms, second-language learners, or learner-paced lessons (S2).
- Modality: spoken words beat printed words with animation, 18 of 19 tests, d = 1.00 (S2).
- Spatial contiguity: printed words placed next to what they name, 9 of 9 tests, d = 0.82 (S2). The losing condition in the source was a caption at the bottom of the screen (S1).
- Coherence: cutting extraneous material, 18 of 19 tests, d = 0.86. Background music and decorative clips hurt (S1, S2).

**Keep:** short labels (1-4 words, inference) attached to their object, formulas and symbols, a segment title as a heading, arrows and highlights. **Cut:** sentences that repeat the narration, bottom captions, decorative text, music. The current numbered captions should become short titles (inference). Keep the transcript, but folded and opt-in.

## Structured notes next to the video

Notes are read before or after the video, so redundancy does not strictly apply; the problem is that today's notes add nothing. They should do what the video cannot:

1. **Big idea**: one sentence at the top. Signaling: outlines and headings help (S2).
2. **Key terms** before the embed: the name plus a one-line description of each part. Pre-training: 10 of 10 tests, d = 0.78 (S2).
3. **Video embed.**
4. **Numbered steps**: one line, one key-frame still, and one timestamp per segment. Static frames can be compared and re-checked; animations are fleeting (S4). Key frames revealed one at a time and left visible improved learning (Arguel & Jamet 2009, in S6). Signposts help re-watching (S8).
5. **Table or comparison**: information the narration cannot hold, playing a complementary role (S9).
6. **Worked example** with labeled substeps. Labeled, visually separated substeps improved transfer (Catrambone 1995, in S6).
7. **Check yourself**: 2-3 prompts to summarize, self-explain, or predict. Generative activity: 37 of 44 tests, d = 0.71 (S2). Prediction helps (S4).
8. **Sources**: one block at the end. A citation after every sentence is extraneous clutter (coherence, inference).

## Representation choice

Animation beats static pictures overall (d = 0.37), more for representational (0.40), realistic (0.76) and procedural-motor content (1.06) (S5). Tversky (S4): many apparent wins came from extra information or interactivity, not motion; expect gains for continuous change, fine microsteps and viewpoint changes; prefer schematic; static diagrams with arrows can match animation.

| Knowledge type | Best form | Animate? | Basis |
|---|---|---|---|
| Process, discrete steps (algorithm, procedure) | One segment per step, plus a static step strip in the notes | Yes, segmented | S4, S5, S6 |
| Continuous transformation (morph, rotation, geometric proof, flow) | Animation | Yes, the core use | S4 |
| Structure or system (parts and relations) | Static labeled diagram first, then animate only the flow through it | Static, then animate | S1, S2, S4 |
| Cause and effect (mechanism) | Narrated animation, one causal link per segment, plus an arrow diagram in the notes | Yes | S1 |
| Comparison | Side by side, or a table | No; morph A into B only if the difference is a transformation (inference) | S4, S9 |
| Quantitative relationship | Graph (rate shown as slope) | Only to show how the curve responds to a parameter (inference) | S4 |
| Classification or hierarchy | Tree or table | No; a progressive build is optional (inference) | S4 |
| Spatial layout, 3D | Diagram | Yes, for viewpoint changes | S4 |
| Definition or single fact | Text in the notes | No (inference) | S2 coherence |

## Decision rules for the engine

1. **Audio first.** Generate the narration, measure real durations, and set every animation's timing from the audio. Never guess durations (S1, S2; method is inference).
2. **One phrase, one visual event**, starting at the phrase onset (0.3 s tolerance, inference). Never let drift exceed one phrase (S1).
3. **Segment = 1-2 sentences, 8-15 s.** Split anything over 20 s at an event boundary (S1; cap is inference).
4. **End each segment on a silent 2 s hold** of the finished frame (S6, S7).
5. **Video target is 3 min or less, with a hard cap of 6 min.** Split bigger lessons into several videos, each covering one sub-idea (S8).
6. **Pre-train**: key terms plus a static labeled diagram before the first video (S2, S3).
7. **No on-screen sentence that repeats the narration.** Captions stay off by default (S1, S2).
8. **Labels sit next to their object**, 1-4 words; formulas are allowed (S2; word cap is inference).
9. **Cue at the spoken moment, sparingly**: at most one highlight active at a time (S2 says "used sparingly"; the cap is inference).
10. **No music, decorative motion, or realistic textures**; keep the style schematic (S1, S4).
11. **Animate only change over time**; everything else stays static (S4, S5).
12. **Keep each step's result on screen** and export one key frame per segment for the notes (S4, S6).
13. **Notes follow the template above.** No note sentence copies the narration, and there is one Sources block (S2, S9; inference).
14. **Conversational, human-sounding voice** that says "you" (personalization: 13 of 15 tests, d = 1.00; voice: 6 of 7, d = 0.74; S2). The current 2.6 words/s (156 wpm) matches Guo's mean (S8).
15. **Adapt to the learner**: novices get small segments and pre-training. After demonstrated mastery, merge segments and skip pre-training (expertise reversal, S6; S2). Keep segmenting on by default, because S7 found that high-prior-knowledge learners also gained on retention.
