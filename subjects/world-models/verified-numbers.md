# Verified numbers — world models

Every row below was produced by a research pass and then attacked by an independent
adversarial verifier against the primary source. **The caveat column is the point** — most
of these numbers circulate without their protocol and are wrong or misleading as usually
quoted. Do not cite a row without its caveat.

Assembled 2026-09-02.

## ~10^14 bytes on BOTH sides

**LLM corpus: roughly 30 trillion tokens (he also states it as 20 trillion words) at about 3 bytes/token. Child: 16,000 waking hours x 3600 s/h x about 2x10^6 bytes/s of optic nerve = 1.15x10^14. The slide's punchline is that these are about the SAME.**

- Source: Verbatim from the ETH Zurich talk, 29 May 2026, confirmed against a transcript of that talk.
- Caveat: He credits vision AND touch, not vision alone. The optic-nerve figure is stated as 2 million fibres at about 1 byte/s each, not as a '1-2 MB/s' range, and it is an order-of-magnitude estimate he has himself revised tenfold since 2024. Bandwidth is not information content.

## 400,000 years

**How long one human reading continuously would need to consume the LLM training corpus.**

- Source: ETH Zurich talk, 29 May 2026.
- Caveat: The figure drifted across retellings: 170,000 years (Jan 2024, 8 h/day, 1E13 tokens), about 100,000 (Mar 2024, 12 h/day), 400,000 (2026, 3E13 tokens). Teach the TIME ratio - four years versus 400,000 - since that, not any data ratio, is where the rhetorical force now lives.

## 50x - RETIRED

**The January 2024 claim that a four-year-old has seen fifty times more data than the biggest LLMs. It is the most-quoted figure about this talk and it is no longer the deck's claim.**

- Source: LeCun on X, status 1750614681209983231, 25 January 2024 (snowflake decodes to 2024-01-25T20:20:39Z).
- Caveat: That post's own factors ('1E13 tokens x 0.75 word/token x 2 bytes/token = 1E13 bytes' against a child's 1E15) give 100, not 50 - the post is internally inconsistent. The ratio becomes consistent only with his 9 March 2024 restatement (1E13 two-byte tokens = 2E13 bytes). Teach the factors and flag the slip; do not teach the ratio as if it followed from the January numbers.

## half-length about 0.693/e (69 tokens at e=1%, 693 at e=0.1%)

**Under LeCun's autoregressive model, the answer length at which the probability of being entirely correct falls to one half.**

- Source: LeCun on X, status 1640122342570336267, created 2023-03-26T22:43:33Z.
- Caveat: The date is 26 March 2023, not 27 as commonly repeated, and the status is marked '1/' - the independence condition and the 'training shrinks e but cannot eliminate it' remark belong to the thread continuation. 'Exponentially diverging diffusion process' is rhetorical: the object is a geometric survival probability.

## 75.8% versus 77.6%

**MAE's own reported ImageNet-1K linear-probe comparison at ViT-L: MAE against MoCo v3. This is the paper-internal frozen-representation gap.**

- Source: MAE (He et al., CVPR 2022), which states its ViT-L 'still lags behind contrastive methods under this protocol: e.g., MoCo v3 has 77.6%'.
- Caveat: The widely circulated '68.0 (MAE ViT-B) vs 76.7 (MoCo v3) vs 78.2 (DINO)' row does NOT appear in the MAE paper; those three figures come from three different repositories' own probe recipes and are not one matched comparison. Do not teach it.

## 73.5% -> 81.0%

**MAE ViT-L (800-epoch pretraining) going from a frozen linear probe to unfreezing a single transformer block.**

- Source: MAE, CVPR 2022, section 4.3 and Figure 9.
- Caveat: 73.5 is the 800-epoch probe; the 1600-epoch probe is 75.8 - two different numbers that are routinely conflated. The authors' stated conclusion is the weaker 'linear separability is not the sole metric for evaluating representation quality', not a rejection of linear probing, which they continue to use as their main ablation signal.

## 83.6% versus 83.2%

**End-to-end fine-tuned ViT-B on ImageNet-1K: MAE against MoCo v3 - the ranking reverses relative to frozen evaluation.**

- Source: The official facebookresearch/mae and facebookresearch/moco-v3 repository tables.
- Caveat: Not a matched comparison: MAE pretrains 1600 epochs and fine-tunes with its own recipe; MoCo v3 pretrains 300 and fine-tunes with the 150-epoch DeiT recipe. MAE's own reading of its table is 'for ViT-B, all methods perform closely' - a 0.4-point difference is not a win.

## under 1200 GPU-hours; 79.3%

**I-JEPA ViT-H/14 pretraining cost on ImageNet (16 A100s in under 72 hours) and its 300-epoch ImageNet linear-probe accuracy.**

- Source: I-JEPA (Assran et al., CVPR 2023): 79.3 is verified in Table 1; the GPU-hour sentence is in the Introduction's contributions list and Section 7.
- Caveat: The 'over 2.5x faster than a ViT-S/16 with iBOT and over 10x more efficient than a ViT-H/14 with MAE' sentence is NOT in the abstract, and the comparisons are against each baseline's own published recipe (iBOT at 800 epochs, MAE at 1600), not equal-epoch runs. The 16 x 72 = 1152 reconciliation is the reader's arithmetic, not the paper's.

## 98% / 66% / 62%

**V-JEPA violation-of-expectation accuracy on IntPhys, GRASP and InfLevel-lab, where pixel-prediction video models and multimodal LLMs sit near the 50% chance baseline. Emerges at ~115M parameters and with as little as 128 hours of video.**

- Source: Garrido et al., 'Intuitive physics understanding emerges from self-supervised pretraining on natural videos' (arXiv:2502.11831); Meta released the raw per-model surprise tensors and a notebook regenerating every figure.
- Caveat: The same paper reports near-chance performance on properties involving object interactions - solidity, collision - so the high numbers cover single-object properties (permanence, continuity, shape and colour constancy). Detecting impossibility is not acting competently.

## 57.51% versus 96.44% human

**V-JEPA 2 against humans on IntPhys 2, the deliberately harder Unreal Engine successor built because IntPhys 1 had saturated. On Minimal Video Pairs, 44.5% against 92.9% human with chance at 25%.**

- Source: Meta's V-JEPA 2 companion benchmark release (IntPhys 2, arXiv:2506.09849; MVP, arXiv:2506.09987; CausalVQA).
- Caveat: Evidence and counter-evidence come from the same lab, released simultaneously with the model. Reported model scores on IntPhys 2 cluster in the low-to-mid 50s against a 50% chance baseline, and sources disagree on which model leads. The roughly 43-point drop from IntPhys 1 indicates the original was largely solvable by low-level statistical cues.

## 80% / 50%, about 16 s per action

**V-JEPA 2-AC zero-shot pick-and-place success with a cup and a box on Franka arms in two labs absent from the training data, planning by Cross-Entropy Method over an L1 latent goal energy, against roughly 4 minutes per action for a pixel-generating Cosmos baseline. Full table: Reach 100, Grasp cup 60, Grasp box 20.**

- Source: Official facebookresearch/vjepa2 README table; the planning-speed comparison is from the V-JEPA 2 paper (arXiv:2506.09985) via secondary rendering.
- Caveat: The famous '62 hours of unlabelled DROID video' trains only the action-conditioned predictor on a FROZEN encoder that carries over a million hours of internet video - it is the marginal cost of adding actions, not the total budget. Grasping a box at 20% is the honest limit, multi-stage behaviour uses hand-specified gripper scheduling, and there is no independent third-party reproduction of the robot results.

## 77.1% and 78.5% - not 79%

**LeJEPA's ImageNet-1k online linear-probe results actually reported in the v3 body: ViT-L (0.3B) and ConvNeXtV2-H (0.6B).**

- Source: LeJEPA (Balestriero and LeCun, arXiv:2511.08544v3), body and appendix.
- Caveat: The abstract's headline '79% with a ViT-H/14' is not substantiated anywhere in the v3 body or appendix - the only ViT-H/14 rows in the paper are I-JEPA baselines. Also treat 'one hyperparameter' precisely: it is one LOSS TRADE-OFF hyperparameter (lambda, about 0.05 in the paper's ablations, 0.02 in the repository's minimal example); slice count, quadrature knots, view counts, learning rate and weight decay all remain, and 'no schedulers' means no EMA/temperature schedules, not no learning-rate schedule.

## $1.03B at $3.5B pre-money

**AMI Labs' seed round, announced 10 March 2026 - reported as the largest seed round for a European company. LeCun is executive chair; Alexandre Lebrun is CEO.**

- Source: TechCrunch and Bloomberg, March 2026.
- Caveat: The '$7 billion' figure on aggregator sites and a '$30M' headline are both wrong. His departure from Meta was announced November 2025, not 'late 2024' or 'January 2026' as some secondary pages state. As of September 2026 AMI has shipped no model; independent forecasters put a first public release at a 2028 median.


---

# Contested — where LeCun's framing is a bet, not a finding

Nine points where the talk states as settled something that is disputed. Each gives
LeCun's position, the strongest counter, and who makes it.

## Whether pixel-space generative prediction is a dead end for world modelling, or merely a less efficient route

**LeCun:** Abandon generative models in favour of joint-embedding architectures; at ETH he extended the advice beyond LLMs - 'if you want world models, do NOT work on video generation.' Prediction in observation space wastes capacity on unpredictable detail and cannot produce the representations planning needs.

**Counter:** Apple's AIM does pure autoregressive PIXEL prediction on 2B uncurated images and reaches 84.0% ImageNet from a frozen trunk at 7B with no saturation; AIMv2-3B reaches 89.5% frozen, above DINOv3's 88.4% (though with paired text, so not label-free). Veo 3 shows emergent zero-shot segmentation, physical-property understanding and maze-solving at 78% pass@10 from pure generation. The defensible version of LeCun's claim is about efficiency - roughly an order of magnitude less data for comparable frozen quality - not impossibility. The counter-counter is Kang et al. (ICML 2025): video generators generalize case-based, ranking cues colour > size > velocity > shape, and fail out-of-distribution regardless of scale.

**Who:** Apple (El-Nouby et al., AIM, ICML 2024; Fini et al., AIMv2, CVPR 2025); Google DeepMind (Wiedemer et al., arXiv:2509.20328). Counter-counter from Kang et al., ICML 2025 (arXiv:2411.02385), which supports LeCun.

## Whether the (1-e)^n autoregressive divergence argument applies to real LLMs

**LeCun:** 'Auto-Regressive LLMs are exponentially diverging diffusion processes': with e the per-token probability of exiting the tree of correct answers, an answer of length n is correct with probability (1-e)^n; training can shrink e but not remove the exponent.

**Counter:** The algebra is not in dispute; the modelling step is. LLM errors are not i.i.d. per token, are concentrated at sparse decision-point 'key tokens', and are frequently self-corrected downstream, with correct answers behaving as attractors that different token paths converge to - so real degradation is far slower than geometric. Two further precisions: the cited status (26 March 2023, not 27) is marked '1/', so the independence condition belongs to the thread continuation and should not be attributed to it; and 'exponentially diverging diffusion process' is rhetoric - the object is a geometric survival probability, not a diffusion process. Teach it as LeCun's argument under an explicit assumption, never as a theorem.

**Who:** Widely rebutted; the corpus's specific attributions (a LessWrong rebuttal, a 2026 Brando Miranda write-up) could not be verified, so cite the class of objection rather than a named author.

## Whether guardrails-as-cost-terms make an objective-driven system 'intrinsically safe' and unjailbreakable

**LeCun:** Verbatim at ETH, with a conditional that is routinely dropped: a system constructed this way 'CAN BE MADE intrinsically safe, because it has to obey and optimize the guardrail objective with every output it produces... Here you can't jailbreak the system.' The contrast drawn is with fine-tuning an LLM, which he says always leaves a jailbreak.

**Counter:** The rebuttal is structural and the learner can check it without any citation: a guardrail is a learned cost evaluated against states predicted by the LEARNED WORLD MODEL, so the safety property is inherited from exactly the component whose reliability is in question - and it fails hardest on the out-of-distribution situations where safety matters most. Worse, the planner is by construction an optimizer searching for low-energy action sequences, which is precisely an adversarial search against an imperfect learned objective; the specification-gaming literature is a catalogue of that failure. 'More controllable than RLHF' is defensible; 'cannot be jailbroken' is not.

**Who:** The specification-gaming literature; critics of the ETH talk. Note the widely cited technical write-up of this talk could not be reached in verification, so present the argument on its merits rather than as a sourced attribution.

## Whether the data-volume slide licenses a conclusion about learning at all (bandwidth versus information)

**LeCun:** Text is too low-bandwidth a modality (under 12 bytes/second) to learn how the world works; a four-year-old takes in about 10^14 bytes through vision and touch, the same order as a 30-trillion-token corpus, in four years rather than 400,000. Conclusion: 'we're not going to get anything like human-like intelligence by training on text alone.'

**Counter:** The step from channel bandwidth to information content is the weak link. Optic-nerve bytes are hugely redundant, actively selected by saccades rather than uniformly sampled, and cross-checked by other senses; congenitally blind children do not show correspondingly impoverished world models. LeCun's own numbers are unstable - the per-fibre rate has moved by a factor of ten across his retellings (20 MB/s in March 2024 versus ~2 MB/s in 2026) and the reading-time figure drifted 170k to ~100k to 400k years. He also relies on redundancy as a VIRTUE for self-supervised learning while the byte count treats it as content. The 2024 'scarcity' leg is retired by his own current numbers, which make the two corpora equal.

**Who:** General critics of the byte-counting; and, on the retired scarcity leg, LeCun's own 2026 revision of the slide.

## Whether encoder-encoder, continuous-latent-only, non-generative architectures are sufficient for a world model

**LeCun:** World models should not be simulators, digital twins, generative models or video generators; prediction belongs in an abstract representation space, with uncertainty pushed into a regularized latent rather than into a normalized distribution.

**Counter:** Xing and co-authors argue directly that sensory-data-only inputs, continuous latent representations, encoder-encoder architectures and latent-space-only objectives are structurally insufficient, and propose PAN - hierarchical, multi-level, mixed continuous/discrete, and generative. Gary Marcus attacks from a third direction, arguing that an ego-driven block against symbolic AI means LeCun misunderstands what a world model has to be. Note also a historical correction that cuts against a too-clean story: LeCun's own 2022 paper CALLS the world model 'a kind of simulator of the relevant aspects of world' and names step 3 of Mode-2 'simulation' - the sharp world-model-versus-simulator rhetoric is later LeCun and must not be back-projected onto v0.9.2.

**Who:** Eric Xing, Mingkai Deng, Jinyu Hou et al., 'Critiques of World Models' (arXiv:2507.05169; title and month corroborated only - author list, date and quoted phrases unverified, and PAN is a separate later paper, arXiv:2511.09057). Gary Marcus, separately and on different grounds.

## Whether RL should be demoted to a last resort in favour of MPC

**LeCun:** Abandon RL in favour of model-predictive control, using RL only when planning fails to produce the predicted outcome, to adjust the world model or the critic. The argument is mechanical: with a good model and objective, MPC is zero-shot on a new task, whereas RL needs enormous numbers of trials per task. Note the preface he attaches to the whole 'abandon' slide and that secondary coverage drops: 'at least partially, or minimize'.

**Counter:** The Dreamer line amortizes the search into weights and works at scale: DreamerV3 (Nature 2025) masters 150+ tasks with a single fixed hyperparameter configuration and is the first to collect diamonds in Minecraft from scratch without human data. TD-MPC2 combines search WITH a learned terminal value and a policy prior, suggesting the dichotomy is false rather than a choice. From the opposite direction, Richard Sutton objects that passive observation of recorded data is the wrong substrate entirely and that experiential RL from interaction is the road - an objection that lands on V-JEPA pretrained on unlabelled internet video, and to which V-JEPA 2-AC's action-conditioned post-training is precisely the concession.

**Who:** Hafner et al. (Dreamer/DreamerV3); Hansen et al. (TD-MPC2); Richard Sutton, from the opposite side.

## Whether V-JEPA's intuitive-physics results show physical understanding

**LeCun:** Latent-space video prediction is measurably 'surprised' by physically impossible videos - 98% on IntPhys, 66% GRASP, 62% InfLevel-lab - while pixel-space video prediction and multimodal LLMs sit near chance, and this emerges at ~115M parameters and as little as 128 hours of video. The win is therefore architectural, not a matter of scale.

**Counter:** The same lab's harder successor benchmark knocks everything back: V-JEPA 2 scores 57.51% on IntPhys 2 against 96.44% human, and 44.5% on MVP against 92.9% human (chance 25%), with reported model scores clustering in the low-to-mid 50s and sources disagreeing on which model leads. The ~43-point collapse indicates IntPhys 1 was largely solvable by low-level cues. Even the original paper reports near-chance performance on properties involving object INTERACTIONS - solidity, collision. Detecting impossibility is also not the same as acting competently.

**Who:** Meta's own companion benchmarks, released alongside V-JEPA 2 (IntPhys 2, MVP, CausalVQA) - the counter-evidence and the evidence come from the same lab.

## Whether the contrastive / non-contrastive taxonomy is a real separation

**LeCun:** Abandon contrastive methods in favour of regularized ones: the number of contrastive samples needed to raise energy everywhere off the manifold may, in the worst case, grow exponentially with the dimension of the representation, whereas regularized methods minimize the volume of low-energy space and are less exposed to the curse of dimensionality.

**Counter:** LeCun states this as a volume-covering intuition with explicit hedges ('may... in the worst case') and does not prove it. The nearest rigorous statement, the InfoNCE bound I >= log N - L_N, caps CERTIFIED mutual information at log N nats - a fact about the estimator, not a theorem that representation quality degrades exponentially, and several papers show representation quality is not monotone in that bound. More decisively, Garrido, Chen, Bardes, Najman and LeCun (ICLR 2023) show contrastive and covariance-based criteria can be related algebraically and are equivalent under limited assumptions, improving SimCLR to match VICReg and vice versa. Dimensional collapse also afflicts contrastive methods, so it is not the price of going non-contrastive.

**Who:** Garrido, Chen, Bardes, Najman and LeCun (ICLR 2023) - LeCun's own group published the result weakening the strong form of his taxonomy; Jing, Vincent, LeCun and Tian (ICLR 2022) on dimensional collapse.

## Whether this route rather than scaling reaches human-level intelligence

**LeCun:** 'On the highway towards Human-Level AI, Large Language Model is an off-ramp'; at Brown, the industry bet that LLMs reach human-level intelligence is 'complete BS'. His timeline claim is deliberately weak: 'at the very best, we might be convinced that we're on a good path towards human intelligence - but not yet at human intelligence - within five years.'

**Counter:** His specific dated predictions have a poor record: the early-2023 'GPT-5000' claim that a text-only system could never infer that an object on a pushed table moves with it was falsified within about a year, and announced walls keep failing to appear. The structural counter is stronger than any benchmark: no published JEPA-based system has demonstrated open-ended autonomous competence comparable to a frontier LLM - the results are representation results and short-horizon manipulation - and AMI Labs, funded at $1.03B in March 2026, had shipped no model as of September 2026. His own hedge cuts both ways: he also says LLMs 'will keep scaling and keep being useful', and the emerging architecture is hybrid, which makes 'nobody in their right mind would use them' hard to score. Do not teach 'off-ramp is deliberately not a dead end' - on Lex Fridman he conjoined them: 'an off-ramp, a distraction, a dead end.'

**Who:** The scaling camp broadly; Gary Marcus, who backs LeCun against Meta's leadership while predicting the venture fails.

