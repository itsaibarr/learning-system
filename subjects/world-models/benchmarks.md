# Benchmark reference — physical reasoning

One section per benchmark. **Never quote a number without its protocol row** — the relative
and absolute metrics on the same model and same items differ by 30 points, and several
headline figures are a max over context settings that also inflates the untrained control.

## IntPhys (Riochet et al., 2018; arXiv:1803.07616)

**Kind:** violation-detection  
**Measures:** Whether a plausibility/surprise score separates matched possible vs impossible synthetic (UE4) videos across three blocks: O1 object permanence, O2 shape constancy, O3 spatio-temporal continuity, each crossed with visible/occluded

**Protocol:** Training set is 15,000 possible-only videos of 100 frames; dev 360 videos, test 3,600 videos (whole test set, NOT per block — the 'per block' figure is a threefold inflation). Test items come in matched quadruplets (two possible beginnings x two possible endings) so possible and impossible movies are built from the same frames and differ only in temporal splicing. TWO metrics that must never be quoted interchangeably: relative/pairwise (rank the two highest-implausibility movies in a quadruplet as impossible) and absolute (1-AUC over the whole set, requiring a calibrated global threshold).

**Chance:** 50% under the relative/pairwise metric; for the absolute metric, whatever a calibrated threshold yields (the empirical untrained-network floor recomputed from released data is ~50.0%)

**Human:** Reported pairwise error 10/15/13/16/20/40% and single-video (1-AUROC) 18/30/22/30/28/47% across O1-O3 visible/occluded. PROVENANCE CAUTION: these were extracted from comparison tables in Garrido et al. (arXiv:2502.11831), not from the IntPhys paper; whether they are original or re-collected, and with how many participants, is unverified. Humans lose 8-17 points moving relative->absolute, and at continuity/occluded they are near chance either way.

**Best model:** V-JEPA ViT-H (RoPE, VideoMix2M) 98.33% relative on the DEV split, recomputed from the authors' released per-video CSVs — but that is a per-property max over six context settings, and the same model's absolute accuracy is 68.06% (79.72% with an oracle-swept threshold). Untrained ViT-L control 51.44%. Pixel-space V-JEPA-L 58.89% vs 91.67% for its representation-space twin; VideoMAEv2-g 59.44%; Qwen2-VL-72B 63.89% (68.89% with a property-specific prompt); Gemini 1.5 Pro 47.78%.

## IntPhys 2 (Bordes, Garrido, Kao, Williams, Rabbat, Dupoux, 2025; arXiv:2506.09849)

**Kind:** violation-detection  
**Measures:** Same violation-of-expectation logic over four principles (Permanence, Immutability, Spatio-Temporal Continuity, Solidity) in photorealistic Unreal Engine 5.4 scenes with moving cameras, complex occlusion and distractors

**Protocol:** Per-video binary possible/impossible. Splits confirmed from the official repo: Debug 5 scenes/60 videos; Main 253 scenes/1,012 videos (Easy/Medium/Hard); Held-Out 86 scenes/344 videos with metadata withheld and a HuggingFace leaderboard. Two structurally different tracks over the same stimuli: prompted-MLLM classification and prediction-based surprise (V-JEPA family, VideoMAEv2, Cosmos). CRITICAL, from the repo's own scoring notebook: reported per-split figures are a np.max over prompt variants x seeds x frame-rate x camera condition, and unparseable model answers count as errors.

**Chance:** 50% (balanced binary)

**Human:** 96.44% overall / 92.44% held-out as widely reported; the official README says only 'near-perfect accuracy'. The digits are unverified against the PDF in this corpus and should be checked before printing.

**Best model:** Gemini 2.5 Flash ~55.6% overall (MLLM track); V-JEPA 2 ~57.5% overall (surprise track); GPT-4o ~53.8%; Cosmos-Predict1-4B ~49.4%, i.e. below chance. Digits unverified against the PDF. The README's own verbatim summary is 'most models performing at chance levels (50%)' — and it exempts nobody, so it indicts the prediction-based world models too, not only the MLLMs.

## InfLevel (Weihs, Yuile, Baillargeon, Fisher, Marcus, Mottaghi, Kembhavi; TMLR 2022)

**Kind:** violation-detection  
**Measures:** Continuity, solidity and gravity, modelled on developmental paradigms, over real infant-lab video (InfLevel-Lab) and AI2-THOR renders (InfLevel-Sim)

**Protocol:** The only benchmark in this landscape that FORBIDS training, fine-tuning and even linear probing by design, on the stated grounds that a probe 'confound[s] physical understanding with feature extraction'. Model emits one plausibility score per video (large = plausible); the shipped evaluator compares matched trial types and returns accuracy plus one- and two-sided p-values. Gravity and solidity items require binding an earlier priming segment (e.g. does this container have a false bottom?) to a later event.

**Chance:** 50%

**Human:** Adults near 100% in the authors' exploratory experiments (no fuller human study reported)

**Best model:** Ten video architectures across ~60 experiments at or near chance on all three principles. V-JEPA ViT-H reaches 61.53% overall on InfLevel-lab under the surprise metric — but the per-property recomputation is decisive: object permanence 72.1 vs 52.5 untrained, while GRAVITY is 50.4 vs 51.0 untrained and SOLIDITY 51.4 vs 51.9 untrained, i.e. two complete nulls with tiny variance for trained and untrained models alike.

## GRASP Level 2 (Jassim, Holubar, Richter, Wolff, Ohmer, Bruni; arXiv:2311.09048)

**Kind:** violation-detection  
**Measures:** Eight intuitive-physics principles — continuity, solidity, inertia, gravity, collision, object permanence, support, unchangeableness — in Unity, over 16 tests / 4,096 videos, with a Level 1 language-grounding pre-test

**Protocol:** As originally evaluated the readout is language-mediated (video-LLM binary judgement), and the repo ships binary, one-shot, chain-of-thought, open-ended and — uniquely — a text-only control (level2_text.yaml, scene descriptions instead of video) that isolates language prior from perception. But the readout is NOT intrinsically linguistic: Meta's released code runs GRASP level 2 through a frozen V-JEPA surprise metric with no language in the loop. Venue 'IJCAI 2024' is asserted in the corpus but the repo's own BibTeX records an arXiv preprint; verify.

**Chance:** 50%

**Human:** ~80% average (single extraction, IJCAI PDF unreachable) — markedly below the ~96% human ceiling on IntPhys 2 and ~100% on InfLevel, so model-human gaps are not comparable across these three supposedly equivalent suites

**Best model:** All video-LLMs in the original paper at or below 50%. V-JEPA ViT-H 66.36% under surprise — but only 51.1-57.5% at any single fixed context length, while the untrained ViT-L control is 48.7-49.7% fixed and 55.9% after the same per-property max. On 'Unchangeableness' (colour constancy) the signal is systematically INVERTED for some checkpoints (0.0-5.5% accuracy at longer contexts, i.e. reliably more surprised by the legal video), which the max-over-contexts aggregation hides.

## LikePhys (arXiv:2510.11512; ICLR 2026)

**Kind:** violation-detection  
**Measures:** Whether a video DIFFUSION model's own likelihood prefers the valid member of an appearance-matched valid/invalid pair, over 12 scenarios in rigid-body, continuum, fluid mechanics and optics

**Protocol:** Training-free and language-free: the denoising loss is used as an ELBO likelihood surrogate; metric is Plausibility Preference Error (PPE). This is the cleanest existing template for asking a generative model whether it 'notices' without asking it to speak.

**Chance:** Not stated in the corpus for PPE — the random-preference baseline must be recovered from the paper before any 'above chance' claim

**Human:** No human accuracy baseline; PPE is reported to align with human preference at Kendall's tau = 0.44

**Best model:** No per-model PPE values retrievable. DiT-based architectures reportedly beat UNet-based; all struggle on complex fluid dynamics. GeoPhys is reported at 98.3% on LikePhys, but whether that is the same quantity as PPE is unresolved.

## ImplausiBench / TRAVL (Motamed, Chen, Van Gool, Laina; arXiv:2510.07550)

**Kind:** violation-detection  
**Measures:** Whether a VLM judge flags physically implausible generated video, with style-matched pairs (shared first frame and visual style) and grounded MCQs authored to strip language shortcuts

**Protocol:** 300 videos, 150 real + 150 implausible, scored separately on each subset under human gold judgement and a stricter LLM-as-judge. Note 'Human'/'LLM' name the JUDGE of the model's answer, not a human solver.

**Chance:** Not published; the raw subset accuracies are not stated relative to any baseline

**Human:** No human performance baseline exists for this benchmark — do not pair its numbers with a human ceiling

**Best model:** The asymmetry is the result, not the ranking: Gemini 2.5 Pro 41.3% implausible vs 100.0% real (human-judged; 29.3/78.0 LLM-judged); GPT-4o 32.7/84.7; Qwen2.5-VL 18.7/96.7; pretrained LLaVA-NeXT 3.3/98.7. TRAVL fine-tuning lifts implausible detection to 52.7% while dropping real to 47.3%, i.e. it partly trades one response bias for the other.

## IPV-Bench / Impossible Videos (Bai, Ci, Shou; ICML 2025, arXiv:2503.14378)

**Kind:** violation-detection  
**Measures:** 902 curated impossible videos over 4 domains / 14 categories spanning physical, biological, geographical and social impossibility, plus 260 generation prompts

**Protocol:** Three understanding tasks — binary Judgement, multi-choice QA, open-ended QA. The authors report F1 alongside accuracy explicitly because some models answer Yes (or No) for the majority of videos, i.e. raw judgement accuracy is corrupted by response bias.

**Chance:** 50% on the binary Judgement task

**Human:** Not retrieved

**Best model:** Not retrievable — the leaderboard exists only as images in the repo, and per-model figures returned by search were mutually inconsistent. Do not quote any IPV-Bench number without the accuracy+F1 pair from the tables.

## PhysGame (arXiv:2412.01800)

**Kind:** violation-detection  
**Measures:** Detection of physical-commonsense glitches occurring naturally in real gameplay video — 880 videos, 4 domains (mechanics, kinematics, optics, material properties), 12 subcategories

**Protocol:** Multiple choice for video LLMs. Methodologically interesting because the violations are in-the-wild rather than authored — but gameplay glitches are stylistically marked, so a model may be detecting 'game bug' rather than 'solidity violation'.

**Chance:** Unverified (option count not confirmed; 4-option MC would put it at 25%)

**Human:** Not retrieved

**Best model:** GPT-4o 56.1%, Gemini-1.5-Pro 55.2% among proprietary models; the authors' fine-tuned PhysVLM is SOTA and wins 6 of 12 subcategories.

## MVP / Minimal Video Pairs (Krojer, Komeili, Ross, Garrido, Sinha, Ballas, Assran; arXiv:2506.09987)

**Kind:** physical-QA  
**Measures:** Physical and spatio-temporal video understanding with shortcuts deliberately removed; its intuitive-physics subset is repackaged IntPhys, InfLevel, GRASP and CLEVRER stimuli turned into questions

**Protocol:** 55K multiple-choice items from nine sources. Every item has a minimal-change partner: visually similar video, identical question and options, opposite correct answer; paired_accuracy credits only both-correct, so a model exploiting visual or textual bias scores 0%, not 25%. This is the hybrid that proves the conflation is real — and a low MVP score cannot distinguish 'did not notice' from 'could not verbalize'.

**Chance:** 25% for an unbiased random guesser at the pair level (0.5 x 0.5); a systematically biased model scores 0%

**Human:** 92.9%

**Best model:** 40.2% best open-source in the paper — but FAIR's own V-JEPA 2 README records the previous best as 39.9% (InternVL-2.5) and V-JEPA 2 at 44.5%, so 'best model ~40%' is stale and the two figures may be different splits (mvp vs mvp_mini). Resolve before tabulating.

## PhysBench (Chow, Mao, Li, Seita, Guizilini, Wang; ICLR 2025)

**Kind:** physical-QA  
**Measures:** VLM understanding of physical properties, relationships, scenes and dynamics — 10,002 test items, 4 categories / 19 subclasses

**Protocol:** Zero-shot-style multiple choice, no task-specific training; option counts vary by item. The paper's PhysAgent scaffolding adds 18.4% to GPT-4o overall, with the largest relative gain on its weakest category.

**Chance:** NOT PUBLISHED. The README states no random baseline anywhere and option counts vary, so no PhysBench score may be described as 'X points above chance'.

**Human:** 95.87% overall (property 97.10, relationships 95.67, scene 94.91, dynamics 95.68)

**Best model:** Top entry in the repo's December-2024 leaderboard excerpt is InternVL2.5-38B at 51.94; GPT-4o 49.49. The diagnostic split is within-model: GPT-4o scores 64.80 on object relationships (static, prior-solvable) but 30.15 on scene understanding — though this ordering reverses in several lower-ranked rows, so it is a pattern in strong models, not a law.

## CausalVQA (Foss, Evans, Mitts, Sinha, Rizvi, Kao; Meta 2025)

**Kind:** physical-QA  
**Measures:** Causal reasoning over real Ego-Exo4D video: counterfactual, hypothetical, anticipation, planning, descriptive

**Protocol:** 1,586 items = 793 paired questions over 779 real, physically possible video segments, with perturbed-and-reordered second option sets and difficulty tiers calibrated against 273 annotators; test answers withheld. No impossible event is ever shown — impossibility, where present, lives in the question text.

**Chance:** Unknown: paired-accuracy chance is the square of single-question chance and the option count per question is not stated publicly. Do not assume 50%.

**Human:** 84.78% paired (95.05 Easy / 77.32 Medium / 60.05 Hard)

**Best model:** Gemini 2.5 Flash 61.66% overall, 53.46% on Reasoning questions

## CLEVRER (Yi et al., ICLR 2020)

**Kind:** physical-QA  
**Measures:** Descriptive, explanatory, predictive and counterfactual reasoning over synthetic collision video

**Protocol:** Short rendered videos; open-vocabulary descriptive plus multiple-select explanatory/predictive/counterfactual. All stimuli are physically valid; the 'predictive' subset is prediction, not violation detection. Two accuracy conventions (per-option vs per-question) coexist and give substantially different numbers.

**Chance:** Convention-dependent; must be stated with the accuracy convention

**Human:** Not retrieved in this corpus

**Best model:** NS-DR 88.02% on descriptive questions; a second circulating figure (99.68% explanatory) appears to come from a later method and an unclear convention — do not quote CLEVRER numbers without resolving this.

## Physion (Bear et al., NeurIPS 2021 D&B)

**Kind:** physical-prediction  
**Measures:** Physical prediction: given 1.5s of a wholly possible scene, will the red agent object contact the yellow patient zone? Eight scenarios in ThreeDWorld.

**Protocol:** REQUIRES a supervised readout by construction: pretrain a dynamics module with its native loss, freeze it, then train a per-scenario linear logistic regression on labelled data. This is precisely what InfLevel forbids, which is why Physion numbers can never be quoted alongside VoE numbers as the same capacity. No impossible event is ever shown.

**Chance:** 50%

**Human:** ~0.71 average across scenarios (a second source says ~75%; the commonly cited 73.9% is unconfirmed) — a low ceiling, so the human-model gap here is ~71 vs mid-60s, nothing like the ~40-point gaps on VoE suites

**Best model:** Object-centric graph/particle models given ground-truth TDW particles (GNS, GNS-RANSAC, DPI) match human accuracy on many scenarios; among vision-only models, ImageNet-pretrained Transformer encoders (pDeIT-mlp/lstm) lead and beat fully TDW-trained models.

## Physion++ (Tung et al., NeurIPS 2023 D&B)

**Kind:** physical-prediction  
**Measures:** Prediction that requires online inference of latent mechanical properties — mass, friction, elasticity, deformability

**Protocol:** 384 rigid-body trials across five categories (Mass Collision 64, Friction Collision 64, Friction Platform 64, Bounce Platform 96, Bounce Wall 96). Still no impossible events.

**Chance:** 50%

**Human:** Reported as not reached by any model; the numeric human baseline was not retrievable

**Best model:** No verified numbers. All video models fail to reach human-level prediction on all four properties, most only slightly above chance; models encoding objectness do better; particle models with 3D representations and direct access to the latent properties do best. The finding that matters most: all models correlate POORLY with human predictions, so even where accuracy is nonzero the error profile is not human-like.

## Physics-IQ (Motamed, Culp, Swersky, Jaini, Geirhos; WACV 2026) and Physics-IQ Verified (arXiv:2606.18943)

**Kind:** physical-prediction  
**Measures:** Whether a generative video model's continuation of a real filmed scenario obeys physics — solid mechanics, fluid dynamics, optics, thermodynamics, magnetism

**Protocol:** 396 camera-captured (not rendered) 4K/30fps videos, each scenario shot from 3 angles and recorded twice so the ceiling is the empirical physical variance between two real takes. Model is conditioned on a starting image (i2v) or preceding clip (v2v/multiframe) and must generate the continuation; scored by spatial IoU, spatiotemporal IoU, weighted spatial IoU and MSE against the real held-out continuation. Verified (2026) refines 57.6% of samples and improves 34.8% of prompts and produces ranking changes (Kendall tau 0.46) — never mix Original and Verified scores.

**Chance:** NONE. There is no guessing baseline: 0 is the floor by clipping and 100 is defined as a physically realistic continuation differing only by physical randomness.

**Human:** No human accuracy baseline exists — 'real-video ceiling' and 'human baseline' are not the same thing and must not be conflated

**Best model:** Paper-era: VideoPoet multiframe 29.5%, Lumiere 23.0%, Runway Gen-3 22.8%, Sora 10.0% — and Sora was simultaneously the MOST visually deceptive model (55.6% on an MLLM 2AFC realism test where 50% is chance), which is the realism/physics dissociation. Current Original leaderboard: Magi-1 24B + GeoPhys best-of-N v2v 64.5%, Cosmos3-Super v2v 59.7%, Sora 2 i2v 42.3%. Verified: Magi-1 + GeoPhys BoN v2v 58.2 +/- 1.8; best single-model i2v Cosmos3-Super-Image2Video 39.5 +/- 0.8; Sora 2 i2v 26.5 +/- 0.8. Top entries use inference-time best-of-N reranking against an external verifier, so unaided single-sample generation is well under half the ceiling.

## GeoPhys (Internò, Pondaven, Issa, Pizzati, Pinto, Olhofer, Laptev, Torr, Simoncelli, Hammer, Klindt; arXiv:2606.20707)

**Kind:** violation-detection  
**Measures:** Whether violation detection needs a world model at all: five training-free kinematic statistics — speed variation, curvature, angle consistency, acceleration, linear-prediction residual — computed on frozen per-frame image-encoder features treated as a trajectory in representation space

**Protocol:** No learned parameters, no video pretraining, no physics supervision. Backbones DINOv2, DINOv3, CORnet-S, VOneNet, 'none trained on video or physics'. Also deployed as a best-of-N verifier on Physics-IQ at 1.5x lower wall-clock and 4.65x lower memory than a V-JEPA 2 verifier.

**Chance:** Inherits the host benchmark's chance (50% on IntPhys 2)

**Human:** Inherits the host benchmark's human baseline

**Best model:** Reported 93.3% on IntPhys 2 and 98.3% on LikePhys where V-JEPA 2, GPT-4o, Gemini and twelve video diffusion models sit near chance; lifts MAGI-1 24B from 50.01% to 64.50% on Physics-IQ; reported to align with human EEG responses to object-permanence violations. HANDLE WITH CARE: single very recent preprint, README only, no result tables, code not released at the time of reading, and the IntPhys 2 split for 93.3% is unstated. If it replicates, it is the single most consequential result in this table — for and against.

## X-VoE (Dai, Wang, Jia, Zhang, Zhu, Zhang, Zhu; ICCV 2023 Oral)

**Kind:** other  
**Measures:** Explanatory rather than discriminative violation-of-expectation: each scenario is instantiated in three settings demanding that the model reconstruct the occluded scene state accounting for the violation, not merely flag it

**Protocol:** Explanation-based learning system infers occluded object states from visual sequences alone, without explicit occlusion labels, and can visually expound a VoE event by reconstructing the concealed scene. Whether the three settings genuinely test explication or just add discrimination conditions is unresolved.

**Chance:** Not applicable / not retrieved

**Human:** Not retrieved

**Best model:** Not retrieved. Included because it is the field's only serious attempt to raise the bar from detection to explanation, and because it mirrors the psychology-side shift (Stahl & Feigenson; Margoni, Surian & Baillargeon) toward VoE as a trigger for explanation search rather than a surprise readout.

