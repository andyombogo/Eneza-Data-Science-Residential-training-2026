# Project 7 — Maternal & Child Health Outcomes

**Task 1: Predict a mother's risk level from routine clinical measurements**
(age, blood pressure, blood sugar, heart rate)

Part of the [Eneza Data Science Residential Training 2026](../README.md) mini-project
on maternal & child health outcomes ([full brief](../Project_7.md), [group plan](PLAN.md)).
This README documents Task 1 in detail; see `PLAN.md` for how it fits into the
project's other three tasks (regional/wealth disaggregation, fairness & calibration
audit, and intervention targeting).

## 1. Problem statement

Maternal mortality is often preventable when at-risk pregnancies are flagged early.
Task 1 builds a classifier that predicts a mother's **risk level** — `low risk`,
`mid risk`, or `high risk` — from six routine clinical measurements that can be
collected at a basic antenatal visit, without lab infrastructure:

| Feature       | Description                          | Unit    |
|---------------|---------------------------------------|---------|
| `Age`         | Mother's age                          | years   |
| `SystolicBP`  | Upper blood pressure reading          | mmHg    |
| `DiastolicBP` | Lower blood pressure reading          | mmHg    |
| `BS`          | Blood glucose level                   | mmol/L  |
| `BodyTemp`    | Body temperature                      | °F      |
| `HeartRate`   | Resting heart rate                    | bpm     |

Target: `RiskLevel` ∈ {`low risk`, `mid risk`, `high risk`}.

This model is a **decision-support screening tool**, not a diagnostic device — see
[Limitations & ethics](#7-limitations--ethical-considerations).

## 2. Dataset

- **Source:** [UCI Maternal Health Risk Data Set](https://archive.ics.uci.edu/dataset/863/maternal+health+risk) (id `863`), collected from rural health facilities and hospitals in Bangladesh via IoT-based risk monitoring.
- **Size:** 1,014 rows × 7 columns (6 features + target).
- **Class balance:** low risk 406 (40%), mid risk 336 (33%), high risk 272 (27%) — moderately imbalanced but not severe.
- **Access:** not committed to the repo (see `.gitignore`). Fetched on demand via `scripts/download_data.py`, which pulls it through the [`ucimlrepo`](https://pypi.org/project/ucimlrepo/) package and writes it to `data/raw/maternal_health_risk.csv`.

## 3. Repository layout

```
project7-maternal-child-health/
├── PLAN.md                       # group task breakdown, owners, workflow
├── requirements.txt               # pinned Python dependencies
├── scripts/
│   └── download_data.py          # fetches raw dataset from UCI repo (not committed)
├── src/
│   └── task1_risk_classifier.py  # Task 1: train + evaluate the risk classifier
├── data/
│   └── raw/                      # gitignored — populated by download_data.py
└── models/
    └── risk_classifier.joblib    # gitignored — trained model artifact
```

## 4. Setup

Requires Python 3.10+.

```bash
# from project7-maternal-child-health/
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## 5. Reproducing the results

```bash
# 1. Download the raw dataset (writes data/raw/maternal_health_risk.csv)
python scripts/download_data.py

# 2. Train and evaluate the classifier (writes models/risk_classifier.joblib)
python src/task1_risk_classifier.py
```

Running `task1_risk_classifier.py` will:

1. Load `data/raw/maternal_health_risk.csv` (raises `FileNotFoundError` with a
   clear message if the download step hasn't been run yet).
2. Split into train/test sets (80/20, stratified by `RiskLevel`, `random_state=42`
   for reproducibility).
3. Train a `RandomForestClassifier` (300 trees) on the six clinical features.
4. Print a confusion matrix and a per-class precision/recall/F1 classification
   report on the held-out test set.
5. Save the fitted model to `models/risk_classifier.joblib` for reuse (e.g. by
   the Task 3 fairness/calibration audit).

## 6. Modelling approach

- **Algorithm:** Random Forest was chosen as a strong, low-effort baseline for
  small tabular clinical data — it handles non-linear interactions between
  vitals (e.g. BP × blood sugar) without feature scaling, and gives a sensible
  feature-importance readout for clinical interpretability.
- **Evaluation:** stratified train/test split with per-class precision/recall/F1
  and a confusion matrix, since misclassifying `high risk` as `low risk` is far
  costlier than the reverse — overall accuracy alone would hide that.
- **Reproducibility:** a fixed `random_state=42` is used for both the split and
  the model so results are deterministic across runs.

### Suggested extensions (not yet implemented)

- Compare against a simpler baseline (logistic regression) and a gradient-boosted
  model to sanity-check whether the Random Forest's extra complexity is earning
  its keep.
- Hyperparameter tuning via cross-validation (current settings are reasonable
  defaults, not tuned).
- Feature importance / SHAP analysis to check the model is leaning on clinically
  plausible signals (e.g. blood sugar and BP should dominate over heart rate).

## 7. Limitations & ethical considerations

- **Not a clinical diagnostic tool.** This model supports triage/screening
  discussions; it must not replace clinical judgement or be deployed without
  supervision by qualified health workers.
- **Population mismatch risk.** The training data comes from health facilities
  in Bangladesh. Vitals thresholds and risk patterns may not transfer directly
  to a Kenyan population — this is a key caveat to flag before any real-world
  use, and motivates the fairness/calibration audit in Task 3.
- **Class imbalance & cost asymmetry.** `high risk` is the minority class
  (27%) and also the class where false negatives (predicting `low`/`mid` when
  truly `high risk`) are most dangerous. Recall on `high risk` should be
  scrutinised specifically, not just overall accuracy.
- **Fairness across subgroups.** Task 3 (see `PLAN.md`) audits this model's
  performance and calibration across age groups to check it doesn't
  systematically under- or over-flag risk for any subgroup.
- **Data protection.** Although this dataset is de-identified and public,
  any future work with real patient-level data (e.g. Kenyan facility records)
  must follow the Kenya Data Protection Act, 2019, and be documented in the
  project's ethics/Data Protection notes.

## 8. Status

Implemented: data download script, Random Forest baseline, train/test evaluation
with confusion matrix + classification report, saved model artifact.

See `PLAN.md` for the status of Tasks 2–4 (regional/wealth EDA, fairness &
calibration audit, intervention targeting) and for task ownership within the
group.
