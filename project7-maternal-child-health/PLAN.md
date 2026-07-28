# Project 7 — Maternal & Child Health Outcomes: Group Plan

Mini-project development window (per training schedule): **July 27 – Aug 5, 2026**.
Final presentation: **August 7, 2026**.

## Tasks (from Project_7.md)

| # | Task | Owner | Status |
|---|------|-------|--------|
| 1 | Predict maternal risk level from clinical measurements (UCI Maternal Health Risk) | John Andrew & Jared Onsomu | Done |
| 2 | Describe how Kenyan maternal/child indicators (stunting, skilled birth attendance, immunisation) vary by region & wealth quintile (DHS/UNICEF) | Kevinson Mwangi & Elphas Abok | In progress — national stunting done (17.4%), county-level/immunisation/skilled birth attendance/wealth quintile still pending |
| 3 | Audit the risk model for fairness across age groups & check calibration | John Andrew & Jared Onsomu | Done — on `task3-fairness-calibration` branch, pending review/merge |
| 4 | Discuss where to target interventions | TBD | Not started |

Every member should be able to explain the whole project, not just their own task.

## Workflow

- One feature branch per task (e.g. `task1-risk-classifier`), merged via PR.
- Track task breakdown with GitHub issues.
- Do not commit raw data — scripts fetch it on demand (`scripts/download_data.py`).
- Pin dependencies in `requirements.txt`.

### Branch flow

```
upstream/main   (ENEZA-DSI/Eneza-Data-Science-Residential-training-2026 — the org repo)
      ↓  fork
your main       (andyombogo/Eneza-Data-Science-Residential-training-2026, branch: main)
      ↓  branch
project7-setup  (this project's integration branch — everyone's task branches merge here)
      ↓  branch
task branches   (e.g. task2-regional-indicators, one per task)
      ↓  PR
project7-setup  (merge task work back in)
      ↓  PR (once the whole project is ready)
upstream/main
```

Confirmed state: `origin` = `andyombogo/Eneza-Data-Science-Residential-training-2026`
(fork), `upstream` = `ENEZA-DSI/Eneza-Data-Science-Residential-training-2026`
(org repo); `main` is in sync with `upstream/main` (no drift). `project7-setup`
is the integration branch — the Streamlit app is deployed from it, so **don't
rename it** without updating the Streamlit Cloud app's branch setting too. Note
this repo's own naming is `project7-setup`, not `project-7` — same role, just
that name; rename only if the team wants to, since it'd need a matching update
on the live deploy.

`task2-regional-indicators` followed this correctly (branched off
`project7-setup`) and has now been merged back in. `task3-fairness-calibration`
follows it too (pushed, awaiting your review/merge). Task 1's work was
committed directly to `project7-setup` rather than through its own task
branch + PR — a gap versus the intended workflow above, left as-is since
it's already merged, but the branch-per-task pattern is now the norm for
Tasks 2 onward. Collaborators need push access to `origin` to work this way
(see repo Settings → Collaborators) — otherwise they fork `origin`
themselves and PR into `project7-setup`.

**Task 3 method note:** audits the Task 1 model using out-of-fold
predictions across the full 1,014-row dataset (5-fold CV, same tuned
config as production) rather than only the 203-row test set — the
smallest age/class subgroup has as few as ~39 cases, too little for a
trustworthy fairness comparison from the test set alone. See
`src/task3_fairness_audit.py` (shared by the notebook and the Streamlit
page) and `notebooks/task3_fairness_calibration_audit.ipynb` for the full
derivation. Headline finding: a real (bootstrap-CI-supported) fairness gap
— the model catches ~85% of true high-risk cases among mothers under 20,
vs. ~96% for the 20–34 reference group.

**Task 2 data note:** the KDHS 2022 microdata (`KEKR8BFL.DTA`) used for this
analysis is restricted-access (DHS Program data request), unlike Task 1's
openly downloadable UCI dataset — it isn't and can't be committed or
fetched by a script. Only the aggregate, non-identifying results derived
from it live in the repo (`project7-maternal-child-health/data/processed/`),
consumed by the Task 2 Streamlit page. See
`notebooks/task2_regional_indicators.qmd` for the R analysis source (needs
R + the restricted data file to actually run) and that JSON file's own
notes for exactly what's computed vs. still pending.

## Deliverables checklist

- [x] Reproducible notebook (Task 1: `notebooks/task1_risk_classifier_eda.ipynb`; Task 3: `notebooks/task3_fairness_calibration_audit.ipynb`)
- [ ] Disaggregated EDA (region / wealth quintile) — Task 2: national stunting done, county-level/wealth-quintile pending
- [x] Predictive model (Task 1) / [x] subgroup equity & calibration audit (Task 3, pending merge)
- [ ] Report with ethics / Data Protection notes + each member's role
