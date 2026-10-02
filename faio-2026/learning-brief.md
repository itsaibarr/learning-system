# Learning Brief: FAIO 2026 (Fizmat AI Olympiad)

Created: 2026-09-08 · Status: done (qualifier 2026-09-20 over; archived 2026-10-03)

| Field | Value |
| --- | --- |
| Why this, why now | Online qualifier is Sun 2026-09-20, 10:00–14:00 Astana, on Yandex.Contest; the final is 26–29 Oct in Almaty and only the qualifier stands between the team and it |
| Target outcome | Team scores in the top 50 of the online qualifier; I solve every hand-maths and stdin task in the archive under the time caps in `faio/practice/README.md` |
| Deadline / cadence | Qualifier 2026-09-20 · final 2026-10-26→29 · weekday blocks 2.5–3 h after school, weekends 4–6 h |
| Current level | See "Strand floors and ceilings" below — from the 2026-09-08 audit, **untested** until probed |
| Constraints | School until ~15:35 on weekdays; blocks end by 19:30; fixed Daryn blocks Sep 14–15; mocks Sun 2026-09-13 10:00–14:00 and Fri 2026-09-18 16:30–20:30; team of 3 with unknown teammate skills |
| Map | [[Maps/FAIO-2026]] |
| Active cycle | faio-2026/study-cycle.md |
| Quiz surface | vault `Reviews/` — questions as checkbox notes; see decision-log 2026-09-08 |

## Strand floors and ceilings

Ratings below are read off the readiness table in the audit (`aibar` repo,
`faio/audit-2026-09-08.md` §3), not off a probe. Every row is **untested** until the
probe writes a bracketed floor/ceiling into it.

| Strand | From the audit | Probe status |
| --- | --- | --- |
| Probability, expectation, Bayes | Strong on paper (A-Level Maths + Further Maths, Altyn Tulek 3rd) but no stats-specific practice on record | untested |
| Descriptive statistics (mean/median/mode/std/IQR/z-score) | Same evidence base; no artefact | untested |
| Linear algebra, least squares, coordinate geometry | Strong on paper | untested |
| Python I/O under 1 s / 64 MB limits | Adequate; stdin/stdout contest format is new | untested |
| sklearn pipeline (load → CV → predict → CSV) | Unproven — no pandas/sklearn artefact anywhere | untested |
| Feature engineering: text, time series, images | Gap; qualifier-level versions are feature engineering, not deep learning | untested |
| Contest platforms (Yandex.Contest, Kaggle) | Gap — one evening fixes it | untested |

## Open gaps
- Teammates' names and current skills — blocks role assignment (B tabular/text, C CV/signal)
- LLM and pretrained-model rules for the online round — organisers say "announced in the participants' chat"; internet and documentation are confirmed allowed (organiser email 2026-09-08)
