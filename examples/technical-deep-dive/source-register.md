# Source Register: LLM context windows

| Source | Type | Reliability | Last checked | Used for |
| --- | --- | --- | --- | --- |
| Vaswani et al., "Attention Is All You Need" (arXiv:1706.03762) | primary | high | 2026-08-31 | attention-cost node |
| Su et al., "RoFormer: Rotary Position Embedding" (arXiv:2104.09864) | primary | high | 2026-08-31 | position-encoding node |
| Liu et al., "Lost in the Middle" (arXiv:2307.03172) | primary | high | 2026-08-31 | experiment design |
| Anthropic docs — context windows | vendor | high | 2026-08-31 | token accounting, caching behavior |

Rules: primary > secondary > vendor. Drop rows that were never used. A source worth
reading deeply gets its own note in vault `Sources/`, linked here.
