# Decision Log: LLM context windows

| Date | Decision | Why | Revisit when |
| --- | --- | --- | --- |
| 2026-08-31 | Test "Lost in the Middle" on a current model myself instead of trusting the 2023 result | positional retrieval quality directly changes how I prompt daily | switching primary model |
| 2026-08-31 | Put task instructions and key facts at the edges of long prompts | experiment.md confirmed middle-position degradation | model cards claim uniform retrieval |
