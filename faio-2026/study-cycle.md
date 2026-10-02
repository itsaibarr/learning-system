# Study Cycle: FAIO 2026 — Qualifier sprint

Dates: 2026-09-08 → 2026-09-20 (13 days; long for a cycle, but it ends at the exam)
Goal this cycle: every archived hand-maths and stdin task passes its checker under its
time cap, the sklearn pipeline runs end to end on three data shapes, and both team mocks
are scored under the 4-hour clock.

Rows are the daily table in the `aibar` repo, `tasks/plan.md`.

| # | Task | Type | Done | Evidence |
| --- | --- | --- | --- | --- |
| 1 | Tue 09-08 — setup: env, accounts, datasets, organiser message, kickoff to teammates | practice | ☐ | `import` check exits 0; 37/37 in `tests/faio`; kickoff message sent |
| 2 | Wed 09-09 — maths by hand: q25_1–3, q24A, B, E, H, m24A; probability/stats note read back | practice | ☐ | 8/8 checker passes; times in the log header |
| 3 | Thu 09-10 — stdin/stdout: q24C, D, F, G, I, J, m24B, 15 min each | practice | ☐ | 7/7 pass under 1 s on the largest generated tests; 3 format rules in the standing rules |
| 4 | Fri 09-11 — tabular template + language ID (q25_4): char n-gram TF-IDF + logreg, 5-fold CV | practice | ☐ | CV accuracy recorded; `submission_check.py` validates the file |
| 5 | Sat 09-12 — IMU time series (q25_5) and shape counting (q25_6, OpenCV contours) | practice | ☐ | Two validated submission files; local metric each; contour score ≥0.9 on train |
| 6 | Sat 09-12 evening — k-means from given centroids (m24D) and linear SVM by GD (m24F) | practice | ☐ | k-means ≥0.95 × reference; SVM accuracy ≥0.97 |
| 7 | Sun 09-13 10:00–14:00 — **team mock #1**, six fresh tasks, contest protocol | mock | ☐ | Mock score sheet; every miss a row in the mistake log |
| 8 | Sun 09-13 15:00–16:00 — mock #1 error review, roles adjusted from observed strengths | review | ☐ | Mistake-log rows with kind + fix; roles written into the plan |
| 9 | Mon 09-14 — re-solve every mock #1 miss cold; algorithms drill set 1 (dict counting, sort keys, prefix sums, two pointers) | practice | ☐ | Re-solves pass; 4/4 drills pass |
| 10 | Tue 09-15 — algorithms drill set 2 (BFS, binary search on answer, 1-D DP, queue simulation); revisit any probability miss | practice | ☐ | 4/4 pass in ≤20 min each |
| 11 | Wed 09-16 — finals transfer: FFT pitch features + cosine retrieval on Colab; 30-min team sync | practice | ☐ | One scored late submission on each; sync notes (roles, laptops, submission protocol) |
| 12 | Thu 09-17 — recommender baseline and JSON-lookup QA, 90 min each | practice | ☐ | Baselines produce valid files; one lesson each in `faio/notes/finals-transfer.md` |
| 13 | Fri 09-18 16:30–20:30 — **team mock #2**, six unseen tasks; review 20:30–21:00; 48-h protocol starts | mock | ☐ | Mock #2 score sheet; mistake log complete; revision queue empty or scheduled |
| 14 | Sat 09-19 10:00–11:30 — revision queue only; registration confirmed before 18:00; laptops checked | review | ☐ | Every item in `faio/contest-checklist.md` ticked by 20:00 |
| 15 | Sun 09-20 10:00–14:00 — **qualifier** | mock | ☐ | Standings screenshot; log filled the same evening |

Rules:
- Every cycle mixes learning with **retrieval practice** — a cycle of only
  reading/watching is invalid by construction.
- "Done" requires evidence, not attendance.
- End of cycle → weekly review; unfinished tasks are re-decided, never auto-rolled.

Links: brief faio-2026/learning-brief.md · mistake log faio-2026/mistake-log.md · map [[Maps/FAIO-2026]]
