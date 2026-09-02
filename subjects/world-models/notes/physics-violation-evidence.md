# Concept: what the physics-violation evidence actually shows

**In one sentence:** V-JEPA's headline 98% on IntPhys was largely low-level cues — its own
successor benchmark drops it to 57.5% against 96.4% human — but a *competence profile* survives
that a pure novelty detector cannot produce: single-object properties yes, object interactions
at chance.

**Hangs off:** [surprise-is-not-understanding.md](surprise-is-not-understanding.md) — the confound
says a spike may track unfamiliarity rather than impossibility. Selective failure is the
discriminating test, because novelty is uniform across violation types and competence is not.

**The click:** the argument does not resolve to yes or no. It resolves to a **profile**, and the
profile is the finding.

## The evidence, both directions

| Result | Number | What it does to the claim |
| --- | --- | --- |
| V-JEPA on IntPhys | 98% (chance 50%) | supports — pixel-prediction models and multimodal LLMs sit near chance |
| V-JEPA on GRASP / InfLevel-lab | 66% / 62% | supports, weakly |
| Emerges at | ~115M params, as little as 128 h video | supports **architectural**, not scale |
| Same paper, object interactions (solidity, collision) | **near chance** | the dissociation — this is the load-bearing row |
| V-JEPA 2 on IntPhys 2 | **57.51%** vs 96.44% human | undercuts — ~43-point drop from IntPhys 1 |
| V-JEPA 2 on Minimal Video Pairs | **44.5%** vs 92.9% human (chance 25%) | undercuts — below chance-adjusted midpoint |

Evidence and counter-evidence come from **the same lab, released simultaneously** — Meta shipped
IntPhys 2, MVP and CausalVQA alongside V-JEPA 2. That is unusual and worth saying plainly.

## What follows

1. **The 98% was mostly low-level cues.** A benchmark built to be harder should cost a few points,
   not 43. The drop is the measurement of how much of IntPhys 1 was solvable without physics.
2. **The dissociation survives the drop.** Permanence, continuity, shape and colour constancy are
   learned; solidity and collision are not. Both classes are equally absent from training video, so
   novelty predicts *uniform* sensitivity and does not get one.
3. **So the defensible claim is narrow:** something structured is present, it is thin, it covers
   single objects and not their interactions, and it is nowhere near human.

**Watch out:** "detecting impossibility" and "acting competently" are different capacities, and a
result about one is routinely cited about the other. Keep them apart.

**Re-analysable:** Meta released the raw per-model surprise tensors plus a notebook that regenerates
every figure — the profile can be re-cut without re-running anything.

| Claim | Evidence | Confidence |
| --- | --- | --- |
| V-JEPA 98/66/62 on IntPhys/GRASP/InfLevel-lab, baselines near chance | Garrido et al., arXiv:2502.11831 | high |
| Near-chance on solidity and collision in that same paper | same | high |
| V-JEPA 2: 57.51% IntPhys 2, 44.5% MVP, against 96.44% / 92.9% human | Meta companion benchmarks, arXiv:2506.09849 and 2506.09987 | high — but model scores cluster in the low-to-mid 50s and sources disagree on which model leads |

Links: numbers [../verified-numbers.md](../verified-numbers.md) · source
[../sources/lecun-eth-2026.md](../sources/lecun-eth-2026.md) · map [../map.md](../map.md)
