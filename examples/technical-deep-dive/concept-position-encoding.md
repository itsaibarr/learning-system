# Concept: position must be injected

**In one sentence:** Attention itself is order-blind (a set operation), so every
transformer must inject token position separately — and *how* it's injected (e.g.
RoPE's rotation by position) is what makes extending a trained context window hard.

**Hangs off:** [[concept-attention-cost]] — attention compares token pairs; nothing in
that comparison encodes which came first.

**The click:** "why can't you just run it on longer input?" answered itself: positions
beyond training range produce rotations the model never saw.

| Claim | Evidence / derivation | Confidence |
| --- | --- | --- |
| Removing position information makes attention permutation-invariant | follows from the attention definition (softmax over pairwise dot products) | high |
| RoPE encodes relative position by rotating query/key vectors as a function of absolute position | Su et al., §3 | high |

**Watch out:** "the model reads left to right" — only the *causal mask* gives
direction; attention weights themselves have no inherent order.

Links: register source-register.md · cards: tag `context-windows`
