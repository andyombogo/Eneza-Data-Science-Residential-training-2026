# Project 7 — Maternal & Child Health Outcomes: Group Plan

Mini-project development window (per training schedule): **July 27 – Aug 5, 2026**.
Final presentation: **August 7, 2026**.

## Tasks (from Project_7.md)

| # | Task | Owner | Status |
|---|------|-------|--------|
| 1 | Predict maternal risk level from clinical measurements (UCI Maternal Health Risk) | John Andrew & Jared Onsomu | Done |
| 2 | Describe how Kenyan maternal/child indicators (stunting, skilled birth attendance, immunisation) vary by region & wealth quintile (DHS/UNICEF) | Kevinson Mwangi & Elphas Abok | Not started |
| 3 | Audit the risk model for fairness across age groups & check calibration | TBD | Not started |
| 4 | Discuss where to target interventions | TBD | Not started |

Every member should be able to explain the whole project, not just their own task.

## Workflow

- One feature branch per task (e.g. `task1-risk-classifier`), merged via PR.
- Track task breakdown with GitHub issues.
- Do not commit raw data — scripts fetch it on demand (`scripts/download_data.py`).
- Pin dependencies in `requirements.txt`.

## Deliverables checklist

- [x] Reproducible notebook (Task 1: `notebooks/task1_risk_classifier_eda.ipynb`)
- [ ] Disaggregated EDA (region / wealth quintile) — Task 2
- [x] Predictive model (Task 1) / [ ] subgroup equity & calibration audit — Task 3
- [ ] Report with ethics / Data Protection notes + each member's role
