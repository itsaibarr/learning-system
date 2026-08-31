# Experiment: does position in context change retrieval quality?

Decision-log rows: see `decision-log.md` in this folder.

**Objective question:** If the same fact sits at the start, middle, or end of a long
prompt, does answer accuracy change?

**Smallest experiment:** one script, one model, one fact ("the vault key is 7381")
planted at 3 positions inside ~20k tokens of filler; 10 trials per position; ask for
the key; score exact match.

**Observed (what changed and why):** start/end retrieval near-perfect; middle
measurably worse — consistent with Liu et al. even on a newer model. Practical
consequence adopted: put task instructions and key facts at the edges of long prompts.

**Explain-back check (playbook §4 step 4):** passed — explained why attention makes
middle positions hardest without notes; quiz-checked on the causal-mask distinction.

**Card-worthy principle (recurring, not one-off):** edge placement of critical
context — drafted under tag `context-windows`.
