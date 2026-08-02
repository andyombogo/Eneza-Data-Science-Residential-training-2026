# Ethics & Data Protection

Required by the project brief's deliverables list ("report with ethics /
Data Protection notes"). This project works with restricted, individual-
level survey microdata and produces county-level findings intended to
influence resource allocation — both carry real obligations.

## KDHS microdata handling

- The KDHS 2022 Kids' Recode file is obtained only via an approved data
  request to The DHS Program, under their data-use agreement.
- It is **never committed to this repository** at any pipeline stage —
  `data/raw/` (the raw file and all individual-level intermediates produced
  by `scripts/clean_data.R` / `compute_indicators.R`) is gitignored
  unconditionally.
- Only aggregate, non-identifying outputs (county-level prevalence + CIs,
  wealth-quintile summaries) are committed to `data/processed/`. No output
  in this repository can be traced back to an individual respondent,
  household, or cluster.
- County-level estimates carry design-based confidence intervals precisely
  so that low-certainty estimates (small cluster counts) aren't presented
  with false precision — see `docs/methodology.md`.

## Kenya Data Protection Act, 2019

This project does not currently process real-time or facility-level patient
data. If future work extends this analysis with Kenyan facility records or
any other personally identifiable health data, that work must be reviewed
against the Data Protection Act, 2019 before it begins — in particular its
requirements around lawful basis for processing, data minimisation, and
data subject rights. This is a forward-looking note, not a compliance claim
about the current KDHS-only analysis (KDHS microdata is already
de-identified and access-controlled by DHS's own agreement).

## Responsible use of the intervention ranking

The Task 4 prioritization (`data/processed/task4_priority_counties.csv`) is
a **prioritization signal, not a causal finding** — see the explicit caveat
on the Policy Recommendations app page. Two risks this creates if the
ranking is used carelessly:

- **Treating a wide-confidence-interval county the same as a narrow one.**
  The app and `docs/methodology.md` surface CI width alongside every
  ranking specifically so resourcing decisions don't over-read noisy
  estimates as certain ones.
- **Treating "not flagged" as "no need."** The v1 threshold (national + 1
  SD) is a starting point for prioritization, not a certification that
  unflagged counties have no gap — many counties above the national average
  but below the flag threshold still have a real, just less extreme, gap.

## Roles

See `README.md` § Team for current task ownership and `PLAN.md` for the
group's branch/review workflow.
