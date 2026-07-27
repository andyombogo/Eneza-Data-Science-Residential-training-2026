# Project 7 — Maternal & Child Health Outcomes

### Task 1: Predict a mother's risk level from routine clinical measurements

Part of the [Eneza Data Science Residential Training 2026](../README.md) mini-project
on maternal & child health outcomes ([full brief](../Project_7.md), [group plan](PLAN.md)).
This README documents Task 1 in full; see `PLAN.md` for how it fits into the
project's other three tasks (regional/wealth disaggregation, fairness &
calibration audit, and intervention targeting) and for group ownership.

**Task 1 owners:** John Andrew, Jared Onsomu.

## At a glance

| | |
|---|---|
| **Question** | Given age, blood pressure, blood sugar, body temperature and heart rate, is a mother `low`, `mid`, or `high` risk? |
| **Data** | [UCI Maternal Health Risk](https://archive.ics.uci.edu/dataset/863/maternal+health+risk) — 1,014 rows, 6 features, 3 classes |
| **Model** | Random Forest (tuned) — chosen over Logistic Regression and Gradient Boosting after cross-validated comparison, not by default |
| **Result** | 86.2% test accuracy; **94.5% recall on `high risk`**, the class that matters most operationally |
| **Reproduce** | `python scripts/download_data.py && python src/task1_risk_classifier.py`, or open `notebooks/task1_risk_classifier_eda.ipynb` |

## Contents

1. [Problem statement](#1-problem-statement)
2. [Dataset](#2-dataset)
3. [Repository layout](#3-repository-layout)
4. [Setup](#4-setup)
5. [Reproducing the results](#5-reproducing-the-results)
6. [Why a stratified train/test split](#6-why-a-stratified-traintest-split)
7. [Modelling approach: choosing and tuning the model](#7-modelling-approach-choosing-and-tuning-the-model)
8. [Results](#8-results)
9. [Limitations & ethical considerations](#9-limitations--ethical-considerations)
10. [Status](#10-status)

## 1. Problem statement

Maternal mortality is often preventable when at-risk pregnancies are flagged
early. Task 1 builds a classifier that predicts a mother's **risk level** —
`low risk`, `mid risk`, or `high risk` — from six routine clinical measurements
that can be collected at a basic antenatal visit, without lab infrastructure:

| Feature       | Description                  | Unit    |
|---------------|-------------------------------|---------|
| `Age`         | Mother's age                  | years   |
| `SystolicBP`  | Upper blood pressure reading  | mmHg    |
| `DiastolicBP` | Lower blood pressure reading  | mmHg    |
| `BS`          | Blood glucose level           | mmol/L  |
| `BodyTemp`    | Body temperature              | °F      |
| `HeartRate`   | Resting heart rate            | bpm     |

Target: `RiskLevel` ∈ {`low risk`, `mid risk`, `high risk`}.

This model is a **decision-support screening tool**, not a diagnostic device —
see [Limitations & ethics](#9-limitations--ethical-considerations).

## 2. Dataset

- **Source:** [UCI Maternal Health Risk Data Set](https://archive.ics.uci.edu/dataset/863/maternal+health+risk) (id `863`), collected from rural health facilities and hospitals in Bangladesh via IoT-based risk monitoring.
- **Size:** 1,014 rows × 7 columns (6 features + target).
- **Class balance:** low risk 406 (40%), mid risk 336 (33%), high risk 272 (27%) — moderately imbalanced, which is why the split strategy in Section 6 matters.
- **Access:** not committed to the repo (see `.gitignore`). Fetched on demand via `scripts/download_data.py`, which pulls it through the [`ucimlrepo`](https://pypi.org/project/ucimlrepo/) package and writes it to `data/raw/maternal_health_risk.csv`.

## 3. Repository layout

```
project7-maternal-child-health/
├── PLAN.md                       # group task breakdown, owners, workflow
├── requirements.txt               # pinned Python dependencies
├── scripts/
│   └── download_data.py          # fetches raw dataset from UCI repo (not committed)
├── src/
│   └── task1_risk_classifier.py  # Task 1: load data, split, train, evaluate, save model
├── notebooks/
│   └── task1_risk_classifier_eda.ipynb  # Task 1: EDA, model comparison, tuning, evaluation
├── data/
│   └── raw/                      # gitignored — populated by download_data.py
└── models/
    └── risk_classifier.joblib    # gitignored — trained model artifact
```

## 4. Setup

Requires Python 3.10+. Dependencies are pinned in `requirements.txt` for
reproducibility.

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

# 3. (optional) open the full EDA + model-selection notebook
jupyter lab notebooks/task1_risk_classifier_eda.ipynb
```

Running `task1_risk_classifier.py` will:

1. Load `data/raw/maternal_health_risk.csv` (raises `FileNotFoundError` with a
   clear message if the download step hasn't been run yet).
2. Split into train/test sets via `split_data()` — 80/20, **stratified** by
   `RiskLevel`, `random_state=42` for reproducibility (why: Section 6).
3. Train a `RandomForestClassifier` with hyperparameters chosen by the grid
   search in the notebook (Section 7 below).
4. Print a confusion matrix and a per-class precision/recall/F1 classification
   report on the held-out test set.
5. Save the fitted model to `models/risk_classifier.joblib` for reuse (e.g. by
   the Task 3 fairness/calibration audit).

`notebooks/task1_risk_classifier_eda.ipynb` imports `load_data` / `split_data` /
`train` directly from `src/task1_risk_classifier.py` — one source of truth for
data loading and the train/test split — and builds the full narrative on top:
data-quality checks, class-balance and per-feature distribution plots, a
correlation heatmap, a live demonstration of why the split is stratified, a
cross-validated comparison of three candidate algorithms, a hyperparameter
search, and final evaluation with a feature-importance chart. It is committed
with outputs already populated; run `download_data.py` first so it can find
the raw CSV, and re-run the notebook if you want fresh numbers after a code
change.

## 6. Why a stratified train/test split?

`RiskLevel` is imbalanced (Section 2: ~40/33/27%). `train_test_split(...,
stratify=y)` forces the train and test sets to each preserve that same ratio.
Without it, a single unlucky random split could under-represent `high risk` in
the test set — the class where a missed detection is most costly — making its
recall estimate unreliable.

The notebook demonstrates this rather than just asserting it: it draws 20
random 80/20 splits *without* stratification and compares the `high risk`
test-set share against the stratified split actually used for training.

| | `high risk` share of test set |
|---|---|
| True population share | 26.8% |
| Stratified split (`random_state=42`, used for training) | 27.1% |
| 20× unstratified splits | mean 27.6%, **range 23.2% – 31.5%** |

With only ~270 high-risk rows to begin with, an 80/20 split leaves just ~55 in
the test fold — small enough that luck-of-the-draw shifts the minority-class
share by several points. Stratification pins it to the true ratio, which is
what makes the `high risk` recall figure reported in Section 8 trustworthy
rather than a roll of the dice.

## 7. Modelling approach: choosing and tuning the model

Random Forest was **not** picked by default — the notebook cross-validates
three candidates on the training split (5-fold stratified, evaluated on
accuracy and macro recall/F1 so the majority `low risk` class can't hide a
weak `high risk` score) before choosing one to tune:

| Model | What it is | Why it might win here | Why it might lose here |
|---|---|---|---|
| **Logistic Regression** | Linear baseline (scaled features) | Fast, directly interpretable via coefficients | Assumes roughly linear risk boundaries; the EDA shows `BS` behaves more like a threshold than a smooth linear signal |
| **Random Forest** | Ensemble of independent decision trees | Captures non-linear thresholds and feature interactions (e.g. "high BP *and* high BS") without needing feature scaling | Less directly interpretable than a linear model (mitigated with feature importances, Section 8 results) |
| **Gradient Boosting** | Trees built sequentially to correct prior errors | Can outperform Random Forest on some tabular problems | More hyperparameters to get wrong; higher overfitting risk on a dataset this size (~1,000 rows) |

**Cross-validated results (5-fold, training split only):**

| Model | CV accuracy | CV recall (macro) | CV F1 (macro) |
|---|---|---|---|
| **Random Forest** | 0.815 | 0.819 | **0.819** |
| Gradient Boosting | 0.788 | 0.789 | 0.792 |
| Logistic Regression | 0.620 | 0.614 | 0.607 |

The linear baseline is clearly outmatched (macro F1 0.61 vs 0.79–0.82),
confirming the EDA's read that risk boundaries here aren't linear. Random
Forest edges out Gradient Boosting and is preferred whenever the two are
close, since it overfits less readily on a dataset this small and needs less
tuning to reach its ceiling.

**Hyperparameter tuning:** a grid search over `n_estimators` (200/300/500),
`max_depth` (None/10/20), and `min_samples_leaf` (1/2/4) — 27 candidates,
5-fold CV, scored on macro F1 — found a configuration that beats the untuned
default:

| | `n_estimators` | `max_depth` | `min_samples_leaf` | CV macro F1 |
|---|---|---|---|---|
| Untuned default | 300 | unlimited | 1 | 0.819 |
| **Tuned (shipped)** | **200** | **20** | **1** | **0.827** |

The gain is modest (+0.008), which is itself informative: the untuned default
was already close to this model family's ceiling on this dataset. The tuned
configuration is what `src/task1_risk_classifier.py` ships, since it's a free
improvement with no added inference cost.

## 8. Results

Final model (tuned Random Forest) on the held-out test set (203 rows, never
used during model selection or tuning):

| Class | Precision | Recall | F1 | Support |
|---|---|---|---|---|
| **high risk** | 0.963 | **0.945** | 0.954 | 55 |
| mid risk | 0.753 | 0.866 | 0.806 | 67 |
| low risk | 0.903 | 0.802 | 0.850 | 81 |
| **Accuracy** | | | **0.862** | 203 |

`high risk` recall (0.945) is the number that matters most operationally —
of 55 truly high-risk mothers in the test set, the model flags 52. Feature
importances confirm the model leans on `BS` and the two blood-pressure
readings most heavily, matching both the EDA and clinical expectation; full
breakdown and plots are in the notebook.

### Suggested next steps (not yet implemented)

- Probability calibration check (are predicted probabilities trustworthy, not
  just the top class?) — planned as part of the Task 3 calibration audit.
- SHAP values for per-prediction explanations, useful if this were ever shown
  to a clinician rather than just reported in aggregate.

## 9. Limitations & ethical considerations

- **Not a clinical diagnostic tool.** This model supports triage/screening
  discussions; it must not replace clinical judgement or be deployed without
  supervision by qualified health workers.
- **Population mismatch risk.** The training data comes from health facilities
  in Bangladesh. Vitals thresholds and risk patterns may not transfer directly
  to a Kenyan population — this is a key caveat to flag before any real-world
  use, and motivates the fairness/calibration audit in Task 3.
- **Class imbalance & cost asymmetry.** `high risk` is the minority class
  (27%) and also the class where false negatives (predicting `low`/`mid` when
  truly `high risk`) are most dangerous. This is why the split is stratified
  (Section 6) and why recall — not just accuracy — is reported per class
  (Section 8).
- **Fairness across subgroups.** Task 3 (see `PLAN.md`) audits this model's
  performance and calibration across age groups to check it doesn't
  systematically under- or over-flag risk for any subgroup.
- **Data protection.** Although this dataset is de-identified and public,
  any future work with real patient-level data (e.g. Kenyan facility records)
  must follow the Kenya Data Protection Act, 2019, and be documented in the
  project's ethics/Data Protection notes.

## 10. Status

**Done:** data download script, EDA (class balance, feature distributions,
correlation), a justified and cross-validated model choice, hyperparameter
tuning, final evaluation with confusion matrix + classification report +
feature importances, a live demonstration of why the split is stratified,
saved model artifact, fully executed reproducible notebook, pinned
dependencies.

**Open (optional refinements, not blockers):** probability calibration check,
per-prediction explanations (SHAP).

See `PLAN.md` for the status of Tasks 2–4 (regional/wealth EDA, fairness &
calibration audit, intervention targeting) and for task ownership within the
group.
