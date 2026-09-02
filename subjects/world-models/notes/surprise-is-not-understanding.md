# Concept: surprise is not understanding

**In one sentence:** A world model's prediction error spiking on an impossible video shows it
registered something *unfamiliar*, not that it knows which physical law broke — because
impossibility entails unfamiliarity, the two cannot be separated by the spike alone.

**Hangs off:** [map.md](../map.md) U6 — an event absent from training is unfamiliar whatever the
reason it was absent. Physical impossibility is one such reason, so every impossible clip is also
an unfamiliar one, by construction rather than by accident.

**The click:** prediction error is a *novelty detector*. Impossibility is one cause of novelty,
not the only one — a ferrofluid clip is perfectly legal and would spike just as hard. And matched
pairs cannot rescue it: the violation **is** the novelty, so the two properties are logically
entangled, not merely correlated.

**The inversion this forces:** the vivid result is the weak one. A novelty detector can produce a
surprise spike; it cannot forecast where a thrown object lands, and it cannot answer a
counterfactual. So evidence for understanding is *stronger* the more boring it looks —

```
  weakest   error(impossible) > error(possible)          a novelty detector produces this
     ↓      probe separates possible from impossible     same disputed signal, measured better
     ↓      selective failure across violation types     structure a novelty detector lacks
  strongest frozen repr. → trajectory / depth readout,   requires carrying state forward
            generalizing to unseen masses
```

| Claim | Evidence / derivation | Confidence |
| --- | --- | --- |
| V-JEPA's internal prediction error spikes on physically impossible video | LeCun, ETH Zürich 2026-05-29 — sliding 16-frame window; his example is a thrown ball that vanishes. He hedges: the system "understands", in his own audible scare quotes | high (claim is his; the interpretation is what is contested) |
| The talk offers no control for the novelty explanation | Same source — no matched-statistics condition is described, no benchmark protocol or chance baseline given | high |
| Information maximization has no usable lower bound | Same source — LeCun states every empirical measure is an *upper* bound, so one maximizes an upper bound and hopes | high (his own admission) |
| Selective failure across violation types is the discriminating test | Derivation, not citation: a pure novelty detector should fire uniformly, so an uneven competence profile is structure it cannot produce | medium — pending the V-JEPA physics paper |

**Watch out:** a linear probe on the frozen representation is *not* a control here. It separates
the clips using the very novelty signal in dispute, so both explanations predict it succeeds. An
experiment is a control only when the competing explanations predict **different** outcomes.

Links: source [lecun-eth-2026.md](../sources/lecun-eth-2026.md) · cards: tag `world-models`
