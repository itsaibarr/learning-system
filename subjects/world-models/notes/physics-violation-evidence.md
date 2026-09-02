# Concept: what the physics-violation evidence actually shows

> Rewritten 2026-09-02 after recomputation from Meta's released per-video CSVs. The first draft
> of this note took the headline 98% at face value. It does not survive its own protocol.

**In one sentence:** Representation-space surprise is a real but readout-dependent signal that
survives the field's best low-level control on its easiest synthetic benchmark, and does not
survive photorealism, real lab video, absolute calibration, or several individual physical
principles — which is what a good anomaly detector looks like, not physical understanding.

**Hangs off:** [surprise-is-not-understanding.md](surprise-is-not-understanding.md) — the confound
says a spike may track unfamiliarity rather than impossibility.

**The click:** a likelihood-shaped score **has no modal category**. It can represent *"rarely
happens."* It cannot represent *"cannot happen."* That is not a measurement problem to be
engineered away; it is the shape of the instrument.

## The headline, and what the protocol does to it

| | Value |
| --- | --- |
| V-JEPA ViT-H, IntPhys, **relative** (rank the odd one out in a matched quadruplet) | **98.33%** — dev split, per-property *max* over six context lengths |
| Same model, same items, **absolute** (single video, calibrated threshold) | **68.06%** |
| Same model, absolute, GRASP / InfLevel-lab | ~52.0% / ~52.8% (untrained ≈ 50.0–50.7%) |
| Untrained ViT-L control, 20 seeds | 51.44 ± 0.67 |

Humans also lose 8–17 points moving relative → absolute, so absolute failure is *partly* a
property of the protocol. The informative quantity is therefore the model-versus-human **gap
profile**, never the raw drop.

## The aggregation is doing argumentative work

| | fixed context | after max-over-contexts |
| --- | --- | --- |
| V-JEPA-H, GRASP | 51.1–57.5% | 66.36% |
| 20 untrained ViT-L controls, GRASP | 48.7–49.7% | **55.9%** |

The published "untrained networks" bar is itself partly a selection artifact. The defensible GRASP
effect is roughly **8 points over control at fixed context**, not the ~10.5 the headline implies.
Any single-number claim needs a held-out context-selection protocol first.

## Per-property: present, absent, and inverted

| Principle | V-JEPA | Untrained control |
| --- | --- | --- |
| InfLevel object permanence | 72.1 | 52.5 |
| InfLevel **gravity** | 50.4 ± 0.4 | 51.0 ± 1.5 |
| InfLevel **solidity** | 51.4 ± 1.3 | 51.9 ± 1.7 |
| GRASP colour constancy | 58.1 | **63.9** — below random init |
| GRASP "Unchangeableness", long contexts | **0.00–5.47%** | — |

That last row is the most interesting result in the whole literature and nobody has explained it:
the model is **reliably more surprised by the physically legal video**. A consistent sign error,
not noise — and the max-over-contexts aggregation conceals it inside a 58–65% category bar.

## What genuinely survives — the matched ablation

The strongest evidence for LeCun is not the headline. It is a controlled comparison holding
architecture, data (HowTo100M) and evaluation fixed, changing **only the prediction space**:

```
  predict in pixel space            IntPhys 58.89%     (VideoMAEv2-g, independent 1B model: 59.44%)
  predict in representation space   IntPhys 91.67%
```

And unlike the headline it is *more* robust at fixed context (≈51–56% vs ≈86–91%) than under
max-selection. This is the empirical core of "predict in representation space, not pixels."

Cheap, too: ~129 hours of unique video already gives 75.6%; 1% of HowTo100M gives 94.4%; a 115M
ViT-B gives 90.6%. But the curve is **flat above 1%** (94.4 / 95.0 / 92.2 / 93.9 / 91.7) — which
cuts both ways: if a 115M model on five days of video saturates the benchmark, the benchmark may
be what is being measured.

**Watch out:** InfLevel forbids training, fine-tuning *and linear probing* by design, on the
stated grounds that a probe confounds physical understanding with feature extraction. That is the
benchmark's authors independently reaching the conclusion about probes reached here on 2026-09-02.

Links: [../paper-evidence-map.md](../paper-evidence-map.md) · [../benchmarks.md](../benchmarks.md)
· [../verified-numbers.md](../verified-numbers.md) · map [../map.md](../map.md)
