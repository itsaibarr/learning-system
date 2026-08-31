# Concept: why context length is expensive

**In one sentence:** Self-attention compares every token with every other token, so
compute grows with the square of sequence length — the context window is a cost
ceiling, not an arbitrary limit.

**Hangs off:** "a transformer processes tokens, not text" — attention is defined
pairwise over those tokens, so quadratic growth follows from the definition.

**The click:** "context window" stopped being a product spec and became $O(n^2)$
attention plus a KV cache that grows linearly with every generated token.

| Claim | Evidence / derivation | Confidence |
| --- | --- | --- |
| Attention cost scales $O(n^2 \cdot d)$ with sequence length $n$ | Vaswani et al. §4, complexity table | high |
| Inference caches per-token keys/values (KV cache), so long contexts cost memory even after prefill | standard transformer inference; Anthropic docs on prompt caching | high |

**Watch out:** I assumed models "re-read" the whole prompt each generated token from
scratch — the KV cache is exactly what avoids that.

Links: register source-register.md · cards: tag `context-windows` · experiment experiment.md
